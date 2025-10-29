# Next Steps for Magnus Deal Scout Agent

## Immediate Actions (Do This First)

### 1. Test the Setup ✅

```bash
cd backend

# Verify structure
ls -la app/
ls -la tests/
ls -la alembic/

# Check imports (should show no errors)
python -c "from app.main import app; print('✓ Imports work')"
python -c "from app.config import settings; print('✓ Config works')"
python -c "from app.models import User; print('✓ Models work')"
```

### 2. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# REQUIRED: Change these values in .env
# SECRET_KEY=<generate-a-strong-random-key>
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/deal_scout
# REDIS_URL=redis://localhost:6379/0
# CELERY_BROKER_URL=redis://localhost:6379/0
# CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Generate a secure SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Start with Docker (Easiest)

```bash
# Build and start all services
docker-compose up --build

# In another terminal, check services
docker-compose ps

# View logs
docker-compose logs -f api
docker-compose logs -f celery_worker

# Create initial database migration
docker-compose exec api alembic revision --autogenerate -m "Initial schema"
docker-compose exec api alembic upgrade head
```

### 4. Verify Everything Works

```bash
# Test health endpoint
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs

# View Flower (Celery monitoring)
open http://localhost:5555

# Register a test user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","full_name":"Test User"}'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass123"
```

## Priority Implementations

### High Priority (Week 1-2)

1. **Complete Email Verification**
   - File: `app/api/v1/auth.py`
   - Implement actual email sending with verification tokens
   - Add email templates
   - Test with real SMTP server

2. **Implement Password Reset**
   - File: `app/api/v1/auth.py`
   - Generate reset tokens
   - Send reset emails
   - Create reset endpoint

3. **Add Rate Limiting**
   - Install: `pip install slowapi`
   - Add to `app/main.py`
   - Configure limits per endpoint
   - Test with load testing tools

4. **Implement Alert Sending**
   - File: `app/tasks/alerts.py`
   - Email alerts (SMTP)
   - SMS alerts (Twilio)
   - Webhook alerts
   - Test each channel

5. **Run Initial Tests**
   ```bash
   # Install test dependencies
   pip install -r requirements.txt

   # Run tests
   pytest

   # Check coverage
   pytest --cov=app tests/

   # Should see basic tests passing
   ```

### Medium Priority (Week 3-4)

6. **Integrate Facebook Scraper**
   - Move `facebook_scraper.py` to `app/agents/`
   - Integrate with Celery tasks
   - Handle authentication
   - Test scraping

7. **Add Admin Endpoints**
   - Create `app/api/v1/admin.py`
   - User management
   - System statistics
   - Task monitoring
   - Requires superuser role

8. **Implement Subscription Logic**
   - Add Stripe integration
   - Enforce tier limits
   - Billing webhooks
   - Subscription management UI

9. **Set Up Sentry**
   ```bash
   pip install sentry-sdk
   ```
   - Add to `app/main.py`
   - Configure DSN in `.env`
   - Test error reporting

10. **Add More Tests**
    - Celery task tests
    - Agent/scraper tests
    - Integration tests
    - E2E tests

### Lower Priority (Week 5+)

11. **Performance Optimization**
    - Add caching with Redis
    - Optimize database queries
    - Add database indexes
    - Profile and benchmark

12. **Advanced Features**
    - Search analytics
    - Price history tracking
    - Listing recommendations
    - Export functionality

13. **Documentation**
    - API documentation
    - Architecture diagrams
    - Deployment guides
    - User manual

## Security Hardening

### Immediate Security Tasks

1. **Secret Management**
   ```bash
   # Never commit .env file
   # Use AWS Secrets Manager / Vault in production
   # Rotate keys regularly
   ```

2. **CORS Configuration**
   - File: `app/main.py`
   - Change from `["*"]` to specific domains
   - Test from frontend

3. **TrustedHost Middleware**
   - File: `app/main.py`
   - Already fixed to use CORS origins
   - Add production domains to .env

4. **Input Validation**
   - Review all Pydantic schemas
   - Add sanitization for user inputs
   - Test with malicious payloads

5. **SQL Injection Prevention**
   - Already handled by SQLAlchemy ORM
   - Never use raw SQL without parameters
   - Add query auditing

