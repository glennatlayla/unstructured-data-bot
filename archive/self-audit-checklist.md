# Self-Audit & Validation Checklist

## Environment
- [ ] Docker Engine running; `docker compose version` works
- [ ] Git configured; SSH key to GitHub loaded
- [ ] Node 18+ / npm; Python 3.11+
- [ ] Azure CLI installed and logged in
- [ ] SSH key pair generated for Azure VM access
- [ ] Domain name registered and DNS zone configured

## Bring-up
- [ ] `docker compose up --build -d` completes
- [ ] /healthz endpoints for orchestrator (8080), ingestion (8081), bot (3978), admin-ui (3000), cost (8082), authz (8083), enhanced-ai-pipeline (8085)
- [ ] MongoDB connectivity (27017)
- [ ] Redis connectivity (6379)
- [ ] Azurite blob storage (10000)

## Workplan Run
- [ ] `python menu-workplan-execution.py --next` runs Step 1 and commits
- [ ] `--generate-curl` creates curltest/run_all.sh
- [ ] All subsequent steps pass and commit

## Core Services Validation
- [ ] **AuthZ Service** - Principal resolution and security filtering
- [ ] **RAG Orchestrator** - Query processing with security trimming
- [ ] **Ingestion Service** - MCP integration and change detection
- [ ] **Teams Bot** - OAuth integration and conversational interface
- [ ] **Admin UI** - Policy management and cost visibility
- [ ] **Cost Service** - Usage tracking and forecasting

## Enhanced AI Pipeline Validation
- [ ] **Enhanced AI Pipeline** - Hierarchical metadata processing and intelligent chunking
- [ ] **Azure OpenAI Integration** - Endpoint connectivity and API access
- [ ] **Enhanced Document Summarization** - AI-powered content summarization with hierarchical structure
- [ ] **Intelligent Embedding Generation** - Vector embeddings with semantic context
- [ ] **Advanced Sensitive Data Classification** - PII/PHI/PCI/ITAR detection with confidence scoring
- [ ] **Intelligent Chunking** - Adaptive chunking based on document structure and content type
- [ ] **Hierarchical Metadata Processing** - Multi-level metadata structure with contextual information
- [ ] **Multi-Level Caching** - Metadata, embedding, and query caching with TTL management

## Enhanced RAG Metadata Design Validation
- [ ] **Hierarchical Metadata Structure** - Core, content, semantic, security, processing, and contextual metadata
- [ ] **Intelligent Chunking Strategy** - Semantic boundaries, document structure awareness, and adaptive chunking
- [ ] **Multi-Modal Metadata Support** - Text, images, tables, and document structure metadata
- [ ] **Contextual Metadata** - Temporal, spatial, organizational, and relational context
- [ ] **Enhanced Indexing Strategy** - Composite indexes for common query patterns
- [ ] **Advanced Caching Strategy** - Multi-level caching with LRU eviction and TTL
- [ ] **Hybrid Retrieval** - Vector search, keyword search, semantic search, and reranking
- [ ] **Contextual Retrieval** - User context, query context, and document context

## MCP Server Integration
- [ ] **Box MCP Server** - OAuth authentication and file operations
- [ ] **Microsoft files MCP Server** - SharePoint/OneDrive integration
- [ ] **Python MCP Interpreter** - Controlled execution environment

## Security Testing
- [ ] **Security Trimming** - Test users (bob@acme.com, alice@acme.com, eve@acme.com)
- [ ] **Principal Resolution** - User and group access validation
- [ ] **Access Control** - Final gate validation for document access
- [ ] **OAuth Flows** - Teams SSO and Box authentication
- [ ] **Enhanced Security Metadata** - Sensitivity flags, classification confidence, and access levels

## Data Processing Validation
- [ ] **File Ingestion** - Incremental scanning and change detection
- [ ] **ACL Capture** - Permission and collaboration data
- [ ] **Document Versioning** - Version tracking across providers
- [ ] **Enhanced Metadata Extraction** - File type detection, content extraction, and hierarchical processing
- [ ] **Intelligent Chunking** - Document structure-aware chunking with semantic boundaries
- [ ] **Hierarchical Metadata Processing** - Multi-level metadata structure with contextual information

