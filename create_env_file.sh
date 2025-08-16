#!/bin/bash

# Script to create .env file with Azure configuration
# This script will create a .env file with placeholder values that you need to fill in

echo "🔧 Creating .env file for Azure configuration..."
echo ""

# Check if .env already exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Backing up to .env.backup"
    cp .env .env.backup
fi

# Create .env file with Azure configuration
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

echo "✅ .env file created successfully!"
echo ""
echo "🔑 IMPORTANT: You need to update the following values with your real Azure credentials:"
echo "   - AZURE_OPENAI_KEY: Your actual Azure OpenAI API key"
echo "   - AZURE_AI_SEARCH_KEY: Your actual Azure AI Search API key"
echo "   - MICROSOFT_APP_PASSWORD: Your actual Microsoft Teams Bot app password"
echo ""
echo "📝 Edit the .env file and replace the placeholder values, then run:"
echo "   python test_azure_integration.py"
echo ""
echo "🚀 After updating the credentials, your Azure integration should work!"
