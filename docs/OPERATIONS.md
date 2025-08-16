# Operations Guide

## Overview
This guide covers operational procedures, troubleshooting, and maintenance for the Unstructured Data Indexing & AI-Query Application.

## Daily Operations

### Health Monitoring
```bash
# Check all service health
for service in orchestrator authz ai-pipeline bot admin-ui; do
  echo "Checking $service..."
  curl -s http://localhost:$(docker-compose port $service 80 | cut -d: -f2)/healthz | jq '.status'
done

# Monitor container status
docker-compose ps

# Check resource usage
docker stats --no-stream
```

### Log Monitoring
```bash
# View all service logs
docker-compose logs -f

# Monitor specific service logs
docker-compose logs -f orchestrator
docker-compose logs -f authz

# Search logs for errors
docker-compose logs | grep -i error
docker-compose logs | grep -i exception
```

### Performance Monitoring
```bash
# Check database performance
docker-compose exec mongodb mongo --eval "
db.stats()
"

# Check Redis performance
docker-compose exec redis redis-cli info memory

# Monitor API response times
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8080/healthz"
```

## Troubleshooting

### Service Won't Start
```bash
# Check container logs
docker-compose logs <service-name>

# Check container status
docker-compose ps -a

# Check resource availability
docker system df
df -h

# Restart specific service
docker-compose restart <service-name>
```

### Database Issues
```bash
# Check MongoDB connectivity
docker-compose exec mongodb mongo --eval "db.runCommand({ping: 1})"

# Check MongoDB status
docker-compose exec mongodb mongo --eval "
db.serverStatus()
"

# Check MongoDB logs
docker-compose logs mongodb

# Restart MongoDB
docker-compose restart mongodb
```

### Network Issues
```bash
# Check inter-service communication
docker-compose exec orchestrator ping mongodb
docker-compose exec orchestrator ping redis

# Check network configuration
docker network ls
docker network inspect unstructured-data-bot_default

# Test service endpoints
curl -v http://localhost:8080/healthz
curl -v http://localhost:8083/healthz
```

### Memory Issues
```bash
# Check memory usage
docker stats --no-stream

# Check memory limits
docker-compose exec <service-name> cat /proc/1/limits

# Restart memory-intensive services
docker-compose restart ai-pipeline
docker-compose restart orchestrator
```

## Maintenance Procedures

### Regular Maintenance
```bash
# Weekly: Clean up old logs
docker system prune -f

# Weekly: Update base images
docker-compose pull

# Monthly: Clean up unused volumes
docker volume prune -f

# Monthly: Check disk space
df -h
docker system df
```

### Database Maintenance
```bash
# Check database size
docker-compose exec mongodb mongo --eval "
db.stats()
"

# Clean up old data
docker-compose exec mongodb mongo --eval "
db.qa_logs.deleteMany({
  created_at: {\$lt: new Date(Date.now() - 90*24*60*60*1000)}
})
"

# Optimize collections
docker-compose exec mongodb mongo --eval "
db.files.reIndex()
db.qa_logs.reIndex()
"
```

### Log Rotation
```bash
# Rotate application logs
docker-compose exec orchestrator logrotate -f /etc/logrotate.conf

# Archive old logs
tar -czf logs-$(date +%Y%m%d).tar.gz logs/
rm logs/*.log

# Clean up old log archives
find . -name "logs-*.tar.gz" -mtime +30 -delete
```

## Backup and Recovery

### Database Backup
```bash
# Create MongoDB backup
docker-compose exec mongodb mongodump \
  --db unstructured_data_bot \
  --out /backup/$(date +%Y%m%d_%H%M%S)

# Copy backup to host
docker cp mongodb:/backup/$(date +%Y%m%d_%H%M%S) ./backups/

# Create compressed backup
tar -czf backup-$(date +%Y%m%d_%H%M%S).tar.gz backups/
```

### Configuration Backup
```bash
# Backup environment files
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Backup Docker Compose files
cp docker-compose.yml docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S)

# Backup application configs
tar -czf config-backup-$(date +%Y%m%d_%H%M%S).tar.gz \
  services/*/config/ \
  services/*/app/config/
```

### Recovery Procedures
```bash
# Restore MongoDB from backup
docker-compose exec mongodb mongorestore \
  --db unstructured_data_bot \
  /backup/20250127_143022/unstructured_data_bot/

# Restore configuration
cp .env.backup.20250127_143022 .env

# Restart services with restored config
docker-compose down
docker-compose up -d
```

## Scaling Operations

### Horizontal Scaling
```bash
# Scale specific services
docker-compose up -d --scale orchestrator=3
docker-compose up -d --scale ai-pipeline=2

# Check scaled services
docker-compose ps

# Monitor load distribution
docker stats --no-stream
```

### Resource Limits
```bash
# Set memory limits for services
docker-compose exec orchestrator bash -c "
echo 'memory: 2g' > /sys/fs/cgroup/memory/memory.limit_in_bytes
"

# Set CPU limits
docker-compose exec orchestrator bash -c "
echo '100000' > /sys/fs/cgroup/cpu/cpu.cfs_quota_us
"
```

