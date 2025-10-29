# Magnus Deal Scout Agent - Backend

A FastAPI-based marketplace aggregation and monitoring platform that scrapes multiple marketplaces (eBay, Facebook, Gumtree, Craigslist) and alerts users to new deals.

## Features

- **Multi-Marketplace Scraping**: eBay, Facebook Marketplace, Gumtree, Craigslist
- **Real-time Alerts**: Email, SMS, Push notifications, Webhooks
- **Search Management**: Create custom searches with filters
- **User Authentication**: JWT-based authentication
- **Background Tasks**: Celery for async scraping
- **RESTful API**: FastAPI with automatic documentation
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Caching**: Redis for performance
- **Monitoring**: Flower for Celery task monitoring

## Tech Stack

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary database
- **Redis** - Cache and message broker
- **Celery** - Async task queue
- **Pydantic** - Data validation
- **JWT** - Authentication tokens
- **Docker** - Containerization

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 16+
- Redis 7+

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
cd backend

# Create environment file
cp .env.example .env
# Edit .env and set your SECRET_KEY and other variables

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f api
```

**Services will be available at:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Flower (Celery monitoring): http://localhost:5555

### Option 2: Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env file with your configuration

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload
```

**In separate terminals, start:**

```bash
# Celery worker
celery -A app.tasks.celery_app worker -l info

# Celery beat (scheduler)
celery -A app.tasks.celery_app beat -l info

# Flower (optional monitoring)
celery -A app.tasks.celery_app flower
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── api/                 # API endpoints
│   │   ├── deps.py          # Dependencies (auth)
│   │   └── v1/              # API v1 routes
│   │       ├── auth.py
│   │       ├── searches.py
│   │       ├── listings.py
│   │       ├── alerts.py
│   │       └── dashboard.py
│   ├── core/                # Core functionality
│   │   └── security.py      # JWT & password hashing
│   ├── models/              # SQLAlchemy models
│   │   └── __init__.py
│   ├── schemas/             # Pydantic schemas
│   │   └── __init__.py
│   ├── agents/              # Marketplace scrapers
│   │   ├── base.py
│   │   ├── ebay.py
│   │   ├── facebook.py
│   │   ├── gumtree.py
│   │   └── craigslist.py
│   └── tasks/               # Celery tasks
│       ├── celery_app.py
│       ├── scraping.py
│       └── alerts.py
├── tests/                   # Test suite
│   ├── conftest.py
│   └── test_api.py
├── alembic/                 # Database migrations
│   ├── env.py
│   └── versions/
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── docker-compose.yml      # Docker services
├── Dockerfile              # Docker build
└── README.md               # This file
```

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# View history
alembic history
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

## API Usage Examples

### Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "John Doe"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepassword"
```

### Create a Search

```bash
curl -X POST "http://localhost:8000/api/v1/searches" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "iPhone Deals",
    "keywords": "iPhone 13",
    "marketplaces": ["ebay", "gumtree"],
    "min_price": 200,
    "max_price": 600,
    "check_interval_minutes": 60
  }'
```

### Get Recent Listings

```bash
curl "http://localhost:8000/api/v1/listings/recent?hours=24" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Configuration

Key environment variables in `.env`:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/deal_scout

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Secret (CHANGE THIS!)
SECRET_KEY=your-secret-key-here

# CORS
CORS_ORIGINS=http://localhost:3000

# Marketplace API Keys (optional)
EBAY_APP_ID=your-ebay-app-id
FACEBOOK_ACCESS_TOKEN=your-facebook-token
```

## Monitoring

### Flower Dashboard

Access Celery task monitoring at: http://localhost:5555

Features:
- View active/scheduled tasks
- Monitor worker performance
- Inspect task results
- Retry failed tasks

### Logs

```bash
# Docker logs
docker-compose logs -f api
docker-compose logs -f celery_worker

# Check specific service
docker-compose logs -f postgres
docker-compose logs -f redis
```

## Production Deployment

### Security Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=False`
- [ ] Configure proper `CORS_ORIGINS`
- [ ] Use strong database passwords
- [ ] Enable SSL/TLS
- [ ] Set up rate limiting
- [ ] Configure Sentry for error tracking
- [ ] Use environment-specific `.env` files
- [ ] Review and restrict API keys

### Deployment Options

1. **Railway/Render** - Easiest
2. **AWS/GCP/Azure** - More control
3. **Docker + Kubernetes** - Full control

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Connect to database
docker exec -it deal_scout_db psql -U postgres -d deal_scout
```

### Celery Worker Not Processing

```bash
# Check Redis connection
redis-cli ping

# View worker logs
docker-compose logs celery_worker

# Purge all tasks
celery -A app.tasks.celery_app purge
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or change PORT in .env
```

## Contributing

1. Create a feature branch
2. Make changes
3. Write/update tests
4. Run tests: `pytest`
5. Format code: `black app tests`
6. Check types: `mypy app`
7. Submit pull request

## License

MIT License

## Support

- Documentation: See `/docs` folder
- Issues: GitHub Issues
- Email: support@dealscout.com
