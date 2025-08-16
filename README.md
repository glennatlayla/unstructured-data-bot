# Unstructured Data Indexing & AI-Query Application

> **Enterprise-grade system for indexing and querying unstructured data from Box, SharePoint, and OneDrive with AI-powered search and security trimming.**

## 🚀 Quick Start

```bash
# Start all services
python3 menu-workplan-execution.py --next

# Interactive mode
python3 menu-workplan-execution.py

# Test Azure integration
python3 test_azure_integration.py
```

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Documentation Map](#documentation-map)
- [Getting Started](#getting-started)
- [Development](#development)
- [Deployment](#deployment)
- [Testing](#testing)

## 🎯 Overview

This application is a **comprehensive enterprise data platform** that transforms unstructured data from multiple sources into searchable, AI-queryable content. It provides:

- **Multi-source integration** with Box, SharePoint, and OneDrive
- **AI-powered search** using Azure OpenAI and vector embeddings
- **Enterprise security** with rights-aware querying and security trimming
- **Cost management** with usage tracking and forecasting
- **Modern architecture** built on microservices and containerization

## 🏗️ Architecture

### Core Components

| Service | Port | Purpose | Technology |
|---------|------|---------|------------|
| **Admin UI** | 3000 | Policy editor, dashboard | Next.js |
| **Orchestrator** | 8080 | Query orchestration | Python |
| **Ingestion** | 8081 | Data ingestion pipeline | Python |
| **AuthZ** | 8083 | Authorization & security | Python |
| **AI Pipeline** | 8085 | AI processing & embeddings | Python |
| **Teams Bot** | 3978 | Conversational interface | Node.js |
| **Cost Service** | 8082 | Cost tracking | Python |
| **MCP Connectors** | 8086-7 | External integrations | Python |

### Data Flow

```
1. Admin connects sources → 2. Ingestion discovers files → 3. AI processes content
4. Indexes in MongoDB + Azure Search → 5. User queries via Teams/UI
6. Security trimming → 7. AI-powered responses with cost tracking
```

## ✨ Features

### 🔐 Security & Compliance
- **Multi-tenant isolation** with per-tenant data partitioning
- **Security trimming** at query time with principal intersection checks
- **Sensitive data classification** (PII/PHI/PCI/ITAR)
- **Audit trails** with immutable logs and security decision traces

### 🤖 AI & Intelligence
- **Intelligent document processing** with hierarchical metadata
- **Multi-vector embeddings** for semantic search
- **Advanced summarization** with structured JSON output
- **Confidence-based classification** with admin-configurable policies

### 💰 Cost Management
- **Real-time cost tracking** per tenant and operation
- **Usage forecasting** and budget management
- **Cost optimization** with automatic model selection
- **Spend analytics** and reporting

### 🔌 Integration
- **Model Context Protocol (MCP)** for external services
- **OAuth integration** with Entra ID
- **RESTful APIs** for all services
- **Webhook support** for real-time updates

## 📚 Documentation Map

### **Primary Documentation**
- **[`docs/SPECIFICATION.md`](docs/SPECIFICATION.md)** - Complete software specification (v3)
- **[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)** - System architecture and design decisions
- **[`docs/API_REFERENCE.md`](docs/API_REFERENCE.md)** - Service APIs and endpoints

### **Implementation Guides**
- **[`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)** - Development setup and workflow
- **[`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)** - Production deployment guide
- **[`docs/TESTING.md`](docs/TESTING.md)** - Testing strategy and procedures

### **Operational Documentation**
- **[`docs/OPERATIONS.md`](docs/OPERATIONS.md)** - Monitoring, troubleshooting, and maintenance
- **[`docs/SECURITY.md`](docs/SECURITY.md)** - Security features and compliance
- **[`docs/COST_MANAGEMENT.md`](docs/COST_MANAGEMENT.md)** - Cost tracking and optimization

### **Legacy Files** (Being Consolidated)
- `AZURE_DEPLOYMENT_GUIDE.md` → Merged into `docs/DEPLOYMENT.md`
- `BUILD_SEQUENCE_*.md` → Merged into `docs/DEVELOPMENT.md`
- `ENHANCED_DEPLOYMENT_PLAN.md` → Merged into `docs/DEPLOYMENT.md`
- `LOCAL_TESTING_*.md` → Merged into `docs/TESTING.md`
- `PRODUCTION_REQUIREMENTS_*.md` → Merged into `docs/SPECIFICATION.md`
- `RAG_METADATA_*.md` → Merged into `docs/ARCHITECTURE.md`
- `self-audit-checklist.md` → Merged into `docs/OPERATIONS.md`

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- Azure subscription with OpenAI, AI Search, and Key Vault
- Microsoft 365 account for Teams integration

### Environment Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd "Unstructured Data Bot"

# Create environment file
./create_env_file.sh

# Edit .env with your Azure credentials
nano .env

# Start services
docker-compose up -d
```

### First Run
```bash
# Execute the workplan
python3 menu-workplan-execution.py

# Test Azure integration
python3 test_azure_integration.py

# Access Admin UI
open http://localhost:3000
```

## 🛠️ Development

### Project Structure
```
services/           # Microservices
├── admin-ui/      # Next.js admin interface
├── orchestrator/  # Main API gateway
├── ingestion/     # Data ingestion pipeline
├── authz/         # Authorization service
├── ai-pipeline/   # AI processing
├── bot/           # Teams bot service
└── cost/          # Cost management

docker/            # Docker configurations
infra/             # Infrastructure as code
scripts/           # Utility scripts
tests/             # Test suites
```

### Development Workflow
```bash
# Interactive development
python3 menu-workplan-execution.py

# Run specific tests
python3 test_azure_integration.py
python3 test_model_routing.py

# Check service health
curl http://localhost:8080/healthz
```

## 🚀 Deployment

### Local Development
```bash
docker-compose up -d
```

### Production (Azure)
```bash
# Provision Azure resources
./scripts/azure/provision_complete.sh

# Deploy services
./scripts/azure/provision_ai_components.sh
```

### Monitoring
- **Health checks**: `/healthz` endpoints on all services
- **Logs**: Centralized logging via Docker Compose
- **Metrics**: Built-in performance monitoring
- **Cost tracking**: Real-time spend analytics

## 🧪 Testing

### Test Categories
- **Unit tests**: Individual service functionality
- **Integration tests**: Service-to-service communication
- **Azure integration**: Cloud service connectivity
- **Security tests**: Authorization and access control
- **End-to-end**: Complete workflow validation

### Running Tests
```bash
# All tests
python3 -m pytest tests/

# Specific test suite
python3 test_azure_integration.py
python3 test_model_routing.py

# Security validation
python3 test_key_vault.py
```

## 📞 Support

### Getting Help
1. **Check the logs**: `docker-compose logs <service-name>`
2. **Review documentation**: See the [Documentation Map](#documentation-map)
3. **Run diagnostics**: `python3 menu-workplan-execution.py --diagnose`
4. **Check health**: All services expose `/healthz` endpoints

### Common Issues
- **Environment variables**: Ensure `.env` file is properly configured
- **Azure connectivity**: Verify credentials and network access
- **Service dependencies**: Check Docker Compose service health
- **Port conflicts**: Ensure required ports are available

## 📄 License

This project is proprietary software. All rights reserved.

---

**Last Updated**: August 2024  
**Version**: 3.0  
**Status**: Production Ready ✅
