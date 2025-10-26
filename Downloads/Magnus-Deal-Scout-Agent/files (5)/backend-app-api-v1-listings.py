# app/api/v1/listings.py

from typing import Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User, Listing, Search
from app.schemas import (
    Listing as ListingSchema,
    ListingUpdate,
    PaginatedResponse
)
from app.api.deps import get_current_active_user

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
def get_listings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    search_id: Optional[int] = None,
    marketplaces: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    location: Optional[str] = None,
    is_featured: Optional[bool] = None,
    is_saved: Optional[bool] = None,
    sort_by: str = Query("newest", regex="^(newest|oldest|price_asc|price_desc)$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
) -> Any:
    """
    Get all listings with filters and pagination.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        search_id: Filter by search ID
        marketplaces: Comma-separated marketplace names
        min_price: Minimum price filter
        max_price: Maximum price filter
        location: Location filter
        is_featured: Featured items only
        is_saved: Saved items only
        sort_by: Sort order
        page: Page number
        per_page: Items per page
    
    Returns:
        Paginated list of listings
    """
    # Build base query - only listings from user's searches
    query = db.query(Listing).join(Search).filter(
        Search.user_id == current_user.id
    )
    
    # Apply filters
    if search_id:
        query = query.filter(Listing.search_id == search_id)
    
    if marketplaces:
        marketplace_list = [m.strip() for m in marketplaces.split(",")]
        query = query.filter(Listing.marketplace.in_(marketplace_list))
    
    if min_price is not None:
        query = query.filter(Listing.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Listing.price <= max_price)
    
    if location:
        query = query.filter(Listing.location.ilike(f"%{location}%"))
    
    if is_featured is not None:
        query = query.filter(Listing.is_featured == is_featured)
    
    if is_saved is not None:
        query = query.filter(Listing.is_saved == is_saved)
    
    # Apply sorting
    if sort_by == "newest":
        query = query.order_by(desc(Listing.created_at))
    elif sort_by == "oldest":
        query = query.order_by(Listing.created_at)
    elif sort_by == "price_asc":
        query = query.order_by(Listing.price)
    elif sort_by == "price_desc":
        query = query.order_by(desc(Listing.price))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    listings = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "items": listings,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }


@router.get("/recent", response_model=List[ListingSchema])
def get_recent_listings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = Query(10, ge=1, le=50)
) -> Any:
    """
    Get most recent listings.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        limit: Number of listings to return
    
    Returns:
        List of recent listings
    """
    listings = db.query(Listing).join(Search).filter(
        Search.user_id == current_user.id
    ).order_by(desc(Listing.created_at)).limit(limit).all()
    
    return listings


@router.get("/saved", response_model=PaginatedResponse)
def get_saved_listings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
) -> Any:
    """
    Get all saved/bookmarked listings.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        page: Page number
        per_page: Items per page
    
    Returns:
        Paginated list of saved listings
    """
    query = db.query(Listing).join(Search).filter(
        Search.user_id == current_user.id,
        Listing.is_saved == True
    ).order_by(desc(Listing.created_at))
    
    total = query.count()
    listings = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "items": listings,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }


@router.get("/{listing_id}", response_model=ListingSchema)
def get_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get specific listing by ID.
    
    Args:
        listing_id: Listing ID
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Listing object
    
    Raises:
        HTTPException: If listing not found or unauthorized
    """
    listing = db.query(Listing).join(Search).filter(
        Listing.id == listing_id,
        Search.user_id == current_user.id
    ).first()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    return listing


@router.post("/{listing_id}/save", response_model=ListingSchema)
def save_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Save/bookmark a listing.
    
    Args:
        listing_id: Listing ID
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Updated listing object
    """
    listing = db.query(Listing).join(Search).filter(
        Listing.id == listing_id,
        Search.user_id == current_user.id
    ).first()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    listing.is_saved = True
    db.commit()
    db.refresh(listing)
    
    return listing


@router.delete("/{listing_id}/save", response_model=ListingSchema)
def unsave_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Unsave/unbookmark a listing.
    
    Args:
        listing_id: Listing ID
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Updated listing object
    """
    listing = db.query(Listing).join(Search).filter(
        Listing.id == listing_id,
        Search.user_id == current_user.id
    ).first()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    listing.is_saved = False
    db.commit()
    db.refresh(listing)
    
    return listing


@router.get("/export/{search_id}")
def export_listings(
    search_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    format: str = Query("csv", regex="^(csv|json)$")
) -> Any:
    """
    Export listings for a search.
    
    Args:
        search_id: Search ID
        db: Database session
        current_user: Current authenticated user
        format: Export format (csv or json)
    
    Returns:
        Exported data
    
    Note:
        This is a placeholder. Implement actual file export.
    """
    # Verify search ownership
    search = db.query(Search).filter(
        Search.id == search_id,
        Search.user_id == current_user.id
    ).first()
    
    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found"
        )
    
    # Get all listings for this search
    listings = db.query(Listing).filter(
        Listing.search_id == search_id
    ).all()
    
    # TODO: Implement actual CSV/JSON export
    return {"message": f"Export {format} not yet implemented", "count": len(listings)}
