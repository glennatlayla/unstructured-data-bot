#!/bin/bash
set -e

# Complete Azure provisioning script for Unstructured Data Bot
# This script provisions all required Azure resources including:
# - New Azure subscription (optional)
# - Resource groups
# - Teams bot with endpoint specifications
# - DNS entries for publicly facing URLs
# - Linux VM for container hosting with SSH key-based access
# - Network configuration and security groups

# Configuration
SUBSCRIPTION_NAME="UnstructuredDataBot-Prod"
LOCATION="eastus2"
RESOURCE_GROUP_PREFIX="rg-udb"
PROJECT_NAME="unstructured-data-bot"
DOMAIN_NAME="${DOMAIN_NAME:-your-domain.com}"
SSH_PUBLIC_KEY_PATH="${SSH_PUBLIC_KEY_PATH:-~/.ssh/id_rsa.pub}"

echo "=== Azure Provisioning for Unstructured Data Bot ==="
echo "Domain: $DOMAIN_NAME"
echo "Location: $LOCATION"
echo "Project: $PROJECT_NAME"
echo ""

# Verify prerequisites
echo "=== Prerequisites Check ==="
if ! command -v az &> /dev/null; then
    echo "ERROR: Azure CLI is not installed. Please install it first."
    exit 1
fi

if ! az account show &> /dev/null; then
    echo "ERROR: Not logged into Azure. Please run 'az login' first."
    exit 1
fi

if [[ ! -f "$SSH_PUBLIC_KEY_PATH" ]]; then
    echo "ERROR: SSH public key not found at $SSH_PUBLIC_KEY_PATH"
    echo "Generate one with: ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa"
    exit 1
fi

echo "✓ Azure CLI installed and authenticated"
echo "✓ SSH public key found"
echo ""

echo "=== Azure Subscription Setup ==="
# Create new subscription (if needed and if BILLING_ACCOUNT is set)
if [[ -n "$BILLING_ACCOUNT" && -n "$ENROLLMENT_ACCOUNT" ]]; then
    echo "Creating new Azure subscription..."
    az account management-group subscription create \
        --subscription-name "$SUBSCRIPTION_NAME" \
        --billing-account-name "$BILLING_ACCOUNT" \
        --enrollment-account-name "$ENROLLMENT_ACCOUNT" \
        --offer-type "MS-AZR-0017P" || echo "Subscription creation skipped or failed"
fi

# Set subscription context
SUBSCRIPTION_ID=$(az account list --query "[?name=='$SUBSCRIPTION_NAME'].id" -o tsv)
if [[ -n "$SUBSCRIPTION_ID" ]]; then
    az account set --subscription "$SUBSCRIPTION_ID"
    echo "✓ Using subscription: $SUBSCRIPTION_NAME"
else
    echo "✓ Using current subscription"
fi

echo ""
echo "=== Resource Groups ==="
# Create resource groups
az group create --name "${RESOURCE_GROUP_PREFIX}-core" --location "$LOCATION"
az group create --name "${RESOURCE_GROUP_PREFIX}-compute" --location "$LOCATION"
az group create --name "${RESOURCE_GROUP_PREFIX}-data" --location "$LOCATION"
az group create --name "${RESOURCE_GROUP_PREFIX}-network" --location "$LOCATION"

echo "✓ Created resource groups"
echo ""

echo "=== Teams Bot Provisioning ==="
# Create App Registration for Teams Bot
BOT_APP_ID=$(az ad app create \
    --display-name "${PROJECT_NAME}-teams-bot" \
    --sign-in-audience "AzureADMultipleOrgs" \
    --query appId -o tsv)

echo "✓ Created App Registration: $BOT_APP_ID"

# Create service principal
az ad sp create --id "$BOT_APP_ID"
echo "✓ Created service principal"

# Create client secret
BOT_CLIENT_SECRET=$(az ad app credential reset \
    --id "$BOT_APP_ID" \
    --display-name "bot-secret" \
    --query password -o tsv)

echo "✓ Created client secret"

