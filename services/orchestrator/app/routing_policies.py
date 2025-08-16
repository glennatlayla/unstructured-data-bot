"""
Routing Policies Module

This module defines routing policies for intelligent model selection based on
tenant, feature, budget constraints, and feature flags.
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel

from .model_registry import ModelRegistry, model_registry

logger = logging.getLogger(__name__)


class QualityPriority(str, Enum):
    """Quality priority levels for model selection."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ModelSelectionRules:
    """Rules for model selection with fallback options."""
    primary: str
    fallback: Optional[str] = None
    budget_fallback: Optional[str] = None


@dataclass
class BudgetConstraints:
    """Budget constraints for model usage."""
    monthly_budget: float
    cost_threshold: float  # 0.0 to 1.0, percentage of budget to trigger downshift
    automatic_downshift: bool = True


@dataclass
class FeatureFlags:
    """Feature flags for routing behavior."""
    a_b_testing: bool = False
    quality_priority: bool = True


@dataclass
class RoutingPolicy:
    """Complete routing policy for a tenant and feature."""
    tenant_id: str
    feature: str
    model_selection_rules: ModelSelectionRules
    budget_constraints: BudgetConstraints
    feature_flags: FeatureFlags
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


class RoutingPolicyManager:
    """Manages routing policies for intelligent model selection."""
    
    def __init__(self, config_path: str = "model_registry.json"):
        self.config_path = config_path
        self.policies: Dict[str, RoutingPolicy] = {}
        self.budget_tracker: Dict[str, Dict[str, float]] = {}  # tenant_id -> {month: amount}
        self.load_policies()
    
    def load_policies(self) -> None:
        """Load routing policies from configuration."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                
                self.policies.clear()
                for policy_data in config.get('routing_policies', []):
                    policy = self._create_routing_policy(policy_data)
                    key = f"{policy.tenant_id}:{policy.feature}"
                    self.policies[key] = policy
                
                logger.info(f"Loaded {len(self.policies)} routing policies")
            else:
                logger.warning(f"Routing policies config not found: {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load routing policies: {e}")
    
    def _create_routing_policy(self, policy_data: Dict[str, Any]) -> RoutingPolicy:
        """Create a RoutingPolicy instance from configuration data."""
        return RoutingPolicy(
            tenant_id=policy_data['tenant_id'],
            feature=policy_data['feature'],
            model_selection_rules=ModelSelectionRules(**policy_data['model_selection_rules']),
            budget_constraints=BudgetConstraints(**policy_data['budget_constraints']),
            feature_flags=FeatureFlags(**policy_data['feature_flags'])
        )
    
    def get_policy(self, tenant_id: str, feature: str) -> Optional[RoutingPolicy]:
        """Get routing policy for a specific tenant and feature."""
        key = f"{tenant_id}:{feature}"
        return self.policies.get(key)
    
    def get_default_policy(self, feature: str) -> Optional[RoutingPolicy]:
        """Get default routing policy for a feature."""
        return self.get_policy("default", feature)
    
    def select_model(self, tenant_id: str, feature: str, 
                    required_capabilities: List[str] = None,
                    quality_priority: bool = None,
                    budget_override: Optional[float] = None) -> Optional[str]:
        """
        Select the best model based on routing policy and constraints.
        
        Args:
            tenant_id: Tenant identifier
            feature: Feature name (qa, summarize, embed, chat)
            required_capabilities: Required model capabilities
            quality_priority: Override quality priority from policy
            budget_override: Override budget constraint
            
        Returns:
            Selected model deployment name or None if no suitable model
        """
        # Get routing policy
        policy = self.get_policy(tenant_id, feature) or self.get_default_policy(feature)
        if not policy:
            logger.warning(f"No routing policy found for {tenant_id}:{feature}")
            return None
        
        # Check budget constraints
        if not self._check_budget_constraints(tenant_id, policy, budget_override):
            # Use budget fallback if available
            if policy.model_selection_rules.budget_fallback:
                fallback_model = policy.model_selection_rules.budget_fallback
                if self._validate_model_capabilities(fallback_model, required_capabilities):
                    logger.info(f"Using budget fallback model: {fallback_model}")
                    return fallback_model
        
        # Determine quality priority
        if quality_priority is None:
            quality_priority = policy.feature_flags.quality_priority
        
        # Select model based on priority
        if quality_priority:
            # Try primary model first
            if self._validate_model_capabilities(policy.model_selection_rules.primary, required_capabilities):
                return policy.model_selection_rules.primary
            
            # Try fallback model
            if policy.model_selection_rules.fallback:
                if self._validate_model_capabilities(policy.model_selection_rules.fallback, required_capabilities):
                    return policy.model_selection_rules.fallback
        else:
            # Cost-optimized selection
            if policy.model_selection_rules.fallback:
                if self._validate_model_capabilities(policy.model_selection_rules.fallback, required_capabilities):
                    return policy.model_selection_rules.fallback
            
            if self._validate_model_capabilities(policy.model_selection_rules.primary, required_capabilities):
                return policy.model_selection_rules.primary
        
        logger.warning(f"No suitable model found for {tenant_id}:{feature}")
        return None
    
    def _validate_model_capabilities(self, deployment_name: str, 
                                   required_capabilities: List[str]) -> bool:
        """Validate if a model supports required capabilities."""
        if not required_capabilities:
            return True
        
        model = model_registry.get_model(deployment_name)
        if not model or model.health_status != "healthy":
            return False
        
        return all(cap in model.capabilities for cap in required_capabilities)
    
    def _check_budget_constraints(self, tenant_id: str, policy: RoutingPolicy, 
                                budget_override: Optional[float] = None) -> bool:
        """Check if budget constraints allow using the primary model."""
        if not policy.budget_constraints.automatic_downshift:
            return True
        
        current_month = datetime.now().strftime("%Y-%m")
        current_budget = self.budget_tracker.get(tenant_id, {}).get(current_month, 0.0)
        
        budget_limit = budget_override or policy.budget_constraints.monthly_budget
        threshold = budget_limit * policy.budget_constraints.cost_threshold
        
        return current_budget < threshold
    
    def record_usage_cost(self, tenant_id: str, amount: float) -> None:
        """Record usage cost for budget tracking."""
        current_month = datetime.now().strftime("%Y-%m")
        
        if tenant_id not in self.budget_tracker:
            self.budget_tracker[tenant_id] = {}
        
        if current_month not in self.budget_tracker[tenant_id]:
            self.budget_tracker[tenant_id][current_month] = 0.0
        
        self.budget_tracker[tenant_id][current_month] += amount
        logger.debug(f"Recorded cost for {tenant_id}: {amount} (monthly total: {self.budget_tracker[tenant_id][current_month]})")
    
    def get_budget_status(self, tenant_id: str) -> Dict[str, Any]:
        """Get budget status for a tenant."""
        current_month = datetime.now().strftime("%Y-%m")
        current_budget = self.budget_tracker.get(tenant_id, {}).get(current_month, 0.0)
        
        # Get all policies for this tenant
        tenant_policies = [p for p in self.policies.values() if p.tenant_id == tenant_id]
        total_monthly_budget = sum(p.budget_constraints.monthly_budget for p in tenant_policies)
        
        return {
            "tenant_id": tenant_id,
            "current_month": current_month,
            "current_spend": current_budget,
            "total_monthly_budget": total_monthly_budget,
            "remaining_budget": total_monthly_budget - current_budget,
            "utilization_percentage": (current_budget / total_monthly_budget * 100) if total_monthly_budget > 0 else 0
        }
    
    def refresh_policies(self) -> None:
        """Refresh policies from configuration."""
        self.load_policies()
    
    def get_policy_summary(self) -> Dict[str, Any]:
        """Get a summary of all routing policies."""
        return {
            "total_policies": len(self.policies),
            "policies_by_tenant": {},
            "policies_by_feature": {},
            "budget_tracking_enabled": any(p.budget_constraints.automatic_downshift for p in self.policies.values())
        }


# Global routing policy manager instance
routing_policy_manager = RoutingPolicyManager()
