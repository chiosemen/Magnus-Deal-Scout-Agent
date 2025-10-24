# Marketplace Monitor Backend - Development Guide

## Quick Start

### Using Docker Compose (Recommended for Development)

```bash
# Start all services
docker-compose up

# Or run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

Access:
- API: http://localhost:8000
- API Docs: http://localhost:8000/api/v1/docs
- Flower (Celery monitoring): http://localhost:5555

### Manual Setup

1. **Setup environment**:
```bash
chmod +x setup.sh
./setup.sh
```

2. **Start services manually**:

Terminal 1 - API:
```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Celery Worker (Monitoring):
```bash
source venv/bin/activate
celery -A app.workers.celery_app worker -Q marketplace_monitoring -l info -c 4
```

Terminal 3 - Celery Worker (Alerts):
```bash
source venv/bin/activate
celery -A app.workers.celery_app worker -Q alerts -l info -c 2
```

Terminal 4 - Celery Beat (Scheduler):
```bash
source venv/bin/activate
celery -A app.workers.celery_app beat -l info
```

Terminal 5 - Flower (Optional monitoring):
```bash
source venv/bin/activate
celery -A app.workers.celery_app flower
```

## Database Migrations

### Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations:
```bash
alembic upgrade head
```

### Rollback migration:
```bash
alembic downgrade -1
```

### View migration history:
```bash
alembic history
```

## API Testing

### Register a user:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
  }'
```

### Login:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

Save the `access_token` from the response.

### Create a search:
```bash
curl -X POST "http://localhost:8000/api/v1/searches/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Search",
    "description": "Looking for iPhone deals",
    "criteria": {
      "keywords": ["iPhone 13", "iPhone 14"],
      "max_price": 400,
      "exclude_keywords": ["broken", "faulty"],
      "location": "London"
    },
    "marketplaces": ["ebay"],
    "alert_channels": ["email"],
    "check_frequency_minutes": 30
  }'
```

## Architecture Overview

### Components:

1. **FastAPI Application** (`app/main.py`)
   - REST API endpoints
   - Authentication & authorization
   - Request validation with Pydantic

2. **Database Models** (`app/models/`)
   - SQLAlchemy ORM models
   - PostgreSQL for persistent data

3. **Celery Workers** (`app/workers/`)
   - `monitoring_tasks.py`: Polls marketplaces for new listings
   - `alert_tasks.py`: Sends notifications to users
   - Celery Beat: Schedules periodic tasks

4. **Services Layer** (to be implemented in `app/services/`)
   - Business logic
   - Marketplace integrations
   - Helper functions

### Data Flow:

1. User creates a search configuration via API
2. Celery Beat triggers `check_all_active_searches` every 5 minutes
3. For each search, a task is queued to check that specific search
4. Worker fetches listings from marketplaces (eBay API, scraping, etc.)
5. New listings are stored in database
6. Alert tasks are queued for each new listing
7. Alert workers send notifications via email, SMS, webhook, etc.

## Configuration

### Environment Variables:

All configuration is in `.env`. Key variables:

- **Database**: `DATABASE_URL`
- **Redis**: `REDIS_URL`, `CELERY_BROKER_URL`
- **eBay**: `EBAY_APP_ID`, `EBAY_CERT_ID`, `EBAY_DEV_ID`
- **Email**: `SENDGRID_API_KEY`
- **SMS**: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`
- **Payments**: `STRIPE_SECRET_KEY`

### Subscription Tiers:

Defined in `app/api/users.py`:

- **FREE**: 2 searches, 1 marketplace
- **STARTER**: 5 searches, 1 marketplace  
- **PRO**: 25 searches, 3 marketplaces
- **BUSINESS**: Unlimited searches, 4 marketplaces

## Implementing New Marketplaces

To add a new marketplace (e.g., Facebook, Gumtree):

1. Add to `Marketplace` enum in `app/models/__init__.py`
2. Implement search function in `app/workers/monitoring_tasks.py`:
   ```python
   def search_your_marketplace(criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
       # Your implementation
       pass
   ```
3. Add to the marketplace check in `check_search` task
4. Test thoroughly!

## Testing

### Run tests:
```bash
pytest
```

### Run specific test file:
```bash
pytest tests/test_auth.py
```

### Run with coverage:
```bash
pytest --cov=app tests/
```

## Deployment

### Production Checklist:

- [ ] Set `DEBUG=False` in `.env`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure production database (not SQLite)
- [ ] Set up SSL/TLS certificates
- [ ] Configure rate limiting
- [ ] Set up monitoring (Sentry)
- [ ] Use managed Redis (AWS ElastiCache, Redis Cloud)
- [ ] Set up backups
- [ ] Configure CORS for production domain
- [ ] Use production eBay credentials
- [ ] Set up Stripe webhooks
- [ ] Configure CDN for static assets
- [ ] Set up logging aggregation

### Deployment Options:

1. **Railway / Render** (Easiest):
   - Push code to GitHub
   - Connect repository
   - Set environment variables
   - Deploy automatically

2. **AWS / GCP / Azure** (More control):
   - Use ECS/App Engine/App Service for API
   - Use managed PostgreSQL (RDS/Cloud SQL/Azure DB)
   - Use managed Redis (ElastiCache/Memorystore)
   - Configure auto-scaling

3. **Docker + Kubernetes** (Full control):
   - Build Docker images
   - Deploy to Kubernetes cluster
   - Configure horizontal pod autoscaling
   - Set up ingress for load balancing

## Monitoring & Debugging

### View Celery tasks in Flower:
http://localhost:5555

### Check Redis:
```bash
redis-cli
> KEYS *
> GET key_name
```

### Check PostgreSQL:
```bash
psql -h localhost -U postgres -d marketplace_monitor
\dt  -- List tables
SELECT * FROM users;
```

### View API logs:
```bash
docker-compose logs -f api
```

### View worker logs:
```bash
docker-compose logs -f celery_worker_monitoring
docker-compose logs -f celery_worker_alerts
```

## Performance Optimization

### Database:
- Add indexes for frequently queried fields
- Use connection pooling
- Consider read replicas for heavy loads

### Caching:
- Cache frequently accessed data in Redis
- Cache marketplace API responses (with TTL)
- Use ETags for HTTP caching

### Background Tasks:
- Scale Celery workers horizontally
- Use different queues for different priorities
- Monitor queue lengths and adjust worker count

## Security Best Practices

- Keep dependencies updated
- Use environment variables for secrets
- Validate all user input
- Rate limit API endpoints
- Use HTTPS in production
- Implement proper CORS policies
- Hash passwords with bcrypt
- Use JWT with short expiration times
- Sanitize data before scraping
- Implement request signing for webhooks

## Troubleshooting

### Workers not processing tasks:
- Check Redis connection
- Verify Celery workers are running
- Check worker logs for errors
- Ensure correct queue names

### eBay API not working:
- Verify API credentials in `.env`
- Check if using correct environment (sandbox vs production)
- Review eBay API rate limits
- Check API compatibility version

### Database migrations failing:
- Check database connection
- Review migration file for errors
- Try running migrations one at a time
- Check for conflicting schema changes

### High memory usage:
- Limit Celery worker concurrency
- Optimize database queries
- Clear old listings periodically
- Use pagination for large result sets

## Support & Resources

- FastAPI Docs: https://fastapi.tiangolo.com
- Celery Docs: https://docs.celeryproject.org
- SQLAlchemy Docs: https://docs.sqlalchemy.org
- eBay API Docs: https://developer.ebay.com
- Stripe API Docs: https://stripe.com/docs/api

## Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Run tests and linting
5. Submit pull request

## License

MIT License