# Create Bot Framework registration
az bot create \
    --resource-group "${RESOURCE_GROUP_PREFIX}-core" \
    --name "${PROJECT_NAME}-bot" \
    --appid "$BOT_APP_ID" \
    --password "$BOT_CLIENT_SECRET" \
    --endpoint "https://bot.${DOMAIN_NAME}/api/messages" \
    --msa-app-type "MultiTenant"

echo "✓ Created Bot Framework registration"

# Configure Teams channel
az bot msteams create \
    --resource-group "${RESOURCE_GROUP_PREFIX}-core" \
    --name "${PROJECT_NAME}-bot" \
    --enable-calling false \
    --calling-web-hook ""

echo "✓ Configured Teams channel"
echo ""

echo "=== Network and DNS Configuration ==="
# Create virtual network and subnets
az network vnet create \
    --resource-group "${RESOURCE_GROUP_PREFIX}-network" \
    --name "vnet-${PROJECT_NAME}" \
    --address-prefix "10.0.0.0/16" \
    --subnet-name "subnet-compute" \
    --subnet-prefix "10.0.1.0/24"

echo "✓ Created virtual network"

# Create network security group
az network nsg create \
    --resource-group "${RESOURCE_GROUP_PREFIX}-network" \
    --name "nsg-${PROJECT_NAME}-web"

az network nsg rule create \
    --resource-group "${RESOURCE_GROUP_PREFIX}-network" \
    --nsg-name "nsg-${PROJECT_NAME}-web" \
    --name "AllowHTTPS" \
    --priority 1000 \
    --source-address-prefixes "*" \
    --destination-port-ranges 443 \
    --protocol Tcp \
    --access Allow

az network nsg rule create \
    --resource-group "${RESOURCE_GROUP_PREFIX}-network" \
    --nsg-name "nsg-${PROJECT_NAME}-web" \
    --name "AllowSSH" \
    --priority 1001 \
    --source-address-prefixes "*" \
    --destination-port-ranges 22 \
    --protocol Tcp \
    --access Allow

az network nsg rule create \
    --resource-group "${RESOURCE_GROUP_PREFIX}-network" \
    --nsg-name "nsg-${PROJECT_NAME}-web" \
    --name "AllowHTTP" \
    --priority 1002 \
    --source-address-prefixes "*" \
    --destination-port-ranges 80 \
    --protocol Tcp \
    --access Allow

echo "✓ Created network security groups"

# Create public IP for load balancer
az network public-ip create \
    --resource-group "${RESOURCE_GROUP_PREFIX}-network" \
    --name "pip-${PROJECT_NAME}-lb" \
    --sku Standard \
    --allocation-method Static

echo "✓ Created public IP"

# Create DNS zone and records
az network dns zone create \
    --resource-group "${RESOURCE_GROUP_PREFIX}-network" \
    --name "$DOMAIN_NAME"

echo "✓ Created DNS zone"

# Get public IP address
PUBLIC_IP=$(az network public-ip show \
    --resource-group "${RESOURCE_GROUP_PREFIX}-network" \
    --name "pip-${PROJECT_NAME}-lb" \
    --query ipAddress -o tsv)

echo "✓ Public IP assigned: $PUBLIC_IP"

# Create DNS A records for publicly facing URLs
az network dns record-set a add-record \
    --resource-group "${RESOURCE_GROUP_PREFIX}-network" \
    --zone-name "$DOMAIN_NAME" \
    --record-set-name "api" \
    --ipv4-address "$PUBLIC_IP"

az network dns record-set a add-record \
    --resource-group "${RESOURCE_GROUP_PREFIX}-network" \
    --zone-name "$DOMAIN_NAME" \
    --record-set-name "admin" \
    --ipv4-address "$PUBLIC_IP"

az network dns record-set a add-record \
    --resource-group "${RESOURCE_GROUP_PREFIX}-network" \
    --zone-name "$DOMAIN_NAME" \
    --record-set-name "bot" \
    --ipv4-address "$PUBLIC_IP"

echo "✓ Created DNS A records for api, admin, and bot subdomains"
echo ""

