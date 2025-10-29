# System Architecture

## Overview

Magnus Deal Scout Agent is a distributed system for aggregating and monitoring marketplace listings across multiple platforms.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         End Users                                │
│                  (Web, Mobile, API Clients)                      │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ HTTPS
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                    Load Balancer (ALB/Nginx)                     │
│                  SSL Termination, Rate Limiting                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼────────┐ ┌─────▼──────┐ ┌───────▼────────┐
│  FastAPI App   │ │ FastAPI App│ │  FastAPI App   │
│   (Worker 1)   │ │ (Worker 2) │ │   (Worker 3)   │
└────────┬───────┘ └──────┬─────┘ └────────┬───────┘
         │                │                 │
         └────────────────┼─────────────────┘
                          │
      ┌───────────────────┼───────────────────┐
      │                   │                   │
┌─────▼─────┐      ┌──────▼─────┐     ┌──────▼──────┐
│PostgreSQL │      │   Redis    │     │   Celery    │
│    DB     │      │   Cache    │     │   Workers   │
│           │      │ & Queue    │     │   (x4)      │
└───────────┘      └────────────┘     └──────┬──────┘
                                              │
                           ┌──────────────────┼──────────────────┐
                           │                  │                  │
                    ┌──────▼─────┐  ┌────────▼────┐  ┌─────────▼────┐
                    │    eBay    │  │  Facebook   │  │   Gumtree    │
                    │  Scraper   │  │  Scraper    │  │   Scraper    │
                    └────────────┘  └─────────────┘  └──────────────┘
```

## Component Details

### 1. API Layer (FastAPI)

**Technology:** FastAPI + Uvicorn
**Instances:** 4+ workers (auto-scaling)
**Responsibilities:**
- Handle HTTP requests
- Authentication & authorization
- Request validation
- Response serialization
- Rate limiting
- Metrics collection

**Endpoints:**
- Authentication: `/api/v1/auth/*`
- Searches: `/api/v1/searches/*`
- Listings: `/api/v1/listings/*`
- Alerts: `/api/v1/alerts/*`
- Monitoring: `/api/v1/monitoring/*`

**Configuration:**
```yaml
workers: 4
worker_class: uvicorn.workers.UvicornWorker
timeout: 30
keepalive: 5
max_requests: 1000
max_requests_jitter: 100
```

---

### 2. Database Layer (PostgreSQL)

**Technology:** PostgreSQL 16
**Configuration:**
- Primary-replica setup
- Connection pooling (20 connections)
- Automatic backups (daily)

**Schema:**

```
┌─────────────┐
│    Users    │
│─────────────│
│ id (PK)     │
│ email       │
│ password    │
│ tier        │
└──────┬──────┘
       │
       │ 1:N
       │
┌──────▼──────┐         ┌─────────────┐
│   Searches  │──────N:M│  Listings   │
│─────────────│         │─────────────│
│ id (PK)     │         │ id (PK)     │
│ user_id(FK) │         │ search_id   │
│ keywords    │         │ external_id │
│ marketplaces│         │ marketplace │
│ filters     │         │ title       │
│ status      │         │ price       │
└──────┬──────┘         │ url         │
       │                └─────────────┘
       │ 1:N
       │
┌──────▼──────┐
│   Alerts    │
│─────────────│
│ id (PK)     │
│ user_id(FK) │
│ search_id   │
│ channel     │
│ config      │
└─────────────┘
```

**Indexes:**
```sql
CREATE INDEX idx_searches_user_status ON searches(user_id, status);
CREATE INDEX idx_listings_search_marketplace ON listings(search_id, marketplace);
CREATE INDEX idx_listings_price ON listings(price);
CREATE UNIQUE INDEX idx_listings_unique ON listings(marketplace, external_id);
```

---

### 3. Cache Layer (Redis)

**Technology:** Redis 7
**Configuration:**
- Master-replica setup
- Persistence: RDB + AOF
- Max memory: 4GB
- Eviction policy: allkeys-lru

**Use Cases:**

1. **Caching:**
   ```
   Key: search:{id}:listings
   TTL: 300 seconds
   Data: Serialized listing objects
   ```

2. **Session Storage:**
   ```
   Key: session:{token}
   TTL: 3600 seconds
   Data: User session data
   ```

3. **Rate Limiting:**
   ```
   Key: ratelimit:{user_id}:{minute}
   TTL: 60 seconds
   Data: Request count
   ```

4. **Message Queue (Celery):**
   ```
   Queue: celery
   Queue: celery:priority
   ```

---

### 4. Task Queue (Celery)

**Technology:** Celery 5.3
**Workers:** 4+ instances
**Queues:**
- `default`: General tasks
- `scraping`: Marketplace scraping tasks
- `alerts`: Notification tasks
- `maintenance`: Cleanup and maintenance

**Task Types:**

**Scraping Tasks:**
```python
@celery_app.task
def run_search_task(search_id: int):
    """Execute marketplace scraping for a search"""
    # Priority: Normal
    # Timeout: 30 minutes
    # Retry: 3 attempts
```

**Alert Tasks:**
```python
@celery_app.task
def trigger_alerts_task(search_id: int, new_listings: int):
    """Send notifications for new listings"""
    # Priority: High
    # Timeout: 5 minutes
    # Retry: 5 attempts
```

**Beat Schedule:**
```python
{
    'check-active-searches': {
        'task': 'app.tasks.scraping.check_active_searches',
        'schedule': crontab(minute='*/15'),  # Every 15 min
    },
    'cleanup-old-listings': {
        'task': 'app.tasks.scraping.cleanup_old_listings',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}