### Load Balancing
```bash
# Configure Nginx load balancer
cat > nginx.conf << EOF
upstream orchestrator {
    server localhost:8080;
    server localhost:8081;
    server localhost:8082;
}

server {
    listen 80;
    location / {
        proxy_pass http://orchestrator;
    }
}
EOF

# Restart Nginx
docker-compose restart nginx
```

## Security Operations

### Access Control
```bash
# Review user permissions
docker-compose exec mongodb mongo --eval "
db.users.find({}, {user_id: 1, permissions: 1, last_login: 1})
"

# Check failed login attempts
docker-compose exec mongodb mongo --eval "
db.auth_logs.find({status: 'failed'}, {user_id: 1, timestamp: 1, ip: 1})
"

# Review API access logs
docker-compose logs orchestrator | grep "unauthorized"
```

### Security Monitoring
```bash
# Check for suspicious activity
docker-compose exec mongodb mongo --eval "
db.qa_logs.find({
  question: /\$where|javascript|eval/
}, {user_id: 1, question: 1, timestamp: 1})
"

# Monitor sensitive data access
docker-compose exec mongodb mongo --eval "
db.qa_logs.find({
  'sensitivity_flags': {\$exists: true, \$ne: []}
}, {user_id: 1, question: 1, sensitivity_flags: 1})
"
```

### Incident Response
```bash
# Isolate compromised service
docker-compose stop <compromised-service>

# Preserve evidence
docker-compose logs <compromised-service> > incident-logs.txt
docker inspect <container-id> > container-info.txt

# Restore from backup
docker-compose up -d <compromised-service>
```

## Performance Optimization

### Database Optimization
```bash
# Create indexes for performance
docker-compose exec mongodb mongo --eval "
db.files.createIndex({tenant_id: 1, modified_at: -1})
db.files.createIndex({allowed_principals: 1})
db.qa_logs.createIndex({timestamp: -1})
"

# Analyze query performance
docker-compose exec mongodb mongo --eval "
db.files.find({tenant_id: 'test'}).explain('executionStats')
"
```

### Cache Optimization
```bash
# Check Redis cache hit rate
docker-compose exec redis redis-cli info stats | grep hit

# Optimize cache settings
docker-compose exec redis redis-cli config set maxmemory-policy allkeys-lru

# Monitor cache performance
docker-compose exec redis redis-cli monitor
```

### Application Optimization
```bash
# Profile application performance
docker-compose exec orchestrator python -m cProfile -o profile.stats app/main.py

# Analyze memory usage
docker-compose exec orchestrator python -c "
import tracemalloc
tracemalloc.start()
# Run your code here
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
print('[ Top 10 memory users ]')
for stat in top_stats[:10]:
    print(stat)
"
```

## Monitoring and Alerting

### Health Check Automation
```bash
# Automated health monitoring script
cat > health_monitor.sh << 'EOF'
#!/bin/bash
while true; do
    for service in orchestrator authz ai-pipeline bot admin-ui; do
        status=$(curl -s http://localhost:$(docker-compose port $service 80 | cut -d: -f2)/healthz | jq -r '.status')
        if [ "$status" != "healthy" ]; then
            echo "$(date): $service is unhealthy - $status" >> health_alerts.log
            # Send alert (email, Slack, etc.)
        fi
    done
    sleep 30
done
EOF

chmod +x health_monitor.sh
./health_monitor.sh &
```

### Performance Alerts
```bash
# Monitor response times
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8080/healthz" | \
awk '{if($1 > 1000) print "High response time: " $1 "ms"}'

# Monitor memory usage
docker stats --no-stream | awk 'NR>1 {if($4 > 80) print "High memory usage: " $4}'

# Monitor disk usage
df -h | awk 'NR>1 {if($5 > 80) print "High disk usage: " $5}'
```

## Emergency Procedures

### Service Outage Response
```bash
# 1. Assess impact
docker-compose ps
curl -s http://localhost:8080/healthz

# 2. Check logs for errors
docker-compose logs --tail=100

# 3. Restart critical services
docker-compose restart orchestrator
docker-compose restart authz

# 4. Verify recovery
curl -s http://localhost:8080/healthz
```

### Data Loss Prevention
```bash
# Stop all write operations
docker-compose stop ingestion
docker-compose stop ai-pipeline

# Create emergency backup
docker-compose exec mongodb mongodump --db unstructured_data_bot --out /emergency-backup

# Copy emergency backup
docker cp mongodb:/emergency-backup ./emergency-backup-$(date +%Y%m%d_%H%M%S)
```

### Rollback Procedures
```bash
# Rollback to previous version
git log --oneline -5
git checkout <previous-commit-hash>

# Restart with previous version
docker-compose down
docker-compose up -d

# Verify rollback
curl -s http://localhost:8080/healthz
```

## Next Steps
1. Set up automated monitoring and alerting
2. Implement backup automation
3. Create runbooks for common issues
4. Establish performance baselines
5. Plan disaster recovery procedures

---
*Last Updated: 2025-01-27*
*Version: 1.0*
