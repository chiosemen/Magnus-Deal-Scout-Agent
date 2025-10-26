# app/api/v1/alerts.py

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Alert, Search
from app.schemas import (
    AlertCreate,
    AlertUpdate,
    Alert as AlertSchema,
    Message
)
from app.api.deps import get_current_active_user

router = APIRouter()


@router.get("", response_model=List[AlertSchema])
def get_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    search_id: int = None
) -> Any:
    """Get all alerts for current user"""
    query = db.query(Alert).filter(Alert.user_id == current_user.id)
    
    if search_id:
        query = query.filter(Alert.search_id == search_id)
    
    return query.all()


@router.post("", response_model=AlertSchema, status_code=status.HTTP_201_CREATED)
def create_alert(
    alert_in: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Create new alert"""
    # Verify search ownership
    search = db.query(Search).filter(
        Search.id == alert_in.search_id,
        Search.user_id == current_user.id
    ).first()
    
    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found"
        )
    
    alert = Alert(
        user_id=current_user.id,
        **alert_in.model_dump()
    )
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    return alert


@router.put("/{alert_id}", response_model=AlertSchema)
def update_alert(
    alert_id: int,
    alert_in: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Update alert"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    update_data = alert_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(alert, field, value)
    
    db.commit()
    db.refresh(alert)
    
    return alert


@router.delete("/{alert_id}", response_model=Message)
def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Delete alert"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    db.delete(alert)
    db.commit()
    
    return {"message": "Alert deleted successfully"}


# app/api/v1/dashboard.py

from sqlalchemy import func
from datetime import datetime, timedelta
from app.models import Listing, SearchStatus
from app.schemas import DashboardStats

dashboard_router = APIRouter()


@dashboard_router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get dashboard statistics"""
    # Total searches
    total_searches = db.query(func.count(Search.id)).filter(
        Search.user_id == current_user.id
    ).scalar()
    
    # Active searches
    active_searches = db.query(func.count(Search.id)).filter(
        Search.user_id == current_user.id,
        Search.status == SearchStatus.ACTIVE
    ).scalar()
    
    # Total listings
    total_listings = db.query(func.count(Listing.id)).join(Search).filter(
        Search.user_id == current_user.id
    ).scalar()
    
    # New listings today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    new_today = db.query(func.count(Listing.id)).join(Search).filter(
        Search.user_id == current_user.id,
        Listing.created_at >= today_start
    ).scalar()
    
    # Saved listings
    saved_listings = db.query(func.count(Listing.id)).join(Search).filter(
        Search.user_id == current_user.id,
        Listing.is_saved == True
    ).scalar()
    
    return {
        "total_searches": total_searches,
        "active_searches": active_searches,
        "total_listings": total_listings,
        "new_listings_today": new_today,
        "saved_listings": saved_listings
    }


@dashboard_router.get("/activity")
def get_dashboard_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    days: int = 7
) -> Any:
    """Get activity data for charts"""
    # TODO: Implement activity aggregation
    return []
