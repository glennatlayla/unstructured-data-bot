#!/usr/bin/env bash
set -euo pipefail
echo '== curl test run =='
echo 'Test: MongoDB health check'
code=$(curl -s -o /tmp/resp.json -w '%{http_code}' 'http://localhost:27017')
if [ '$code' != '200' ]; then echo 'FAIL http://localhost:27017 -> '$code; exit 1; fi
echo 'Test: Azurite blob service'
code=$(curl -s -o /tmp/resp.json -w '%{http_code}' 'http://localhost:10000')
if [ '$code' != '400' ]; then echo 'FAIL http://localhost:10000 -> '$code; exit 1; fi
echo 'Test: AuthZ health endpoint'
code=$(curl -s -o /tmp/resp.json -w '%{http_code}' 'http://localhost:8083/healthz')
if [ '$code' != '200' ]; then echo 'FAIL http://localhost:8083/healthz -> '$code; exit 1; fi
if command -v jq >/dev/null 2>&1; then
  jq -e 'has("status") and .["status"]=="ok"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field status'; exit 1)
  jq -e 'has("service") and .["service"]=="authz"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field service'; exit 1)
else
  grep -q '"status": "ok"' /tmp/resp.json || (echo 'FAIL JSON field status'; exit 1)
  grep -q '"service": "authz"' /tmp/resp.json || (echo 'FAIL JSON field service'; exit 1)
fi
echo 'Test: Orchestrator health endpoint'
code=$(curl -s -o /tmp/resp.json -w '%{http_code}' 'http://localhost:8080/healthz')
if [ '$code' != '200' ]; then echo 'FAIL http://localhost:8080/healthz -> '$code; exit 1; fi
if command -v jq >/dev/null 2>&1; then
  jq -e 'has("status") and .["status"]=="ok"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field status'; exit 1)
  jq -e 'has("service") and .["service"]=="orchestrator"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field service'; exit 1)
else
  grep -q '"status": "ok"' /tmp/resp.json || (echo 'FAIL JSON field status'; exit 1)
  grep -q '"service": "orchestrator"' /tmp/resp.json || (echo 'FAIL JSON field service'; exit 1)
fi
echo 'Test: Box MCP server health'
code=$(curl -s -o /tmp/resp.json -w '%{http_code}' 'http://localhost:8086/healthz')
if [ '$code' != '200' ]; then echo 'FAIL http://localhost:8086/healthz -> '$code; exit 1; fi
echo 'Test: Microsoft files MCP server health'
code=$(curl -s -o /tmp/resp.json -w '%{http_code}' 'http://localhost:8087/healthz')
if [ '$code' != '200' ]; then echo 'FAIL http://localhost:8087/healthz -> '$code; exit 1; fi
echo 'Test: Enhanced AI pipeline health endpoint'
code=$(curl -s -o /tmp/resp.json -w '%{http_code}' 'http://localhost:8085/healthz')
if [ '$code' != '200' ]; then echo 'FAIL http://localhost:8085/healthz -> '$code; exit 1; fi
if command -v jq >/dev/null 2>&1; then
  jq -e 'has("status") and .["status"]=="ok"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field status'; exit 1)
  jq -e 'has("service") and .["service"]=="enhanced-ai-pipeline"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field service'; exit 1)
  jq -e 'has("version") and .["version"]=="2.0.0"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field version'; exit 1)
else
  grep -q '"status": "ok"' /tmp/resp.json || (echo 'FAIL JSON field status'; exit 1)
  grep -q '"service": "enhanced-ai-pipeline"' /tmp/resp.json || (echo 'FAIL JSON field service'; exit 1)
  grep -q '"version": "2.0.0"' /tmp/resp.json || (echo 'FAIL JSON field version'; exit 1)
