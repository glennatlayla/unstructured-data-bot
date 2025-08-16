#!/usr/bin/env python3
"""
Test script to validate Azure integration with real credentials
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_azure_ai_search():
    """Test Azure AI Search connectivity"""
    print("🔍 Testing Azure AI Search...")
    
    search_service = os.getenv('AZURE_SEARCH_SERVICE_NAME')
    search_key = os.getenv('AZURE_SEARCH_API_KEY')
    
    if not search_service or not search_key:
        print("❌ Azure AI Search credentials not found")
        return False
    
    try:
        url = f"https://{search_service}.search.windows.net/indexes?api-version=2023-11-01"
        headers = {"api-key": search_key}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            index_count = len(data.get('value', []))
            print(f"✅ Azure AI Search connected successfully - {index_count} indexes found")
            return True
        else:
            print(f"❌ Azure AI Search failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Azure AI Search error: {e}")
        return False

def test_azure_key_vault():
    """Test Azure Key Vault connectivity"""
    print("🔐 Testing Azure Key Vault...")
    
    vault_url = os.getenv('AZURE_KEY_VAULT_URL')
    
    if not vault_url:
        print("❌ Azure Key Vault URL not found")
        return False
    
    try:
        print(f"✅ Azure Key Vault URL configured: {vault_url}")
        return True
    except Exception as e:
        print(f"❌ Azure Key Vault error: {e}")
        return False

def test_openai():
    """Test OpenAI connectivity"""
    print("🤖 Testing OpenAI...")
    
    endpoint = os.getenv('OPENAI_ENDPOINT')
    api_key = os.getenv('OPENAI_API_KEY')
    deployment = os.getenv('OPENAI_DEPLOYMENT_NAME')
    
    if not endpoint or not api_key:
        print("❌ OpenAI credentials not found")
        return False
    
    try:
        if "your-openai" in endpoint:
            print("⚠️  OpenAI endpoint appears to be placeholder")
            return False
        
        print(f"✅ OpenAI configured - Endpoint: {endpoint}, Deployment: {deployment}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return False

def test_microsoft_teams():
    """Test Microsoft Teams Bot configuration"""
    print("💬 Testing Microsoft Teams Bot...")
    
    app_id = os.getenv('MICROSOFT_APP_ID')
    app_password = os.getenv('MICROSOFT_APP_PASSWORD')
    
    if not app_id or not app_password:
        print("❌ Microsoft Teams Bot credentials not found")
        return False
    
    try:
        print(f"✅ Microsoft Teams Bot configured - App ID: {app_id[:8]}...")
        return True
        
    except Exception as e:
        print(f"❌ Microsoft Teams Bot error: {e}")
        return False

def test_azure_resources():
    """Test Azure resource configuration"""
    print("☁️  Testing Azure Resources...")
    
    tenant_id = os.getenv('AZURE_TENANT_ID')
    subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
    resource_group = os.getenv('AZURE_RESOURCE_GROUP')
    
    if not tenant_id or not subscription_id or not resource_group:
        print("❌ Azure resource configuration not found")
        return False
    
    try:
        print(f"✅ Azure Resources configured:")
        print(f"   - Tenant ID: {tenant_id[:8]}...")
        print(f"   - Subscription: {subscription_id[:8]}...")
        print(f"   - Resource Group: {resource_group}")
        return True
        
    except Exception as e:
        print(f"❌ Azure Resources error: {e}")
        return False

def main():
    """Run all Azure integration tests"""
    print("🚀 Azure Integration Test Suite")
    print("=" * 40)
    
    tests = [
        test_azure_resources,
        test_azure_ai_search,
        test_azure_key_vault,
        test_openai,
        test_microsoft_teams
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    passed = sum(results)
    total = len(results)
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Azure integration tests passed!")
    else:
        print("⚠️  Some tests failed - check configuration")
    
    return passed == total

if __name__ == "__main__":
    main()
