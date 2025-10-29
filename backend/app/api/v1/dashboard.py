# app/api/v1/dashboard.py

from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User, Search, Listing, SearchStatus
from app.schemas import DashboardStats
from app.api.deps import get_current_active_user

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get dashboard statistics for current user"""

    # Total searches
    total_searches = db.query(func.count(Search.id)).filter(
        Search.user_id == current_user.id
    ).scalar()

    # Active searches
    active_searches = db.query(func.count(Search.id)).filter(
        Search.user_id == current_user.id,
        Search.status == SearchStatus.ACTIVE
    ).scalar()

    # Get user's search IDs
    user_search_ids = db.query(Search.id).filter(
        Search.user_id == current_user.id
    ).all()
    user_search_ids = [s[0] for s in user_search_ids]

    # Total listings
    total_listings = db.query(func.count(Listing.id)).filter(
        Listing.search_id.in_(user_search_ids)
    ).scalar() if user_search_ids else 0

    # New listings today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    new_listings_today = db.query(func.count(Listing.id)).filter(
        Listing.search_id.in_(user_search_ids),
        Listing.created_at >= today_start
    ).scalar() if user_search_ids else 0

    # Saved listings
    saved_listings = db.query(func.count(Listing.id)).filter(
        Listing.search_id.in_(user_search_ids),
        Listing.is_saved == True
    ).scalar() if user_search_ids else 0

    return {
        "total_searches": total_searches or 0,
        "active_searches": active_searches or 0,
        "total_listings": total_listings or 0,
        "new_listings_today": new_listings_today or 0,
        "saved_listings": saved_listings or 0
    }
