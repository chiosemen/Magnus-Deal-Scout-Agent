# app/api/v1/listings.py

from typing import Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User, Listing, Search, Marketplace
from app.schemas import Listing as ListingSchema, ListingUpdate, Message
from app.api.deps import get_current_active_user

router = APIRouter()


@router.get("", response_model=List[ListingSchema])
def get_listings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    search_id: Optional[int] = None,
    marketplace: Optional[Marketplace] = None,
    is_saved: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
) -> Any:
    """Get listings with optional filters"""
    # Get user's search IDs
    user_search_ids = db.query(Search.id).filter(
        Search.user_id == current_user.id
    ).all()
    user_search_ids = [s[0] for s in user_search_ids]

    query = db.query(Listing).filter(Listing.search_id.in_(user_search_ids))

    if search_id:
        if search_id not in user_search_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        query = query.filter(Listing.search_id == search_id)

    if marketplace:
        query = query.filter(Listing.marketplace == marketplace)

    if is_saved is not None:
        query = query.filter(Listing.is_saved == is_saved)

    listings = query.order_by(desc(Listing.created_at)).offset(skip).limit(limit).all()
    return listings


@router.get("/recent", response_model=List[ListingSchema])
def get_recent_listings(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get recent listings from the last N hours"""
    user_search_ids = db.query(Search.id).filter(
        Search.user_id == current_user.id
    ).all()
    user_search_ids = [s[0] for s in user_search_ids]

    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    listings = db.query(Listing).filter(
        Listing.search_id.in_(user_search_ids),
        Listing.created_at >= cutoff_time
    ).order_by(desc(Listing.created_at)).limit(100).all()

    return listings


@router.get("/{listing_id}", response_model=ListingSchema)
def get_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get specific listing by ID"""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()

    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )

    # Verify user has access to this listing
    search = db.query(Search).filter(
        Search.id == listing.search_id,
        Search.user_id == current_user.id
    ).first()

    if not search:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return listing


@router.patch("/{listing_id}", response_model=ListingSchema)
def update_listing(
    listing_id: int,
    listing_in: ListingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Update listing (e.g., toggle saved status)"""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()

    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )

    # Verify access
    search = db.query(Search).filter(
        Search.id == listing.search_id,
        Search.user_id == current_user.id
    ).first()

    if not search:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    update_data = listing_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(listing, field, value)

    db.commit()
    db.refresh(listing)

    return listing


@router.get("/saved", response_model=List[ListingSchema])
def get_saved_listings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get all saved listings for current user"""
    user_search_ids = db.query(Search.id).filter(
        Search.user_id == current_user.id
    ).all()
    user_search_ids = [s[0] for s in user_search_ids]

    listings = db.query(Listing).filter(
        Listing.search_id.in_(user_search_ids),
        Listing.is_saved == True
    ).order_by(desc(Listing.created_at)).all()

    return listings
