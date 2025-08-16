# Development Guide

> **Complete development setup and workflow for the Unstructured Data Indexing & AI-Query Application**

**Version**: 3.0  
**Last Updated**: 2025-01-27  
**Status**: Active Development

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing Strategy](#testing-strategy)
- [Debugging & Troubleshooting](#debugging--troubleshooting)
- [Code Standards & Conventions](#code-standards--conventions)
- [Contributing Guidelines](#contributing-guidelines)
- [Performance Considerations](#performance-considerations)
- [Security Best Practices](#security-best-practices)

## Overview

This guide covers the complete development workflow for building, testing, and deploying the Unstructured Data Indexing & AI-Query Application. The system is built as a microservices architecture with containerized services, comprehensive testing, and automated deployment pipelines.

### Development Philosophy

- **Test-Driven Development**: All features require tests before implementation
- **Container-First**: All services run in Docker containers for consistency
- **Security by Design**: Security validation at every layer
- **Performance Monitoring**: Continuous performance tracking and optimization
- **Documentation as Code**: All APIs and interfaces documented

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| **Docker** | 24.0+ | Container runtime |
| **Docker Compose** | 2.20+ | Multi-container orchestration |
| **Python** | 3.11+ | Backend services |
| **Node.js** | 18.0+ | Frontend and bot services |
| **Git** | 2.30+ | Version control |
| **Azure CLI** | 3.0+ | Azure deployment (optional) |

### System Requirements

- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 20GB available space
- **CPU**: 4 cores minimum, 8 cores recommended
- **OS**: macOS 12+, Ubuntu 22.04+, Windows 11+

### Azure Prerequisites (for deployment)

- Azure subscription with billing enabled
- Azure CLI installed and authenticated (`az login`)
- Contributor access to subscription
- Domain name for production deployment

## Development Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/unstructured-data-bot.git
cd unstructured-data-bot
```

### 2. Environment Configuration

Create environment file from template:

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

**Required Environment Variables**:

```bash
# Azure Configuration
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net/
AZURE_SEARCH_API_KEY=your-search-key
AZURE_KEY_VAULT_URL=https://your-vault.vault.azure.net/

# MongoDB Configuration
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/unstructured_data

# Application Configuration
TENANT_ID=default
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

### 3. Docker Setup

Ensure Docker is running and accessible:

```bash
# Verify Docker installation
docker --version
docker-compose --version

# Start Docker daemon (if needed)
sudo systemctl start docker
sudo systemctl enable docker
```

### 4. Service Dependencies

Start required external services:

```bash
# Start MongoDB (if not using Docker)
docker run -d --name mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  mongo:7.0

# Start Redis (if needed)
docker run -d --name redis \
  -p 6379:6379 \
  redis:7.0-alpine
```

## Project Structure

```
unstructured-data-bot/
├── services/                 # Microservices
│   ├── admin-ui/            # Next.js admin interface
│   ├── ai-pipeline/         # AI processing service
│   ├── authz/               # Authorization service
│   ├── bot/                 # Teams bot service
│   ├── cost/                # Cost tracking service
│   ├── ingestion/           # Data ingestion service
│   ├── mcp-connectors/      # MCP integration services
│   ├── orchestrator/        # Main orchestration service
│   └── prefilter/           # Content preprocessing
├── docker/                  # Docker configurations
│   ├── admin-ui/           # Admin UI container
│   ├── ai-pipeline/        # AI Pipeline container
│   ├── authz/              # AuthZ container
│   ├── bot/                # Bot container
│   ├── cost/               # Cost service container
│   ├── ingestion/          # Ingestion container
│   ├── mcp-box-server/     # Box MCP server
│   ├── mcp-files-server/   # Files MCP server
│   ├── orchestrator/       # Orchestrator container
│   └── prefilter/          # Pre-filter container
├── scripts/                 # Automation scripts
│   ├── azure/              # Azure deployment scripts
│   ├── backup/             # Backup and restore scripts
│   ├── teams/              # Teams bot configuration
│   └── testing/            # Test automation
├── docs/                   # Documentation
├── tests/                  # Test suites
└── docker-compose.yml      # Service orchestration
```

## Development Workflow

### 1. Local Development

Start the complete development environment:

```bash
# Start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check service health
./scripts/health-check.sh
```

### 2. Service Development

#### Python Services

```bash
# Navigate to service directory
cd services/orchestrator

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run service locally
python app/main.py
```

#### Node.js Services

```bash
# Navigate to service directory
cd services/admin-ui

# Install dependencies
npm install

# Run tests
npm test

# Start development server
npm run dev
```

### 3. Testing Workflow

```bash
# Run all tests
./scripts/run-tests.sh

# Run specific service tests
docker-compose exec orchestrator python -m pytest

# Run integration tests
./scripts/integration-test.sh

# Run performance tests
./scripts/performance-test.sh
```

### 4. Build and Deploy

```bash
# Build specific service
docker-compose build orchestrator

# Build all services
docker-compose build

# Deploy to local environment
docker-compose up -d --build

# Deploy to Azure (if configured)
./scripts/azure/deploy.sh
```

## Testing Strategy

### Testing Pyramid

```
    /\
   /  \     E2E Tests (5%)
  /____\    Integration Tests (15%)
 /      \   Unit Tests (80%)
/________\
```

### Unit Testing

**Coverage Requirements**: Minimum 80% code coverage

```python
# Example unit test
import pytest
from app.intelligent_router import IntelligentRouter

def test_model_selection():
    router = IntelligentRouter()
    model = router.select_model("financial_analysis", budget=100)
    assert model.name == "gpt-4-turbo"
    assert model.cost_per_1k_tokens <= 0.03
```

### Integration Testing

**Test Environment**: Docker Compose with test databases

```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
pytest tests/integration/ --docker

# Cleanup test environment
docker-compose -f docker-compose.test.yml down -v
```

### End-to-End Testing

**Test Scenarios**: Complete user workflows

```bash
# Run E2E tests
./scripts/e2e-test.sh

# Test specific scenarios
pytest tests/e2e/test_teams_bot.py::test_financial_query
```

### Performance Testing

**Performance Targets**:

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Query Response Time** | < 2 seconds | 95th percentile |
| **Ingestion Throughput** | > 1000 files/hour | Per tenant |
| **Concurrent Users** | > 100 | Without degradation |
| **Memory Usage** | < 2GB | Per service container |

```bash
# Run performance tests
./scripts/performance-test.sh

# Load testing
locust -f tests/performance/locustfile.py
```

## Debugging & Troubleshooting

### Common Issues

#### 1. Service Won't Start

```bash
# Check service logs
docker-compose logs <service-name>

# Check service status
docker-compose ps

# Restart specific service
docker-compose restart <service-name>
```

#### 2. Build Failures

```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache

# Check Dockerfile syntax
docker build --dry-run .
```

#### 3. Connection Issues

```bash
# Check network connectivity
docker-compose exec <service> ping <target-service>

# Verify environment variables
docker-compose exec <service> env | grep AZURE

# Check service health endpoints
curl http://localhost:8080/healthz
```

### Debug Mode

Enable debug logging:

```bash
# Set debug environment
export LOG_LEVEL=DEBUG
export DEBUG=true

# Start services with debug
docker-compose up -d --build

# View debug logs
docker-compose logs -f --tail=100
```

### Remote Debugging

#### Python Services

```python
# Add debug breakpoint
import pdb; pdb.set_trace()

# Or use debugpy for VS Code
import debugpy
debugpy.listen(5678)
debugpy.wait_for_client()
```

#### Node.js Services

```javascript
// Add debug breakpoint
debugger;

// Or use --inspect flag
// package.json
"scripts": {
  "debug": "node --inspect=0.0.0.0:9229 app/index.js"
}
```

## Code Standards & Conventions

### Python Standards

**Style Guide**: PEP 8 with Black formatting

```bash
# Install development tools
pip install black flake8 mypy pytest

# Format code
black services/orchestrator/

# Lint code
flake8 services/orchestrator/

# Type checking
mypy services/orchestrator/
```

**Code Structure**:
```python
"""
Service module for intelligent routing and model selection.

This module provides intelligent routing capabilities for AI model selection
based on query type, budget constraints, and performance requirements.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for AI model selection."""
    name: str
    cost_per_1k_tokens: float
    capabilities: List[str]
```

### Node.js Standards

**Style Guide**: ESLint with Prettier

```bash
# Install development tools
npm install --save-dev eslint prettier

# Format code
npm run format

# Lint code
npm run lint
```

**Code Structure**:
```javascript
/**
 * Admin UI service for policy management and system monitoring.
 * 
 * @module admin-ui
 * @requires express
 * @requires next
 */

const express = require('express');
const next = require('next');

class AdminUIService {
  constructor() {
    this.app = express();
    this.nextApp = next({ dev: process.env.NODE_ENV !== 'production' });
  }
}

module.exports = AdminUIService;
```

### API Design Standards

**RESTful Conventions**:
- Use HTTP methods correctly (GET, POST, PUT, DELETE)
- Consistent URL patterns (`/api/v3/resource`)
- Standard HTTP status codes
- JSON request/response format

**Error Handling**:
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "tenant_id",
      "issue": "Required field missing"
    }
  }
}
```

## Contributing Guidelines

### Development Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow coding standards
   - Add tests for new functionality
   - Update documentation

3. **Test Changes**
   ```bash
   # Run tests
   ./scripts/run-tests.sh
   
   # Check code quality
   ./scripts/code-quality.sh
   ```

4. **Submit Pull Request**
   - Include description of changes
   - Reference related issues
   - Ensure CI/CD passes

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests pass and coverage maintained
- [ ] Documentation updated
- [ ] Security considerations addressed
- [ ] Performance impact assessed
- [ ] Error handling implemented
- [ ] Logging appropriate

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples**:
```
feat(orchestrator): add intelligent model routing

fix(authz): resolve principal resolution race condition

docs(api): update endpoint documentation
```

## Performance Considerations

### Optimization Strategies

1. **Caching**
   - Redis for session data
   - In-memory caching for frequent queries
   - CDN for static assets

2. **Async Processing**
   - Background tasks for heavy operations
   - Queue-based processing for ingestion
   - Non-blocking API calls

3. **Database Optimization**
   - Index optimization for common queries
   - Connection pooling
   - Query result caching

4. **Resource Management**
   - Container resource limits
   - Auto-scaling based on load
   - Graceful degradation

### Monitoring & Metrics

**Key Metrics**:
- Response time percentiles
- Throughput (requests/second)
- Error rates
- Resource utilization
- Cost per operation

**Tools**:
- Azure Monitor
- Application Insights
- Custom metrics collection
- Performance dashboards

## Security Best Practices

### Authentication & Authorization

1. **Token Management**
   - Secure token storage in Key Vault
   - Regular token rotation
   - Scope-limited access tokens

2. **Principal Resolution**
   - Validate user permissions
   - Security trimming at query time
   - Audit all access decisions

3. **API Security**
   - Rate limiting
   - Input validation
   - SQL injection prevention
   - XSS protection

### Data Protection

1. **Encryption**
   - Data at rest encryption
   - TLS for data in transit
   - Key rotation policies

2. **Access Control**
   - Least privilege principle
   - Tenant isolation
   - Regular access reviews

3. **Audit & Compliance**
   - Comprehensive logging
   - Security event monitoring
   - Compliance reporting

### Security Testing

```bash
# Run security tests
./scripts/security-test.sh

# Dependency vulnerability scan
npm audit
pip-audit

# Container security scan
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image <image-name>
```

---

**Next**: [Deployment Guide](DEPLOYMENT.md) | [Testing Guide](TESTING.md) | [Operations Guide](OPERATIONS.md)

**Back to**: [README](../README.md) | [API Reference](API_REFERENCE.md) | [Architecture](ARCHITECTURE.md)
