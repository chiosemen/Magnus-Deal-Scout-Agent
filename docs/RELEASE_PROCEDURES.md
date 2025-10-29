# Release Procedures

## Overview

This document outlines the standardized procedures for releasing new versions of the Magnus Deal Scout Agent to production.

## Release Schedule

- **Regular Releases**: Every 2 weeks (Tuesday, 10:00 AM UTC)
- **Hotfix Releases**: As needed, typically within 4 hours
- **Security Patches**: Immediate, with emergency change process

## Pre-Release Checklist

### 1 Week Before Release

- [ ] Code freeze for non-critical features
- [ ] Complete all automated tests
- [ ] Update CHANGELOG.md
- [ ] Review and merge all approved PRs
- [ ] Create release branch from `main`

### 3 Days Before Release

- [ ] Deploy to staging environment
- [ ] Run full regression test suite
- [ ] Performance testing
- [ ] Security scan
- [ ] Database migration dry-run

### 1 Day Before Release

- [ ] Final smoke testing on staging
- [ ] Notify stakeholders of upcoming release
- [ ] Prepare rollback plan
- [ ] Review monitoring dashboards
- [ ] Ensure on-call engineer is available

### Release Day

- [ ] Final go/no-go decision (9:00 AM UTC)
- [ ] Create backup of production database
- [ ] Verify all dependencies are available
- [ ] Prepare incident response team

---

## Release Types

### Regular Release (Planned)

**Purpose**: New features, improvements, non-critical bug fixes

**Process:**
1. Create release candidate
2. Deploy to staging
3. Run test suite
4. Deploy to production
5. Monitor for 2 hours
6. Mark release as stable

**Approval Required**: Team Lead + 1 Engineer Review

---

### Hotfix Release (Urgent)

**Purpose**: Critical bugs, security patches, data integrity issues

**Process:**
1. Create hotfix branch from `main`
2. Implement fix
3. Fast-track testing
4. Deploy directly to production
5. Backport to development

**Approval Required**: On-Call Engineer or Team Lead

---

### Emergency Release (Critical)

**Purpose**: Service outage, security breach, data loss

**Process:**
1. Implement fix on hotfix branch
2. Minimal testing (smoke test only)
3. Immediate deployment
4. Post-deployment validation
5. Full post-mortem

**Approval Required**: Engineering Manager or CTO

---

## Deployment Process

### Step 1: Prepare Release

```bash
# Checkout main branch
git checkout main
git pull origin main

# Create release branch
git checkout -b release/v1.2.3

# Update version numbers
# - backend/app/__init__.py
# - backend/app/config.py
# - package.json (if applicable)

# Update CHANGELOG.md
vim CHANGELOG.md

# Commit version bump
git add .
git commit -m "chore: bump version to 1.2.3"
git push origin release/v1.2.3
```

### Step 2: Run Tests

```bash
# Run full test suite
cd backend
pytest -v --cov=app tests/

# Run linting
black app tests --check
isort app tests --check
flake8 app tests
mypy app

# Run security scan
bandit -r app

# Check dependencies for vulnerabilities
pip-audit
```

### Step 3: Build and Tag

```bash
# Build Docker image
docker build -t deal-scout-api:1.2.3 .
docker tag deal-scout-api:1.2.3 deal-scout-api:latest

# Tag release in git
git tag -a v1.2.3 -m "Release version 1.2.3"
git push origin v1.2.3

# Push Docker images
docker push deal-scout-api:1.2.3
docker push deal-scout-api:latest
```

### Step 4: Deploy to Staging

```bash
# Update staging environment
kubectl config use-context staging
kubectl set image deployment/deal-scout-api api=deal-scout-api:1.2.3

# Wait for rollout
kubectl rollout status deployment/deal-scout-api

# Run database migrations
kubectl exec -it deployment/deal-scout-api -- alembic upgrade head

# Verify staging health
curl https://staging.dealscout.com/health
curl https://staging.dealscout.com/api/v1/monitoring/health/detailed
```

### Step 5: Staging Validation

Run smoke tests:
```bash
# API endpoint tests
pytest tests/integration/ --env=staging

# Manual verification
# - Register new user
# - Create search
# - Verify scraping works
# - Check alerts
# - View dashboard
```

Performance tests:
```bash
# Load test
locust -f tests/load_test.py --host=https://staging.dealscout.com

# Ensure:
# - p95 response time < 500ms
# - Error rate < 0.5%
# - Throughput >= production baseline
```

### Step 6: Production Deployment

```bash
# Switch to production context
kubectl config use-context production

# Create database backup
pg_dump -h production-db.dealscout.com -U postgres deal_scout > backup_$(date +%Y%m%d_%H%M%S).sql

# Deploy new version (rolling update)
kubectl set image deployment/deal-scout-api api=deal-scout-api:1.2.3

# Watch rollout
kubectl rollout status deployment/deal-scout-api

# Run database migrations
kubectl exec -it deployment/deal-scout-api -- alembic upgrade head

# Verify production health
curl https://api.dealscout.com/health
```

