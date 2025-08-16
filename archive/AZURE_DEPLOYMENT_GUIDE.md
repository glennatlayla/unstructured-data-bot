# Azure Deployment Guide

## 🎯 **Azure Container Deployment**

This guide explains how to deploy containers to the newly provisioned Azure subscription and resource group.

## ✅ **Current Implementation**

### **Menu Options**
The build menu system now includes Azure deployment options:

```
================  Build & Test Manager  ================
1) Show workplan status
2) Generate curl test harness
3) Bring up containers (local)
4) Bring down containers (local)
5) Run NEXT step (execute + test + commit)
6) Rollback to previous step
7) Rollback to specific step ID
8) Azure Deployment Options  ← NEW!
9) Exit
========================================================
```

### **Azure Deployment Options**
When you select option 8, you get:

```
================  Azure Deployment Options  ================
a) Deploy containers to Azure VM
b) Stop containers on Azure VM
c) Show Azure deployment status
d) Back to main menu
========================================================
```

## 🚀 **How It Works**

### **1. Prerequisites**
- ✅ Azure subscription provisioned (Step 13 completed)
- ✅ SSH key pair configured
- ✅ Azure CLI installed and authenticated
- ✅ VM created with Docker and Docker Compose

### **2. Deployment Process**
When you select "Deploy containers to Azure VM":

1. **Check VM Status**: Verifies Azure VM exists and is accessible
2. **SSH Connection**: Tests SSH connectivity to the VM
3. **Git Pull**: Pulls latest code from GitHub
4. **Container Deployment**: 
   - Stops existing containers
   - Pulls latest images
   - Starts containers with latest code

### **3. Deployment Commands**
```bash
# Deploy to Azure VM
ssh unstructured-data-bot-vm 'cd /opt/unstructured-data-bot && \
git pull origin main && \
docker-compose down && \
docker-compose pull && \
docker-compose up -d --build'

# Stop containers on Azure VM
ssh unstructured-data-bot-vm 'cd /opt/unstructured-data-bot && \
docker-compose down'

# Check status on Azure VM
ssh unstructured-data-bot-vm 'cd /opt/unstructured-data-bot && \
docker-compose ps'
```

## 🎯 **Usage Examples**

### **1. Local Development**
```bash
# Local container management
python3 menu-workplan-execution.py
# Select option 3: Bring up containers (local)
# Select option 4: Bring down containers (local)
```

### **2. Azure Deployment**
```bash
# Azure container management
python3 menu-workplan-execution.py
# Select option 8: Azure Deployment Options
# Select option a: Deploy containers to Azure VM
```

### **3. Environment Variable Mode**
```bash
# Enable Azure deployment mode
export AZURE_DEPLOYMENT=true
python3 menu-workplan-execution.py
# Options 3 and 4 now deploy to Azure automatically
```

## 🔧 **Technical Details**

### **Azure VM Configuration**
- **Resource Group**: `rg-udb-compute`
- **VM Name**: `vm-unstructured-data-bot-host`
- **SSH Host**: `unstructured-data-bot-vm` (configured in `~/.ssh/config`)
- **Application Directory**: `/opt/unstructured-data-bot`

### **Container Services**
The following services are deployed to Azure:
- **Orchestrator**: Main RAG orchestrator service
- **AI Pipeline**: Enhanced AI processing pipeline
- **Teams Bot**: Microsoft Teams bot service
- **Admin UI**: Next.js admin interface
- **MongoDB**: Database service
- **Redis**: Caching service

### **Network Configuration**
- **Public IP**: Assigned to load balancer
- **DNS**: `api.your-domain.com`, `admin.your-domain.com`, `bot.your-domain.com`
- **SSL**: Configured with Let's Encrypt certificates
- **Firewall**: HTTPS (443) and SSH (22) ports open

## 📊 **Status Monitoring**

### **Azure Status Check**
```bash
# Check Azure deployment status
python3 menu-workplan-execution.py
# Select option 8: Azure Deployment Options
# Select option c: Show Azure deployment status
```

This will show:
- ✅ Azure VM IP address
- ✅ Container status for all services
- ✅ Service health and uptime

### **Service Endpoints**
After deployment, services are available at:
- **API**: `https://api.your-domain.com`
- **Admin UI**: `https://admin.your-domain.com`
- **Teams Bot**: `https://bot.your-domain.com`

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **1. VM Not Found**
```bash
# Error: Azure VM not found
# Solution: Run Azure provisioning first
python3 menu-workplan-execution.py --status
# Check if Step 13 is completed
```

#### **2. SSH Connection Failed**
```bash
# Error: Cannot connect to Azure VM
# Solution: Check SSH configuration
ssh unstructured-data-bot-vm
# Verify SSH key is configured
```

#### **3. Container Deployment Failed**
```bash
# Error: Docker deployment failed
# Solution: Check VM resources and Docker installation
ssh unstructured-data-bot-vm 'docker --version'
ssh unstructured-data-bot-vm 'docker-compose --version'
```

### **Manual Deployment**
If automated deployment fails, you can manually deploy:

```bash
# SSH to Azure VM
ssh unstructured-data-bot-vm

# Navigate to application directory
cd /opt/unstructured-data-bot

# Pull latest code
git pull origin main

# Deploy containers
docker-compose down
docker-compose pull
docker-compose up -d --build

# Check status
docker-compose ps
```

## 📈 **Benefits**

### **1. Production Ready**
- ✅ Full Azure infrastructure provisioning
- ✅ Automatic container deployment
- ✅ SSL certificate management
- ✅ Load balancer configuration
- ✅ DNS management

### **2. Scalable Architecture**
- ✅ Container orchestration
- ✅ Service discovery
- ✅ Health monitoring
- ✅ Automatic scaling capabilities

### **3. Enterprise Features**
- ✅ Teams integration
- ✅ SSO authentication
- ✅ Security trimming
- ✅ Audit logging

## 🎯 **Next Steps**

1. **Complete Azure Provisioning** (Step 13)
2. **Test Azure Deployment** (Option 8a)
3. **Configure SSL Certificates** (automatic with Let's Encrypt)
4. **Set Up Monitoring** (Azure Monitor integration)
5. **Configure Backup** (Azure Backup for data)

This implementation ensures that your containers are deployed to the newly provisioned Azure subscription and resource group, not just locally!
