# Ingestion Service

The Ingestion Service is responsible for scanning and indexing files from various cloud storage providers (Box, SharePoint, OneDrive) using MCP (Model Context Protocol) integration.

## Features

- **Multi-source Support**: Box, SharePoint, OneDrive integration
- **Change Detection**: Intelligent detection of file modifications, additions, and deletions
- **ACL Capture**: Comprehensive permission and access control list management
- **MCP Integration**: Model Context Protocol client for standardized cloud storage access
- **Background Processing**: Asynchronous file processing with background tasks
- **Health Monitoring**: Comprehensive health checks and status monitoring

## Architecture

### Core Components

1. **DirectoryTraverser** (`traverse.py`)
   - Handles directory traversal and file discovery
   - Supports full and incremental scanning modes
   - Processes file metadata and content hashes

2. **ChangeDetector** (`change_detection.py`)
   - Detects file changes between scans
   - Tracks modification history
   - Provides change analytics and summaries

3. **ACLCapture** (`acl_capture.py`)
   - Captures and processes access control lists
   - Supports Box and Microsoft 365 permission formats
   - Analyzes permission patterns for security insights

4. **MCPClient** (`mcp_client.py`)
   - Manages connections to MCP servers
   - Provides unified interface for different cloud providers
   - Handles authentication and API calls

## API Endpoints

### Health & Status
- `GET /healthz` - Basic health check
- `GET /health/detailed` - Comprehensive health check including MCP servers
- `GET /mcp/status` - Status of all MCP servers

### Ingestion Management
- `POST /start` - Start ingestion process
- `POST /stop` - Stop ongoing ingestion
- `POST /rescan` - Rescan specific paths
- `GET /status` - Get ingestion status

### Monitoring & Analytics
- `GET /permissions/{tenant_id}/{source}` - Permission summary
- `GET /analytics/changes/{tenant_id}` - Change analytics
- `POST /cleanup/old-records` - Clean up old records

### MCP Testing
- `POST /mcp/test/{source}` - Test MCP connection

## Configuration

### Environment Variables
- `MONGODB_URL` - MongoDB connection string
- `REDIS_URL` - Redis connection string

### MCP Server URLs
- Box: `http://mcp-box-server:8086`
- SharePoint/OneDrive: `http://mcp-files-server:8087`

## Usage Examples

### Start Ingestion
```bash
curl -X POST "http://localhost:8081/start" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant1",
    "source": "box",
    "mode": "incremental"
  }'
```

### Check Health
```bash
curl "http://localhost:8081/health/detailed"
```

### Get Change Analytics
```bash
curl "http://localhost:8081/analytics/changes/tenant1?days=30"
```

## Development

### Running Tests
```bash
cd services/ingestion
python -m pytest tests/
```

### Local Development
```bash
cd services/ingestion
uvicorn app.main:app --reload --host 0.0.0.0 --port 8081
```

## Dependencies

- FastAPI - Web framework
- Uvicorn - ASGI server
- PyMongo - MongoDB driver
- Redis - Redis client
- HTTPX - HTTP client for MCP communication
- Pydantic - Data validation

## Docker

```bash
# Build image
docker build -t ingestion-service ./docker/ingestion

# Run container
docker run -p 8081:8081 ingestion-service
```

## Integration

The service integrates with:
- **MongoDB**: File metadata and change history storage
- **Redis**: Caching and job queue management
- **MCP Servers**: Cloud storage provider APIs
- **Orchestrator Service**: Main application coordination
