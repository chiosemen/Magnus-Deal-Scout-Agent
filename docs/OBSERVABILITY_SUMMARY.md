# Observability & Operations - Implementation Summary

## Overview

This document summarizes the observability, monitoring, and operational tooling added to the Magnus Deal Scout Agent platform.

---

## What Was Implemented

### 1. Structured Logging (`app/core/logging.py`)

**Features:**
- JSON-formatted logs for easy parsing
- Contextual information (timestamp, environment, service, version)
- Configurable log levels
- Third-party library noise reduction

**Usage:**
```python
from app.core.logging import get_logger

logger = get_logger(__name__)
logger.info("User created", extra={"user_id": user.id, "email": user.email})
logger.error("Search failed", extra={"search_id": search_id, "error": str(e)})
```

**Log Format:**
```json
{
  "timestamp": "2024-10-28T10:00:00.000Z",
  "level": "INFO",
  "service": "Deal Scout API",
  "version": "1.0.0",
  "environment": "production",
  "name": "app.api.v1.searches",
  "message": "Search created successfully",
  "user_id": 123,
  "search_id": 456
}
```

---

### 2. Sentry Integration (`app/core/monitoring.py`)

**Features:**
- Automatic error tracking
- Performance monitoring (transactions, traces)
- Release tracking
- User context
- Breadcrumbs
- Custom before_send filtering

**Configuration:**
```python
# .env
SENTRY_DSN=https://xxx@sentry.io/xxx

# Automatic initialization in app/main.py
init_sentry()
```

**Integrations:**
- FastAPI (HTTP requests)
- SQLAlchemy (database queries)
- Redis (cache operations)
- Celery (background tasks)

**Features:**
- Sensitive data scrubbing (Authorization headers, cookies)
- Health check filtering
- Release version tracking
- Environment tagging

---

### 3. Prometheus Metrics (`app/core/monitoring.py`)

**Metrics Exposed:**

**HTTP Metrics:**
```
http_requests_total{method, endpoint, status}  # Counter
http_request_duration_seconds{method, endpoint}  # Histogram
```

**Celery Metrics:**
```
celery_tasks_total{task_name, status}  # Counter
celery_task_duration_seconds{task_name}  # Histogram
```

**Marketplace Metrics:**
```
marketplace_scrapes_total{marketplace, status}  # Counter
marketplace_listings_scraped_total{marketplace}  # Counter
```

**System Metrics:**
```
active_searches_total  # Gauge
database_connections_total  # Gauge
```

**Access:**
```bash
# Metrics endpoint
curl http://localhost:8000/api/v1/monitoring/metrics
```

---

### 4. Health Check Endpoints (`app/api/v1/monitoring.py`)

**Basic Health Check:**
```
GET /health

Response:
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production"
}
```

**Detailed Health Check:**
```
GET /api/v1/monitoring/health/detailed

Response:
{
  "status": "healthy",
  "timestamp": "2024-10-28T10:00:00Z",
  "components": {
    "database": {
      "status": "healthy",
      "connections": 5,
      "pool_size": 10
    },
    "redis": {
      "status": "healthy",
      "used_memory": "245MB",
      "connected_clients": 3
    },
    "celery": {
      "status": "healthy",
      "workers": 4,
      "worker_names": ["worker1@host", ...]
    },
    "system": {
      "status": "healthy",
      "cpu_percent": 35,
      "memory_percent": 65,
      "disk_percent": 45
    },
    "application": {
      "status": "healthy",
      "active_searches": 150,
      "listings_last_24h": 1234,
      "failed_tasks_last_hour": 2
    }
  }
}
```

**Kubernetes Probes:**
```
GET /api/v1/monitoring/health/ready  # Readiness probe
GET /api/v1/monitoring/health/live   # Liveness probe
```

---

### 5. Request Tracking Middleware

**Features:**
- Automatic timing of all HTTP requests
- Metrics collection
- X-Process-Time header
- Error tracking

**Implementation:**
```python
@app.middleware("http")
async def track_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    track_request_metrics(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
        duration=duration
    )

    response.headers["X-Process-Time"] = str(duration)
    return response
```

---

## Operational Documentation Created

### 1. RUNBOOK.md (Operations Playbook)

**Contents:**
- Service overview and architecture
- On-call response procedures
- Common issues and resolutions
- Monitoring and alerts
- Escalation procedures
- Useful commands
- Post-incident review process

