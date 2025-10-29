# app/api/v1/monitoring.py

from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta
import psutil

from app.database import get_db, get_redis, engine
from app.models import Search, Listing, TaskLog, SearchStatus
from app.core.monitoring import metrics_endpoint, active_searches, database_connections

router = APIRouter()


@router.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return metrics_endpoint()


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Detailed health check with component status

    Returns status of:
    - API service
    - Database connectivity
    - Redis connectivity
    - Celery workers
    - System resources
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {}
    }

    # Check database
    try:
        db.execute(text("SELECT 1"))
        db_connection_count = engine.pool.size()
        health_status["components"]["database"] = {
            "status": "healthy",
            "connections": db_connection_count,
            "pool_size": engine.pool.size()
        }
        database_connections.set(db_connection_count)
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # Check Redis
    try:
        redis = get_redis()
        redis.ping()
        redis_info = redis.info()
        health_status["components"]["redis"] = {
            "status": "healthy",
            "used_memory": redis_info.get("used_memory_human"),
            "connected_clients": redis_info.get("connected_clients")
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["components"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # Check Celery workers
    try:
        from app.tasks.celery_app import celery_app
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()

        if active_workers:
            health_status["components"]["celery"] = {
                "status": "healthy",
                "workers": len(active_workers),
                "worker_names": list(active_workers.keys())
            }
        else:
            health_status["status"] = "degraded"
            health_status["components"]["celery"] = {
                "status": "degraded",
                "message": "No active workers found"
            }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["components"]["celery"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # System resources
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        health_status["components"]["system"] = {
            "status": "healthy",
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent
        }

        # Warn if resources are high
        if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
            health_status["status"] = "degraded"
            health_status["components"]["system"]["status"] = "degraded"
    except Exception as e:
        health_status["components"]["system"] = {
            "status": "unknown",
            "error": str(e)
        }

    # Application metrics
    try:
        active_search_count = db.query(func.count(Search.id)).filter(
            Search.status == SearchStatus.ACTIVE
        ).scalar()

        recent_listings = db.query(func.count(Listing.id)).filter(
            Listing.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).scalar()

        failed_tasks = db.query(func.count(TaskLog.id)).filter(
            TaskLog.status == "failed",
            TaskLog.created_at >= datetime.utcnow() - timedelta(hours=1)
        ).scalar()

        health_status["components"]["application"] = {
            "status": "healthy",
            "active_searches": active_search_count,
            "listings_last_24h": recent_listings,
            "failed_tasks_last_hour": failed_tasks
        }

        active_searches.set(active_search_count)

        if failed_tasks > 10:
            health_status["status"] = "degraded"
            health_status["components"]["application"]["status"] = "degraded"
            health_status["components"]["application"]["warning"] = "High task failure rate"

    except Exception as e:
        health_status["components"]["application"] = {
            "status": "unknown",
            "error": str(e)
        }

    return health_status


@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Readiness probe for Kubernetes
    Returns 200 if service is ready to accept traffic
    """
    try:
        # Check database
        db.execute(text("SELECT 1"))

        # Check Redis
        redis = get_redis()
        redis.ping()

        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness probe for Kubernetes
    Returns 200 if service is alive
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }
