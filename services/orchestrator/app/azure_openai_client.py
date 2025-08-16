"""
Azure OpenAI Client Module

This module provides a client for Azure OpenAI services with integration
to the model registry and intelligent routing system.
"""

import os
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import httpx
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from tenacity import retry, stop_after_attempt, wait_exponential

from .model_registry import ModelRegistry, model_registry
from .intelligent_router import IntelligentRouter, intelligent_router, RoutingRequest

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """Chat message for OpenAI API."""
    role: str  # system, user, assistant
    content: str
    name: Optional[str] = None


@dataclass
class ChatCompletionRequest:
    """Request for chat completion."""
    messages: List[ChatMessage]
    model: Optional[str] = None  # If None, will be selected by router
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None
    stream: bool = False


@dataclass
class ChatCompletionResponse:
    """Response from chat completion."""
    content: str
    model_used: str
    tokens_used: int
    cost: float
    latency_ms: float
    finish_reason: str


@dataclass
class EmbeddingRequest:
    """Request for text embedding."""
    text: str
    model: Optional[str] = None  # If None, will be selected by router


@dataclass
class EmbeddingResponse:
    """Response from text embedding."""
    embedding: List[float]
    model_used: str
    tokens_used: int
    cost: float
    latency_ms: float


class AzureOpenAIClient:
    """
    Azure OpenAI client with intelligent routing and model registry integration.
    
    Features:
    - Automatic model selection based on routing policies
    - Budget-aware model selection with automatic downshift
    - Usage tracking and cost monitoring
    - Health monitoring and fallback handling
    - Support for user overrides
    """
    
    def __init__(self):
        self.model_registry = model_registry
        self.intelligent_router = intelligent_router
        self.clients: Dict[str, AzureOpenAI] = {}
        self.credential = DefaultAzureCredential()
        self._initialize_clients()
    
    def _initialize_clients(self) -> None:
        """Initialize Azure OpenAI clients for all models."""
        try:
            # Get endpoint and API key from environment or Key Vault
            endpoint = self._get_openai_endpoint()
            api_key = self._get_openai_api_key()
            
            if not endpoint or not api_key:
                logger.error("Failed to get OpenAI endpoint or API key")
                return
            
            # Create client for each model
            for model_name in self.model_registry.models.keys():
                try:
                    client = AzureOpenAI(
                        azure_endpoint=endpoint,
                        api_key=api_key,
                        api_version="2024-05-13"
                    )
                    self.clients[model_name] = client
                    logger.info(f"Initialized client for model: {model_name}")
                except Exception as e:
                    logger.error(f"Failed to initialize client for {model_name}: {e}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI clients: {e}")
    
    def _get_openai_endpoint(self) -> Optional[str]:
        """Get OpenAI endpoint from environment or Key Vault."""
        # Try environment variable first
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if endpoint:
            return endpoint
        
        # Try Key Vault
        try:
            key_vault_name = os.getenv("AZURE_KEY_VAULT_NAME")
            if key_vault_name:
                secret_client = SecretClient(
                    vault_url=f"https://{key_vault_name}.vault.azure.net/",
                    credential=self.credential
                )
                secret = secret_client.get_secret("OpenAI-Endpoint")
                return secret.value
        except Exception as e:
            logger.warning(f"Failed to get endpoint from Key Vault: {e}")
        
        return None
    
    def _get_openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key from environment or Key Vault."""
        # Try environment variable first
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if api_key:
            return api_key
        
        # Try Key Vault
        try:
            key_vault_name = os.getenv("AZURE_KEY_VAULT_NAME")
            if key_vault_name:
                secret_client = SecretClient(
                    vault_url=f"https://{key_vault_name}.vault.azure.net/",
                    credential=self.credential
                )
                secret = secret_client.get_secret("OpenAI-API-Key")
                return secret.value
        except Exception as e:
            logger.warning(f"Failed to get API key from Key Vault: {e}")
        
        return None
    
    def chat_completion(self, request: ChatCompletionRequest, 
                       tenant_id: str = "default",
                       feature: str = "chat",
                       user_override: Optional[str] = None) -> ChatCompletionResponse:
        """
        Generate chat completion with intelligent model routing.
        
        Args:
            request: Chat completion request
            tenant_id: Tenant identifier for routing policies
            feature: Feature name for routing policies
            user_override: Optional model override from user
            
        Returns:
            Chat completion response with model details
        """
        start_time = time.time()
        
        # Determine required capabilities
        required_capabilities = ["chat"]
        if any("vision" in msg.content.lower() for msg in request.messages):
            required_capabilities.append("vision")
        if any("tool" in msg.content.lower() for msg in request.messages):
            required_capabilities.append("tools")
        
        # Route to appropriate model
        routing_request = RoutingRequest(
            tenant_id=tenant_id,
            feature=feature,
            required_capabilities=required_capabilities,
            user_override=user_override,
            context_length_estimate=self._estimate_context_length(request.messages)
        )
        
        routing_response = self.intelligent_router.route_request(routing_request)
        
        if not routing_response.selected_model:
            raise ValueError(f"Failed to route request: {routing_response.routing_reason}")
        
        # Execute the request
        try:
            response = self._execute_chat_completion(request, routing_response.selected_model)
            
            # Calculate metrics
            latency_ms = (time.time() - start_time) * 1000
            cost = self._calculate_chat_cost(routing_response.selected_model, response)
            
            # Update usage tracking
            self._update_usage_tracking(tenant_id, routing_response.selected_model, cost)
            
            return ChatCompletionResponse(
                content=response.choices[0].message.content,
                model_used=routing_response.selected_model,
                tokens_used=response.usage.total_tokens,
                cost=cost,
                latency_ms=latency_ms,
                finish_reason=response.choices[0].finish_reason
            )
            
        except Exception as e:
            # Update model health on failure
            self.model_registry.update_model_health(
                routing_response.selected_model, "unhealthy", error_count=1
            )
            raise e
    
    def _execute_chat_completion(self, request: ChatCompletionRequest, model_name: str):
        """Execute chat completion with the specified model."""
        client = self.clients.get(model_name)
        if not client:
            raise ValueError(f"No client available for model: {model_name}")
        
        # Convert to OpenAI API format
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty,
            stop=request.stop,
            stream=request.stream
        )
        
        return response
    
    def create_embedding(self, request: EmbeddingRequest,
                        tenant_id: str = "default",
                        feature: str = "embed",
                        user_override: Optional[str] = None) -> EmbeddingResponse:
        """
        Create text embedding with intelligent model routing.
        
        Args:
            request: Embedding request
            tenant_id: Tenant identifier for routing policies
            feature: Feature name for routing policies
            user_override: Optional model override from user
            
        Returns:
            Embedding response with model details
        """
        start_time = time.time()
        
        # Route to appropriate model
        routing_request = RoutingRequest(
            tenant_id=tenant_id,
            feature=feature,
            required_capabilities=["embeddings"],
            user_override=user_override,
            context_length_estimate=len(request.text.split())
        )
        
        routing_response = self.intelligent_router.route_request(routing_request)
        
        if not routing_response.selected_model:
            raise ValueError(f"Failed to route request: {routing_response.routing_reason}")
        
        # Execute the request
        try:
            response = self._execute_embedding(request, routing_response.selected_model)
            
            # Calculate metrics
            latency_ms = (time.time() - start_time) * 1000
            cost = self._calculate_embedding_cost(routing_response.selected_model, response)
            
            # Update usage tracking
            self._update_usage_tracking(tenant_id, routing_response.selected_model, cost)
            
            return EmbeddingResponse(
                embedding=response.data[0].embedding,
                model_used=routing_response.selected_model,
                tokens_used=response.usage.total_tokens,
                cost=cost,
                latency_ms=latency_ms
            )
            
        except Exception as e:
            # Update model health on failure
            self.model_registry.update_model_health(
                routing_response.selected_model, "unhealthy", error_count=1
            )
            raise e
    
    def _execute_embedding(self, request: EmbeddingRequest, model_name: str):
        """Execute embedding with the specified model."""
        client = self.clients.get(model_name)
        if not client:
            raise ValueError(f"No client available for model: {model_name}")
        
        response = client.embeddings.create(
            model=model_name,
            input=request.text
        )
        
        return response
    
    def _estimate_context_length(self, messages: List[ChatMessage]) -> int:
        """Estimate context length for messages."""
        # Simple estimation - in practice, you'd want more sophisticated token counting
        total_length = 0
        for message in messages:
            total_length += len(message.content.split()) + 10  # Add overhead for role and formatting
        return total_length
    
    def _calculate_chat_cost(self, model_name: str, response) -> float:
        """Calculate cost for chat completion."""
        model = self.model_registry.get_model(model_name)
        if not model:
            return 0.0
        
        input_cost = response.usage.prompt_tokens * model.cost_per_token.input
        output_cost = response.usage.completion_tokens * model.cost_per_token.output
        return input_cost + output_cost
    
    def _calculate_embedding_cost(self, model_name: str, response) -> float:
        """Calculate cost for embedding."""
        model = self.model_registry.get_model(model_name)
        if not model:
            return 0.0
        
        return response.usage.total_tokens * model.cost_per_token.input
    
    def _update_usage_tracking(self, tenant_id: str, model_name: str, cost: float) -> None:
        """Update usage tracking for budget management."""
        # Update model registry usage
        self.model_registry.record_usage(model_name)
        
        # Update routing policy manager budget tracking
        self.intelligent_router.routing_policy_manager.record_usage_cost(tenant_id, cost)
    
    def get_model_health(self, model_name: str) -> Dict[str, Any]:
        """Get health status for a specific model."""
        model = self.model_registry.get_model(model_name)
        if not model:
            return {"status": "not_found"}
        
        return {
            "deployment_name": model.deployment_name,
            "health_status": model.health_status,
            "last_health_check": model.last_health_check.isoformat() if model.last_health_check else None,
            "error_count": model.error_count,
            "total_requests": model.total_requests,
            "total_tokens": model.total_tokens
        }
    
    def refresh_clients(self) -> None:
        """Refresh Azure OpenAI clients."""
        self._initialize_clients()
    
    def get_available_models(self) -> List[str]:
        """Get list of available model names."""
        return list(self.clients.keys())


# Global Azure OpenAI client instance
azure_openai_client = AzureOpenAIClient()
