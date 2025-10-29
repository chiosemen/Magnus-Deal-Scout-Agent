# app/core/monitoring.py

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time
from functools import wraps
from typing import Callable
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Prometheus Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

celery_tasks_total = Counter(
    'celery_tasks_total',
    'Total Celery tasks',
    ['task_name', 'status']
)

celery_task_duration_seconds = Histogram(
    'celery_task_duration_seconds',
    'Celery task duration in seconds',
    ['task_name']
)

marketplace_scrapes_total = Counter(
    'marketplace_scrapes_total',
    'Total marketplace scraping attempts',
    ['marketplace', 'status']
)

marketplace_listings_scraped = Counter(
    'marketplace_listings_scraped_total',
    'Total listings scraped',
    ['marketplace']
)

active_searches = Gauge(
    'active_searches_total',
    'Number of active searches'
)

database_connections = Gauge(
    'database_connections_total',
    'Number of active database connections'
)


def init_sentry() -> None:
    """Initialize Sentry error tracking"""
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            release=f"{settings.APP_NAME}@{settings.APP_VERSION}",
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
                RedisIntegration(),
                CeleryIntegration(),
            ],
            traces_sample_rate=0.1 if settings.ENVIRONMENT == "production" else 1.0,
            profiles_sample_rate=0.1 if settings.ENVIRONMENT == "production" else 1.0,
            send_default_pii=False,
            before_send=before_send_sentry,
        )
        logger.info("Sentry initialized successfully")
    else:
        logger.warning("Sentry DSN not configured, error tracking disabled")


def before_send_sentry(event, hint):
    """Filter and modify events before sending to Sentry"""
    # Don't send health check errors
    if 'request' in event and '/health' in event.get('request', {}).get('url', ''):
        return None

    # Scrub sensitive data
    if 'request' in event:
        headers = event['request'].get('headers', {})
        if 'Authorization' in headers:
            headers['Authorization'] = '[Filtered]'
        if 'Cookie' in headers:
            headers['Cookie'] = '[Filtered]'

    return event


def track_request_metrics(method: str, endpoint: str, status: int, duration: float) -> None:
    """Track HTTP request metrics"""
    http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)


def track_celery_task(task_name: str, status: str, duration: float) -> None:
    """Track Celery task metrics"""
    celery_tasks_total.labels(task_name=task_name, status=status).inc()
    celery_task_duration_seconds.labels(task_name=task_name).observe(duration)


def track_marketplace_scrape(marketplace: str, status: str, listings_count: int = 0) -> None:
    """Track marketplace scraping metrics"""
    marketplace_scrapes_total.labels(marketplace=marketplace, status=status).inc()
    if listings_count > 0:
        marketplace_listings_scraped.labels(marketplace=marketplace).inc(listings_count)


def metrics_endpoint() -> Response:
    """Endpoint to expose Prometheus metrics"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


def timed_operation(operation_name: str):
    """Decorator to time and log operations"""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"{operation_name} completed", extra={
                    "operation": operation_name,
                    "duration_seconds": duration,
                    "status": "success"
                })
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{operation_name} failed", extra={
                    "operation": operation_name,
                    "duration_seconds": duration,
                    "status": "error",
                    "error": str(e)
                }, exc_info=True)
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"{operation_name} completed", extra={
                    "operation": operation_name,
                    "duration_seconds": duration,
                    "status": "success"
                })
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{operation_name} failed", extra={
                    "operation": operation_name,
                    "duration_seconds": duration,
                    "status": "error",
                    "error": str(e)
                }, exc_info=True)
                raise

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