## Enhanced Database Schema Validation
- [ ] **MongoDB Enhanced Schema** - Hierarchical metadata structure with nested objects
- [ ] **Chunks Collection** - Enhanced chunk metadata with semantic context and positioning
- [ ] **Processing State** - Enhanced processing state with version tracking
- [ ] **Indexes** - Composite indexes for common query patterns and performance optimization
- [ ] **Data Consistency** - Transaction-based operations and rollback capability

## Azure Integration
- [ ] **Azure AI Search Enhanced** - Vector and keyword hybrid retrieval with hierarchical metadata
- [ ] **Key Vault** - Secrets management and access
- [ ] **Blob Storage** - Backup and artifact storage
- [ ] **Teams Bot Registration** - App registration and channel configuration
- [ ] **Enhanced Search Index** - Multi-vector support and contextual metadata

## Performance Optimization Validation
- [ ] **Multi-Level Caching** - Metadata cache (15 min TTL), embedding cache (1 hour TTL), query cache (5 min TTL)
- [ ] **Indexing Strategy** - Composite indexes for tenant_id, source, modified_at, sensitivity_flags, allowed_principals
- [ ] **Chunking Optimization** - Adaptive chunking based on document structure and content type
- [ ] **Query Optimization** - Hybrid retrieval with vector, keyword, semantic search, and reranking
- [ ] **Response Time** - P95 time-to-first-token < 3s, p95 total answer < 10s

## Advanced RAG Features Validation
- [ ] **Hybrid Retrieval** - Vector search, keyword search, semantic search, and reranking
- [ ] **Contextual Retrieval** - User context, query context, and document context
- [ ] **Query Expansion** - Synonym matching, query expansion, and intent recognition
- [ ] **Intelligent Chunking** - Semantic boundaries, document structure awareness
- [ ] **Hierarchical Metadata** - Multi-level metadata structure with contextual information

## Production Readiness
- [ ] **Backup/Restore** - Data backup and recovery procedures with enhanced metadata
- [ ] **Cost Metering** - Usage tracking and budget controls
- [ ] **Monitoring** - Application insights and logging with enhanced metrics
- [ ] **SSL Certificates** - HTTPS configuration for all endpoints
- [ ] **Schema Migration** - Backward compatibility and gradual migration strategy
- [ ] **Performance Monitoring** - Enhanced performance metrics and alerting

## Integration Testing
- [ ] **End-to-End Workflows** - Complete user journeys with enhanced RAG capabilities
- [ ] **Error Handling** - Graceful failure and recovery with enhanced error tracking
- [ ] **Performance** - Response times and throughput with enhanced caching
- [ ] **Scalability** - Load testing and resource utilization with enhanced indexing
- [ ] **Enhanced RAG Testing** - Hierarchical metadata, intelligent chunking, and contextual retrieval

## Enhanced Testing Scenarios
- [ ] **Hierarchical Metadata Processing** - Test multi-level metadata structure
- [ ] **Intelligent Chunking** - Test adaptive chunking for different document types
- [ ] **Enhanced Summarization** - Test hierarchical summary generation
- [ ] **Advanced Classification** - Test sensitive data classification with confidence scoring
- [ ] **Multi-Level Caching** - Test caching strategies and TTL management
- [ ] **Hybrid Retrieval** - Test vector, keyword, and semantic search combinations
- [ ] **Contextual Retrieval** - Test user and document context integration
- [ ] **Performance Optimization** - Test indexing strategies and query optimization

## Exit Criteria
- [ ] All steps completed successfully
- [ ] curl harness green (all HTTP tests pass)
- [ ] Meaningful commit per step
- [ ] All services healthy and responsive
- [ ] Security features validated
- [ ] Enhanced AI pipeline functional with hierarchical metadata
- [ ] Intelligent chunking operational
- [ ] Multi-level caching implemented
- [ ] Hybrid retrieval working
- [ ] Teams bot operational
- [ ] Admin UI accessible
- [ ] Azure resources provisioned
- [ ] Production deployment ready
- [ ] Enhanced RAG metadata design validated
- [ ] Performance targets met
- [ ] Schema migration completed
- [ ] Backward compatibility maintained
