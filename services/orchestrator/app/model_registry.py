"""
Model Registry Module

This module provides a centralized registry for managing Azure OpenAI model deployments,
their capabilities, performance characteristics, and health status.
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import httpx
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance characteristics of a model."""
    latency: str  # very_low, low, medium, high
    quality: str  # low, medium, high
    context_length: int


@dataclass
class RateLimits:
    """Rate limiting constraints for a model."""
    requests_per_minute: int
    tokens_per_minute: int


@dataclass
class CostPerToken:
    """Cost per token for input and output."""
    input: float
    output: float


@dataclass
class ModelInfo:
    """Complete information about a model deployment."""
    deployment_name: str
    endpoint: str
    api_version: str
    capabilities: List[str]
    performance_metrics: PerformanceMetrics
    tags: List[str]
    health_status: str
    rate_limits: RateLimits
    cost_per_token: CostPerToken
    last_health_check: Optional[datetime] = None
    error_count: int = 0
    total_requests: int = 0
    total_tokens: int = 0


class ModelRegistry:
    """Centralized registry for managing Azure OpenAI model deployments."""
    
    def __init__(self, config_path: str = "model_registry.json"):
        self.config_path = config_path
        self.models: Dict[str, ModelInfo] = {}
        self.last_config_load = None
        self.load_config()
    
    def _resolve_environment_variables(self, value: str) -> str:
        """Resolve environment variables in configuration values."""
        if isinstance(value, str) and value.startswith("$"):
            # Handle $VARIABLE_NAME format
            env_var = value[1:]  # Remove the $ prefix
            resolved = os.getenv(env_var)
            if resolved:
                logger.info(f"Resolved {value} -> {resolved}")
                return resolved
            else:
                logger.warning(f"Environment variable {env_var} not found, using literal value: {value}")
                return value
        elif isinstance(value, str) and value in os.environ:
            # Handle direct environment variable names
            resolved = os.getenv(value)
            if resolved:
                logger.info(f"Resolved {value} -> {resolved}")
                return resolved
            else:
                logger.warning(f"Environment variable {value} not found, using literal value: {value}")
                return value
        return value
    
    def load_config(self) -> None:
        """Load model registry configuration from JSON file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                
                self.models.clear()
                for model_data in config.get('models', []):
                    # Resolve environment variables in the model data
                    resolved_model_data = self._resolve_model_data(model_data)
                    model = self._create_model_info(resolved_model_data)
                    self.models[model.deployment_name] = model
                
                self.last_config_load = datetime.now()
                logger.info(f"Loaded {len(self.models)} models from {self.config_path}")
            else:
                logger.warning(f"Model registry config not found: {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load model registry config: {e}")
    
    def _resolve_model_data(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve environment variables in model data recursively."""
        resolved_data = {}
        for key, value in model_data.items():
            if isinstance(value, dict):
                resolved_data[key] = self._resolve_model_data(value)
            elif isinstance(value, list):
                resolved_data[key] = [self._resolve_environment_variables(item) if isinstance(item, str) else item for item in value]
            elif isinstance(value, str):
                resolved_data[key] = self._resolve_environment_variables(value)
            else:
                resolved_data[key] = value
        return resolved_data
    
    def _create_model_info(self, model_data: Dict[str, Any]) -> ModelInfo:
        """Create a ModelInfo instance from configuration data."""
        return ModelInfo(
            deployment_name=model_data['deployment_name'],
            endpoint=model_data['endpoint'],
            api_version=model_data['api_version'],
            capabilities=model_data['capabilities'],
            performance_metrics=PerformanceMetrics(**model_data['performance_metrics']),
            tags=model_data['tags'],
            health_status=model_data['health_status'],
            rate_limits=RateLimits(**model_data['rate_limits']),
            cost_per_token=CostPerToken(**model_data['cost_per_token'])
        )
    
    def get_model(self, deployment_name: str) -> Optional[ModelInfo]:
        """Get a model by deployment name."""
        return self.models.get(deployment_name)
    
    def get_models_by_capability(self, capability: str) -> List[ModelInfo]:
        """Get all models that support a specific capability."""
        return [model for model in self.models.values() if capability in model.capabilities]
    
    def get_models_by_tag(self, tag: str) -> List[ModelInfo]:
        """Get all models with a specific tag."""
        return [model for model in self.models.values() if tag in model.tags]
    
    def get_healthy_models(self) -> List[ModelInfo]:
        """Get all models with healthy status."""
        return [model for model in self.models.values() if model.health_status == "healthy"]
    
    def update_model_health(self, deployment_name: str, health_status: str, error_count: int = 0) -> None:
        """Update the health status of a model."""
        if deployment_name in self.models:
            model = self.models[deployment_name]
            model.health_status = health_status
            model.last_health_check = datetime.now()
            model.error_count = error_count
            logger.info(f"Updated health status for {deployment_name}: {health_status}")
    
    def record_usage(self, deployment_name: str, request_count: int = 1, token_count: int = 0) -> None:
        """Record usage statistics for a model."""
        if deployment_name in self.models:
            model = self.models[deployment_name]
            model.total_requests += request_count
            model.total_tokens += token_count
            logger.debug(f"Recorded usage for {deployment_name}: {request_count} requests, {token_count} tokens")
    
    def get_model_cost_estimate(self, deployment_name: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate the cost for using a model with given token counts."""
        model = self.get_model(deployment_name)
        if model:
            input_cost = input_tokens * model.cost_per_token.input
            output_cost = output_tokens * model.cost_per_token.output
            return input_cost + output_cost
        return 0.0
    
    def refresh_config(self) -> None:
        """Refresh the configuration from the file."""
        self.load_config()
    
    def get_registry_summary(self) -> Dict[str, Any]:
        """Get a summary of the model registry."""
        return {
            "total_models": len(self.models),
            "healthy_models": len(self.get_healthy_models()),
            "models_by_capability": {
                capability: len(self.get_models_by_capability(capability))
                for capability in set().union(*[model.capabilities for model in self.models.values()])
            },
            "last_updated": self.last_config_load.isoformat() if self.last_config_load else None
        }


# Global model registry instance
model_registry = ModelRegistry()
