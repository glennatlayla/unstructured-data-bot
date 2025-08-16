# Testing Guide

## Overview
This guide covers the comprehensive testing strategy and procedures for the Unstructured Data Indexing & AI-Query Application.

## Testing Strategy

### Testing Pyramid
- **Unit Tests**: Individual component testing (70%)
- **Integration Tests**: Service interaction testing (20%)
- **End-to-End Tests**: Full workflow testing (10%)

### Testing Environments
- **Local Development**: Docker Compose with test data
- **Azure Development**: VM-based testing environment
- **Production Staging**: AKS-based pre-production testing

## Unit Testing

### Python Services
```bash
# Run unit tests for specific service
docker-compose exec orchestrator python -m pytest
docker-compose exec authz python -m pytest
docker-compose exec ai-pipeline python -m pytest

# Run with coverage
docker-compose exec orchestrator python -m pytest --cov=app --cov-report=html

# Run specific test file
docker-compose exec orchestrator python -m pytest tests/test_routing.py
```

### Node.js Services
```bash
# Run unit tests for Teams Bot
docker-compose exec bot npm test

# Run unit tests for Admin UI
docker-compose exec admin-ui npm test

# Run with coverage
docker-compose exec admin-ui npm run test:coverage
```

### Test Structure
```
services/
├── orchestrator/
│   ├── tests/
│   │   ├── test_intelligent_router.py
│   │   ├── test_model_registry.py
│   │   └── test_routing_policies.py
│   └── app/
├── authz/
│   ├── tests/
│   │   ├── test_principal_resolution.py
│   │   └── test_security_filters.py
│   └── app/
└── ai-pipeline/
    ├── tests/
    │   ├── test_summarization.py
    │   └── test_embedding.py
    └── app/
```

## Integration Testing

### Service Communication Tests
```bash
# Test inter-service communication
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"question": "test query", "user_id": "test-user"}'

# Test AuthZ integration
curl -X GET "http://localhost:8083/resolve?upn=test@example.com"

# Test AI Pipeline integration
curl -X POST http://localhost:8085/summarize \
  -H "Content-Type: application/json" \
  -d '{"file_id": "test-file", "content": "test content"}'
```

### Database Integration Tests
```bash
# Test MongoDB connectivity
docker-compose exec orchestrator python -c "
from pymongo import MongoClient
client = MongoClient('mongodb://mongodb:27017/')
db = client.test_db
print('MongoDB connection successful')
"

# Test Redis connectivity
docker-compose exec orchestrator python -c "
import redis
r = redis.Redis(host='redis', port=6379, db=0)
r.ping()
print('Redis connection successful')
"
```

### MCP Connector Tests
```bash
# Test Box MCP Server
curl -s http://localhost:8086/healthz | jq '.status'

# Test Microsoft Files MCP Server
curl -s http://localhost:8087/healthz | jq '.status'

# Test MCP Python Interpreter
curl -X POST http://localhost:8088/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello World\")"}'
```

## End-to-End Testing

### Complete Workflow Tests
```bash
# Test complete ingestion pipeline
python3 -m ingestion.traverse --tenant test --source box --mode full --paths "/test"

# Test complete Q&A workflow
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What documents contain sensitive information?",
    "user_id": "test-user",
    "tenant_id": "test-tenant"
  }'
```

### User Journey Tests
```bash
# Test Teams Bot interaction
curl -X POST http://localhost:3978/api/messages \
  -H "Content-Type: application/json" \
  -d '{
    "type": "message",
    "text": "Hello, can you help me find documents?",
    "from": {"id": "test-user"},
    "conversation": {"id": "test-conversation"}
  }'

# Test Admin UI workflows
curl -s http://localhost:3000/api/policies | jq '.policies'
```

## Performance Testing

### Load Testing
```bash
# Test API performance with Apache Bench
ab -n 1000 -c 10 http://localhost:8080/healthz

# Test concurrent users
ab -n 1000 -c 50 -p test_query.json -T application/json \
  http://localhost:8080/query

# Test database performance
docker-compose exec orchestrator python -c "
import time
from pymongo import MongoClient
client = MongoClient('mongodb://mongodb:27017/')
db = client.test_db

start = time.time()
for i in range(1000):
    db.files.find_one({'tenant_id': 'test'})
end = time.time()
print(f'1000 queries in {end - start:.2f} seconds')
"
```

### Memory and Resource Testing
```bash
# Monitor container resource usage
docker stats --no-stream

# Check memory usage patterns
docker-compose exec orchestrator python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"

# Test memory leaks
for i in {1..100}; do
  curl -s http://localhost:8080/healthz > /dev/null
  sleep 1
done
docker stats --no-stream
```

