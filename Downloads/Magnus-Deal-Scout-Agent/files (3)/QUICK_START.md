# ⚡ Quick Start Guide - Get Running in 5 Minutes!

## 🎯 Goal
Get your Marketplace Monitor backend running locally in under 5 minutes.

---

## 📋 Prerequisites

Before starting, make sure you have:

- ✅ **Python 3.11+** installed
- ✅ **Docker Desktop** installed (easiest method)
- ✅ **Git** installed
- ✅ A code editor (VS Code recommended)

Check your versions:
```bash
python --version    # Should be 3.11+
docker --version    # Should be 20.10+
git --version       # Any recent version
```

---

## 🚀 Method 1: Docker Compose (Recommended - 2 Minutes)

**This is the easiest way!** Docker Compose will set up everything for you.

### Step 1: Get the Code
```bash
# Navigate to where you want the project
cd ~/projects

# If you have it locally already
cd marketplace-monitor-backend

# Or download from wherever you saved it
```

### Step 2: Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env  # or use your favorite editor

# Minimum required changes:
# - Set SECRET_KEY to a random string (mash your keyboard!)
# - Add eBay API keys if you have them (optional for testing)
```

### Step 3: Start Everything
```bash
# Start all services
docker-compose up

# Or run in background
docker-compose up -d
```

**That's it!** 🎉

Services are now running:
- 🌐 **API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/api/v1/docs
- 🌸 **Flower** (worker monitor): http://localhost:5555
- 🗄️ **PostgreSQL**: localhost:5432
- ⚡ **Redis**: localhost:6379

---

## 🛠️ Method 2: Manual Setup (5 Minutes)

If you prefer to run things manually or don't want to use Docker:

### Step 1: Setup Virtual Environment
```bash
cd marketplace-monitor-backend

# Create virtual environment
python -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# You should see (venv) in your terminal now
```

### Step 2: Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install all packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Step 3: Start PostgreSQL & Redis

**Option A: Use Docker for just the databases**
```bash
docker-compose up postgres redis -d
```

**Option B: Install locally**
```bash
# Mac (with Homebrew)
brew install postgresql redis
brew services start postgresql
brew services start redis

# Ubuntu/Debian
sudo apt install postgresql redis-server
sudo systemctl start postgresql
sudo systemctl start redis

# Windows
# Download and install from:
# https://www.postgresql.org/download/windows/
# https://redis.io/download
```

### Step 4: Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit with your favorite editor
code .env  # VS Code
nano .env  # Terminal

# Set these:
SECRET_KEY=your-secret-key-here-make-it-long-and-random
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/marketplace_monitor
REDIS_URL=redis://localhost:6379/0
```

### Step 5: Setup Database
```bash
# Run migrations
alembic upgrade head

# Seed sample templates
python -m app.utils.seed_templates
```

### Step 6: Start All Services

You'll need **4 terminal windows**:

**Terminal 1 - API Server:**
```bash
source venv/bin/activate  # if not already activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Celery Worker (Monitoring):**
```bash
source venv/bin/activate
celery -A app.workers.celery_app worker -Q marketplace_monitoring -l info
```

**Terminal 3 - Celery Worker (Alerts):**
```bash
source venv/bin/activate
celery -A app.workers.celery_app worker -Q alerts -l info
```

**Terminal 4 - Celery Beat (Scheduler):**
```bash
source venv/bin/activate
celery -A app.workers.celery_app beat -l info
```

**Optional Terminal 5 - Flower (Monitoring):**
```bash
source venv/bin/activate
celery -A app.workers.celery_app flower
```

**Done!** All services are now running! 🎉

---

## ✅ Verify Everything Works

### Test 1: API Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "development",
  "app_name": "Marketplace Monitor"
}
```

### Test 2: Open API Docs
Open your browser to: http://localhost:8000/api/v1/docs

You should see the Swagger UI with all your endpoints!

### Test 3: Register a User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'
```

### Test 4: Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

You'll get an `access_token` - save it!

### Test 5: Create a Search
```bash
# Replace YOUR_TOKEN with the access_token from above
curl -X POST "http://localhost:8000/api/v1/searches/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Search",
    "criteria": {
      "keywords": ["iPhone"],
      "max_price": 500
    },
    "marketplaces": ["ebay"],
    "alert_channels": ["email"],
    "check_frequency_minutes": 30
  }'
```

### Test 6: Check Celery Workers
Open Flower: http://localhost:5555

You should see your workers running and tasks being processed!

---

## 🧪 Test Facebook Scraper (Optional)

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run test suite
python test_facebook_scraper.py

# Watch it work (visible browser)
# Edit test_facebook_scraper.py and set headless=False
```

---

## 🎨 Next Steps: Connect Your Frontend

### 1. Configure CORS
In your `.env` file, add your frontend URL:
```bash
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

Restart the API server.

### 2. Use the API from Next.js
```typescript
// lib/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});