**Key Sections:**
- High API Response Time → diagnosis & resolution
- Celery Queue Backlog → scaling & purging
- Scraping Failures → rate limiting & code updates
- Database Connection Pool Exhausted → connection management
- External API Outage → graceful degradation
- Memory Leaks → profiling & limits

**SLA Commitments:**
- Uptime Target: 99.5%
- Response Time p95: < 500ms
- Error Rate: < 0.5%
- RTO: 1 hour
- RPO: 5 minutes

---

### 2. RELEASE_PROCEDURES.md

**Contents:**
- Release schedule (every 2 weeks)
- Pre-release checklist
- Deployment process (step-by-step)
- Rollback procedures
- Database migration best practices
- Monitoring during release
- Communication plan
- Post-release activities

**Release Types:**
- Regular Release (planned features)
- Hotfix Release (urgent bugs)
- Emergency Release (critical issues)

**Deployment Steps:**
1. Prepare release (version bump, changelog)
2. Run tests (unit, integration, security)
3. Build and tag Docker images
4. Deploy to staging
5. Staging validation (smoke tests, load tests)
6. Production deployment (rolling update)
7. Post-deployment validation
8. Announcement and documentation

---

### 3. API_REFERENCE.md

**Contents:**
- Complete API endpoint documentation
- Authentication guide
- Request/response examples
- Error codes and handling
- Rate limiting information
- Pagination support
- OpenAPI specification links

**Endpoints Documented:**
- Authentication (register, login, me)
- Searches (CRUD operations)
- Listings (filtering, saving)
- Alerts (notifications)
- Dashboard (statistics)
- Monitoring (health, metrics)

---

### 4. ARCHITECTURE.md

**Contents:**
- High-level system architecture diagram
- Component details (API, Database, Cache, Queue)
- Data flow diagrams
- Security architecture
- Scalability approach
- Monitoring & observability
- Disaster recovery
- Technology stack summary

**Architecture Diagrams:**
```
Users
  ↓
Load Balancer
  ↓
FastAPI (x4)
  ↓
PostgreSQL / Redis / Celery Workers
  ↓
Marketplace Agents (eBay, Facebook, etc.)
```

---

### 5. DATA_RETENTION_PRIVACY.md

**Contents:**
- Data collection practices
- Retention periods
- GDPR compliance
- User rights (access, erasure, portability)
- Data deletion procedures
- Third-party data sharing
- Marketplace data privacy
- Cookie policy
- Data breach notification
- International data transfers

**Key Policies:**
- Active listings: 30 days
- User activity logs: 90 days
- Deleted user data: 30 days grace period
- Backups: 30 days (daily), 90 days (weekly), 1 year (monthly)
- No sale of personal data
- Standard Contractual Clauses for US transfers

---

## Monitoring Setup

### Grafana Dashboards

**Recommended Dashboards:**
1. **API Overview**
   - Request rate (req/sec)
   - Response time percentiles (p50, p95, p99)
   - Error rate (%)
   - Active connections

2. **Database Performance**
   - Connection count
   - Query duration
   - Cache hit rate
   - Slow queries

3. **Celery Monitoring**
   - Queue depth by queue
   - Task success/failure rate
   - Worker count
   - Task duration distribution

4. **System Resources**
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network traffic

5. **Business Metrics**
   - Active searches
   - Listings scraped (by marketplace)
   - New user signups
   - Alert delivery rate

### Alert Configuration

**Critical Alerts (PagerDuty):**
- API error rate > 5%
- Database connections > 95%
- All Celery workers down
- Disk usage > 95%

**Warning Alerts (Slack):**
- API response time p95 > 1s
- Celery queue depth > 1000
- Failed tasks > 50/hour
- Memory usage > 80%

---

## Development Dependencies

Updated `requirements.txt` with:
```
# Monitoring & Observability
sentry-sdk[fastapi]==1.40.0
prometheus-client==0.19.0
python-json-logger==2.0.7
psutil==5.9.7
```

---

## Usage Examples

### Logging

```python
from app.core.logging import get_logger

logger = get_logger(__name__)

# Simple logging
logger.info("Search created")

# Structured logging
logger.info("User action", extra={
    "action": "create_search",
    "user_id": user.id,
    "search_id": search.id,
    "marketplaces": search.marketplaces
})

# Error logging with context
try:
    result = scrape_marketplace(search)
except Exception as e:
    logger.error(
        "Scraping failed",
        extra={
            "search_id": search.id,
            "marketplace": marketplace,
            "error": str(e)
        },
        exc_info=True
    )
```

