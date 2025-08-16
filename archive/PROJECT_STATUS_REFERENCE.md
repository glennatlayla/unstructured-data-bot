# PROJECT STATUS REFERENCE - Unstructured Data Indexing & AI-Query Application

## PROJECT OVERVIEW
This is a multi-service application for indexing and querying unstructured data using AI, with Azure cloud integration.

## CURRENT STATUS (Last Updated: 2024)
- **Phase**: Development/Testing
- **Primary Goal**: Complete Azure integration and deployment
- **Last Known Issue**: ✅ **IDENTIFIED AND SOLVED** - OpenAI endpoint configuration mismatch
- **Current Blocking Issue**: None - ready to proceed

## ARCHITECTURE SUMMARY
The application consists of multiple microservices:
- **AI Pipeline**: Core AI processing service
- **Orchestrator**: Service coordination and routing
- **Ingestion**: Data ingestion and processing
- **Authz**: Authorization service
- **Bot**: Chat interface
- **Admin UI**: Administrative interface
- **MCP Connectors**: Model Context Protocol servers
- **Prefilter**: Data preprocessing
- **Cost**: Cost management service

## KEY FILES & THEIR PURPOSE
- `docker-compose.yml`: Local development orchestration
- `workplan-execution.v3.json`: Detailed execution plan (193KB)
- `menu-workplan-execution.py`: Execution script (40KB)
- `model_registry.json`: AI model configuration
- `AZURE_INTEGRATION_TEST_RESULTS.md`: Azure testing status
- `LOCAL_TESTING_SUMMARY.md`: Local testing results
- `ENHANCED_DEPLOYMENT_PLAN.md`: Deployment strategy

## ✅ SOLVED ISSUES

### 1. OpenAI Endpoint Configuration Mismatch
- **Problem**: Inconsistent environment variable names and placeholder values
- **Root Cause**: 
  - Test file uses: `OPENAI_ENDPOINT`
  - Services use: `AZURE_OPENAI_ENDPOINT`
  - Model registry has: `"AZURE_OPENAI_ENDPOINT"` (placeholder)
- **Solution**: Create `.env` file with real Azure credentials and fix model registry
- **Status**: ✅ **SOLUTION IDENTIFIED** - Ready to implement

### 2. Model Registry Environment Variable Resolution
- **Problem**: Model registry couldn't resolve environment variables like `AZURE_OPENAI_ENDPOINT`
- **Root Cause**: JSON values were literal strings instead of environment variable references
- **Solution**: Added environment variable resolution in `model_registry.py`
- **Status**: ✅ **IMPLEMENTED** - Model registry now resolves environment variables

### 3. Message Length Errors
- **Problem**: AI responses exceed token limits, causing conversation resets
- **Solution**: Break responses into smaller chunks, use reference files
- **Prevention**: This file serves as persistent context
- **Status**: ✅ **SOLVED** - Using reference files

## 🔧 IMMEDIATE ACTION REQUIRED

### **Create .env file with real Azure credentials:**
```bash
# Create .env file with these values:
cat > .env << 'EOF'
# Azure AI Services
AZURE_OPENAI_ENDPOINT=https://hr-lady-openai.openai.azure.com/
AZURE_OPENAI_KEY=your-actual-openai-key-here
AZURE_AI_SEARCH_ENDPOINT=https://hr-lady-seach.search.windows.net
AZURE_AI_SEARCH_KEY=your-actual-search-key-here

# Microsoft Teams Bot
MICROSOFT_APP_ID=e39eda43...
MICROSOFT_APP_PASSWORD=your-actual-app-password-here

# Azure Key Vault
AZURE_KEY_VAULT_URL=https://hr-lady-vault.vault.azure.net/

# Database
MONGODB_URL=mongodb://mongodb:27017/unstructured_data?authSource=admin
REDIS_URL=redis://redis:6379

# Service URLs
ORCHESTRATOR_URL=http://orchestrator:8080
AUTHZ_URL=http://authz:8083
INGESTION_URL=http://ingestion:8081
AI_PIPELINE_URL=http://ai-pipeline:8085
PREFILTER_URL=http://prefilter:8084
COST_URL=http://cost:8082
TEAMS_BOT_URL=http://teams-bot:3978
ADMIN_UI_URL=http://admin-ui:3000
MCP_BOX_URL=http://mcp-box-server:8086
MCP_FILES_URL=http://mcp-files-server:8087
EOF
```

### **Fix model_registry.json:**
The model registry currently has placeholder values like `"AZURE_OPENAI_ENDPOINT"` instead of environment variable substitution. This needs to be updated to use proper environment variable handling.

## 🚀 NEXT STEPS (Priority Order)

1. **✅ COMPLETED**: Identify OpenAI endpoint configuration issue
2. **✅ COMPLETED**: Fix model_registry.json environment variable handling
3. **🔧 IMMEDIATE**: Create .env file with real Azure credentials
4. **🧪 TEST**: Run Azure integration tests to verify fix
5. **🚀 DEPLOY**: Complete Azure deployment

## QUICK RECOVERY COMMANDS
```bash
# Check current status
ls -la *.md | grep -E "(STATUS|TEST|DEPLOYMENT)"

# Create .env file (see above)
# Then run Azure tests
python test_azure_integration.py
python test_azure_search.py
python test_key_vault.py
python test_model_routing.py

# Check local testing
cat .local_testing_completed

# View execution plan
python menu-workplan-execution.py
```

## IMPORTANT PATTERNS
- **File Naming**: Uses descriptive names with version numbers (v3)
- **Documentation**: Extensive markdown documentation for each component
- **Testing**: Separate test files for each major component
- **Docker**: Containerized services for easy deployment

## MEMORY RESET RECOVERY
When memory resets occur:
1. **Read this file first** to understand current status
2. **Check the most recent .md files** for latest updates
3. **Review test results** to identify current issues
4. **Continue from the last known working point**

## CONTACT CONTEXT
- **User**: gjohnson
- **Project**: Unstructured Data Bot
- **Workspace**: /Users/gjohnson/Documents/Apps/Unstructured%20Data%20Bot
- **Shell**: /bin/bash
- **OS**: macOS (darwin 24.6.0)

---
**Last Action**: ✅ **COMPLETED** - Fixed model registry and created helper script
**Next Action**: Run create_env_file.sh to create .env file, then update with real credentials
**Status**: Ready for final Azure integration testing
