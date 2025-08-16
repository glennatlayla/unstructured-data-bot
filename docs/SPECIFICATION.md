# Software Specification (v3)

> **Complete specification for the Unstructured Data Indexing & AI-Query Application**

**Document Status**: Production Ready • **Date**: August 2024 • **Version**: 3.0

## 📋 Table of Contents

- [Executive Summary](#executive-summary)
- [Goals & Scope](#goals--scope)
- [Definitions & Acronyms](#definitions--acronyms)
- [System Architecture](#system-architecture)
- [Component Specifications](#component-specifications)
- [Security & Compliance](#security--compliance)
- [Data Flow & Processing](#data-flow--processing)
- [Performance & Scalability](#performance--scalability)
- [Deployment & Operations](#deployment--operations)

## 🎯 Executive Summary

This system indexes large, unstructured enterprise repositories (Box, SharePoint, OneDrive), applies metadata extraction and optional sensitive-data classification, and exposes natural-language Q&A via a Microsoft Teams bot and an Admin Web UI. It supports incremental scanning, durable progress tracking, rights-aware (security-trimmed) retrieval, cost visibility with forecast, and answer rendering including tables and charts.

### Key Capabilities
- **Multi-Provider Support**: Box, SharePoint, OneDrive via Model Context Protocol (MCP) servers
- **Intelligent Processing**: Incremental scanning, change detection, metadata extraction, AI summarization
- **Security-First Design**: Rights-aware querying, security trimming, tenant isolation, sensitive data classification
- **Enterprise Features**: Cost visibility with forecasting, audit trails, policy management, backup/restore
- **Modern Architecture**: Containerized microservices, MongoDB + Azure AI Search, Azure OpenAI integration

## 🎯 Goals & Scope

### Goals
- Connect to Box, SharePoint, and OneDrive at enterprise scale via Model Context Protocol (MCP) servers
- Traverse deep directory trees efficiently; resume and re-scan only when items change
- Create a master index (MongoDB) and a vector index (Azure AI Search) for retrieval-augmented generation (RAG)
- Provide end-user Q&A in Teams; provide admin controls (policies, cost tracking, directory selection, processing controls) in a Web UI
- Ensure strong security (least privilege, tenant isolation, secrets in Key Vault) and governance (audit, PII/PHI/ITAR controls)
- Enforce per-user rights at query time (security trimming) so users only discover and retrieve data they are authorized to access

### Out of Scope
- End-user document editing
- DLP beyond the defined policy enforcement
- Non-Microsoft chat surfaces other than Teams

## 📚 Definitions & Acronyms

- **MCP** — Model Context Protocol: standardized way for tools/servers to expose capabilities to models/clients
- **MCP Python Interpreter** — MCP tool for controlled execution of Python utilities
- **Box MCP Server** — MCP server providing Box file system tools
- **Microsoft files-mcp-server** — MCP server exposing SharePoint/OneDrive file system tools
- **RAG** — Retrieval Augmented Generation
- **PII/PHI/PCI/ITAR** — Sensitive data categories
- **Security trimming** — Restricting query scope and results based on the caller's effective permissions
- **OBO (On-Behalf-Of)** — OAuth flow where a service exchanges a user token for downstream resource access

## 🏗️ System Architecture

### Core Components

| Component | Technology | Purpose | Port |
|-----------|------------|---------|------|
| **Admin Web UI** | Next.js | Policy editor, dashboard, controls | 3000 |
| **Teams Bot Service** | Python/Node | Conversational interface, OAuth | 3978 |
| **RAG Orchestrator** | Python | Query processing, security filtering | 8080 |
| **Ingestion & Monitor** | Python | Data ingestion, change detection | 8081 |
| **Authorization (AuthZ)** | Python | Principal resolution, security | 8083 |
| **AI Pipeline** | Python | Summarization, embeddings | 8085 |
| **Cost Service** | Python | Cost tracking, forecasting | 8082 |
| **MCP Connectors** | Python | External integrations | 8086-7 |

### Data Stores
- **Master Database**: MongoDB (file catalog, processing state, ACLs, policies, costs)
- **Vector Index**: Azure AI Search (embeddings, metadata, security principals)
- **Object Store**: Azure Blob (artifacts, charts, exports, backups)
- **Secrets**: Azure Key Vault (credentials, configuration)
- **Cache**: Redis (session data, principal caching)

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Orchestration**: Kubernetes (AKS for production)
- **Monitoring**: Azure Monitor, Application Insights
- **CI/CD**: GitHub Actions, Azure DevOps

## 🔧 Component Specifications

### 5.1 Ingestion & Monitor Service

**Responsibilities**: Discovery, change detection, enqueueing, orchestration of file pipeline, poisoning/redo handling, metrics, ACL capture.

#### Directory Traversal Controller
Directory traversal operates in three modes:
- **CLI**: `python -m ingestion.traverse --tenant TENANT --source {box\|sharepoint\|onedrive} --mode {full\|incremental} [--paths "/Finance,/HR"]`
- **Scheduler**: CronJob (AKS) for periodic incremental scans (default hourly, tenant-configurable)
- **Event-driven**: Webhook/MCP event ingester maps provider change notifications to targeted re-scan queue items

#### Change Detection & ACLs
- A file is re-processed only if any of: modified_time, provider version/ETag, content hash, or ACL hash has changed
- During ingestion, the service captures provider ACLs for each item:
  - **Box**: collaborators (users/groups), roles (viewer, editor, etc.), shared link scope
  - **SharePoint/OneDrive**: inheritance, unique permissions, sharing links, role assignments
- The ACL snapshot is normalized and hashed; stored with each file record and propagated to the index

#### Throughput & Backpressure
- Work queues sized per tenant
- HPA scales workers by queue depth/latency
- Max parallelism per provider to respect API limits

### 5.2 Pre-filter & Metadata Extraction

- Normalizes provider metadata (file_id, path, size, mime, author, modified_time, permissions)
- Extracts text (Office/PDF) with progress recording
- Files are not re-scanned unless metadata values change
- Emits a canonical document for downstream summarization and embedding

### 5.3 Sensitive Data Classification & Policies

#### Admin-Configurable "Sensitive Data" Definition
Admin UI provides a policy editor to define what "sensitive data" means per tenant:
- **Categories**: PII, PCI, PHI, ITAR/EAR, Trade Secrets, Legal Privilege, HR
- **Detectors**: Enable/disable built-in regex/patterns or NLP classifiers; define custom regexes
- **Examples/Exclusions**: Provide examples and explicit exclusions
- **Enforcement**: Choose behaviors on retrieval/answer: mask, block, alert, or allow with banner

#### Optional Directory Selection
- Admins see a browsable directory tree via MCP providers
- Can select folders to prioritize classification/summarization
- Restrict Q&A scope or trigger ad-hoc re-processing

### 5.4 Summarization & Embeddings

- **Summaries**: Azure OpenAI (GPT-4-class) produces compact JSON summary with fields: title, purpose, entities, dates, table of contents, and key facts
- **Embeddings**: Azure OpenAI text-embedding model with chunking by semantic boundaries (target 1–2k tokens)
- **Index Update**: Upsert to Azure AI Search (vector + keyword) with file_id, tenant_id, path, sensitivity flags, allowed_principals/groups, and summary facets

### 5.5 Authorization (Security Trimming) & RAG Orchestration

#### Identity & Token Flow
- **Teams auth**: Bot authenticates the user with Entra ID
- **On-Behalf-Of**: Orchestrator exchanges Teams token for Microsoft Graph and SharePoint/OneDrive access
- **Box consent**: Users sign into Box via OAuth; tokens stored encrypted and rotated
- **Identity mapping**: Maintains mapping from Teams UPN → Entra object ID/Group IDs → provider identities

#### Security Filter Construction
- At query time, AuthZ Service resolves caller's effective principals:
  - Direct user ID for each provider
  - Group memberships
  - Special scopes from sharing links (if allowed by policy)
- Orchestrator queries Azure AI Search with security filter: return only documents where caller's principals intersect allowed_principals/allowed_groups
- Final gate: Per-item allow/deny check via AuthZ using latest provider tokens

#### Retrieval, Prompting & Rendering
- Retrieval uses security-filtered vector + keyword search
- Prompt construction includes only accessible content
- Answer rendering only includes rows from permitted items
- If question targets restricted areas: "Some requested data is restricted for your account"

#### Caching & Performance
- Per-user principal cache with short TTL (5–15 minutes)
- Index filters push down most trimming to Azure AI Search
- Final gate limited to top-k results

#### Model Registry & Intelligent Routing

**Model Registry**: Centralized catalog of available Azure OpenAI deployments with metadata:
- Endpoint, deployment name, API version
- Capabilities (vision, tools, function calling, context length)
- Performance characteristics (latency, quality, cost per token)
- Tags (model family, purpose, availability)
- Health status and rate limits

**Routing Policies**: Tenant and feature-specific model selection rules:
- Quality-focused: qa → gpt-4o, summarize → gpt-4o-mini
- Cost-optimized: embed → text-embedding-3-large, chat → gpt-35-turbo
- Capability-based: vision tasks → gpt-4o, tool use → gpt-4o
- Latency-sensitive: real-time chat → gpt-35-turbo, batch processing → gpt-4o

**Intelligent Router**: Runtime model selection based on:
- Task requirements (vision, tools, function calling)
- Quality vs. latency budget constraints
- Feature flags and A/B testing configurations
- Current model availability and health status
- Cost optimization and budget enforcement

**Usage Tracking & Budget Management**:
- Per-model usage logging with tenant, feature, and cost attribution
- Automatic downshift to cheaper models when budget caps are reached
- Real-time cost monitoring and alerting
- Performance analytics and model comparison metrics

### 5.6 Cost Metering & Forecast Service

- Meters tokens/ops/runtime per tenant and operation
- Aggregates usage data and provides forecasting
- Exposed to Admin UI for cost visibility and budget management
- Supports cost optimization and alerting

### 5.7 Admin Web UI

**Core Features**:
- Policy editor for sensitive data classification
- Directory picker for source selection
- Run controls for ingestion and processing
- Spend dashboard with cost analytics
- Answer audit and security logs
- Connection manager for provider consents

**User Experience**:
- Intuitive policy configuration
- Real-time cost monitoring
- Comprehensive audit trails
- Easy provider management

## 🔐 Security & Compliance

### Multi-Tenant Isolation
- Single control plane with per-tenant credentials and policy records
- Data partitioning at DB/Index level via tenant_id
- Storage isolation via per-tenant containers
- Security trimming always evaluated per-tenant and per-user

### Access Control
- **Least Privilege**: Users only access data they're authorized for
- **Security Trimming**: Query results filtered by effective permissions
- **Principal Resolution**: Comprehensive identity mapping across providers
- **Token Management**: Secure storage and rotation of OAuth tokens

### Data Protection
- **Encryption**: Data encrypted at rest and in transit
- **Secrets Management**: Credentials stored in Azure Key Vault
- **Audit Logging**: Comprehensive security decision trails
- **Compliance**: Support for PII/PHI/PCI/ITAR requirements

## 🔄 Data Flow & Processing

### High-Level Flow
1. **Admin connects sources** (Box/SharePoint/OneDrive)
2. **Ingestion traverse** discovers files and emits work items
3. **Pre-filter extracts** text/metadata and captures provider ACLs
4. **Summarizer creates** structured summary JSON; Embedder produces embeddings
5. **Index update** in MongoDB + AI Search including allowed principals
6. **User queries** in Teams → Bot obtains identity and provider tokens (OBO) → AuthZ resolves principals → Orchestrator queries with security filter → Post-process with tables/graphs
7. **Costs metered** and forecasted; policies enforced

### Processing Pipeline
```
Source Connection → Discovery → Change Detection → ACL Capture → Text Extraction → 
AI Processing → Indexing → Security Filtering → Query Processing → Response Generation
```

## 📈 Performance & Scalability

### Throughput Optimization
- **Parallel Processing**: Multi-worker ingestion with configurable parallelism
- **Incremental Updates**: Only process changed files
- **Caching**: Principal and metadata caching with configurable TTL
- **Queue Management**: Work queues sized per tenant with backpressure handling

### Scalability Features
- **Horizontal Scaling**: Auto-scaling based on queue depth and latency
- **Resource Management**: Respects provider API limits and rate limits
- **Load Distribution**: Work distributed across multiple workers
- **Performance Monitoring**: Real-time metrics and alerting

## 🚀 Deployment & Operations

### Environment Requirements
- **Python**: 3.9+ for all Python services
- **Node.js**: 18+ for Teams bot and Admin UI
- **Docker**: 20.10+ with Docker Compose
- **Azure Services**: OpenAI, AI Search, Key Vault, Blob Storage
- **Infrastructure**: Kubernetes (AKS) for production, Docker Compose for development

### Deployment Models
- **Development**: Docker Compose with local services
- **Staging**: Kubernetes with Azure services
- **Production**: Full Azure deployment with monitoring and scaling

### Monitoring & Observability
- **Health Checks**: `/healthz` endpoints on all services
- **Metrics**: Performance and business metrics
- **Logging**: Structured logging with correlation IDs
- **Alerting**: Automated alerting for critical issues

### Backup & Recovery
- **Data Backup**: Regular MongoDB and Azure Search backups
- **Configuration Backup**: Version-controlled configuration files
- **Disaster Recovery**: Multi-region deployment options
- **Rollback Capabilities**: Automated rollback to previous versions

---

**Next**: See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture decisions and [DEVELOPMENT.md](DEVELOPMENT.md) for implementation guidance.
