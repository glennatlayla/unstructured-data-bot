#!/bin/bash
# Azure AI Components Provisioning Script
# This script sets up Azure OpenAI deployments and configures the model registry

set -e

# Configuration
RESOURCE_GROUP="hr-lady-resource-group"
LOCATION="eastus2"
OPENAI_RESOURCE_NAME="hr-lady-openai"
KEY_VAULT_NAME="hr-lady-vault"
SUBSCRIPTION_ID="9d130b71-f32a-4a0e-a9b4-046744eae265"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v az &> /dev/null; then
        log_error "Azure CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! az account show &> /dev/null; then
        log_error "Not logged into Azure. Please run 'az login' first."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Set subscription
set_subscription() {
    log_info "Setting Azure subscription..."
    az account set --subscription $SUBSCRIPTION_ID
    log_success "Subscription set to: $SUBSCRIPTION_ID"
}

# Create Azure OpenAI resource
create_openai_resource() {
    log_info "Creating Azure OpenAI resource..."
    
    # Check if resource already exists
    if az cognitiveservices account show --name $OPENAI_RESOURCE_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
        log_warning "Azure OpenAI resource '$OPENAI_RESOURCE_NAME' already exists"
        return 0
    fi
    
    # Create the resource
    az cognitiveservices account create \
        --name $OPENAI_RESOURCE_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --kind OpenAI \
        --sku S0 \
        --yes
    
    log_success "Azure OpenAI resource created: $OPENAI_RESOURCE_NAME"
}

# Deploy GPT-4o model
deploy_gpt4o() {
    log_info "Deploying GPT-4o model..."
    
    # Check if deployment already exists
    if az cognitiveservices account deployment show \
        --name "gpt-4o" \
        --resource-group $RESOURCE_GROUP \
        --account-name $OPENAI_RESOURCE_NAME &> /dev/null; then
        log_warning "GPT-4o deployment already exists"
        return 0
    fi
    
    # Deploy GPT-4o
    az cognitiveservices account deployment create \
        --name "gpt-4o" \
        --resource-group $RESOURCE_GROUP \
        --account-name $OPENAI_RESOURCE_NAME \
        --deployment-name "gpt-4o" \
        --model-name "gpt-4o" \
        --model-version "2024-05-13" \
        --model-format OpenAI \
        --scale-type Standard \
        --capacity 1
    
    log_success "GPT-4o model deployed successfully"
}

# Deploy GPT-4o-mini model
deploy_gpt4o_mini() {
    log_info "Deploying GPT-4o-mini model..."
    
    # Check if deployment already exists
    if az cognitiveservices account deployment show \
        --name "gpt-4o-mini" \
        --resource-group $RESOURCE_GROUP \
        --account-name $OPENAI_RESOURCE_NAME &> /dev/null; then
        log_warning "GPT-4o-mini deployment already exists"
        return 0
    fi
    
    # Deploy GPT-4o-mini
    az cognitiveservices account deployment create \
        --name "gpt-4o-mini" \
        --resource-group $RESOURCE_GROUP \
        --account-name $OPENAI_RESOURCE_NAME \
        --deployment-name "gpt-4o-mini" \
        --model-name "gpt-4o-mini" \
        --model-version "2024-05-13" \
        --model-format OpenAI \
        --scale-type Standard \
        --capacity 1
    
    log_success "GPT-4o-mini model deployed successfully"
}

# Deploy GPT-35-turbo model
deploy_gpt35_turbo() {
    log_info "Deploying GPT-35-turbo model..."
    
    # Check if deployment already exists
    if az cognitiveservices account deployment show \
        --name "gpt-35-turbo" \
        --resource-group $RESOURCE_GROUP \
        --account-name $OPENAI_RESOURCE_NAME &> /dev/null; then
        log_warning "GPT-35-turbo deployment already exists"
        return 0
    fi
    
    # Deploy GPT-35-turbo
    az cognitiveservices account deployment create \
        --name "gpt-35-turbo" \
        --resource-group $RESOURCE_GROUP \
        --account-name $OPENAI_RESOURCE_NAME \
        --deployment-name "gpt-35-turbo" \
        --model-name "gpt-35-turbo" \
        --model-version "0613" \
        --model-format OpenAI \
        --scale-type Standard \
        --capacity 1
    
    log_success "GPT-35-turbo model deployed successfully"
}