### Step 7: Post-Deployment Validation

**Immediate Checks (0-15 minutes):**
```bash
# Check pod status
kubectl get pods -l app=deal-scout-api

# Check logs for errors
kubectl logs -l app=deal-scout-api --since=10m | grep ERROR

# Verify metrics
curl https://api.dealscout.com/api/v1/monitoring/metrics | grep http_requests_total

# Test critical paths
./scripts/smoke_test_production.sh
```

**Extended Monitoring (15-120 minutes):**
- Monitor Grafana dashboards
- Watch Sentry for new errors
- Check Celery queue depths
- Review user feedback channels
- Monitor response times

### Step 8: Announcement

```bash
# Merge release branch to main
git checkout main
git merge release/v1.2.3
git push origin main

# Create GitHub release
gh release create v1.2.3 \
  --title "Release 1.2.3" \
  --notes-file CHANGELOG.md

# Announce in Slack
# Post to #releases channel
# Post to #engineering channel
# Update status page
```

---

## Rollback Procedures

### When to Rollback

Rollback immediately if:
- Error rate > 5%
- Critical feature broken
- Data corruption detected
- Security vulnerability introduced
- Performance degraded > 50%

### Rollback Process

```bash
# Method 1: Rollback to previous deployment
kubectl rollout undo deployment/deal-scout-api

# Method 2: Rollback to specific version
kubectl rollout undo deployment/deal-scout-api --to-revision=<revision-number>

# Method 3: Deploy previous tag
kubectl set image deployment/deal-scout-api api=deal-scout-api:1.2.2

# Verify rollback
kubectl rollout status deployment/deal-scout-api
curl https://api.dealscout.com/health
```

### Database Rollback

```bash
# If migrations were run, rollback database
kubectl exec -it deployment/deal-scout-api -- alembic downgrade -1

# If data corruption, restore from backup
psql -h production-db.dealscout.com -U postgres deal_scout < backup_20241028_100000.sql
```

### Post-Rollback

1. **Investigate root cause**
   - Review logs
   - Check Sentry errors
   - Analyze metrics

2. **Create incident ticket**
   - Document issue
   - Assign to developer
   - Set priority

3. **Fix and redeploy**
   - Create hotfix branch
   - Implement fix
   - Fast-track testing
   - Redeploy

---

## Database Migrations

### Creating Migrations

```bash
# Auto-generate migration
alembic revision --autogenerate -m "Add user preferences table"

# Review generated migration
vim alembic/versions/<revision>_add_user_preferences_table.py

# Test migration locally
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

### Migration Best Practices

1. **Backward Compatible**
   - Add columns as nullable first
   - Backfill data before making required
   - Drop columns in separate release

2. **Test Thoroughly**
   - Test on copy of production data
   - Verify rollback works
   - Check performance impact

3. **Large Tables**
   - Avoid table locks
   - Use online schema changes
   - Consider batched updates

4. **Data Migrations**
   - Separate schema and data changes
   - Make idempotent
   - Add progress logging

### Example: Adding Column

**Release 1:**
```python
# Add column as nullable
def upgrade():
    op.add_column('users', sa.Column('preferences', sa.JSON(), nullable=True))

def downgrade():
    op.drop_column('users', 'preferences')
```

**Release 2:**
```python
# Backfill data
def upgrade():
    op.execute("UPDATE users SET preferences = '{}' WHERE preferences IS NULL")

def downgrade():
    op.execute("UPDATE users SET preferences = NULL")
```

**Release 3:**
```python
# Make required
def upgrade():
    op.alter_column('users', 'preferences', nullable=False)

def downgrade():
    op.alter_column('users', 'preferences', nullable=True)
```

---

## Monitoring During Release

### Key Metrics to Watch

**API Metrics:**
```
http_requests_total
http_request_duration_seconds
http_errors_total
```

**Database Metrics:**
```
database_connections_total
database_query_duration_seconds
database_errors_total
```

**Celery Metrics:**
```
celery_tasks_total{status="success"}
celery_tasks_total{status="failed"}
celery_queue_depth
```

### Alert Thresholds During Release

Stricter thresholds during release window:

| Metric | Normal | During Release |
|--------|--------|---------------|
| Error Rate | < 1% | < 0.5% |
| Response Time (p95) | < 1s | < 800ms |
| Queue Depth | < 1000 | < 500 |

### Monitoring Timeline

```
T+0:  Deploy starts
T+5:  First health checks
T+10: All pods rolled out
T+15: Initial metrics review
T+30: Extended metrics review
T+60: Full system check
T+120: Release declared stable
```

---

## Communication Plan

### Before Release
**Audience: Internal Engineering Team**
- Slack: #releases channel
- Email: engineering@dealscout.com
- Message: Release schedule, what's included, key changes

### During Release
**Audience: Internal Operations Team**
- Slack: #ops channel
- Status: Deploying, health checks, any issues

### After Release
**Audience: All Stakeholders**
- Slack: #general, #customer-success
- Email: all@dealscout.com
- Message: Release summary, new features, known issues

### If Issues Occur
**Audience: Users (via status page)**
- Status Page: https://status.dealscout.com
- Twitter: @DealScoutStatus
- In-app banner

---

## Post-Release Activities

### Release Retrospective (Within 1 Week)

**Agenda:**
1. What went well?
2. What went wrong?
3. What can we improve?
4. Action items

**Participants:**
- Release engineer
- Team lead
- QA engineer
- Product manager (for major releases)

### Documentation Updates

- [ ] Update API documentation
- [ ] Update user guides
- [ ] Update changelog
- [ ] Update runbook (if procedures changed)

### Metrics Review

- [ ] Compare pre/post release metrics
- [ ] Identify performance regressions
- [ ] Track feature adoption
- [ ] Monitor user feedback

---

## Tools & Scripts

### Deployment Scripts

```bash
# scripts/deploy.sh
#!/bin/bash
set -e