```

---

### 5. Scraping Agents

**Architecture:**
```
BaseAgent (Abstract)
    ├── EbayAgent
    ├── FacebookAgent
    ├── GumtreeAgent
    └── CraigslistAgent
```

**Agent Responsibilities:**
- Build search URLs
- Make HTTP requests
- Parse HTML/JSON responses
- Extract structured data
- Handle errors and retries
- Respect rate limits

**Anti-Pattern Measures:**
- Random delays between requests
- User-agent rotation
- Proxy support
- Session management
- Cookie handling

---

## Data Flow

### 1. User Creates Search

```
User → API → PostgreSQL
                ↓
            Celery Task Queued
                ↓
         Worker Executes Scraping
                ↓
         Listings Saved to DB
                ↓
          Alerts Triggered
```

### 2. Periodic Search Execution

```
Celery Beat (Every 15 min)
        ↓
Check Active Searches
        ↓
Queue Tasks for Due Searches
        ↓
Workers Execute Scraping
        ↓
Save New Listings
        ↓
Trigger Alerts
```

### 3. User Views Listings

```
User → API
    ↓
Check Cache (Redis)
    ↓ (cache miss)
Query Database
    ↓
Store in Cache
    ↓
Return to User
```

---

## Security Architecture

### Authentication Flow

```
1. User submits credentials
   ↓
2. API validates password (bcrypt)
   ↓
3. Generate JWT token (HS256)
   ↓
4. Return token to user
   ↓
5. User includes token in subsequent requests
   ↓
6. API validates token signature and expiration
   ↓
7. Extract user ID from token
   ↓
8. Load user from database
   ↓
9. Check user permissions
   ↓
10. Process request
```

### Security Layers

1. **Network Layer:**
   - TLS 1.3 for all connections
   - VPC isolation
   - Security groups
   - WAF rules

2. **Application Layer:**
   - JWT authentication
   - RBAC (Role-Based Access Control)
   - Input validation
   - SQL injection prevention (ORM)
   - XSS prevention
   - CSRF protection

3. **Data Layer:**
   - Encrypted at rest
   - Encrypted in transit
   - Regular backups
   - Access auditing

---

## Scalability

### Horizontal Scaling

**API Servers:**
```
Load Balancer
    ├── API Server 1
    ├── API Server 2
    ├── API Server 3 (auto-scale)
    └── API Server N (auto-scale)
```

**Celery Workers:**
```
Task Queue
    ├── Worker 1 (scraping)
    ├── Worker 2 (scraping)
    ├── Worker 3 (alerts)
    └── Worker N (auto-scale)
