# Local Deployment Guide

## Overview
This guide covers local development and testing deployment for the Unstructured Data Indexing & AI-Query Application using Docker Compose.

## Why Local Testing is Critical

### 🚨 Risks of Skipping Local Testing
- **Network Issues**: Azure deployment failures due to connectivity problems
- **Resource Constraints**: VM memory/disk space issues discovered too late
- **Dependency Problems**: Missing dependencies or version conflicts
- **Configuration Errors**: Environment variables or config file issues
- **Debugging Complexity**: Much harder to debug issues remotely
- **Time Wasting**: Failed deployments waste time and resources

### ✅ Benefits of Local Testing
- **Fast Iteration**: Quick build/test cycles (< 2 minutes vs 15-30 minutes)
- **Easy Debugging**: Direct access to logs and containers
- **Cost Effective**: No Azure costs during development
- **Reliable Validation**: Ensure everything works before Azure deployment
- **Confidence**: Know your deployment will succeed

## Prerequisites

### Local Environment
- Docker Desktop running
- Docker Compose v2 installed
- Git repository cloned
- Sufficient resources (8GB+ RAM, 10GB+ disk space)

### Required Tools
```bash
# Verify Docker installation
docker --version
docker-compose --version

# Check available resources
docker system df
df -h

# Verify Git repository
git status
git remote -v
```

## Local Deployment Workflow

### Step 1: Environment Setup
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

### Step 2: Container Build & Test
```bash
# 1. Start local testing mode
python3 menu-workplan-execution.py

# 2. Select option 3: Bring up containers (local)
# This will:
#   - Build all containers locally
#   - Start all services
#   - Run health checks
#   - Validate functionality
```

### Step 3: Comprehensive Validation
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

## Local Testing Checklist

### ✅ Pre-Testing Validation
- [ ] **Docker Environment**: Docker running and accessible
- [ ] **Resources**: Sufficient disk space (>10GB) and memory (>8GB)
- [ ] **Network**: Internet connectivity for pulling images
- [ ] **Git**: Repository clean and up-to-date
- [ ] **Dependencies**: Required tools installed (Node.js, Python, etc.)

### ✅ Container Build Validation
- [ ] **All Images Build**: No build errors or missing dependencies
- [ ] **Docker Compose**: All services start successfully
- [ ] **Health Checks**: All services respond to health endpoints
- [ ] **Inter-Service Communication**: Services can communicate
- [ ] **Database Connectivity**: MongoDB and Redis accessible

### ✅ Functionality Testing
- [ ] **Core Services**: Orchestrator, AuthZ, AI Pipeline working
- [ ] **MCP Connectors**: Box and Microsoft files servers responding
- [ ] **Teams Bot**: Bot Framework adapter working
- [ ] **Admin UI**: Next.js interface accessible
- [ ] **API Endpoints**: All REST APIs responding correctly

### ✅ Performance Testing
- [ ] **Startup Time**: Containers start within acceptable time (< 5 minutes)
- [ ] **Memory Usage**: Services don't exceed memory limits
- [ ] **Disk Usage**: Containers don't fill disk space
- [ ] **CPU Usage**: Services don't consume excessive CPU
- [ ] **Network Latency**: Inter-service communication is fast

## Local Testing Commands

### 1. Quick Health Check
```bash
# Check all services status
docker-compose ps

# Quick health check for all services
for service in orchestrator authz ai-pipeline bot admin-ui; do
  echo "Checking $service..."
  curl -s http://localhost:$(docker-compose port $service 80 | cut -d: -f2)/healthz
done
```

### 2. Service Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f orchestrator
docker-compose logs -f authz
docker-compose logs -f ai-pipeline

# View last 100 lines of specific service
docker-compose logs --tail=100 orchestrator
```

### 3. Container Management
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# Restart specific service
docker-compose restart orchestrator

# Rebuild specific service
docker-compose up -d --build orchestrator
```

### 4. Resource Monitoring
```bash
# Check container resource usage
docker stats

# Check disk usage
docker system df

# Check network usage
docker network ls
docker network inspect unstructured-data-bot_default
```

## Troubleshooting Common Issues

### Container Won't Start
```bash
# Check container logs
docker-compose logs <service-name>

# Check container status
docker-compose ps -a

# Check resource usage
docker system df
df -h

# Restart Docker Desktop (if needed)
```

### Health Check Failures
```bash
# Check service configuration
docker-compose config

# Check environment variables
docker-compose exec <service-name> env

# Check service dependencies
docker-compose exec <service-name> ps aux
```

### Performance Issues
```bash
# Check resource usage
docker stats

# Check container limits
docker-compose exec <service-name> cat /proc/1/limits

# Check network connectivity
docker-compose exec <service-name> ping <other-service>
```

## Development Workflow

### 1. Code Changes
```bash
# Make code changes
# Test locally
docker-compose up -d --build

# Verify changes work
curl http://localhost:8080/healthz
```

### 2. Testing Changes
```bash
# Run tests
docker-compose exec orchestrator python -m pytest
docker-compose exec authz python -m pytest

# Check logs for errors
docker-compose logs --tail=50
```

### 3. Commit and Deploy
```bash
# Commit changes
git add .
git commit -m "Description of changes"

# Push to remote
git push origin main

# Deploy to Azure (if ready)
python3 menu-workplan-execution.py
# Select option 8: Azure Deployment Options
```

## Environment Configuration

### Local Environment Variables
```bash
# Copy example environment file
cp .env.example .env

# Edit environment variables
nano .env

# Key variables to configure:
# - MONGODB_URI
# - REDIS_URL
# - AZURE_OPENAI_API_KEY
# - AZURE_OPENAI_ENDPOINT
# - TEAMS_BOT_APP_ID
# - TEAMS_BOT_APP_PASSWORD
```

### Docker Compose Configuration
```yaml
# docker-compose.yml key sections:
services:
  orchestrator:
    environment:
      - MONGODB_URI=${MONGODB_URI}
      - REDIS_URL=${REDIS_URL}
    ports:
      - "8080:80"
    volumes:
      - ./logs:/app/logs
```

## Next Steps
1. Complete local testing and validation
2. Fix any issues discovered during local testing
3. Ensure all services are working correctly
4. Plan Azure deployment strategy
5. Use the build menu for automated deployment

---
*Last Updated: 2025-01-27*
*Version: 1.0*