## Security Testing

### Authentication Tests
```bash
# Test unauthenticated access (should fail)
curl -X GET http://localhost:8080/query

# Test invalid tokens
curl -X GET http://localhost:8080/query \
  -H "Authorization: Bearer invalid-token"

# Test expired tokens
curl -X GET http://localhost:8080/query \
  -H "Authorization: Bearer expired-token"
```

### Authorization Tests
```bash
# Test access to restricted resources
curl -X GET "http://localhost:8083/resolve?upn=unauthorized@example.com"

# Test security trimming
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me all documents",
    "user_id": "restricted-user"
  }'
```

### Data Privacy Tests
```bash
# Test PII detection
curl -X POST http://localhost:8085/classify \
  -H "Content-Type: application/json" \
  -d '{"content": "SSN: 123-45-6789"}'

# Test sensitive data masking
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the SSN in document X?",
    "user_id": "test-user"
  }'
```

## Test Data Management

### Test Data Setup
```bash
# Create test tenant
docker-compose exec mongodb mongo --eval "
db.tenants.insertOne({
  tenant_id: 'test-tenant',
  name: 'Test Organization',
  created_at: new Date()
})
"

# Create test user
docker-compose exec mongodb mongo --eval "
db.users.insertOne({
  user_id: 'test-user',
  tenant_id: 'test-tenant',
  upn: 'test@example.com',
  permissions: ['read', 'query']
})
"

# Create test documents
docker-compose exec mongodb mongo --eval "
db.files.insertOne({
  file_id: 'test-file-1',
  tenant_id: 'test-tenant',
  path: '/test/document1.pdf',
  content: 'This is a test document',
  allowed_principals: ['test-user']
})
"
```

### Test Data Cleanup
```bash
# Clean up test data
docker-compose exec mongodb mongo --eval "
db.tenants.deleteMany({tenant_id: 'test-tenant'})
db.users.deleteMany({tenant_id: 'test-tenant'})
db.files.deleteMany({tenant_id: 'test-tenant'})
db.qa_logs.deleteMany({tenant_id: 'test-tenant'})
"
```

## Automated Testing

### CI/CD Pipeline Tests
```bash
# Run all tests before deployment
./scripts/run_tests.sh

# Test specific components
./scripts/test_orchestrator.sh
./scripts/test_authz.sh
./scripts/test_ai_pipeline.sh
```

### Health Check Automation
```bash
# Automated health monitoring
while true; do
  for service in orchestrator authz ai-pipeline bot admin-ui; do
    status=$(curl -s http://localhost:$(docker-compose port $service 80 | cut -d: -f2)/healthz | jq -r '.status')
    if [ "$status" != "healthy" ]; then
      echo "$(date): $service is unhealthy - $status"
    fi
  done
  sleep 30
done
```

## Testing Best Practices

### Test Organization
- **Arrange**: Set up test data and environment
- **Act**: Execute the test scenario
- **Assert**: Verify expected outcomes
- **Cleanup**: Remove test data and restore state

### Test Naming
```python
def test_user_can_query_authorized_documents():
    """Test that users can only query documents they have access to"""
    # Arrange
    user_id = "test-user"
    document_id = "test-doc"
    
    # Act
    response = query_document(user_id, document_id)
    
    # Assert
    assert response.status_code == 200
    assert "content" in response.json()
    
    # Cleanup
    cleanup_test_data()
```

### Test Isolation
- Each test should be independent
- Use unique test data for each test
- Clean up after each test
- Avoid shared state between tests

## Troubleshooting Tests

### Common Test Failures
```bash
# Database connection issues
docker-compose exec mongodb mongo --eval "db.runCommand({ping: 1})"

# Service health issues
docker-compose logs --tail=50 orchestrator

# Network connectivity issues
docker-compose exec orchestrator ping mongodb
docker-compose exec orchestrator ping redis
```

### Debug Test Failures
```bash
# Run tests with verbose output
docker-compose exec orchestrator python -m pytest -v

# Run tests with debug logging
docker-compose exec orchestrator python -m pytest --log-cli-level=DEBUG

# Run specific failing test
docker-compose exec orchestrator python -m pytest tests/test_specific.py::test_function -v
```

## Next Steps
1. Set up automated test suites
2. Implement continuous testing in CI/CD
3. Add performance benchmarking
4. Create security testing automation
5. Establish test coverage requirements

---
*Last Updated: 2025-01-27*
*Version: 1.0*
