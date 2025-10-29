# app/tasks/alerts.py

from datetime import datetime
from typing import Dict, Any
import logging

from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models import Alert, Search

logger = logging.getLogger(__name__)


@celery_app.task
def trigger_alerts_task(search_id: int, new_listings_count: int) -> Dict[str, Any]:
    """
    Trigger alerts for a search with new listings.

    Args:
        search_id: Search ID
        new_listings_count: Number of new listings found

    Returns:
        Alert statistics
    """
    db = SessionLocal()
    try:
        # Get enabled alerts for this search
        alerts = db.query(Alert).filter(
            Alert.search_id == search_id,
            Alert.enabled == True
        ).all()

        sent_count = 0
        for alert in alerts:
            # TODO: Implement actual alert sending based on channel
            # For now, just log
            logger.info(f"Alert {alert.id}: {new_listings_count} new listings for search {search_id}")

            # Update last_triggered_at
            alert.last_triggered_at = datetime.utcnow()
            sent_count += 1

        db.commit()

        return {
            "alerts_sent": sent_count
        }

    finally:
        db.close()
