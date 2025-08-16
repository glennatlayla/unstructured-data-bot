#!/usr/bin/env python3
"""
Test Model Routing System

This script tests the complete model routing system including:
- Model registry functionality
- Routing policies
- Intelligent router
- Azure OpenAI client integration
"""

import os
import sys
import json
import time
from typing import Dict, Any

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services', 'orchestrator', 'app'))

from model_registry import ModelRegistry, model_registry
from routing_policies import RoutingPolicyManager, routing_policy_manager
from intelligent_router import IntelligentRouter, intelligent_router, RoutingRequest
from azure_openai_client import AzureOpenAIClient, azure_openai_client


def test_model_registry():
    """Test the model registry functionality."""
    print("🔍 Testing Model Registry...")
    
    try:
        # Test registry loading
        registry = ModelRegistry("model_registry.json")
        print(f"✅ Loaded {len(registry.models)} models")
        
        # Test model retrieval
        gpt4o = registry.get_model("gpt-4o")
        if gpt4o:
            print(f"✅ Retrieved gpt-4o model with {len(gpt4o.capabilities)} capabilities")
        else:
            print("❌ Failed to retrieve gpt-4o model")
        
        # Test capability filtering
        vision_models = registry.get_models_by_capability("vision")
        print(f"✅ Found {len(vision_models)} models with vision capability")
        
        # Test tag filtering
        high_quality_models = registry.get_models_by_tag("high-quality")
        print(f"✅ Found {len(high_quality_models)} high-quality models")
        
        # Test health status
        healthy_models = registry.get_healthy_models()
        print(f"✅ Found {len(healthy_models)} healthy models")
        
        # Test cost estimation
        cost = registry.get_model_cost_estimate("gpt-4o", 1000, 500)
        print(f"✅ Estimated cost for gpt-4o: ${cost:.6f}")
        
        # Test registry summary
        summary = registry.get_registry_summary()
        print(f"✅ Registry summary: {summary}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model registry test failed: {e}")
        return False


def test_routing_policies():
    """Test the routing policies functionality."""
    print("\n🔍 Testing Routing Policies...")
    
    try:
        # Test policy loading
        policy_manager = RoutingPolicyManager("model_registry.json")
        print(f"✅ Loaded {len(policy_manager.policies)} routing policies")
        
        # Test policy retrieval
        qa_policy = policy_manager.get_policy("default", "qa")
        if qa_policy:
            print(f"✅ Retrieved QA policy for default tenant")
            print(f"   Primary model: {qa_policy.model_selection_rules.primary}")
            print(f"   Fallback model: {qa_policy.model_selection_rules.fallback}")
            print(f"   Budget fallback: {qa_policy.model_selection_rules.budget_fallback}")
        else:
            print("❌ Failed to retrieve QA policy")
        
        # Test default policy fallback
        default_chat_policy = policy_manager.get_default_policy("chat")
        if default_chat_policy:
            print(f"✅ Retrieved default chat policy")
        else:
            print("❌ Failed to retrieve default chat policy")
        
        # Test budget status
        budget_status = policy_manager.get_budget_status("default")
        print(f"✅ Budget status for default tenant: ${budget_status['current_spend']:.2f} / ${budget_status['total_monthly_budget']:.2f}")
        
        # Test usage cost recording
        policy_manager.record_usage_cost("default", 0.05)
        updated_budget = policy_manager.get_budget_status("default")
        print(f"✅ Updated budget after recording cost: ${updated_budget['current_spend']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Routing policies test failed: {e}")
        return False


def test_intelligent_router():
    """Test the intelligent router functionality."""
    print("\n🔍 Testing Intelligent Router...")
    
    try:
        # Test basic routing
        routing_request = RoutingRequest(
            tenant_id="default",
            feature="qa",
            required_capabilities=["chat"],
            quality_priority=True
        )
        
        response = intelligent_router.route_request(routing_request)
        print(f"✅ Routing response: {response.selected_model}")
        print(f"   Reason: {response.routing_reason}")
        print(f"   Fallback used: {response.fallback_used}")
        print(f"   Budget impact: ${response.budget_impact:.6f}")
        
        # Test routing with different features
        features = ["qa", "summarize", "embed", "chat"]
        for feature in features:
            routing_request = RoutingRequest(
                tenant_id="default",
                feature=feature,
                required_capabilities=["chat"] if feature != "embed" else ["embeddings"]
            )
            
            response = intelligent_router.route_request(routing_request)
            print(f"✅ {feature} feature routed to: {response.selected_model}")
        
        # Test user override
        routing_request = RoutingRequest(
            tenant_id="default",
            feature="qa",
            required_capabilities=["chat"],
            user_override="gpt-35-turbo"
        )
        
        response = intelligent_router.route_request(routing_request)
        print(f"✅ User override routed to: {response.selected_model}")
        
        # Test routing analytics
        analytics = intelligent_router.get_routing_analytics()
        print(f"✅ Routing analytics: {analytics['total_requests']} total requests")
        
        return True
        
    except Exception as e:
        print(f"❌ Intelligent router test failed: {e}")
        return False


