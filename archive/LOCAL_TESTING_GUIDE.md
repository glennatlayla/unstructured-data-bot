# Local Testing Guide - Build & Test Before Azure Deployment

## 🎯 **Why Local Testing is Critical**

**Absolutely YES** - I strongly recommend building and testing containers locally before using Azure deployment. Here's why:

### **🚨 Risks of Skipping Local Testing**
- **Network Issues**: Azure deployment failures due to connectivity problems
- **Resource Constraints**: VM memory/disk space issues discovered too late
- **Dependency Problems**: Missing dependencies or version conflicts
- **Configuration Errors**: Environment variables or config file issues
- **Debugging Complexity**: Much harder to debug issues remotely
- **Time Wasting**: Failed deployments waste time and resources

### **✅ Benefits of Local Testing**
- **Fast Iteration**: Quick build/test cycles (< 2 minutes vs 15-30 minutes)
- **Easy Debugging**: Direct access to logs and containers
- **Cost Effective**: No Azure costs during development
- **Reliable Validation**: Ensure everything works before Azure deployment
- **Confidence**: Know your deployment will succeed

## 🏠 **Local Testing Workflow**

### **Step 1: Local Environment Setup**
```bash
# 1. Ensure Docker is running
docker --version
docker-compose --version

# 2. Check available resources
docker system df
df -h

# 3. Verify Git repository
git status
git remote -v
```

### **Step 2: Local Container Build & Test**
```bash
# 1. Start local testing mode
python3 menu-workplan-execution.py

# 2. Select option 1: Bring up containers (local)
# This will:
#   - Build all containers locally
#   - Start all services
#   - Run health checks
#   - Validate functionality
```

### **Step 3: Comprehensive Local Validation**
```bash
# 1. Check all services are running
docker-compose ps

# 2. Validate health endpoints
curl http://localhost:8080/healthz  # Orchestrator
curl http://localhost:8083/healthz  # AuthZ
curl http://localhost:8085/healthz  # Enhanced AI Pipeline
curl http://localhost:3978/healthz  # Teams Bot
curl http://localhost:3000          # Admin UI

# 3. Check container logs for errors
docker-compose logs --tail=50
```

## 🔍 **Local Testing Checklist**

### **✅ Pre-Testing Validation**
- [ ] **Docker Environment**: Docker running and accessible
- [ ] **Resources**: Sufficient disk space (>10GB) and memory (>8GB)
- [ ] **Network**: Internet connectivity for pulling images
- [ ] **Git**: Repository clean and up-to-date
- [ ] **Dependencies**: Required tools installed (Node.js, Python, etc.)

### **✅ Container Build Validation**
- [ ] **All Images Build**: No build errors or missing dependencies
- [ ] **Docker Compose**: All services start successfully
- [ ] **Health Checks**: All services respond to health endpoints
- [ ] **Inter-Service Communication**: Services can communicate
- [ ] **Database Connectivity**: MongoDB and Redis accessible

### **✅ Functionality Testing**
- [ ] **Core Services**: Orchestrator, AuthZ, AI Pipeline working
- [ ] **MCP Connectors**: Box and Microsoft files servers responding
- [ ] **Teams Bot**: Bot Framework adapter working
- [ ] **Admin UI**: Next.js interface accessible
- [ ] **API Endpoints**: All REST APIs responding correctly

### **✅ Performance Testing**
- [ ] **Startup Time**: Containers start within acceptable time (< 5 minutes)
- [ ] **Memory Usage**: Services don't exceed memory limits
- [ ] **Disk Usage**: Containers don't fill disk space
- [ ] **CPU Usage**: Services don't consume excessive CPU
- [ ] **Network Latency**: Inter-service communication is fast

## 🛠️ **Local Testing Commands**

### **1. Quick Health Check**
```bash
# Check all services are running
docker-compose ps

# Test all health endpoints
for service in orchestrator authz ai-pipeline bot admin-ui; do
  echo "Testing $service..."
  curl -s http://localhost:$(case $service in 
    orchestrator) echo "8080";; 
    authz) echo "8083";; 
    ai-pipeline) echo "8085";; 
    bot) echo "3978";; 
    admin-ui) echo "3000";; 
  esac)/healthz || echo "FAILED"
done
```

### **2. Comprehensive Testing**
```bash
# Run all workplan tests locally
python3 menu-workplan-execution.py --status
python3 menu-workplan-execution.py --next

# This will:
# 1. Build all containers
# 2. Start all services
# 3. Run comprehensive tests
# 4. Validate functionality
# 5. Generate test reports
```

### **3. Debug Mode**
```bash
# Start services with debug logging
docker-compose up -d --build
docker-compose logs -f

# Check specific service logs
docker-compose logs orchestrator
docker-compose logs ai-pipeline
docker-compose logs bot
```

## 📊 **Testing Validation Results**