# Deploy text-embedding-3-large model
deploy_embedding_model() {
    log_info "Deploying text-embedding-3-large model..."
    
    # Check if deployment already exists
    if az cognitiveservices account deployment show \
        --name "text-embedding-3-large" \
        --resource-group $RESOURCE_GROUP \
        --account-name $OPENAI_RESOURCE_NAME &> /dev/null; then
        log_warning "text-embedding-3-large deployment already exists"
        return 0
    fi
    
    # Deploy text-embedding-3-large
    az cognitiveservices account deployment create \
        --name "text-embedding-3-large" \
        --resource-group $RESOURCE_GROUP \
        --account-name $OPENAI_RESOURCE_NAME \
        --deployment-name "text-embedding-3-large" \
        --model-name "text-embedding-3-large" \
        --model-version "1" \
        --model-format OpenAI \
        --scale-type Standard \
        --capacity 1
    
    log_success "text-embedding-3-large model deployed successfully"
}

# Get deployment information
get_deployment_info() {
    log_info "Getting deployment information..."
    
    # Get the OpenAI endpoint
    OPENAI_ENDPOINT=$(az cognitiveservices account show \
        --name $OPENAI_RESOURCE_NAME \
        --resource-group $RESOURCE_GROUP \
        --query "properties.endpoint" \
        --output tsv)
    
    # Get the API key
    OPENAI_API_KEY=$(az cognitiveservices account keys list \
        --name $OPENAI_RESOURCE_NAME \
        --resource-group $RESOURCE_GROUP \
        --query "key1" \
        --output tsv)
    
    log_success "OpenAI Endpoint: $OPENAI_ENDPOINT"
    log_success "API Key retrieved successfully"
    
    # Store in Key Vault
    store_in_key_vault "$OPENAI_ENDPOINT" "$OPENAI_API_KEY"
}

# Store secrets in Key Vault
store_in_key_vault() {
    local endpoint=$1
    local api_key=$2
    
    log_info "Storing secrets in Key Vault..."
    
    # Store OpenAI endpoint
    az keyvault secret set \
        --vault-name $KEY_VAULT_NAME \
        --name "OpenAI-Endpoint" \
        --value "$endpoint" \
        --description "Azure OpenAI endpoint URL" \
        --content-type "text/plain"
    
    # Store OpenAI API key
    az keyvault secret set \
        --vault-name $KEY_VAULT_NAME \
        --name "OpenAI-API-Key" \
        --value "$api_key" \
        --description "Azure OpenAI API key" \
        --content-type "text/plain"
    
    log_success "Secrets stored in Key Vault successfully"
}

# Create model registry configuration
create_model_registry() {
    log_info "Creating model registry configuration..."
    
    # Create a JSON file with model registry configuration
    cat > model_registry.json << EOF
{
  "models": [
    {
      "deployment_name": "gpt-4o",
      "endpoint": "AZURE_OPENAI_ENDPOINT",
      "api_version": "2024-05-13",
      "capabilities": ["chat", "vision", "tools", "function_calling"],
      "performance_metrics": {
        "latency": "low",
        "quality": "high",
        "context_length": 128000
      },
      "tags": ["gpt-4", "vision", "tools", "high-quality"],
      "health_status": "healthy",
      "rate_limits": {
        "requests_per_minute": 3000,
        "tokens_per_minute": 150000
      },
      "cost_per_token": {
        "input": 0.000005,
        "output": 0.000015
      }
    },
    {
      "deployment_name": "gpt-4o-mini",
      "endpoint": "AZURE_OPENAI_ENDPOINT",
      "api_version": "2024-05-13",
      "capabilities": ["chat", "vision", "tools", "function_calling"],
      "performance_metrics": {
        "latency": "low",
        "quality": "medium",
        "context_length": 128000
      },
      "tags": ["gpt-4", "vision", "tools", "cost-effective"],
      "health_status": "healthy",
      "rate_limits": {
        "requests_per_minute": 3000,
        "tokens_per_minute": 150000
      },
      "cost_per_token": {
        "input": 0.00000015,
        "output": 0.0000006
      }
    },
    {
      "deployment_name": "gpt-35-turbo",
      "endpoint": "AZURE_OPENAI_ENDPOINT",
      "api_version": "0613",
      "capabilities": ["chat"],
      "performance_metrics": {
        "latency": "very_low",
        "quality": "medium",
        "context_length": 16385
      },
      "tags": ["gpt-35", "fast", "cost-effective"],
      "health_status": "healthy",
      "rate_limits": {
        "requests_per_minute": 3000,
        "tokens_per_minute": 150000
      },
      "cost_per_token": {
        "input": 0.0000015,
        "output": 0.000002
      }
    },
    {
      "deployment_name": "text-embedding-3-large",
      "endpoint": "AZURE_OPENAI_ENDPOINT",
      "api_version": "2024-05-13",
      "capabilities": ["embeddings"],
      "performance_metrics": {
        "latency": "low",
        "quality": "high",
        "context_length": 8192
      },
      "tags": ["embedding", "high-quality"],
      "health_status": "healthy",
      "rate_limits": {
        "requests_per_minute": 3000,
        "tokens_per_minute": 150000
      },
      "cost_per_token": {
        "input": 0.00000013,
        "output": 0.0
      }
    }
  ],
  "routing_policies": [
    {
      "tenant_id": "default",
      "feature": "qa",
      "model_selection_rules": {
        "primary": "gpt-4o",
        "fallback": "gpt-4o-mini",
        "budget_fallback": "gpt-35-turbo"
      },
      "budget_constraints": {
        "monthly_budget": 1000.0,
        "cost_threshold": 0.8,
        "automatic_downshift": true
      },
      "feature_flags": {
        "a_b_testing": false,
        "quality_priority": true
      }
    },
    {
      "tenant_id": "default",
      "feature": "summarize",
      "model_selection_rules": {
        "primary": "gpt-4o-mini",
        "fallback": "gpt-35-turbo"
      },
      "budget_constraints": {
        "monthly_budget": 500.0,
        "cost_threshold": 0.9,
        "automatic_downshift": true
      },
      "feature_flags": {
        "a_b_testing": false,
        "quality_priority": false
      }
    },
    {
      "tenant_id": "default",
      "feature": "embed",
      "model_selection_rules": {
        "primary": "text-embedding-3-large"
      },
      "budget_constraints": {
        "monthly_budget": 200.0,
        "cost_threshold": 0.95,
        "automatic_downshift": false
      },
      "feature_flags": {
        "a_b_testing": false,
        "quality_priority": true
      }
    }
  ]
}
EOF
    
    log_success "Model registry configuration created: model_registry.json"
}