```

**Database:**
```
Primary (Read/Write)
    ├── Replica 1 (Read)
    ├── Replica 2 (Read)
    └── Replica N (Read)
```

### Performance Optimizations

1. **Caching Strategy:**
   - Application-level caching (Redis)
   - Database query caching
   - HTTP caching headers
   - CDN for static assets

2. **Database Optimization:**
   - Proper indexing
   - Connection pooling
   - Query optimization
   - Partitioning (future)

3. **Async Processing:**
   - Background tasks (Celery)
   - Non-blocking I/O (async/await)
   - Batch processing

---

## Monitoring & Observability

### Metrics Collection

```
Application
    ↓
Prometheus Exporter
    ↓
Prometheus Server
    ↓
Grafana Dashboards
```

**Key Metrics:**
- Request rate (req/sec)
- Response time (p50, p95, p99)
- Error rate (%)
- Queue depth
- Database connections
- Cache hit rate

### Logging

```
Application Logs
    ↓
Structured JSON
    ↓
Log Aggregation (ELK/CloudWatch)
    ↓
Search & Analysis
```

### Error Tracking

```
Application Error
    ↓
Sentry SDK
    ↓
Sentry Platform
    ↓
Alert & Notification
```

---

## Disaster Recovery

### Backup Strategy

**Database:**
- Automated daily backups (full)
- Point-in-time recovery (WAL archiving)
- Retention: 30 days
- Geographic replication

**Redis:**
- RDB snapshots (hourly)
- AOF append-only file
- Retention: 7 days

### Recovery Procedures

**RTO (Recovery Time Objective):** 1 hour
**RPO (Recovery Point Objective):** 5 minutes

**Failure Scenarios:**

1. **API Server Failure:**
   - Auto-healing (Kubernetes restarts pod)
   - Load balancer routes to healthy instances
   - Impact: Minimal

2. **Database Failure:**
   - Automatic failover to replica
   - Promote replica to primary
   - Impact: < 5 minutes downtime

3. **Complete Region Failure:**
   - Failover to backup region
   - Restore from backups
   - Impact: 30-60 minutes

---

## Deployment Architecture

### Kubernetes Cluster

```
Namespace: production
    ├── Deployment: api (4 replicas)
    ├── Deployment: celery-worker (4 replicas)
    ├── Deployment: celery-beat (1 replica)
    ├── StatefulSet: postgres (1 primary, 2 replicas)
    ├── StatefulSet: redis (1 primary, 1 replica)
    ├── Service: api-service
    ├── Ingress: api-ingress
    └── ConfigMap: app-config
```

### CI/CD Pipeline

```
Code Push (GitHub)
    ↓
Run Tests (GitHub Actions)
    ↓
Build Docker Image
    ↓
Push to Registry
    ↓
Deploy to Staging
    ↓
Run Integration Tests
    ↓
Manual Approval
    ↓
Deploy to Production
    ↓
Health Check
    ↓
Rollback if Failed
```

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| API | FastAPI + Uvicorn | Web framework |
| Database | PostgreSQL 16 | Primary datastore |
| Cache | Redis 7 | Caching & queue |
| Task Queue | Celery 5.3 | Async tasks |
| Web Server | Nginx | Reverse proxy |
| Container | Docker | Containerization |
| Orchestration | Kubernetes | Container orchestration |
| Monitoring | Prometheus + Grafana | Metrics & dashboards |
| Logging | ELK Stack | Log aggregation |
| Error Tracking | Sentry | Error monitoring |
| CI/CD | GitHub Actions | Automation |

---

## Future Enhancements

1. **GraphQL API** - More flexible querying
2. **WebSocket Support** - Real-time updates
3. **Multi-Region Deployment** - Global availability
4. **Machine Learning** - Price prediction, deal scoring
5. **Search Elasticsearch** - Full-text search
6. **CDN Integration** - Faster content delivery
7. **Microservices** - Split into smaller services

---

**Last Updated**: 2024-10-28
**Architecture Version**: 1.0
**Review Cycle**: Quarterly
