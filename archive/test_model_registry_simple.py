#!/usr/bin/env python3
"""
Simple test script to validate Model Registry environment variable resolution
"""

import os
import sys
import json

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded .env file successfully")
except ImportError:
    print("⚠️  python-dotenv not available, using system environment variables only")

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services', 'orchestrator', 'app'))

def test_model_registry_loading():
    """Test if the model registry can load and resolve environment variables."""
    print("🔍 Testing Model Registry Environment Variable Resolution...")
    
    try:
        # Import the model registry
        from model_registry import ModelRegistry
        
        # Create a registry instance
        registry = ModelRegistry("model_registry.json")
        
        print(f"✅ Model registry loaded successfully with {len(registry.models)} models")
        
        # Check if environment variables were resolved
        for model_name, model_info in registry.models.items():
            print(f"📋 Model: {model_name}")
            print(f"   Endpoint: {model_info.endpoint}")
            print(f"   Deployment: {model_info.deployment_name}")
            print(f"   API Version: {model_info.api_version}")
            print(f"   Capabilities: {', '.join(model_info.capabilities)}")
            print(f"   Health: {model_info.health_status}")
            print()
        
        # Test specific model retrieval
        gpt4o = registry.get_model("gpt-4o")
        if gpt4o:
            print(f"✅ gpt-4o model endpoint: {gpt4o.endpoint}")
            if gpt4o.endpoint.startswith("https://"):
                print("✅ Environment variable resolved successfully!")
                return True
            else:
                print(f"⚠️  Endpoint still appears to be unresolved: {gpt4o.endpoint}")
                return False
        else:
            print("❌ Failed to retrieve gpt-4o model")
            return False
            
    except Exception as e:
        print(f"❌ Model registry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_variables():
    """Test if the required environment variables are set."""
    print("\n🔍 Testing Environment Variables...")
    
    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_KEY",
        "OPENAI_ENDPOINT",
        "OPENAI_API_KEY"
    ]
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask the key for security
            if "KEY" in var:
                masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
            all_set = False
    
    return all_set

def main():
    """Run all tests."""
    print("🚀 Model Registry Environment Variable Test")
    print("=" * 50)
    
    # Test environment variables
    env_ok = test_environment_variables()
    
    if not env_ok:
        print("\n⚠️  Some environment variables are missing. Please check your .env file.")
        return
    
    print("\n" + "=" * 50)
    
    # Test model registry
    registry_ok = test_model_registry_loading()
    
    if registry_ok:
        print("\n🎉 All tests passed! Model registry is working correctly.")
    else:
        print("\n❌ Model registry test failed. Check the configuration.")

if __name__ == "__main__":
    main()