VERSION=$1
ENVIRONMENT=$2

echo "Deploying version $VERSION to $ENVIRONMENT..."

# Validate inputs
if [ -z "$VERSION" ] || [ -z "$ENVIRONMENT" ]; then
    echo "Usage: ./deploy.sh <version> <staging|production>"
    exit 1
fi

# Switch context
kubectl config use-context $ENVIRONMENT

# Deploy
kubectl set image deployment/deal-scout-api api=deal-scout-api:$VERSION

# Wait for rollout
kubectl rollout status deployment/deal-scout-api

# Run health check
./scripts/health_check.sh $ENVIRONMENT

echo "Deployment complete!"
```

### Health Check Script

```bash
# scripts/health_check.sh
#!/bin/bash

ENVIRONMENT=$1
if [ "$ENVIRONMENT" == "staging" ]; then
    URL="https://staging.dealscout.com"
else
    URL="https://api.dealscout.com"
fi

echo "Checking health of $URL..."

# Basic health check
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $URL/health)
if [ "$HTTP_CODE" != "200" ]; then
    echo "❌ Health check failed: HTTP $HTTP_CODE"
    exit 1
fi

echo "✓ Health check passed"

# Detailed health check
curl -s $URL/api/v1/monitoring/health/detailed | jq .

echo "✓ All checks passed"
```

### Smoke Test Script

```bash
# scripts/smoke_test_production.sh
#!/bin/bash
set -e

BASE_URL="https://api.dealscout.com"

echo "Running production smoke tests..."

# Test 1: Health check
echo "Test 1: Health check"
curl -f $BASE_URL/health > /dev/null

# Test 2: Authentication
echo "Test 2: Register and login"
# ... (register user, login, get token)

# Test 3: Core functionality
echo "Test 3: Create search"
# ... (create search with token)

echo "Test 4: Retrieve listings"
# ... (get listings)

echo "✓ All smoke tests passed"
```

---

## Security Considerations

### Pre-Release Security Checklist

- [ ] Dependencies updated to latest secure versions
- [ ] Security scan passed (no high/critical vulnerabilities)
- [ ] Secrets not committed to repository
- [ ] API keys rotated if compromised
- [ ] SSL certificates valid
- [ ] Security headers configured
- [ ] CORS properly configured

### Post-Release Security

- [ ] Monitor Sentry for security-related errors
- [ ] Review access logs for anomalies
- [ ] Check for unusual API usage patterns
- [ ] Verify no sensitive data exposed in logs

---

## Compliance & Audit

### Audit Trail

Every release must include:
1. Git commit SHA
2. Docker image tag
3. Deployment timestamp
4. Approver(s)
5. Rollback procedure used (if any)

**Stored in**: `releases.log` and incident management system

### Compliance Requirements

For regulated features (payments, user data):
- [ ] Security review completed
- [ ] Privacy impact assessment
- [ ] Data retention policies updated
- [ ] User notifications sent (if required)
- [ ] Compliance team approval

---

## Appendix

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **Major** (1.0.0): Breaking changes
- **Minor** (1.1.0): New features, backwards compatible
- **Patch** (1.1.1): Bug fixes

### Release Notes Template

```markdown
# Release v1.2.3

**Release Date**: 2024-10-28
**Type**: Regular Release

## Features
- Added marketplace filtering to dashboard
- Implemented email preferences

## Improvements
- Reduced API response time by 20%
- Enhanced error messages

## Bug Fixes
- Fixed search pagination issue #123
- Resolved alert delivery delay #145

## Technical
- Upgraded FastAPI to 0.109.0
- Added Prometheus metrics
- Database migration: add_user_preferences

## Breaking Changes
None

## Known Issues
- Occasional timeout on Facebook scraping (investigating)

## Rollback Notes
Rollback safe. Database migration is reversible.
```

---

**Last Updated**: 2024-10-28
**Owner**: Platform Engineering Team
**Review Cycle**: Quarterly
