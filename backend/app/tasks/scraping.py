# app/tasks/scraping.py

from celery import Task
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
import logging

from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models import Search, Listing, TaskLog, SearchStatus
from app.agents import (
    EbayAgent,
    FacebookAgent,
    GumtreeAgent,
    CraigslistAgent
)

logger = logging.getLogger(__name__)

# Marketplace agent mapping
AGENT_MAP = {
    "ebay": EbayAgent,
    "facebook": FacebookAgent,
    "gumtree": GumtreeAgent,
    "craigslist": CraigslistAgent,
}


class DatabaseTask(Task):
    """Base task with database session management"""
    _db: Session = None

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(base=DatabaseTask, bind=True)
def run_search_task(self, search_id: int) -> Dict[str, Any]:
    """
    Run marketplace scraping for a specific search.

    Args:
        search_id: ID of the search to execute

    Returns:
        Task result with statistics
    """
    db = self.db

    # Create task log
    task_log = TaskLog(
        task_id=self.request.id,
        task_name="run_search_task",
        status="running",
        search_id=search_id,
        started_at=datetime.utcnow()
    )
    db.add(task_log)
    db.commit()

    try:
        # Get search
        search = db.query(Search).filter(Search.id == search_id).first()
        if not search:
            raise ValueError(f"Search {search_id} not found")

        if search.status != SearchStatus.ACTIVE:
            return {"message": "Search is not active", "listings_found": 0}

        # Track statistics
        total_listings = 0
        new_listings = 0

        # Run scrapers for each marketplace
        for marketplace in search.marketplaces:
            agent_class = AGENT_MAP.get(marketplace)
            if not agent_class:
                logger.warning(f"No agent found for marketplace: {marketplace}")
                continue

            agent = agent_class()
            listings = agent.scrape(search)

            # Save listings to database
            for listing_data in listings:
                # Check if listing already exists
                existing = db.query(Listing).filter(
                    Listing.marketplace == marketplace,
                    Listing.external_id == listing_data["external_id"]
                ).first()

                if not existing:
                    listing = Listing(
                        search_id=search_id,
                        marketplace=marketplace,
                        **listing_data
                    )
                    db.add(listing)
                    new_listings += 1

                total_listings += 1

        # Update search last_checked_at
        search.last_checked_at = datetime.utcnow()
        db.commit()

        # Update task log
        task_log.status = "success"
        task_log.completed_at = datetime.utcnow()
        task_log.result = {
            "total_listings": total_listings,
            "new_listings": new_listings
        }
        db.commit()

        # Trigger alerts if there are new listings
        if new_listings > 0:
            from app.tasks.alerts import trigger_alerts_task
            trigger_alerts_task.delay(search_id, new_listings)

        return {
            "search_id": search_id,
            "total_listings": total_listings,
            "new_listings": new_listings
        }

    except Exception as e:
        # Log error
        logger.error(f"Error in run_search_task: {e}", exc_info=True)
        task_log.status = "failed"
        task_log.completed_at = datetime.utcnow()
        task_log.error = str(e)
        db.commit()
        raise


@celery_app.task(bind=True)
def check_active_searches(self) -> Dict[str, Any]:
    """
    Periodic task to check all active searches that are due.

    Returns:
        Statistics about searches checked
    """
    db = SessionLocal()
    try:
        # Find active searches that need to be checked
        now = datetime.utcnow()
        searches = db.query(Search).filter(
            Search.status == SearchStatus.ACTIVE
        ).all()

        checked_count = 0
        for search in searches:
            # Check if enough time has passed since last check
            if search.last_checked_at:
                time_since_check = now - search.last_checked_at
                if time_since_check.total_seconds() < (search.check_interval_minutes * 60):
                    continue

            # Trigger search task
            run_search_task.delay(search.id)
            checked_count += 1

        logger.info(f"Triggered {checked_count} search tasks")

        return {
            "searches_triggered": checked_count
        }

    finally:
        db.close()


@celery_app.task
def cleanup_old_listings() -> Dict[str, Any]:
    """
    Periodic task to clean up old listings.

    Returns:
        Statistics about cleanup
    """
    db = SessionLocal()
    try:
        # Delete listings older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        deleted = db.query(Listing).filter(
            Listing.created_at < cutoff_date
        ).delete()

        db.commit()

        logger.info(f"Deleted {deleted} old listings")

        return {
            "listings_deleted": deleted
        }

    finally:
        db.close()