### Metrics

```python
from app.core.monitoring import track_marketplace_scrape

# Track scraping attempt
track_marketplace_scrape(
    marketplace="ebay",
    status="success",
    listings_count=25
)

# Track failed scrape
track_marketplace_scrape(
    marketplace="facebook",
    status="failed",
    listings_count=0
)
```

### Timed Operations

```python
from app.core.monitoring import timed_operation

@timed_operation("scrape_ebay")
async def scrape_ebay_listings(search_id: int):
    # Function automatically timed and logged
    ...
```

---

## Kubernetes Integration

### Deployment with Health Checks

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deal-scout-api
spec:
  replicas: 4
  template:
    spec:
      containers:
      - name: api
        image: deal-scout-api:1.0.0
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /api/v1/monitoring/health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/monitoring/health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Prometheus ServiceMonitor

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: deal-scout-api
spec:
  selector:
    matchLabels:
      app: deal-scout-api
  endpoints:
  - port: http
    path: /api/v1/monitoring/metrics
    interval: 30s
```

---

## Alerting Rules

### Prometheus Alert Rules

```yaml
groups:
- name: deal_scout_api
  rules:
  - alert: HighErrorRate
    expr: |
      rate(http_requests_total{status=~"5.."}[5m]) /
      rate(http_requests_total[5m]) > 0.05
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value | humanizePercentage }}"

  - alert: HighResponseTime
    expr: |
      histogram_quantile(0.95,
        rate(http_request_duration_seconds_bucket[5m])
      ) > 1.0
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High API response time"
      description: "p95 latency is {{ $value }}s"

  - alert: CeleryQueueBacklog
    expr: celery_queue_depth > 1000
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Celery queue backlog"
      description: "Queue depth is {{ $value }}"
```

---

## Next Steps

### Immediate Actions

1. **Set up Grafana**
   - Import dashboard templates
   - Configure data sources
   - Set up alerts

2. **Configure Sentry**
   - Create project
   - Set SENTRY_DSN in .env
   - Configure alert rules

3. **Set up Log Aggregation**
   - Configure ELK/CloudWatch
   - Set up log shipping
   - Create saved searches

4. **Test Health Checks**
   - Verify all endpoints
   - Test Kubernetes probes
   - Validate metrics

### Future Enhancements

1. **Distributed Tracing**
   - Add OpenTelemetry
   - Trace requests across services
   - Visualize in Jaeger

2. **Custom Dashboards**
   - Business KPI dashboard
   - Cost optimization dashboard
   - User analytics dashboard

3. **Advanced Alerting**
   - Anomaly detection
   - Predictive alerts
   - Smart alert routing

4. **Compliance**
   - Audit logging
   - Access tracking
   - Compliance reports

---

## Files Created

**Core Application:**
- `backend/app/core/logging.py` - Structured logging
- `backend/app/core/monitoring.py` - Metrics & Sentry
- `backend/app/api/v1/monitoring.py` - Health & metrics endpoints
- `backend/app/main.py` - Updated with observability

**Documentation:**
- `docs/RUNBOOK.md` - Operational playbook
- `docs/RELEASE_PROCEDURES.md` - Deployment guide
- `docs/API_REFERENCE.md` - Complete API docs
- `docs/ARCHITECTURE.md` - System architecture
- `docs/DATA_RETENTION_PRIVACY.md` - Privacy policy
- `docs/OBSERVABILITY_SUMMARY.md` - This document

**Configuration:**
- `backend/requirements.txt` - Updated with monitoring deps

---

## Key Takeaways

✅ **Comprehensive Observability**
- Structured logging for easy parsing
- Prometheus metrics for monitoring
- Sentry integration for error tracking
- Detailed health checks

✅ **Production-Ready Documentation**
- Operational runbooks for on-call engineers
- Step-by-step release procedures
- Complete API reference
- System architecture diagrams
- Privacy and compliance policies

✅ **Monitoring Best Practices**
- Request tracking middleware
- Component health checks
- Business metrics
- Alert thresholds

✅ **Compliance & Privacy**
- GDPR-compliant data retention
- User rights documentation
- Data processing inventory
- Privacy-by-design principles

---

**Implementation Date**: 2024-10-28
**Status**: ✅ Complete
**Next Review**: 2024-11-28 (monthly)

For questions or support, contact: engineering@dealscout.com