### **Success Criteria**
```bash
# ✅ All containers running
docker-compose ps | grep -c "Up" | grep -q "11" && echo "✅ All 11 containers running"

# ✅ All health endpoints responding
curl -s http://localhost:8080/healthz | grep -q "ok" && echo "✅ Orchestrator healthy"
curl -s http://localhost:8083/healthz | grep -q "ok" && echo "✅ AuthZ healthy"
curl -s http://localhost:8085/healthz | grep -q "ok" && echo "✅ AI Pipeline healthy"
curl -s http://localhost:3978/healthz | grep -q "ok" && echo "✅ Bot healthy"
curl -s http://localhost:3000 | grep -q "Next.js" && echo "✅ Admin UI healthy"
```

### **Performance Metrics**
```bash
# Memory usage check
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}"

# Disk usage check
docker system df

# Network connectivity check
docker-compose exec orchestrator ping -c 3 authz
docker-compose exec orchestrator ping -c 3 ai-pipeline
```

## 🚀 **Local to Azure Workflow**

### **1. Local Success Validation**
```bash
# Ensure local deployment is 100% successful
python3 menu-workplan-execution.py --status
# Verify all steps are completed locally
```

### **2. Pre-Azure Checklist**
- [ ] **Local Testing Passed**: All containers and services working
- [ ] **Git Committed**: All changes committed and pushed
- [ ] **Documentation Updated**: Any changes documented
- [ ] **Resources Available**: Azure subscription and VM ready
- [ ] **SSH Access**: SSH keys configured for Azure VM

### **3. Azure Deployment**
```bash
# Set Azure deployment mode
export AZURE_DEPLOYMENT=true

# Run Azure deployment with diagnostics
python3 menu-workplan-execution.py
# Select option 8: Azure Deployment Options
# Select option a: Run Azure diagnostics (pre-flight check)
# Select option b: Deploy containers to Azure VM
```

## 🔧 **Troubleshooting Local Issues**

### **Common Local Problems**

#### **1. Container Build Failures**
```bash
# Clean build
docker-compose down
docker system prune -f
docker-compose build --no-cache

# Check specific service build
docker-compose build orchestrator
docker-compose build ai-pipeline
```

#### **2. Service Startup Issues**
```bash
# Check service logs
docker-compose logs orchestrator
docker-compose logs ai-pipeline

# Check resource usage
docker stats --no-stream

# Restart problematic service
docker-compose restart orchestrator
```

#### **3. Network Connectivity Issues**
```bash
# Check service connectivity
docker-compose exec orchestrator curl -s http://authz:8083/healthz
docker-compose exec orchestrator curl -s http://ai-pipeline:8085/healthz

# Check DNS resolution
docker-compose exec orchestrator nslookup authz
docker-compose exec orchestrator nslookup ai-pipeline
```

#### **4. Resource Constraints**
```bash
# Check available resources
df -h
free -h

# Clean up Docker resources
docker system prune -f
docker volume prune -f
```

## 📈 **Testing Best Practices**

### **1. Incremental Testing**
```bash
# Test core infrastructure first
docker-compose up -d mongodb redis

# Test services one by one
docker-compose up -d authz
docker-compose up -d orchestrator
docker-compose up -d ai-pipeline
docker-compose up -d bot
docker-compose up -d admin-ui
```

### **2. Continuous Validation**
```bash
# Monitor health endpoints continuously
watch -n 5 'curl -s http://localhost:8080/healthz && echo " Orchestrator OK"'

# Monitor container status
watch -n 5 'docker-compose ps'
```

### **3. Performance Monitoring**
```bash
# Monitor resource usage
docker stats --no-stream

# Check for resource leaks
docker system df
```

## 🎯 **Success Metrics**

### **Local Testing Success**
- ✅ **All containers build successfully** (0 build errors)
- ✅ **All services start within 5 minutes** (11/11 services running)
- ✅ **All health endpoints respond** (5/5 endpoints healthy)
- ✅ **No critical errors in logs** (0 critical errors)
- ✅ **Resource usage within limits** (<80% memory, <90% disk)

### **Performance Targets**
- **Startup Time**: < 5 minutes for all services
- **Memory Usage**: < 8GB total for all containers
- **Disk Usage**: < 10GB for all images and volumes
- **Response Time**: < 2 seconds for health endpoints
- **Availability**: 100% service uptime during testing

## 🚀 **Next Steps After Local Success**

1. **Commit Changes**: `git add -A && git commit -m "feat: local testing completed"`
2. **Push to GitHub**: `git push origin main`
3. **Run Azure Diagnostics**: `python3 menu-workplan-execution.py` → Option 8a
4. **Deploy to Azure**: `python3 menu-workplan-execution.py` → Option 8b
5. **Validate Deployment**: `python3 menu-workplan-execution.py` → Option 8e

## ✅ **Conclusion**

**Local testing is essential** for successful Azure deployments. By following this guide, you'll:

- ✅ **Reduce deployment failures** by 80-90%
- ✅ **Speed up development** with faster iteration cycles
- ✅ **Save costs** by avoiding failed Azure deployments
- ✅ **Improve confidence** in your deployment process
- ✅ **Enable better debugging** of issues

**Always test locally first, then deploy to Azure!** This ensures smooth, reliable, and cost-effective deployments.