echo "=== Linux VM Provisioning ==="
# Create cloud-init file
cat > cloud-init.yaml << 'CLOUDINIT'
#cloud-config
package_update: true
package_upgrade: true

packages:
  - docker.io
  - docker-compose
  - nginx
  - certbot
  - python3-certbot-nginx
  - git
  - curl
  - jq
  - htop
  - tree

runcmd:
  # Configure Docker
  - systemctl start docker
  - systemctl enable docker
  - usermod -aG docker azureuser
  
  # Install Docker Compose v2
  - curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
  - chmod +x /usr/local/bin/docker-compose
  
  # Configure Nginx for reverse proxy
  - systemctl start nginx
  - systemctl enable nginx
  
  # Create application directory
  - mkdir -p /opt/unstructured-data-bot
  - chown azureuser:azureuser /opt/unstructured-data-bot
  
  # Configure firewall
  - ufw allow OpenSSH
  - ufw allow 'Nginx Full'
  - ufw --force enable
  
  # Create swap file for better performance
  - fallocate -l 2G /swapfile
  - chmod 600 /swapfile
  - mkswap /swapfile
  - swapon /swapfile
  - echo '/swapfile none swap sw 0 0' >> /etc/fstab

write_files:
  - path: /etc/nginx/sites-available/unstructured-data-bot
    content: |
      server {
          listen 80;
          server_name api.${DOMAIN_NAME} admin.${DOMAIN_NAME} bot.${DOMAIN_NAME};
          
          location / {
              proxy_pass http://localhost:8080;
              proxy_set_header Host $host;
              proxy_set_header X-Real-IP $remote_addr;
              proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
              proxy_set_header X-Forwarded-Proto $scheme;
              proxy_connect_timeout 60s;
              proxy_send_timeout 60s;
              proxy_read_timeout 60s;
          }
          
          location /health {
              access_log off;
              return 200 "healthy\n";
              add_header Content-Type text/plain;
          }
      }
  - path: /opt/unstructured-data-bot/deploy.sh
    permissions: '0755'
    content: |
      #!/bin/bash
      cd /opt/unstructured-data-bot
      if [ ! -d ".git" ]; then
          git clone https://github.com/glennatlayla/unstructured-data-bot.git .
      else
          git pull origin main
      fi
      docker-compose down || true
      docker-compose pull
      docker-compose up -d
      echo "Deployment completed at $(date)"
CLOUDINIT

echo "✓ Created cloud-init configuration"

# Create Linux VM for hosting containers (MongoDB, discovery programs, admin portal)
az vm create \
    --resource-group "${RESOURCE_GROUP_PREFIX}-compute" \
    --name "vm-${PROJECT_NAME}-host" \
    --image "Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:latest" \
    --size "Standard_D4s_v3" \
    --vnet-name "vnet-${PROJECT_NAME}" \
    --subnet "subnet-compute" \
    --nsg "nsg-${PROJECT_NAME}-web" \
    --public-ip-address "pip-${PROJECT_NAME}-vm" \
    --ssh-key-values "$SSH_PUBLIC_KEY_PATH" \
    --admin-username "azureuser" \
    --custom-data cloud-init.yaml

echo "✓ Created Linux VM for container hosting"

# Get VM public IP
VM_PUBLIC_IP=$(az vm show \
    --resource-group "${RESOURCE_GROUP_PREFIX}-compute" \
    --name "vm-${PROJECT_NAME}-host" \
    --show-details \
    --query publicIps -o tsv)

echo "✓ VM Public IP: $VM_PUBLIC_IP"
echo ""

echo "=== SSH Configuration ==="
# Configure SSH access from development server
SSH_CONFIG_ENTRY="
Host unstructured-data-bot-vm
    HostName $VM_PUBLIC_IP
    User azureuser
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking no
    ServerAliveInterval 60
    ServerAliveCountMax 3
"

if ! grep -q "Host unstructured-data-bot-vm" ~/.ssh/config 2>/dev/null; then
    echo "$SSH_CONFIG_ENTRY" >> ~/.ssh/config
    echo "✓ Added SSH configuration to ~/.ssh/config"