def test_azure_openai_client():
    """Test the Azure OpenAI client functionality."""
    print("\n🔍 Testing Azure OpenAI Client...")
    
    try:
        # Test client initialization
        print(f"✅ Available models: {azure_openai_client.get_available_models()}")
        
        # Test model health
        for model_name in ["gpt-4o", "gpt-4o-mini", "gpt-35-turbo"]:
            health = azure_openai_client.get_model_health(model_name)
            print(f"✅ {model_name} health: {health.get('health_status', 'unknown')}")
        
        # Test chat completion (without actual API call)
        from azure_openai_client import ChatMessage, ChatCompletionRequest
        
        messages = [
            ChatMessage(role="system", content="You are a helpful assistant."),
            ChatMessage(role="user", content="Hello, how are you?")
        ]
        
        chat_request = ChatCompletionRequest(messages=messages)
        print(f"✅ Chat request created with {len(messages)} messages")
        
        # Test embedding request (without actual API call)
        from azure_openai_client import EmbeddingRequest
        
        embedding_request = EmbeddingRequest(text="This is a test sentence for embedding.")
        print(f"✅ Embedding request created for text: {embedding_request.text[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Azure OpenAI client test failed: {e}")
        return False


def test_integration():
    """Test the complete integration."""
    print("\n🔍 Testing Complete Integration...")
    
    try:
        # Test end-to-end routing
        print("Testing end-to-end routing workflow...")
        
        # 1. Get routing policy
        policy = routing_policy_manager.get_policy("default", "qa")
        print(f"✅ Retrieved routing policy: {policy.feature}")
        
        # 2. Route request
        routing_request = RoutingRequest(
            tenant_id="default",
            feature="qa",
            required_capabilities=["chat"],
            quality_priority=True
        )
        
        routing_response = intelligent_router.route_request(routing_request)
        print(f"✅ Routed to model: {routing_response.selected_model}")
        
        # 3. Check model in registry
        model = model_registry.get_model(routing_response.selected_model)
        if model:
            print(f"✅ Model found in registry: {model.deployment_name}")
            print(f"   Capabilities: {model.capabilities}")
            print(f"   Health: {model.health_status}")
        else:
            print("❌ Model not found in registry")
        
        # 4. Test budget tracking
        initial_budget = routing_policy_manager.get_budget_status("default")
        print(f"✅ Initial budget: ${initial_budget['current_spend']:.2f}")
        
        # Simulate usage
        routing_policy_manager.record_usage_cost("default", 0.10)
        
        updated_budget = routing_policy_manager.get_budget_status("default")
        print(f"✅ Updated budget: ${updated_budget['current_spend']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


def test_configuration_refresh():
    """Test configuration refresh functionality."""
    print("\n🔍 Testing Configuration Refresh...")
    
    try:
        # Test model registry refresh
        initial_count = len(model_registry.models)
        model_registry.refresh_config()
        refreshed_count = len(model_registry.models)
        print(f"✅ Model registry refreshed: {initial_count} -> {refreshed_count} models")
        
        # Test routing policies refresh
        initial_policy_count = len(routing_policy_manager.policies)
        routing_policy_manager.refresh_policies()
        refreshed_policy_count = len(routing_policy_manager.policies)
        print(f"✅ Routing policies refreshed: {initial_policy_count} -> {refreshed_policy_count} policies")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration refresh test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting Model Routing System Tests\n")
    
    tests = [
        ("Model Registry", test_model_registry),
        ("Routing Policies", test_routing_policies),
        ("Intelligent Router", test_intelligent_router),
        ("Azure OpenAI Client", test_azure_openai_client),
        ("Integration", test_integration),
        ("Configuration Refresh", test_configuration_refresh)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The model routing system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
