# 🚀 DEAL SCOUT BACKEND - QUICK SETUP GUIDE

## 📥 Step 1: Download All Files

You now have **25+ backend files** in `/mnt/user-data/outputs/`.

## 📂 Step 2: Create Project Structure

Create this folder structure on your local machine:

```
deal-scout-backend/
├── .gitignore
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── pytest.ini
├── README.md
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── searches.py
│   │       ├── listings.py
│   │       └── alerts.py (includes dashboard)
│   ├── core/
│   │   ├── __init__.py
│   │   └── security.py
│   ├── agents/
│   │   └── __init__.py (includes all agents)
│   ├── tasks/
│   │   └── __init__.py (includes scraping & alerts)
│   └── utils/
│       └── __init__.py
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
└── tests/
    ├── __init__.py
    └── test_api.py
```

## 🗂️ Step 3: File Mapping Reference

### Root Configuration Files
```
backend-requirements.txt           → requirements.txt
backend-env.example                → .env.example
backend-gitignore.txt              → .gitignore
backend-README.md                  → README.md
backend-docker-files.txt           → Split into 3 files:
  - Dockerfile section             → Dockerfile
  - docker-compose.yml section     → docker-compose.yml
  - .dockerignore section          → .dockerignore
backend-alembic-config.txt         → Split into 3 files:
  - alembic.ini section            → alembic.ini
  - alembic/env.py section         → alembic/env.py
  - script.py.mako section         → alembic/script.py.mako
```

### App Files
```
backend-app-config.py              → app/config.py
backend-app-database.py            → app/database.py
backend-app-main.py                → app/main.py

backend-app-models-all.py          → app/models/__init__.py
backend-app-schemas-all.py         → app/schemas/__init__.py

backend-app-core-security.py       → app/core/security.py
backend-app-celery-tasks.py        → Split into:
  - celery_app section             → app/core/celery_app.py
  - scraping tasks section         → app/tasks/scraping.py
  - alerts tasks section           → app/tasks/alerts.py

backend-app-api-deps.py            → app/api/deps.py
backend-app-api-v1-auth.py         → app/api/v1/auth.py
backend-app-api-v1-searches.py     → app/api/v1/searches.py
backend-app-api-v1-listings.py     → app/api/v1/listings.py
backend-app-api-v1-alerts-dashboard.py → Split into:
  - alerts section                 → app/api/v1/alerts.py
  - dashboard section              → app/api/v1/dashboard.py

backend-app-agents-all.py          → Split into:
  - base.py section                → app/agents/base.py
  - ebay.py section                → app/agents/ebay.py
  - facebook.py section            → app/agents/facebook.py
  - gumtree.py section             → app/agents/gumtree.py
  - craigslist.py section          → app/agents/craigslist.py
  - __init__.py section            → app/agents/__init__.py
```

## 📝 Step 4: Create __init__.py Files

Create empty `__init__.py` files in these directories:
```
touch app/__init__.py
touch app/models/__init__.py (already has content)
touch app/schemas/__init__.py (already has content)
touch app/api/__init__.py
touch app/api/v1/__init__.py
touch app/core/__init__.py
touch app/agents/__init__.py (already has content)
touch app/tasks/__init__.py
touch app/utils/__init__.py
touch tests/__init__.py
```

For `app/api/v1/__init__.py`, add:
```python
# app/api/v1/__init__.py
from . import auth, searches, listings, alerts, dashboard

__all__ = ['auth', 'searches', 'listings', 'alerts', 'dashboard']
```

## ⚙️ Step 5: Setup Environment

```bash
# Create .env from template
cp .env.example .env

# Edit .env with your values
nano .env

# Key values to change:
# - DATABASE_URL
# - REDIS_URL
# - SECRET_KEY (generate with: openssl rand -hex 32)
# - CORS_ORIGINS
```

## 🐳 Step 6: Start with Docker (Easiest)

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f api

# Run migrations
docker-compose exec api alembic upgrade head

# Create first user (optional)
docker-compose exec api python -c "
from app.database import SessionLocal
from app.models import User
from app.core.security import get_password_hash
db = SessionLocal()
user = User(
    email='admin@dealscout.com',
    hashed_password=get_password_hash('admin123'),
    full_name='Admin User',
    is_active=True,
    is_superuser=True
)
db.add(user)
db.commit()
print('Admin user created!')
"
```

## 💻 Step 7: Or Setup Locally

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install --break-system-packages -r requirements.txt

# Setup database
createdb dealscout
alembic upgrade head

# Run services (in separate terminals)
uvicorn app.main:app --reload                    # API
celery -A app.core.celery_app worker -l info     # Worker
celery -A app.core.celery_app beat -l info       # Scheduler
celery -A app.core.celery_app flower             # Monitor
```

## ✅ Step 8: Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# Check API docs
open http://localhost:8000/docs

# Check Flower
open http://localhost:5555

# Test authentication
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'
```

## 🎯 Quick Test Checklist

- [ ] API responds at http://localhost:8000
- [ ] Swagger docs load at /docs
- [ ] Can register a user
- [ ] Can login and get token
- [ ] PostgreSQL connection works
- [ ] Redis connection works
- [ ] Celery worker is running
- [ ] Celery beat is running
- [ ] Flower dashboard loads

## 🗄️ Database Commands

```bash
# Create migration
alembic revision --autogenerate -m "your message"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View current version
alembic current

# View history
alembic history --verbose
```

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/

# Specific test
pytest tests/test_api.py -v
```

## 🐛 Common Issues

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --port 8001
```

### Database Connection Error
```bash
# Check PostgreSQL is running
pg_isready

# Check connection
psql -U dealscout -h localhost

# Reset database
dropdb dealscout
createdb dealscout
alembic upgrade head
```

### Celery Not Working
```bash
# Check Redis
redis-cli ping

# Check worker
celery -A app.core.celery_app inspect active

# Restart with debug
celery -A app.core.celery_app worker -l debug
```

## 📤 Step 9: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: Deal Scout backend"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/deal-scout-backend.git
git push -u origin main
```

## 🎉 Success Indicators

When everything is working:
1. ✅ API returns JSON at http://localhost:8000
2. ✅ Swagger UI loads with all endpoints
3. ✅ Can create user and login
4. ✅ Celery worker shows "ready" in logs
5. ✅ Flower shows active workers
6. ✅ Database has all tables

---

## 📋 FILE MANIFEST

### Generated Files (25 files)

**Configuration (6 files):**
- backend-requirements.txt
- backend-env.example
- backend-gitignore.txt
- backend-docker-files.txt (3 in 1)
- backend-alembic-config.txt (3 in 1)
- backend-README.md

**Core App (4 files):**
- backend-app-config.py
- backend-app-database.py
- backend-app-main.py
- backend-app-core-security.py

**Models & Schemas (2 files):**
- backend-app-models-all.py
- backend-app-schemas-all.py

**API Routes (6 files):**
- backend-app-api-deps.py
- backend-app-api-v1-auth.py
- backend-app-api-v1-searches.py
- backend-app-api-v1-listings.py
- backend-app-api-v1-alerts-dashboard.py

**Celery & Agents (2 files):**
- backend-app-celery-tasks.py (3 in 1)
- backend-app-agents-all.py (6 in 1)

**Documentation (1 file):**
- backend-README.md

**Actual Python Files: ~45+**
(Many generated files contain multiple components)

---

**You're all set! Happy coding! 🚀**