// Add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### 3. Make API Calls
```typescript
// Login
const { data } = await api.post('/auth/login', {
  email: 'test@example.com',
  password: 'testpass123'
});

localStorage.setItem('access_token', data.access_token);

// Create search
await api.post('/searches/', {
  name: 'iPhone Search',
  criteria: { keywords: ['iPhone'], max_price: 500 },
  marketplaces: ['ebay'],
  alert_channels: ['email']
});

// Get listings
const listings = await api.get('/listings/recent?hours=24');
```

---

## 🐛 Troubleshooting

### Problem: "Port 8000 already in use"
```bash
# Find what's using the port
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use a different port
uvicorn app.main:app --reload --port 8001
```

### Problem: "Database connection failed"
```bash
# Check PostgreSQL is running
docker ps  # if using Docker
pg_isready  # if installed locally

# Check connection string in .env
# Make sure DATABASE_URL is correct
```

### Problem: "Redis connection failed"
```bash
# Check Redis is running
docker ps  # if using Docker
redis-cli ping  # should return PONG

# Check REDIS_URL in .env
```

### Problem: "Import errors"
```bash
# Make sure you're in virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Problem: "Celery workers not processing tasks"
```bash
# Check Redis is running
redis-cli ping

# Check worker logs
# Look for errors in the terminal where workers are running

# Restart workers
# Ctrl+C to stop, then restart the command
```

### Problem: "Facebook scraper not working"
```bash
# Install Playwright browsers
playwright install chromium

# Test it
python test_facebook_scraper.py

# Check screenshots if errors occur
# Look for fb_error_*.png files
```

---

## 📚 Important Files Reference

### Configuration
- **`.env`** - All your settings (API keys, database URLs, etc.)
- **`alembic.ini`** - Database migration config
- **`docker-compose.yml`** - Multi-service setup
- **`requirements.txt`** - Python dependencies

### Code
- **`app/main.py`** - FastAPI application entry point
- **`app/config.py`** - Settings management
- **`app/models/__init__.py`** - Database models
- **`app/workers/monitoring_tasks.py`** - Background job logic

### Documentation
- **`README.md`** - Project overview
- **`DEVELOPMENT.md`** - Detailed dev guide
- **`FACEBOOK_INTEGRATION.md`** - Facebook scraper guide
- **`FRONTEND_INTEGRATION.md`** - How to connect frontend

---

## 🎓 Learning Resources

### API Documentation
Once running, visit:
- **Swagger UI**: http://localhost:8000/api/v1/docs (interactive)
- **ReDoc**: http://localhost:8000/api/v1/redoc (documentation)

### Worker Monitoring
- **Flower**: http://localhost:5555 (Celery task monitoring)

### Database
```bash
# Connect to PostgreSQL
docker exec -it marketplace_monitor_db psql -U postgres -d marketplace_monitor

# Or if installed locally
psql -U postgres -d marketplace_monitor

# Useful commands:
\dt          # List tables
\d users     # Describe users table
SELECT * FROM users;
SELECT * FROM search_configs;
```

### Redis
```bash
# Connect to Redis
docker exec -it marketplace_monitor_redis redis-cli

# Or if installed locally
redis-cli

# Useful commands:
KEYS *       # List all keys
GET key_name # Get a value
FLUSHALL     # Clear everything (careful!)
```

---

## 🚀 Quick Commands Cheat Sheet

### Docker Compose
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart api

# Rebuild containers
docker-compose up -d --build

# Stop and remove everything
docker-compose down -v
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Celery
```bash
# Start worker
celery -A app.workers.celery_app worker -Q marketplace_monitoring -l info

# Start beat
celery -A app.workers.celery_app beat -l info

# Start flower
celery -A app.workers.celery_app flower

# Purge all tasks
celery -A app.workers.celery_app purge
```

---

## ✅ Success Checklist

Before moving to frontend development, verify:

- [ ] API responds at http://localhost:8000
- [ ] API docs load at http://localhost:8000/api/v1/docs
- [ ] Can register a new user
- [ ] Can login and get JWT token
- [ ] Can create a search
- [ ] Celery workers are running (check Flower)
- [ ] Database has data (check with psql)
- [ ] Redis is caching (check with redis-cli)
- [ ] No errors in logs

---

## 🎉 You're Ready!

Your backend is now running and ready for frontend integration!

**What you have:**
- ✅ API server running
- ✅ Database with schema
- ✅ Background workers polling
- ✅ Redis caching
- ✅ eBay integration ready
- ✅ Facebook scraper ready
- ✅ Alert system ready

**Next steps:**
1. Build your Next.js frontend
2. Connect to this API
3. Test end-to-end
4. Deploy to production!

**Need help?** Check the documentation files or the API docs!

---

## 📞 Quick Links

- **API Docs**: http://localhost:8000/api/v1/docs
- **Flower**: http://localhost:5555
- **GitHub (if you push)**: Your repo URL
- **Documentation**: All `.md` files in project root

---

**Happy vibe coding!** 🚀😎

Start building that frontend and you'll have a complete SaaS in no time! 💪