6. **API Key Security**
   - Rotate marketplace API keys
   - Store in environment variables
   - Use minimal scopes
   - Monitor usage

## Code Quality Setup

### Linting & Formatting

```bash
# Install development tools
pip install black isort flake8 mypy

# Format code
black app tests
isort app tests

# Lint
flake8 app tests

# Type check
mypy app
```

### Pre-commit Hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
```

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

### CI/CD with GitHub Actions

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        pytest --cov=app tests/
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Deployment Preparation

### Production Checklist

```bash
# 1. Environment Configuration
□ DEBUG=False in production .env
□ Strong SECRET_KEY (32+ characters)
□ Production database credentials
□ Managed Redis instance
□ Valid SSL certificates
□ CORS origins configured
□ Sentry DSN configured

# 2. Database
□ Run migrations: alembic upgrade head
□ Set up backups
□ Configure connection pooling
□ Add monitoring

# 3. Security
□ HTTPS enforced
□ Rate limiting enabled
□ API keys rotated
□ Secrets in vault
□ CORS properly configured
□ TrustedHost configured

# 4. Monitoring
□ Sentry error tracking
□ Application logs
□ Database logs
□ Celery task monitoring
□ Uptime monitoring

# 5. Performance
□ Redis caching enabled
□ Database indexes created
□ Static files served via CDN
□ Load balancer configured
□ Auto-scaling configured
```

### Deployment Options

**Option 1: Railway** (Easiest)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize
railway init

# Deploy
railway up
```

**Option 2: AWS ECS**
```bash
# Build and push Docker image
docker build -t deal-scout-api .
docker tag deal-scout-api:latest <ECR_URL>
docker push <ECR_URL>

# Deploy with ECS task definition
# Configure RDS PostgreSQL
# Configure ElastiCache Redis
# Set up ALB
```

**Option 3: Kubernetes**
```bash
# Create k8s manifests
kubectl apply -f k8s/

# Scale workers
kubectl scale deployment celery-worker --replicas=3
```

## Troubleshooting Common Issues

### Import Errors

```bash
# If you see "No module named 'app'"
# Make sure you're in the backend directory
cd backend

# Add to PYTHONPATH if needed
export PYTHONPATH="${PYTHONPATH}:/path/to/backend"
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
docker exec -it deal_scout_db psql -U postgres -d deal_scout

# View logs
docker-compose logs postgres
```

### Celery Not Processing Tasks

```bash
# Check Redis connection
docker exec -it deal_scout_redis redis-cli ping

# View worker logs
docker-compose logs celery_worker

# Check Flower dashboard
open http://localhost:5555
```

### Tests Failing

```bash
# Clear test database
rm test.db

# Run single test
pytest tests/test_api.py::TestHealth::test_health_check -v

# Check test database
pytest tests/test_api.py -v -s
```

## Resources

### Documentation
- FastAPI: https://fastapi.tiangolo.com
- SQLAlchemy: https://docs.sqlalchemy.org
- Celery: https://docs.celeryproject.org
- Pydantic: https://docs.pydantic.dev
- Alembic: https://alembic.sqlalchemy.org

### Tools
- Postman: API testing
- pgAdmin: Database management
- RedisInsight: Redis management
- Flower: Celery monitoring
- Sentry: Error tracking

### Community
- FastAPI Discord
- Python Reddit
- Stack Overflow
- GitHub Discussions

## Success Criteria

✅ All services start with `docker-compose up`
✅ Health endpoint returns 200
✅ Can register and login users
✅ Can create searches
✅ Tests pass
✅ API documentation accessible
✅ Celery tasks execute
✅ No security warnings

## Timeline

**Week 1**: Setup, basic functionality, initial tests
**Week 2**: Complete TODOs, security hardening
**Week 3**: Advanced features, performance optimization
**Week 4**: Production preparation, deployment
**Week 5+**: Monitoring, maintenance, new features

## Questions?

Review the following files:
- `backend/README.md` - Comprehensive guide
- `RECONSTITUTION_SUMMARY.md` - What was built
- `backend/.env.example` - Configuration options
- `backend/app/main.py` - Application entry point
- `backend/docker-compose.yml` - Service configuration

Good luck with your Magnus Deal Scout Agent! 🚀
