# Deal Scout - Backend API

FastAPI-based backend API for Deal Scout marketplace aggregation platform. Features include user authentication, search management, background scraping tasks, and real-time notifications.

## 🚀 Tech Stack

- **Framework:** FastAPI 0.109.0
- **Database:** PostgreSQL 15+ with SQLAlchemy 2.0
- **Cache/Queue:** Redis 7+
- **Background Jobs:** Celery 5.3 with Flower monitoring
- **Authentication:** JWT with python-jose
- **Web Scraping:** httpx, BeautifulSoup4, Selenium, Playwright
- **Migrations:** Alembic 1.13
- **Testing:** pytest, pytest-asyncio

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration with Pydantic Settings
│   ├── database.py             # Database connection & session
│   ├── models/                 # SQLAlchemy database models
│   │   └── __init__.py         # User, Search, Listing, Alert, TaskLog
│   ├── schemas/                # Pydantic schemas for validation
│   │   └── __init__.py         # Request/response models
│   ├── api/                    # API endpoints
│   │   ├── deps.py             # Dependencies (auth, db)
│   │   └── v1/                 # API version 1
│   │       ├── auth.py         # Authentication endpoints
│   │       ├── searches.py     # Search CRUD endpoints
│   │       ├── listings.py     # Listing endpoints
│   │       ├── alerts.py       # Alert management
│   │       └── dashboard.py    # Dashboard statistics
│   ├── core/                   # Core functionality
│   │   ├── security.py         # JWT & password utilities
│   │   └── celery_app.py       # Celery configuration
│   ├── agents/                 # Marketplace scrapers
│   │   ├── base.py             # Base scraper class
│   │   ├── ebay.py             # eBay scraper
│   │   ├── facebook.py         # Facebook Marketplace
│   │   ├── gumtree.py          # Gumtree scraper
│   │   └── craigslist.py       # Craigslist scraper
│   ├── tasks/                  # Celery background tasks
│   │   ├── scraping.py         # Scraping tasks
│   │   └── alerts.py           # Alert notification tasks
│   └── utils/                  # Utility functions
│       └── helpers.py          # Helper functions
├── alembic/                    # Database migrations
│   ├── env.py                  # Alembic environment
│   ├── script.py.mako          # Migration template
│   └── versions/               # Migration files
├── tests/                      # Test suite
│   └── test_api.py             # API tests
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── Dockerfile                  # Docker container definition
├── docker-compose.yml          # Multi-container setup
├── alembic.ini                 # Alembic configuration
└── README.md                   # This file
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- (Optional) Docker & Docker Compose

### Option 1: Local Development

1. **Create virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**

```bash
pip install --break-system-packages -r requirements.txt
```

3. **Setup environment variables:**

```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Setup database:**

```bash
# Create database
createdb dealscout

# Run migrations
alembic upgrade head
```

5. **Run development server:**

```bash
# API Server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Celery Worker (separate terminal)
celery -A app.core.celery_app worker --loglevel=info

# Celery Beat (separate terminal)
celery -A app.core.celery_app beat --loglevel=info

# Flower Monitoring (separate terminal)
celery -A app.core.celery_app flower --port=5555
```

### Option 2: Docker Compose (Recommended)

1. **Setup environment:**

```bash
cp .env.example .env
# Edit .env with your configuration
```

2. **Start all services:**

```bash
docker-compose up -d
```

3. **Run migrations:**

```bash
docker-compose exec api alembic upgrade head
```

4. **View logs:**

```bash
docker-compose logs -f api
docker-compose logs -f celery-worker
```

## 📊 Services

When running with Docker Compose:

- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Flower:** http://localhost:5555
- **PostgreSQL:** localhost:5432
- **Redis:** localhost:6379

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Register:** `POST /api/v1/auth/register`
2. **Login:** `POST /api/v1/auth/login` (returns access_token)
3. **Use token:** Add header `Authorization: Bearer {access_token}`

## 📚 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Create new user account
- `POST /api/v1/auth/login` - Login and get access token
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/refresh` - Refresh access token