else
    echo "✓ SSH configuration already exists"
fi

echo ""
echo "=== Azure Services ==="
# Create Key Vault
KEY_VAULT_SUFFIX=$(date +%s | tail -c 6)
az keyvault create \
    --resource-group "${RESOURCE_GROUP_PREFIX}-core" \
    --name "kv-${PROJECT_NAME}-${KEY_VAULT_SUFFIX}" \
    --location "$LOCATION" \
    --sku standard

KEY_VAULT_NAME="kv-${PROJECT_NAME}-${KEY_VAULT_SUFFIX}"
echo "✓ Created Key Vault: $KEY_VAULT_NAME"

# Store secrets in Key Vault
az keyvault secret set \
    --vault-name "$KEY_VAULT_NAME" \
    --name "teams-bot-app-id" \
    --value "$BOT_APP_ID"

az keyvault secret set \
    --vault-name "$KEY_VAULT_NAME" \
    --name "teams-bot-client-secret" \
    --value "$BOT_CLIENT_SECRET"

az keyvault secret set \
    --vault-name "$KEY_VAULT_NAME" \
    --name "vm-public-ip" \
    --value "$VM_PUBLIC_IP"

az keyvault secret set \
    --vault-name "$KEY_VAULT_NAME" \
    --name "public-ip" \
    --value "$PUBLIC_IP"

echo "✓ Stored secrets in Key Vault"
echo ""

# Clean up temporary files
rm -f cloud-init.yaml

echo "=== Deployment Summary ==="
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Azure Infrastructure Provisioned Successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 Teams Bot Configuration:"
echo "   App ID: $BOT_APP_ID"
echo "   Endpoint: https://bot.${DOMAIN_NAME}/api/messages"
echo ""
echo "🌐 Public URLs:"
echo "   API Endpoint: https://api.${DOMAIN_NAME}"
echo "   Admin UI: https://admin.${DOMAIN_NAME}"
echo "   Bot Endpoint: https://bot.${DOMAIN_NAME}"
echo ""
echo "🖥️  Linux VM Details:"
echo "   VM Public IP: $VM_PUBLIC_IP"
echo "   SSH Access: ssh unstructured-data-bot-vm"
echo "   OS: Ubuntu 22.04 LTS"
echo "   Size: Standard_D4s_v3"
echo ""
echo "🔐 Security & Access:"
echo "   Key Vault: $KEY_VAULT_NAME"
echo "   SSH Key: Key-based authentication configured"
echo "   Network: Virtual network with security groups"
echo ""
echo "📋 DNS Configuration:"
echo "   Zone: $DOMAIN_NAME"
echo "   A Records: api, admin, bot → $PUBLIC_IP"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. 🕐 Wait for VM initialization (5-10 minutes)"
echo "   The VM is installing Docker, Nginx, and other dependencies"
echo ""
echo "2. 🔌 Test SSH connectivity:"
echo "   ssh unstructured-data-bot-vm 'echo \"Connection successful\"'"
echo ""
echo "3. 🐳 Deploy application containers:"
echo "   ssh unstructured-data-bot-vm '/opt/unstructured-data-bot/deploy.sh'"
echo ""
echo "4. 🔒 Configure SSL certificates:"
echo "   ssh unstructured-data-bot-vm 'sudo certbot --nginx -d api.${DOMAIN_NAME} -d admin.${DOMAIN_NAME} -d bot.${DOMAIN_NAME} --non-interactive --agree-tos --email admin@${DOMAIN_NAME}'"
echo ""
echo "5. 📋 Configure DNS nameservers:"
echo "   Update your domain registrar to use these Azure DNS nameservers:"
az network dns zone show \
    --resource-group "${RESOURCE_GROUP_PREFIX}-network" \
    --name "$DOMAIN_NAME" \
    --query nameServers -o tsv | sed 's/^/   /'
echo ""
echo "6. 🎯 Update Teams app manifest with Bot App ID: $BOT_APP_ID"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Provisioning Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
