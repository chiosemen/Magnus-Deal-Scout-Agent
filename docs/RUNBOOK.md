# Magnus Deal Scout Agent - Operations Runbook

## Table of Contents
1. [Service Overview](#service-overview)
2. [On-Call Response](#on-call-response)
3. [Common Issues](#common-issues)
4. [Monitoring & Alerts](#monitoring--alerts)
5. [Escalation Procedures](#escalation-procedures)
6. [Maintenance Windows](#maintenance-windows)

---

## Service Overview

### Service Details
- **Service Name**: Magnus Deal Scout Agent
- **Description**: Marketplace aggregation and deal monitoring platform
- **Primary Language**: Python 3.11+
- **Framework**: FastAPI
- **Dependencies**: PostgreSQL, Redis, Celery

### Architecture Components
```
┌─────────────────┐
│   Load Balancer │
└────────┬────────┘
         │
    ┌────▼────┐
    │ API (x4)│ ← FastAPI application (4 workers)
    └────┬────┘
         │
    ┌────▼────────┬────────────┐
    │             │            │
┌───▼───┐    ┌───▼───┐   ┌───▼────┐
│PostgreSQL│  │ Redis  │   │ Celery  │
│         │  │        │   │ Workers │
└─────────┘  └────────┘   └─────────┘
```

### SLA & Expectations
- **Uptime Target**: 99.5% (monthly)
- **Response Time**: p95 < 500ms
- **Error Rate**: < 0.5%
- **RTO (Recovery Time Objective)**: 1 hour
- **RPO (Recovery Point Objective)**: 5 minutes

### Service Endpoints
- **Health Check**: `GET /health`
- **Detailed Health**: `GET /api/v1/monitoring/health/detailed`
- **Metrics**: `GET /api/v1/monitoring/metrics`
- **API Docs**: `GET /docs` (production: disabled)

---

## On-Call Response

### Initial Response Checklist

When alerted, follow this sequence:

1. **Acknowledge the alert** (within 5 minutes)
   - Update incident channel
   - Note time of acknowledgment

2. **Check service health**
   ```bash
   # Quick health check
   curl https://api.dealscout.com/health

   # Detailed status
   curl https://api.dealscout.com/api/v1/monitoring/health/detailed
   ```

3. **Check monitoring dashboards**
   - Grafana: https://grafana.dealscout.com
   - Sentry: https://sentry.io/dealscout
   - Flower: https://flower.dealscout.com

4. **Review recent logs**
   ```bash
   # API logs
   kubectl logs -l app=deal-scout-api --tail=100

   # Celery worker logs
   kubectl logs -l app=celery-worker --tail=100

   # Database logs
   kubectl logs -l app=postgres --tail=50
   ```

### Severity Levels

**P0 - Critical** (Response: 15 min, Resolution: 1 hour)
- Service completely down
- Data loss occurring
- Security breach

**P1 - High** (Response: 30 min, Resolution: 4 hours)
- Degraded performance affecting >50% users
- Critical feature unavailable
- Elevated error rates (>5%)

**P2 - Medium** (Response: 2 hours, Resolution: 24 hours)
- Non-critical feature down
- Performance degradation affecting <50% users
- Elevated queue backlogs

**P3 - Low** (Response: 1 day, Resolution: 1 week)
- Minor bugs
- Feature requests
- Documentation issues

---

## Common Issues

### 1. High API Response Time

**Symptoms:**
- p95 response time > 1s
- Slow page loads
- Timeout errors

**Diagnosis:**
```bash
# Check API metrics
curl https://api.dealscout.com/api/v1/monitoring/metrics | grep http_request_duration

# Check database connections
psql -h db.dealscout.com -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# Check Redis
redis-cli -h redis.dealscout.com SLOWLOG GET 10
```

**Resolution:**
1. Check if database query is slow:
   ```bash
   # View slow queries
   psql -h db.dealscout.com -U postgres -d deal_scout -c "
   SELECT query, mean_exec_time, calls
   FROM pg_stat_statements
   ORDER BY mean_exec_time DESC
   LIMIT 10;"
   ```

2. Scale API workers if needed:
   ```bash
   kubectl scale deployment deal-scout-api --replicas=8
   ```

3. Clear Redis cache if stale:
   ```bash
   redis-cli -h redis.dealscout.com FLUSHDB
   ```

4. Check for memory leaks:
   ```bash
   kubectl top pods -l app=deal-scout-api
   ```

**Prevention:**
- Monitor query performance
- Implement caching strategy
- Regular database optimization

---

### 2. Celery Queue Backlog

**Symptoms:**
- Listings not updating
- Alerts not being sent
- Growing queue size

**Diagnosis:**
```bash
# Check Flower dashboard
open https://flower.dealscout.com

# Check queue lengths
redis-cli -h redis.dealscout.com LLEN celery

# Check active workers
celery -A app.tasks.celery_app inspect active
```

**Resolution:**
1. **Scale workers immediately:**
   ```bash
   kubectl scale deployment celery-worker --replicas=6
   ```

2. **Identify stuck tasks:**
   ```bash
   # Check for long-running tasks
   celery -A app.tasks.celery_app inspect active | grep -A 5 "time_start"
   ```

3. **Revoke stuck tasks if needed:**
   ```bash
   celery -A app.tasks.celery_app control revoke <task-id> --terminate
   ```

4. **Purge queue if necessary** (CAUTION):
   ```bash
   # Only in emergency - will lose queued tasks
   celery -A app.tasks.celery_app purge
   ```

**Root Causes:**
- Worker crashed/died
- Task timeout too short
- External API slowness
- Database connection exhaustion

**Prevention:**
- Monitor queue depth
- Set appropriate task timeouts
- Implement retry logic with exponential backoff
- Health check workers

---

### 3. Scraping Failures

**Symptoms:**
- No new listings being scraped
- High failure rate in task logs
- User complaints about missing deals

**Diagnosis:**
```bash
# Check recent scraping tasks
psql -h db.dealscout.com -U postgres -d deal_scout -c "
SELECT marketplace, status, COUNT(*)
FROM task_logs
WHERE task_name = 'run_search_task'
  AND created_at > NOW() - INTERVAL '1 hour'
GROUP BY marketplace, status;"

# Check specific failures
psql -h db.dealscout.com -U postgres -d deal_scout -c "
SELECT error, COUNT(*)
FROM task_logs
WHERE status = 'failed'
  AND created_at > NOW() - INTERVAL '1 hour'
GROUP BY error
LIMIT 10;"
```

**Resolution:**

**Issue: Rate Limited by Marketplace**
```bash
# Reduce scraping frequency temporarily
# Update check_interval_minutes for active searches
psql -h db.dealscout.com -U postgres -d deal_scout -c "
UPDATE searches
SET check_interval_minutes = check_interval_minutes * 2
WHERE status = 'active'
  AND check_interval_minutes < 120;"
```

**Issue: IP Blocked**
- Rotate proxy servers
- Contact marketplace for API access
- Implement backoff strategy

**Issue: Scraper Code Outdated**
- Marketplace changed HTML structure
- Update scraper selectors in `app/agents/`
- Deploy hotfix
- Monitor for similar issues

**Prevention:**
- Monitor scrape success rates
- Implement graceful degradation
- Use official APIs where available
- Respect robots.txt and rate limits

---

### 4. Database Connection Pool Exhausted

**Symptoms:**
- "Too many connections" errors
- API requests timing out
- 500 errors in logs

**Diagnosis:**
```bash
# Check current connections
psql -h db.dealscout.com -U postgres -c "
SELECT state, COUNT(*)
FROM pg_stat_activity
GROUP BY state;"

# Check connection pool settings
psql -h db.dealscout.com -U postgres -c "SHOW max_connections;"
```

**Resolution:**
1. **Immediate action - Kill idle connections:**
   ```bash
   psql -h db.dealscout.com -U postgres -c "
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
     AND state_change < NOW() - INTERVAL '5 minutes';"
   ```

2. **Restart API pods** (forces connection reset):
   ```bash
   kubectl rollout restart deployment/deal-scout-api
   ```

3. **Scale up database** (if needed):
   ```bash
   # Increase max_connections
   # This requires database restart - plan carefully
   ```

**Root Causes:**
- Connection leaks in code
- Pool size too small
- Long-running transactions

**Prevention:**
- Use connection pooling properly (SQLAlchemy)
- Set connection timeouts
- Monitor connection usage
- Implement connection recycling

---

### 5. External API Outage (eBay, Facebook, etc.)

**Symptoms:**
- Specific marketplace failing
- Consistent errors from one source
- External service status page shows issues

**Diagnosis:**
```bash
# Check error patterns by marketplace
psql -h db.dealscout.com -U postgres -d deal_scout -c "
SELECT
  SUBSTRING(error FROM 1 FOR 100) as error_sample,
  COUNT(*)
FROM task_logs
WHERE status = 'failed'
  AND created_at > NOW() - INTERVAL '30 minutes'
  AND task_name LIKE '%scrape%'
GROUP BY error_sample
ORDER BY COUNT(*) DESC;"

# Check external service status
curl https://status.ebay.com
curl https://developers.facebook.com/status
```

**Resolution:**
1. **Verify outage:**
   - Check service status pages
   - Test API directly
   - Check community forums

2. **Disable affected searches temporarily:**
   ```bash
   # Pause searches for affected marketplace
   psql -h db.dealscout.com -U postgres -d deal_scout -c "
   UPDATE searches
   SET status = 'paused'
   WHERE 'ebay' = ANY(marketplaces)
     AND status = 'active';"
   ```

3. **Update incident status page:**
   - Notify users of known issue
   - Provide ETA if available
   - Link to external status page

4. **Re-enable once resolved:**
   ```bash
   # Resume searches
   psql -h db.dealscout.com -U postgres -d deal_scout -c "
   UPDATE searches
   SET status = 'active'
   WHERE 'ebay' = ANY(marketplaces)
     AND status = 'paused';"
   ```

**Prevention:**
- Implement circuit breakers
- Graceful degradation per marketplace
- Status page integration
- User notifications for outages

---

### 6. Memory Leak / High Memory Usage

**Symptoms:**
- OOMKilled pods
- Gradual memory increase
- Pod restarts

**Diagnosis:**
```bash
# Check memory usage
kubectl top pods -l app=deal-scout-api

# Check pod restarts
kubectl get pods -l app=deal-scout-api

# View pod events
kubectl describe pod <pod-name>
```

**Resolution:**
1. **Immediate - Restart affected pods:**
   ```bash
   kubectl rollout restart deployment/deal-scout-api
   ```

2. **Investigate memory leak:**
   ```bash
   # Enable memory profiling
   # Add to API startup: memory_profiler

   # Check for large objects in memory
   # Review recent code changes
   # Look for unclosed connections/files
   ```

3. **Temporary increase memory limits:**
   ```yaml
   # k8s/deployment.yaml
   resources:
     limits:
       memory: "2Gi"  # Increase from 1Gi
   ```

**Root Causes:**
- Unclosed database connections
- Large objects in memory (images, cached data)
- Circular references preventing GC
- Memory-intensive scraping operations

**Prevention:**
- Regular memory profiling
- Implement memory limits
- Use connection pooling
- Stream large datasets

---

## Monitoring & Alerts

### Key Metrics to Watch

**API Metrics:**
- Request rate (requests/sec)
- Response time (p50, p95, p99)
- Error rate (%)
- Active connections

**Database Metrics:**
- Connection count
- Query duration
- Cache hit rate
- Replication lag

**Celery Metrics:**
- Queue depth
- Task success/failure rate
- Worker count
- Task duration

**System Metrics:**
- CPU usage
- Memory usage
- Disk I/O
- Network traffic

### Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| API Response Time (p95) | > 1s | > 3s |
| API Error Rate | > 1% | > 5% |
| Celery Queue Depth | > 1000 | > 5000 |
| Database Connections | > 80% | > 95% |
| Memory Usage | > 80% | > 95% |
| Disk Usage | > 80% | > 95% |
| Failed Tasks (1hr) | > 50 | > 200 |

### Dashboards

**Grafana Dashboards:**
1. **API Overview** - Request rates, latencies, errors
2. **Database Performance** - Connections, queries, replication
3. **Celery Monitoring** - Queue depths, task rates, workers
4. **System Resources** - CPU, memory, disk, network
5. **Business Metrics** - Active searches, listings scraped, users

**Access:**
- Grafana: https://grafana.dealscout.com
- Username: ops@dealscout.com
- Password: (in 1Password vault)

---

## Escalation Procedures

### Escalation Path

**Level 1: On-Call Engineer**
- Initial response
- Follow runbook
- Resolve P2/P3 issues

**Level 2: Team Lead**
- Escalate after 30 minutes if unresolved
- P0/P1 issues
- Complex technical decisions

**Level 3: Engineering Manager**
- Escalate after 1 hour
- Service-wide outages
- External coordination needed

**Level 4: CTO**
- Escalate for critical business impact
- PR/communications needed
- Major security incidents

### When to Escalate

Escalate immediately for:
- Service down > 15 minutes
- Data loss detected
- Security breach suspected
- Unable to diagnose issue

Escalate after attempting resolution:
- Issue persists after following runbook
- Requires code changes
- Needs infrastructure changes
- Affects >50% of users

### Contact Information

| Role | Name | Phone | Email | Availability |
|------|------|-------|-------|--------------|
| On-Call Engineer | Rotating | +1-XXX-XXX-XXXX | oncall@dealscout.com | 24/7 |
| Team Lead | John Doe | +1-XXX-XXX-XXXX | john@dealscout.com | Business hours |
| Engineering Manager | Jane Smith | +1-XXX-XXX-XXXX | jane@dealscout.com | Business hours |
| CTO | Bob Johnson | +1-XXX-XXX-XXXX | bob@dealscout.com | Emergency only |

---

## Maintenance Windows

### Scheduled Maintenance

**Regular Maintenance:**
- **When**: Every Sunday 2:00 AM - 4:00 AM UTC
- **Duration**: Max 2 hours
- **Impact**: Service may be degraded
- **Notification**: 72 hours advance notice

**Activities:**
- Database backups
- Index rebuilding
- Deployment of non-critical updates
- Log rotation
- Certificate renewal

### Emergency Maintenance

**Criteria:**
- Critical security patch
- Data integrity issue
- Service stability at risk

**Process:**
1. Notify users (if time permits)
2. Create incident ticket
3. Perform maintenance
4. Verify service health
5. Post-mortem within 24 hours

### Deployment Process

See [RELEASE_PROCEDURES.md](./RELEASE_PROCEDURES.md) for detailed deployment steps.

---

## Useful Commands

### Quick Status Check
```bash
# All services health
kubectl get pods -A | grep deal-scout

# API health
curl https://api.dealscout.com/health

# Database status
psql -h db.dealscout.com -U postgres -c "SELECT NOW();"

# Redis status
redis-cli -h redis.dealscout.com PING

# Celery workers
celery -A app.tasks.celery_app inspect active_queues
```

### Log Access
```bash
# API logs (last 100 lines)
kubectl logs -l app=deal-scout-api --tail=100 -f

# Celery worker logs
kubectl logs -l app=celery-worker --tail=100 -f

# Filter for errors
kubectl logs -l app=deal-scout-api | grep ERROR

# Specific time range
kubectl logs -l app=deal-scout-api --since=1h
```

### Database Operations
```bash
# Connect to database
psql -h db.dealscout.com -U postgres -d deal_scout

# Check table sizes
psql -h db.dealscout.com -U postgres -d deal_scout -c "
SELECT
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# Active queries
psql -h db.dealscout.com -U postgres -c "
SELECT pid, age(query_start, clock_timestamp()), usename, query
FROM pg_stat_activity
WHERE query != '<IDLE>' AND query NOT ILIKE '%pg_stat_activity%'
ORDER BY query_start;"
```

---

## Post-Incident Review

After resolving a P0 or P1 incident:

1. **Create incident report** (within 24 hours)
   - Timeline of events
   - Root cause analysis
   - Impact assessment
   - Resolution steps taken

2. **Action items**
   - Preventive measures
   - Monitoring improvements
   - Documentation updates
   - Runbook enhancements

3. **Team review** (within 1 week)
   - Share learnings
   - Update procedures
   - Assign follow-up tasks

4. **Customer communication**
   - Post-mortem summary
   - Preventive measures
   - Compensation (if applicable)

---

## Additional Resources

- **API Documentation**: https://docs.dealscout.com/api
- **Architecture Diagrams**: https://docs.dealscout.com/architecture
- **Sentry**: https://sentry.io/dealscout
- **Grafana**: https://grafana.dealscout.com
- **Flower**: https://flower.dealscout.com
- **Status Page**: https://status.dealscout.com
- **Internal Wiki**: https://wiki.dealscout.com

---

**Last Updated**: 2024-10-28
**Maintained By**: Platform Engineering Team
**Review Frequency**: Monthly