fi
echo 'Test: Test enhanced processing endpoint'
code=$(curl -s -o /tmp/resp.json -w '%{http_code}' 'http://localhost:8085/process_enhanced')
if [ '$code' != '200' ]; then echo 'FAIL http://localhost:8085/process_enhanced -> '$code; exit 1; fi
echo 'Test: Bot health endpoint'
code=$(curl -s -o /tmp/resp.json -w '%{http_code}' 'http://localhost:3978/healthz')
if [ '$code' != '200' ]; then echo 'FAIL http://localhost:3978/healthz -> '$code; exit 1; fi
if command -v jq >/dev/null 2>&1; then
  jq -e 'has("status") and .["status"]=="ok"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field status'; exit 1)
  jq -e 'has("service") and .["service"]=="teams-bot"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field service'; exit 1)
else
  grep -q '"status": "ok"' /tmp/resp.json || (echo 'FAIL JSON field status'; exit 1)
  grep -q '"service": "teams-bot"' /tmp/resp.json || (echo 'FAIL JSON field service'; exit 1)
fi
echo 'Test: Bot Framework endpoint accessible'
code=$(curl -s -o /tmp/resp.json -w '%{http_code}' 'http://localhost:3978/api/messages')
if [ '$code' != '401' ]; then echo 'FAIL http://localhost:3978/api/messages -> '$code; exit 1; fi
echo 'Test: Orchestrator service health'
code=$(curl -s -o /tmp/resp.json -w '%{http_code}' 'http://localhost:8080/healthz')
if [ '$code' != '200' ]; then echo 'FAIL http://localhost:8080/healthz -> '$code; exit 1; fi
if command -v jq >/dev/null 2>&1; then
  jq -e 'has("status") and .["status"]=="ok"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field status'; exit 1)
  jq -e 'has("service") and .["service"]=="orchestrator"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field service'; exit 1)
else
  grep -q '"status": "ok"' /tmp/resp.json || (echo 'FAIL JSON field status'; exit 1)
  grep -q '"service": "orchestrator"' /tmp/resp.json || (echo 'FAIL JSON field service'; exit 1)
fi
echo 'Test: AuthZ service health'
code=$(curl -s -o /tmp/resp.json -w '%{http_code}' 'http://localhost:8083/healthz')
if [ '$code' != '200' ]; then echo 'FAIL http://localhost:8083/healthz -> '$code; exit 1; fi
if command -v jq >/dev/null 2>&1; then
  jq -e 'has("status") and .["status"]=="ok"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field status'; exit 1)
  jq -e 'has("service") and .["service"]=="authz"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field service'; exit 1)
else
  grep -q '"status": "ok"' /tmp/resp.json || (echo 'FAIL JSON field status'; exit 1)
  grep -q '"service": "authz"' /tmp/resp.json || (echo 'FAIL JSON field service'; exit 1)
fi
echo 'Test: Ingestion service health'
code=$(curl -s -o /tmp/resp.json -w '%{http_code}' 'http://localhost:8081/healthz')
if [ '$code' != '200' ]; then echo 'FAIL http://localhost:8081/healthz -> '$code; exit 1; fi
if command -v jq >/dev/null 2>&1; then
  jq -e 'has("status") and .["status"]=="ok"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field status'; exit 1)
  jq -e 'has("service") and .["service"]=="ingestion"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field service'; exit 1)
else
  grep -q '"status": "ok"' /tmp/resp.json || (echo 'FAIL JSON field status'; exit 1)
  grep -q '"service": "ingestion"' /tmp/resp.json || (echo 'FAIL JSON field service'; exit 1)
fi
echo 'Test: AI Pipeline service health'
code=$(curl -s -o /tmp/resp.json -w '%{http_code}' 'http://localhost:8085/healthz')
if [ '$code' != '200' ]; then echo 'FAIL http://localhost:8085/healthz -> '$code; exit 1; fi
if command -v jq >/dev/null 2>&1; then
  jq -e 'has("status") and .["status"]=="ok"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field status'; exit 1)
  jq -e 'has("service") and .["service"]=="ai-pipeline"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field service'; exit 1)
