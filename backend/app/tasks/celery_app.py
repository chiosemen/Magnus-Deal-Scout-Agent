# app/tasks/celery_app.py

from celery import Celery
from celery.schedules import crontab
from app.config import settings

# Create Celery app
celery_app = Celery(
    "deal_scout",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.scraping",
        "app.tasks.alerts"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    # Run active searches every 15 minutes
    'check-active-searches': {
        'task': 'app.tasks.scraping.check_active_searches',
        'schedule': crontab(minute='*/15'),
    },
    # Clean up old listings every day at 2 AM
    'cleanup-old-listings': {
        'task': 'app.tasks.scraping.cleanup_old_listings',
        'schedule': crontab(hour=2, minute=0),
    },
}
