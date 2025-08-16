# Azure Deployment Guide

## Overview
This guide covers Azure-specific deployment procedures for the Unstructured Data Indexing & AI-Query Application.

## Prerequisites

### Azure Environment
- Azure CLI installed and authenticated (`az login`)
- Azure subscription with sufficient privileges
- SSH key pair generated (`ssh-keygen -t rsa -b 4096`)
- Domain name registered in Azure DNS

### Development Environment
- PowerShell 7+ or Bash shell
- Git repository access
- Docker and Docker Compose (for local testing)

## Azure Resource Provisioning

### 1. Subscription Setup
```bash
# Create new subscription (if needed)
az account management-group subscription create \
  --subscription-name "UnstructuredDataBot-Prod" \
  --billing-account-name "$BILLING_ACCOUNT" \
  --enrollment-account-name "$ENROLLMENT_ACCOUNT" \
  --offer-type "MS-AZR-0017P"

# Set subscription context
SUBSCRIPTION_ID=$(az account list --query "[?name=='UnstructuredDataBot-Prod'].id" -o tsv)
az account set --subscription "$SUBSCRIPTION_ID"
```

### 2. Resource Groups
```bash
# Create resource groups
LOCATION="eastus2"
RESOURCE_GROUP_PREFIX="rg-udb"

az group create --name "${RESOURCE_GROUP_PREFIX}-core" --location "$LOCATION"
az group create --name "${RESOURCE_GROUP_PREFIX}-compute" --location "$LOCATION"
az group create --name "${RESOURCE_GROUP_PREFIX}-data" --location "$LOCATION"
az group create --name "${RESOURCE_GROUP_PREFIX}-network" --location "$LOCATION"
```

### 3. Teams Bot Registration
```bash
# Create App Registration
BOT_APP_ID=$(az ad app create \
  --display-name "unstructured-data-bot-teams" \
  --sign-in-audience "AzureADMultipleOrgs" \
  --query appId -o tsv)

# Create service principal and client secret
az ad sp create --id "$BOT_APP_ID"
BOT_CLIENT_SECRET=$(az ad app credential reset \
  --id "$BOT_APP_ID" \
  --display-name "bot-secret" \
  --query password -o tsv)

# Create Bot Framework registration
az bot create \
  --resource-group "${RESOURCE_GROUP_PREFIX}-core" \
  --name "unstructured-data-bot" \
  --appid "$BOT_APP_ID" \
  --password "$BOT_CLIENT_SECRET" \
  --endpoint "https://bot.your-domain.com/api/messages" \
  --msa-app-type "MultiTenant"
```

## VM-Based Deployment

### 1. Virtual Network
```bash
# Create virtual network and subnets
az network vnet create \
  --resource-group "${RESOURCE_GROUP_PREFIX}-network" \
  --name "vnet-unstructured-data-bot" \
  --address-prefix "10.0.0.0/16" \
  --subnet-name "subnet-compute" \
  --subnet-prefix "10.0.1.0/24"
```

### 2. Linux VM Creation
```bash
# Create VM with Docker pre-installed
az vm create \
  --resource-group "${RESOURCE_GROUP_PREFIX}-compute" \
  --name "vm-unstructured-data-bot-host" \
  --image "Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:latest" \
  --size "Standard_D4s_v3" \
  --vnet-name "vnet-unstructured-data-bot" \
  --subnet "subnet-compute" \
  --public-ip-address "pip-unstructured-data-bot-vm" \
  --ssh-key-values "$SSH_PUBLIC_KEY_PATH" \
  --admin-username "azureuser" \
  --custom-data cloud-init.yaml
```

### 3. DNS Configuration
```bash
# Create DNS zone and records
az network dns zone create \
  --resource-group "${RESOURCE_GROUP_PREFIX}-network" \
  --name "your-domain.com"

# Get public IP and create A records
PUBLIC_IP=$(az network public-ip show \
  --resource-group "${RESOURCE_GROUP_PREFIX}-network" \
  --name "pip-unstructured-data-bot-lb" \
  --query ipAddress -o tsv)

az network dns record-set a add-record \
  --resource-group "${RESOURCE_GROUP_PREFIX}-network" \
  --zone-name "your-domain.com" \
  --record-set-name "api" \
  --ipv4-address "$PUBLIC_IP"
```

## Container Deployment

### 1. SSH Configuration
```bash
# Configure SSH access from development server
cat >> ~/.ssh/config << EOF
Host unstructured-data-bot-vm
    HostName $VM_PUBLIC_IP
    User azureuser
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking no
EOF

# Test SSH connection
ssh unstructured-data-bot-vm "echo 'SSH connection successful'"
```

### 2. Application Deployment
```bash
# Deploy application containers
ssh unstructured-data-bot-vm 'cd /opt/unstructured-data-bot && \
git pull origin main && \
docker-compose down && \
docker-compose pull && \
docker-compose up -d --build'
```

### 3. Health Verification
```bash
# Check service status
ssh unstructured-data-bot-vm 'cd /opt/unstructured-data-bot && docker-compose ps'

# Verify health endpoints
ssh unstructured-data-bot-vm 'curl -s http://localhost:8080/healthz'
ssh unstructured-data-bot-vm 'curl -s http://localhost:8083/healthz'
```

## Automated Deployment

### Using the Build Menu
```bash
# Start the build menu
python3 menu-workplan-execution.py

# Select Azure deployment options
# Option 8: Azure Deployment Options
#   a) Deploy containers to Azure VM
#   b) Stop containers on Azure VM
#   c) Show Azure deployment status
```

### Environment Variable Mode
```bash
# Enable Azure deployment mode
export AZURE_DEPLOYMENT=true
python3 menu-workplan-execution.py
# Options 3 and 4 now deploy to Azure automatically
```

## Post-Deployment Configuration

### 1. SSL Certificate Setup
```bash
# Configure Let's Encrypt certificates
ssh unstructured-data-bot-vm 'sudo certbot --nginx -d api.your-domain.com -d admin.your-domain.com -d bot.your-domain.com'
```

### 2. Environment Variables
```bash
# Configure application environment variables
ssh unstructured-data-bot-vm 'cd /opt/unstructured-data-bot && \
cp .env.example .env && \
# Edit .env with your configuration values'
```

### 3. Monitoring Setup
```bash
# Configure Azure Monitor and Application Insights
# (See Azure documentation for detailed setup)
```

## Troubleshooting

### Common Issues
- **SSH Connection Failed**: Verify VM public IP and security groups
- **Container Build Errors**: Check Docker logs and resource availability
- **Service Health Failures**: Verify environment variables and dependencies
- **DNS Resolution Issues**: Check DNS zone configuration and A records

### Debug Commands
```bash
# Check VM status
az vm show --resource-group rg-udb-compute --name vm-unstructured-data-bot-host

# View container logs
ssh unstructured-data-bot-vm 'cd /opt/unstructured-data-bot && docker-compose logs -f'

# Check resource usage
ssh unstructured-data-bot-vm 'docker system df && df -h'
```

## Next Steps
1. Complete post-deployment configuration
2. Set up monitoring and alerting
3. Configure backup and recovery procedures
4. Implement CI/CD pipeline integration
5. Plan production deployment strategy

---
*Last Updated: 2025-01-27*
*Version: 1.0*