else
  grep -q '"status": "ok"' /tmp/resp.json || (echo 'FAIL JSON field status'; exit 1)
  grep -q '"service": "ai-pipeline"' /tmp/resp.json || (echo 'FAIL JSON field service'; exit 1)
fi
echo 'Test: Teams bot health'
code=$(curl -s -o /tmp/resp.json -w '%{http_code}' 'http://localhost:3978/healthz')
if [ '$code' != '200' ]; then echo 'FAIL http://localhost:3978/healthz -> '$code; exit 1; fi
if command -v jq >/dev/null 2>&1; then
  jq -e 'has("status") and .["status"]=="ok"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field status'; exit 1)
  jq -e 'has("service") and .["service"]=="teams-bot"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field service'; exit 1)
else
  grep -q '"status": "ok"' /tmp/resp.json || (echo 'FAIL JSON field status'; exit 1)
  grep -q '"service": "teams-bot"' /tmp/resp.json || (echo 'FAIL JSON field service'; exit 1)
fi
echo 'Test: Admin UI accessibility'
code=$(curl -s -o /tmp/resp.json -w '%{http_code}' 'http://localhost:3000')
if [ '$code' != '200' ]; then echo 'FAIL http://localhost:3000 -> '$code; exit 1; fi
echo 'Test: Cost service health'
code=$(curl -s -o /tmp/resp.json -w '%{http_code}' 'http://localhost:8082/healthz')
if [ '$code' != '200' ]; then echo 'FAIL http://localhost:8082/healthz -> '$code; exit 1; fi
if command -v jq >/dev/null 2>&1; then
  jq -e 'has("status") and .["status"]=="ok"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field status'; exit 1)
else
  grep -q '"status": "ok"' /tmp/resp.json || (echo 'FAIL JSON field status'; exit 1)
fi
echo 'Test: Box MCP server health'
code=$(curl -s -o /tmp/resp.json -w '%{http_code}' 'http://localhost:8086/healthz')
if [ '$code' != '200' ]; then echo 'FAIL http://localhost:8086/healthz -> '$code; exit 1; fi
echo 'Test: Microsoft files MCP server health'
code=$(curl -s -o /tmp/resp.json -w '%{http_code}' 'http://localhost:8087/healthz')
if [ '$code' != '200' ]; then echo 'FAIL http://localhost:8087/healthz -> '$code; exit 1; fi
echo 'Test: Enhanced AI pipeline health check'
code=$(curl -s -o /tmp/resp.json -w '%{http_code}' 'http://localhost:8085/healthz')
if [ '$code' != '200' ]; then echo 'FAIL http://localhost:8085/healthz -> '$code; exit 1; fi
if command -v jq >/dev/null 2>&1; then
  jq -e 'has("status") and .["status"]=="ok"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field status'; exit 1)
  jq -e 'has("service") and .["service"]=="enhanced-ai-pipeline"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field service'; exit 1)
  jq -e 'has("version") and .["version"]=="2.0.0"' /tmp/resp.json >/dev/null || (echo 'FAIL JSON field version'; exit 1)
else
  grep -q '"status": "ok"' /tmp/resp.json || (echo 'FAIL JSON field status'; exit 1)
  grep -q '"service": "enhanced-ai-pipeline"' /tmp/resp.json || (echo 'FAIL JSON field service'; exit 1)
  grep -q '"version": "2.0.0"' /tmp/resp.json || (echo 'FAIL JSON field version'; exit 1)
fi
echo 'Test: Test enhanced processing endpoint'
code=$(curl -s -o /tmp/resp.json -w '%{http_code}' 'http://localhost:8085/process_enhanced')
if [ '$code' != '200' ]; then echo 'FAIL http://localhost:8085/process_enhanced -> '$code; exit 1; fi
