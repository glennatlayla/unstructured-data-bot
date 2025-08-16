# System Architecture & Design Decisions

> **Comprehensive architecture documentation for the Unstructured Data Indexing & AI-Query Application**

**Document Status**: Production Ready • **Date**: August 2024 • **Version**: 3.0

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Enhanced RAG Design](#enhanced-rag-design)
- [Service Architecture](#service-architecture)
- [Data Architecture](#data-architecture)
- [Security Architecture](#security-architecture)
- [Integration Patterns](#integration-patterns)
- [Performance & Scalability](#performance--scalability)
- [Deployment Architecture](#deployment-architecture)

## 🏗️ Architecture Overview

### Design Principles
- **Microservices Architecture**: Loosely coupled, independently deployable services
- **Security-First**: Zero-trust security model with comprehensive access controls
- **Scalability**: Horizontal scaling with auto-scaling capabilities
- **Observability**: Comprehensive monitoring, logging, and metrics
- **Cost Optimization**: Intelligent resource allocation and usage tracking

### Technology Stack
- **Backend**: Python 3.9+ with FastAPI/Flask
- **Frontend**: Next.js with TypeScript
- **Database**: MongoDB for metadata, Azure AI Search for vectors
- **AI Services**: Azure OpenAI for summarization and embeddings
- **Infrastructure**: Docker, Kubernetes, Azure Cloud
- **Security**: Azure Key Vault, OAuth 2.0, JWT tokens

## 🤖 Enhanced RAG Design

### 1.1 Enhanced AI Pipeline Service

#### Build Requirements
- **Docker Image**: `enhanced-ai-pipeline:2.0.0`
- **Base Image**: `python:3.12-slim`
- **Dependencies**: 
  - `langchain==0.1.0`
  - `langchain-text-splitters==0.0.1`
  - `spacy==3.7.2`
  - `openai==1.6.1`
  - `azure-search-documents==11.4.0`
  - `transformers==4.36.0`
  - `sentence-transformers==2.2.2`

#### Service Components
1. **EnhancedDocumentSummarizer** - Hierarchical summary generation
2. **IntelligentDocumentEmbedder** - Multi-vector embedding generation
3. **AdvancedSensitiveDataClassifier** - Confidence-based classification
4. **IntelligentChunker** - Adaptive chunking with semantic boundaries
5. **HierarchicalMetadataProcessor** - Multi-level metadata processing
6. **MetadataCacheManager** - Multi-level caching with TTL

#### Deployment Steps
```bash
# Build enhanced AI pipeline
docker build -t enhanced-ai-pipeline:2.0.0 ./docker/ai-pipeline

# Deploy enhanced AI pipeline
docker compose up -d enhanced-ai-pipeline

# Verify deployment
curl -s http://localhost:8085/healthz | jq '.features'
```

### 1.2 Enhanced Database Schema

#### MongoDB Collections Update
```javascript
// Enhanced files collection
db.files.updateMany({}, {
  $set: {
    "hierarchical_metadata": {
      "core": {},
      "content": {},
      "semantic": {},
      "security": {},
      "processing": {},
      "contextual": {}
    },
    "enhanced_summary_ref": {},
    "advanced_classification": {},
    "enhanced_ai_processed_at": null,
    "processing_version": "2.0.0"
  }
});

// Enhanced chunks collection
db.chunks.updateMany({}, {
  $set: {
    "metadata": {
      "chunk_type": "generic",
      "position": 0,
      "length": 0,
      "semantic_context": "",
      "entities": [],
      "sensitivity_flags": [],
      "embedding_model": "text-embedding-ada-002",
      "embedding_version": "1.0"
    }
  }
});
```

#### Index Creation
```javascript
// Enhanced indexes for performance
db.files.createIndex({ "tenant_id": 1, "source": 1, "modified_at": -1 });
db.files.createIndex({ "tenant_id": 1, "hierarchical_metadata.semantic.classification.sensitivity_flags": 1 });
db.files.createIndex({ "tenant_id": 1, "hierarchical_metadata.security.allowed_principals": 1 });
db.files.createIndex({ "tenant_id": 1, "hierarchical_metadata.core.path": 1 });
db.files.createIndex({ "tenant_id": 1, "hierarchical_metadata.contextual.department": 1 });

db.chunks.createIndex({ "file_id": 1, "chunk_id": 1 });
db.chunks.createIndex({ "tenant_id": 1, "file_id": 1 });
db.chunks.createIndex({ "metadata.chunk_type": 1 });
```

### 1.3 Enhanced Azure AI Search Index

#### Index Schema Update
```json
{
  "name": "enhanced-documents-v2",
  "fields": [
    {
      "name": "id",
      "type": "Edm.String",
      "key": true,
      "searchable": false
    },
    {
      "name": "tenant_id",
      "type": "Edm.String",
      "filterable": true,
      "searchable": false
    },
    {
      "name": "file_id",
      "type": "Edm.String",
      "filterable": true,
      "searchable": false
    },
    {
      "name": "content",
      "type": "Edm.String",
      "searchable": true,
      "analyzer": "standard"
    },
    {
      "name": "contentVector",
      "type": "Collection(Edm.Single)",
      "searchable": true,
      "vectorSearchProfile": "default"
    },
    {
      "name": "hierarchical_metadata",
      "type": "Edm.String",
      "searchable": true,
      "filterable": true
    },
    {
      "name": "sensitivity_flags",
      "type": "Collection(Edm.String)",
      "filterable": true,
      "searchable": false
    },
    {
      "name": "allowed_principals",
      "type": "Collection(Edm.String)",
      "filterable": true,
      "searchable": false
    },
    {
      "name": "processing_metadata",
      "type": "Edm.String",
      "searchable": false,
      "filterable": true
    }
  ],
  "vectorSearch": {
    "profiles": [
      {
        "name": "default",
        "algorithm": "hnsw",
        "parameters": {
          "m": 4,
          "efConstruction": 400,
          "efSearch": 500
        }
      }
    ]
  }
}
```

## 🔧 Service Architecture

### Service Communication Patterns

#### Synchronous Communication
- **REST APIs**: Service-to-service communication via HTTP
- **Health Checks**: `/healthz` endpoints for service monitoring
- **Direct Calls**: Orchestrator calling AuthZ and other services

#### Asynchronous Communication
- **Message Queues**: Work item processing via Redis queues
- **Event Streaming**: Change notifications and webhooks
- **Background Jobs**: Long-running tasks like file processing

### Service Dependencies

```
Admin UI → Orchestrator → AuthZ Service
    ↓           ↓           ↓
Teams Bot → Orchestrator → AI Pipeline
    ↓           ↓           ↓
Ingestion → Orchestrator → Cost Service
```

### Service Discovery
- **Local Development**: Docker Compose with service names
- **Production**: Kubernetes service discovery
- **Configuration**: Environment variables for service URLs

## 🗄️ Data Architecture

### Data Flow Architecture

#### Ingestion Pipeline
```
Source Systems → MCP Connectors → Ingestion Service → 
Pre-filter → AI Pipeline → Indexing → Storage
```

#### Query Pipeline
```
User Query → Teams Bot → Orchestrator → AuthZ → 
AI Search → Post-processing → Response
```

### Data Storage Strategy

#### Primary Storage
- **MongoDB**: Metadata, processing state, ACLs, policies
- **Azure AI Search**: Vector embeddings and searchable content
- **Azure Blob**: Large files, artifacts, backups

#### Caching Strategy
- **Redis**: Session data, principal caching, work queues
- **In-Memory**: Service-level caching for frequently accessed data
- **CDN**: Static assets and public content

### Data Models

#### File Metadata Model
```json
{
  "file_id": "string",
  "tenant_id": "string",
  "source": "box|sharepoint|onedrive",
  "path": "string",
  "size": "number",
  "mime_type": "string",
  "modified_at": "datetime",
  "created_at": "datetime",
  "author": "string",
  "hierarchical_metadata": {
    "core": {},
    "content": {},
    "semantic": {},
    "security": {},
    "processing": {},
    "contextual": {}
  },
  "allowed_principals": ["string"],
  "allowed_groups": ["string"],
  "sensitivity_flags": ["string"],
  "processing_state": "string",
  "ai_processed_at": "datetime"
}
```

#### Chunk Model
```json
{
  "chunk_id": "string",
  "file_id": "string",
  "tenant_id": "string",
  "content": "string",
  "embedding": [0.1, 0.2, ...],
  "metadata": {
    "chunk_type": "string",
    "position": "number",
    "length": "number",
    "semantic_context": "string",
    "entities": ["string"],
    "sensitivity_flags": ["string"]
  }
}
```

## 🔐 Security Architecture

### Authentication & Authorization

#### Identity Providers
- **Microsoft Entra ID**: Primary identity provider for Teams users
- **Box OAuth**: Box-specific authentication for file access
- **Service-to-Service**: Managed identities for Azure services

#### Token Management
- **Access Tokens**: Short-lived tokens for API access
- **Refresh Tokens**: Long-lived tokens for token renewal
- **Service Tokens**: Managed identity tokens for Azure services

### Data Security

#### Encryption
- **At Rest**: Azure Storage encryption with customer-managed keys
- **In Transit**: TLS 1.3 for all communications
- **Secrets**: Azure Key Vault for credential storage

#### Access Control
- **Role-Based Access Control (RBAC)**: Azure AD roles and permissions
- **Security Trimming**: Query-time access control based on user permissions
- **Tenant Isolation**: Complete data separation between tenants

### Compliance Features

#### Data Classification
- **Automated Detection**: AI-powered sensitive data identification
- **Policy Enforcement**: Configurable rules for data handling
- **Audit Logging**: Comprehensive access and decision logging

#### Regulatory Support
- **PII/PHI/PCI**: Built-in patterns for common sensitive data types
- **ITAR/EAR**: Export control compliance features
- **GDPR**: Data privacy and right-to-be-forgotten support

## 🔌 Integration Patterns

### MCP (Model Context Protocol) Integration

#### Box MCP Server
- **File System Access**: List, read, and metadata operations
- **Change Detection**: Webhook-based change notifications
- **Permission Management**: ACL reading and validation

#### Microsoft Files MCP Server
- **SharePoint Integration**: Site and document library access
- **OneDrive Integration**: Personal file access
- **Graph API Integration**: User and group management

### External Service Integration

#### Azure Services
- **OpenAI**: GPT models for summarization and chat
- **AI Search**: Vector search and semantic indexing
- **Key Vault**: Secrets and configuration management
- **Blob Storage**: File storage and backup

#### Third-Party Services
- **Box API**: File system and collaboration features
- **Microsoft Graph**: User management and permissions
- **Teams Bot Framework**: Conversational interface

## 📈 Performance & Scalability

### Performance Optimization

#### Caching Strategy
- **Multi-Level Caching**: Redis + in-memory + CDN
- **Cache Invalidation**: TTL-based and event-driven invalidation
- **Cache Warming**: Pre-loading frequently accessed data

#### Query Optimization
- **Index Optimization**: Strategic database and search indexes
- **Query Planning**: Intelligent query routing and optimization
- **Result Caching**: Caching of common query results

### Scalability Features

#### Horizontal Scaling
- **Auto-Scaling**: Kubernetes HPA based on metrics
- **Load Balancing**: Traffic distribution across service instances
- **Queue Management**: Work distribution via Redis queues

#### Resource Management
- **Connection Pooling**: Database and external service connections
- **Rate Limiting**: API rate limiting and throttling
- **Circuit Breakers**: Fault tolerance for external dependencies

## 🚀 Deployment Architecture

### Environment Strategy

#### Development Environment
- **Local Services**: Docker Compose for all services
- **Mock External Services**: LocalStack for Azure services
- **Development Tools**: Hot reloading and debugging support

#### Staging Environment
- **Azure Services**: Real Azure services for testing
- **Kubernetes**: AKS cluster for service orchestration
- **Monitoring**: Full observability and alerting

#### Production Environment
- **Multi-Region**: Geographic distribution for availability
- **High Availability**: Redundant services and data stores
- **Disaster Recovery**: Backup and recovery procedures

### Infrastructure as Code

#### Azure Bicep Templates
- **Resource Groups**: Logical grouping of related resources
- **Networking**: Virtual networks, subnets, and security groups
- **Compute**: AKS clusters and container instances
- **Storage**: Storage accounts and containers

#### Kubernetes Manifests
- **Deployments**: Service deployment configurations
- **Services**: Network service definitions
- **ConfigMaps**: Configuration management
- **Secrets**: Secure credential storage

### Monitoring & Observability

#### Metrics Collection
- **Application Metrics**: Business and technical metrics
- **Infrastructure Metrics**: Resource utilization and performance
- **Custom Metrics**: Domain-specific measurements

#### Logging Strategy
- **Structured Logging**: JSON-formatted log entries
- **Centralized Logging**: Azure Monitor and Log Analytics
- **Log Retention**: Configurable retention policies

#### Alerting & Notification
- **Threshold Alerts**: Performance and error rate alerts
- **Anomaly Detection**: ML-based anomaly identification
- **Escalation**: Automated and manual escalation procedures

---

**Next**: See [DEVELOPMENT.md](DEVELOPMENT.md) for implementation guidance and [DEPLOYMENT.md](DEPLOYMENT.md) for deployment procedures.
