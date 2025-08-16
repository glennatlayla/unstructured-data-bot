"""
Intelligent Router Module

This module provides intelligent model routing based on task requirements,
budget constraints, performance needs, and feature flags.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .model_registry import ModelRegistry, model_registry
from .routing_policies import RoutingPolicyManager, routing_policy_manager

logger = logging.getLogger(__name__)


@dataclass
class RoutingRequest:
    """Request for model routing."""
    tenant_id: str
    feature: str
    required_capabilities: List[str]
    quality_priority: Optional[bool] = None
    budget_override: Optional[float] = None
    latency_requirement: Optional[str] = None  # very_low, low, medium, high
    context_length_estimate: Optional[int] = None
    user_override: Optional[str] = None  # Allow user to override model selection


@dataclass
class RoutingResponse:
    """Response from model routing."""
    selected_model: str
    routing_reason: str
    fallback_used: bool
    budget_impact: float
    estimated_latency: str
    confidence_score: float


class IntelligentRouter:
    """
    Intelligent router that selects the best model based on multiple factors.
    
    Factors considered:
    - Task requirements and capabilities
    - Budget constraints and cost optimization
    - Performance requirements (latency, quality)
    - Model health and availability
    - Feature flags and A/B testing
    - User overrides
    """
    
    def __init__(self):
        self.model_registry = model_registry
        self.routing_policy_manager = routing_policy_manager
        self.usage_tracker = {}
        self.performance_metrics = {}
    
    def route_request(self, request: RoutingRequest) -> RoutingResponse:
        """
        Route a request to the most appropriate model.
        
        Args:
            request: Routing request with all necessary parameters
            
        Returns:
            Routing response with selected model and reasoning
        """
        logger.info(f"Routing request for {request.tenant_id}:{request.feature}")
        
        # Check for user override first
        if request.user_override:
            if self._validate_user_override(request.user_override, request.required_capabilities):
                return self._create_override_response(request.user_override, request)
            else:
                logger.warning(f"User override {request.user_override} not valid for capabilities: {request.required_capabilities}")
        
        # Get routing policy
        policy = self.routing_policy_manager.get_policy(request.tenant_id, request.feature)
        if not policy:
            policy = self.routing_policy_manager.get_default_policy(request.feature)
        
        if not policy:
            logger.error(f"No routing policy found for {request.tenant_id}:{request.feature}")
            return self._create_error_response("No routing policy found")
        
        # Select model based on policy and constraints
        selected_model = self._select_optimal_model(request, policy)
        if not selected_model:
            return self._create_error_response("No suitable model available")
        
        # Create response
        response = self._create_routing_response(request, selected_model, policy)
        
        # Update usage tracking
        self._update_usage_tracking(request.tenant_id, selected_model)
        
        logger.info(f"Selected model {selected_model} for {request.tenant_id}:{request.feature}")
        return response
    
    def _select_optimal_model(self, request: RoutingRequest, policy) -> Optional[str]:
        """Select the optimal model based on request requirements and policy."""
        # Check budget constraints first
        if not self._check_budget_constraints(request.tenant_id, policy, request.budget_override):
            # Use budget fallback
            if policy.model_selection_rules.budget_fallback:
                fallback_model = policy.model_selection_rules.budget_fallback
                if self._validate_model_capabilities(fallback_model, request.required_capabilities):
                    return fallback_model
        
        # Determine quality priority
        quality_priority = request.quality_priority
        if quality_priority is None:
            quality_priority = policy.feature_flags.quality_priority
        
        # Select model based on priority and capabilities
        if quality_priority:
            return self._select_quality_priority_model(request, policy)
        else:
            return self._select_cost_optimized_model(request, policy)
    
    def _select_quality_priority_model(self, request: RoutingRequest, policy) -> Optional[str]:
        """Select model prioritizing quality over cost."""
        # Try primary model first
        if self._validate_model_capabilities(policy.model_selection_rules.primary, request.required_capabilities):
            if self._check_performance_requirements(policy.model_selection_rules.primary, request):
                return policy.model_selection_rules.primary
        
        # Try fallback model
        if policy.model_selection_rules.fallback:
            if self._validate_model_capabilities(policy.model_selection_rules.fallback, request.required_capabilities):
                if self._check_performance_requirements(policy.model_selection_rules.fallback, request):
                    return policy.model_selection_rules.fallback
        
        # Try budget fallback as last resort
        if policy.model_selection_rules.budget_fallback:
            if self._validate_model_capabilities(policy.model_selection_rules.budget_fallback, request.required_capabilities):
                return policy.model_selection_rules.budget_fallback
        
        return None
    
    def _select_cost_optimized_model(self, request: RoutingRequest, policy) -> Optional[str]:
        """Select model prioritizing cost over quality."""
        # Try fallback (cheaper) model first
        if policy.model_selection_rules.fallback:
            if self._validate_model_capabilities(policy.model_selection_rules.fallback, request.required_capabilities):
                if self._check_performance_requirements(policy.model_selection_rules.fallback, request):
                    return policy.model_selection_rules.fallback
        
        # Try primary model
        if self._validate_model_capabilities(policy.model_selection_rules.primary, request.required_capabilities):
            if self._check_performance_requirements(policy.model_selection_rules.primary, request):
                return policy.model_selection_rules.primary
        
        # Try budget fallback
        if policy.model_selection_rules.budget_fallback:
            if self._validate_model_capabilities(policy.model_selection_rules.budget_fallback, request.required_capabilities):
                return policy.model_selection_rules.budget_fallback
        
        return None
    
    def _validate_model_capabilities(self, deployment_name: str, required_capabilities: List[str]) -> bool:
        """Validate if a model supports required capabilities."""
        if not required_capabilities:
            return True
        
        model = self.model_registry.get_model(deployment_name)
        if not model or model.health_status != "healthy":
            return False
        
        return all(cap in model.capabilities for cap in required_capabilities)
    
    def _check_performance_requirements(self, deployment_name: str, request: RoutingRequest) -> bool:
        """Check if a model meets performance requirements."""
        model = self.model_registry.get_model(deployment_name)
        if not model:
            return False
        
        # Check latency requirements
        if request.latency_requirement:
            if not self._meets_latency_requirement(model.performance_metrics.latency, request.latency_requirement):
                return False
        
        # Check context length requirements
        if request.context_length_estimate:
            if request.context_length_estimate > model.performance_metrics.context_length:
                return False
        
        return True
    
    def _meets_latency_requirement(self, model_latency: str, required_latency: str) -> bool:
        """Check if model latency meets requirements."""
        latency_hierarchy = {
            "very_low": 0,
            "low": 1,
            "medium": 2,
            "high": 3
        }
        
        model_level = latency_hierarchy.get(model_latency, 3)
        required_level = latency_hierarchy.get(required_latency, 3)
        
        return model_level <= required_level
    
    def _check_budget_constraints(self, tenant_id: str, policy, budget_override: Optional[float]) -> bool:
        """Check if budget constraints allow using the primary model."""
        if not policy.budget_constraints.automatic_downshift:
            return True
        
        current_month = datetime.now().strftime("%Y-%m")
        current_budget = self.routing_policy_manager.budget_tracker.get(tenant_id, {}).get(current_month, 0.0)
        
        budget_limit = budget_override or policy.budget_constraints.monthly_budget
        threshold = budget_limit * policy.budget_constraints.cost_threshold
        
        return current_budget < threshold
    
    def _validate_user_override(self, deployment_name: str, required_capabilities: List[str]) -> bool:
        """Validate if user override model supports required capabilities."""
        return self._validate_model_capabilities(deployment_name, required_capabilities)
    
    def _create_override_response(self, deployment_name: str, request: RoutingRequest) -> RoutingResponse:
        """Create response for user override."""
        model = self.model_registry.get_model(deployment_name)
        estimated_cost = self._estimate_request_cost(deployment_name, request)
        
        return RoutingResponse(
            selected_model=deployment_name,
            routing_reason="User override",
            fallback_used=False,
            budget_impact=estimated_cost,
            estimated_latency=model.performance_metrics.latency if model else "unknown",
            confidence_score=1.0
        )
    
    def _create_routing_response(self, request: RoutingRequest, selected_model: str, policy) -> RoutingResponse:
        """Create routing response with all details."""
        model = self.model_registry.get_model(selected_model)
        estimated_cost = self._estimate_request_cost(selected_model, request)
        
        # Determine if fallback was used
        fallback_used = selected_model != policy.model_selection_rules.primary
        
        # Determine routing reason
        if fallback_used:
            if selected_model == policy.model_selection_rules.budget_fallback:
                routing_reason = "Budget constraint - using cost-optimized model"
            else:
                routing_reason = "Primary model unavailable - using fallback"
        else:
            routing_reason = "Primary model selected"
        
        return RoutingResponse(
            selected_model=selected_model,
            routing_reason=routing_reason,
            fallback_used=fallback_used,
            budget_impact=estimated_cost,
            estimated_latency=model.performance_metrics.latency if model else "unknown",
            confidence_score=0.9 if not fallback_used else 0.7
        )
    
    def _create_error_response(self, error_message: str) -> RoutingResponse:
        """Create error response when routing fails."""
        return RoutingResponse(
            selected_model="",
            routing_reason=error_message,
            fallback_used=False,
            budget_impact=0.0,
            estimated_latency="unknown",
            confidence_score=0.0
        )
    
    def _estimate_request_cost(self, deployment_name: str, request: RoutingRequest) -> float:
        """Estimate the cost for the request."""
        # This is a simplified estimation - in practice, you'd want more sophisticated token counting
        estimated_input_tokens = request.context_length_estimate or 1000
        estimated_output_tokens = 500  # Default assumption
        
        return self.model_registry.get_model_cost_estimate(
            deployment_name, estimated_input_tokens, estimated_output_tokens
        )
    
    def _update_usage_tracking(self, tenant_id: str, deployment_name: str) -> None:
        """Update usage tracking for analytics."""
        current_time = datetime.now()
        
        if tenant_id not in self.usage_tracker:
            self.usage_tracker[tenant_id] = {}
        
        if deployment_name not in self.usage_tracker[tenant_id]:
            self.usage_tracker[tenant_id][deployment_name] = {
                "total_requests": 0,
                "last_used": None
            }
        
        self.usage_tracker[tenant_id][deployment_name]["total_requests"] += 1
        self.usage_tracker[tenant_id][deployment_name]["last_used"] = current_time
    
    def get_routing_analytics(self, tenant_id: str = None) -> Dict[str, Any]:
        """Get analytics about routing decisions."""
        analytics = {
            "total_requests": 0,
            "models_used": {},
            "fallback_usage": 0,
            "budget_impacts": []
        }
        
        if tenant_id:
            tenant_usage = self.usage_tracker.get(tenant_id, {})
            analytics["total_requests"] = sum(model["total_requests"] for model in tenant_usage.values())
            analytics["models_used"] = {model: data["total_requests"] for model, data in tenant_usage.items()}
        else:
            # Aggregate across all tenants
            for tenant_data in self.usage_tracker.values():
                analytics["total_requests"] += sum(model["total_requests"] for model in tenant_data.values())
                for model, data in tenant_data.items():
                    if model not in analytics["models_used"]:
                        analytics["models_used"][model] = 0
                    analytics["models_used"][model] += data["total_requests"]
        
        return analytics


# Global intelligent router instance
intelligent_router = IntelligentRouter()