### Searches
- `GET /api/v1/searches` - List all searches
- `POST /api/v1/searches` - Create new search
- `GET /api/v1/searches/{id}` - Get search details
- `PUT /api/v1/searches/{id}` - Update search
- `DELETE /api/v1/searches/{id}` - Delete search
- `POST /api/v1/searches/{id}/pause` - Pause search
- `POST /api/v1/searches/{id}/resume` - Resume search
- `POST /api/v1/searches/{id}/trigger` - Trigger immediate search
- `GET /api/v1/searches/{id}/stats` - Get search statistics

### Listings
- `GET /api/v1/listings` - List all listings (with filters)
- `GET /api/v1/listings/recent` - Get recent listings
- `GET /api/v1/listings/saved` - Get saved listings
- `GET /api/v1/listings/{id}` - Get listing details
- `POST /api/v1/listings/{id}/save` - Save/bookmark listing
- `DELETE /api/v1/listings/{id}/save` - Unsave listing
- `GET /api/v1/listings/export/{search_id}` - Export listings

### Alerts
- `GET /api/v1/alerts` - List all alerts
- `POST /api/v1/alerts` - Create new alert
- `PUT /api/v1/alerts/{id}` - Update alert
- `DELETE /api/v1/alerts/{id}` - Delete alert

### Dashboard
- `GET /api/v1/dashboard/stats` - Get dashboard statistics
- `GET /api/v1/dashboard/activity` - Get activity data

## 🔄 Background Tasks

### Celery Workers

The application uses Celery for background job processing:

**Scraping Tasks:**
- `run_search_task(search_id)` - Scrape listings for a search
- `check_active_searches()` - Periodic check for due searches
- `cleanup_old_listings()` - Remove old listings (30+ days)

**Alert Tasks:**
- `trigger_alerts_task(search_id, count)` - Send notifications

### Periodic Schedule

- **Every 15 minutes:** Check active searches
- **Daily at 2 AM:** Cleanup old listings

## 🕷️ Web Scrapers

### Supported Marketplaces

1. **eBay** - Fully implemented
   - Search by keywords
   - Price filtering
   - Image extraction

2. **Gumtree** - Fully implemented
   - Location-based search
   - Price filtering

3. **Craigslist** - Fully implemented
   - Multi-category support
   - Location filtering

4. **Facebook Marketplace** - Placeholder
   - Requires authentication
   - JavaScript rendering needed

### Adding New Scrapers

1. Create new agent in `app/agents/`
2. Inherit from `BaseAgent`
3. Implement `scrape()` method
4. Add to `AGENT_MAP` in `app/tasks/scraping.py`

## 🗄️ Database Migrations

### Create Migration

```bash
alembic revision --autogenerate -m "Description"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

## 🧪 Testing

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

## 📝 Code Quality

```bash
# Format code
black app/

# Sort imports
isort app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

## 🔧 Configuration

Key environment variables:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dealscout

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1

# JWT
SECRET_KEY=your-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
CORS_ORIGINS=http://localhost:3000

# Scraping
SCRAPING_DELAY_SECONDS=2
SCRAPING_MAX_RETRIES=3
```

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure proper `CORS_ORIGINS`
- [ ] Setup SSL/TLS certificates
- [ ] Configure Sentry for error tracking
- [ ] Setup log aggregation
- [ ] Configure database backups
- [ ] Setup monitoring (Flower, Prometheus)
- [ ] Use production ASGI server (Gunicorn with Uvicorn workers)
- [ ] Setup rate limiting
- [ ] Configure firewalls
- [ ] Use environment secrets manager

### Production Command

```bash
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile -
```

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready

# Test connection
psql -U dealscout -d dealscout -h localhost
```

### Redis Connection Issues

```bash
# Check Redis is running
redis-cli ping

# Should return: PONG
```

### Celery Not Processing Tasks

```bash
# Check worker is running
celery -A app.core.celery_app inspect active

# Purge all tasks
celery -A app.core.celery_app purge

# Restart worker
celery -A app.core.celery_app worker --loglevel=debug
```

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Celery Monitoring

Access Flower at http://localhost:5555 to monitor:
- Active workers
- Task history
- Task success/failure rates
- Queue lengths
- Worker resource usage

## 🤝 Contributing

1. Create feature branch
2. Write tests
3. Run linters
4. Submit pull request

## 📄 License

MIT

---

**Built with ❤️ using FastAPI and Python**