# Update .env file
update_env_file() {
    log_info "Updating .env file with new Azure OpenAI configuration..."
    
    # Get the OpenAI endpoint
    OPENAI_ENDPOINT=$(az cognitiveservices account show \
        --name $OPENAI_RESOURCE_NAME \
        --resource-group $RESOURCE_GROUP \
        --query "properties.endpoint" \
        --output tsv)
    
    # Update .env file
    if [ -f ".env" ]; then
        # Backup existing .env
        cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
        log_info "Backed up existing .env file"
        
        # Update OpenAI endpoint
        sed -i.bak "s|OPENAI_ENDPOINT=.*|OPENAI_ENDPOINT=$OPENAI_ENDPOINT|" .env
        
        # Add new environment variables
        echo "" >> .env
        echo "# Azure OpenAI Model Registry Configuration" >> .env
        echo "AZURE_OPENAI_RESOURCE_NAME=$OPENAI_RESOURCE_NAME" >> .env
        echo "AZURE_OPENAI_LOCATION=$LOCATION" >> .env
        echo "AZURE_OPENAI_API_VERSION=2024-05-13" >> .env
        
        # Add model deployment names
        echo "AZURE_OPENAI_GPT4O_DEPLOYMENT=gpt-4o" >> .env
        echo "AZURE_OPENAI_GPT4O_MINI_DEPLOYMENT=gpt-4o-mini" >> .env
        echo "AZURE_OPENAI_GPT35_TURBO_DEPLOYMENT=gpt-35-turbo" >> .env
        echo "AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large" >> .env
        
        # Add Key Vault references
        echo "AZURE_KEY_VAULT_OPENAI_ENDPOINT_SECRET=OpenAI-Endpoint" >> .env
        echo "AZURE_KEY_VAULT_OPENAI_API_KEY_SECRET=OpenAI-API-Key" >> .env
        
        log_success ".env file updated successfully"
    else
        log_warning ".env file not found, skipping update"
    fi
}

# Main execution
main() {
    log_info "Starting Azure AI Components Provisioning..."
    log_info "Resource Group: $RESOURCE_GROUP"
    log_info "Location: $LOCATION"
    log_info "OpenAI Resource: $OPENAI_RESOURCE_NAME"
    
    check_prerequisites
    set_subscription
    
    create_openai_resource
    deploy_gpt4o
    deploy_gpt4o_mini
    deploy_gpt35_turbo
    deploy_embedding_model
    
    get_deployment_info
    create_model_registry
    update_env_file
    
    log_success "Azure AI Components provisioning completed successfully!"
    log_info "Next steps:"
    log_info "1. Review the model_registry.json configuration"
    log_info "2. Update your application to use the new model registry"
    log_info "3. Test the model routing functionality"
}

# Run main function
main "$@"
