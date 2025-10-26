# app/api/v1/searches.py

from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, Search, Listing, SearchStatus
from app.schemas import (
    SearchCreate, 
    SearchUpdate, 
    Search as SearchSchema,
    SearchWithCount,
    PaginatedResponse,
    TaskResponse,
    Message
)
from app.api.deps import get_current_active_user

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
def get_searches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
) -> Any:
    """
    Get all searches for current user with pagination and filtering.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        status: Optional filter by search status
        page: Page number
        per_page: Items per page
    
    Returns:
        Paginated list of searches
    """
    # Build query
    query = db.query(Search).filter(Search.user_id == current_user.id)
    
    # Apply status filter
    if status:
        query = query.filter(Search.status == status)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    searches = query.offset((page - 1) * per_page).limit(per_page).all()
    
    # Add listing count to each search
    search_data = []
    for search in searches:
        search_dict = SearchSchema.model_validate(search).model_dump()
        listing_count = db.query(func.count(Listing.id)).filter(
            Listing.search_id == search.id
        ).scalar()
        search_dict["_count"] = {"listings": listing_count}
        search_data.append(search_dict)
    
    return {
        "items": search_data,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }


@router.get("/{search_id}", response_model=SearchSchema)
def get_search(
    search_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get specific search by ID.
    
    Args:
        search_id: Search ID
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Search object
    
    Raises:
        HTTPException: If search not found or unauthorized
    """
    search = db.query(Search).filter(
        Search.id == search_id,
        Search.user_id == current_user.id
    ).first()
    
    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found"
        )
    
    return search


@router.post("", response_model=SearchSchema, status_code=status.HTTP_201_CREATED)
def create_search(
    search_in: SearchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create new search.
    
    Args:
        search_in: Search creation data
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Created search object
    """
    search = Search(
        user_id=current_user.id,
        **search_in.model_dump()
    )
    
    db.add(search)
    db.commit()
    db.refresh(search)
    
    # TODO: Trigger initial scraping task
    # trigger_search_task.delay(search.id)
    
    return search


@router.put("/{search_id}", response_model=SearchSchema)
def update_search(
    search_id: int,
    search_in: SearchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update existing search.
    
    Args:
        search_id: Search ID
        search_in: Search update data
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Updated search object
    
    Raises:
        HTTPException: If search not found or unauthorized
    """
    search = db.query(Search).filter(
        Search.id == search_id,
        Search.user_id == current_user.id
    ).first()
    
    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found"
        )
    
    # Update only provided fields
    update_data = search_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(search, field, value)
    
    db.commit()
    db.refresh(search)
    
    return search


@router.delete("/{search_id}", response_model=Message)
def delete_search(
    search_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Delete search.
    
    Args:
        search_id: Search ID
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Success message
    
    Raises:
        HTTPException: If search not found or unauthorized
    """
    search = db.query(Search).filter(
        Search.id == search_id,
        Search.user_id == current_user.id
    ).first()
    
    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found"
        )
    
    db.delete(search)
    db.commit()
    
    return {"message": "Search deleted successfully"}


@router.post("/{search_id}/pause", response_model=SearchSchema)
def pause_search(
    search_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Pause a search.
    
    Args:
        search_id: Search ID
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Updated search object
    """
    search = db.query(Search).filter(
        Search.id == search_id,
        Search.user_id == current_user.id
    ).first()
    
    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found"
        )
    
    search.status = SearchStatus.PAUSED
    db.commit()
    db.refresh(search)
    
    return search


@router.post("/{search_id}/resume", response_model=SearchSchema)
def resume_search(
    search_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Resume a paused search.
    
    Args:
        search_id: Search ID
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Updated search object
    """
    search = db.query(Search).filter(
        Search.id == search_id,
        Search.user_id == current_user.id
    ).first()
    
    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found"
        )
    
    search.status = SearchStatus.ACTIVE
    db.commit()
    db.refresh(search)
    
    return search


@router.post("/{search_id}/trigger", response_model=TaskResponse)
def trigger_search(
    search_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Manually trigger a search to run immediately.
    
    Args:
        search_id: Search ID
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Task response with task ID
    """
    search = db.query(Search).filter(
        Search.id == search_id,
        Search.user_id == current_user.id
    ).first()
    
    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found"
        )
    
    # TODO: Trigger Celery task
    # task = trigger_search_task.delay(search.id)
    # task_id = task.id
    task_id = "placeholder-task-id"
    
    return {
        "message": "Search triggered successfully",
        "task_id": task_id
    }


@router.get("/{search_id}/stats")
def get_search_stats(
    search_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get statistics for a search.
    
    Args:
        search_id: Search ID
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Search statistics
    """
    search = db.query(Search).filter(
        Search.id == search_id,
        Search.user_id == current_user.id
    ).first()
    
    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found"
        )
    
    # Get statistics
    total_listings = db.query(func.count(Listing.id)).filter(
        Listing.search_id == search_id
    ).scalar()
    
    # Get today's listings
    from datetime import datetime, timedelta
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    new_today = db.query(func.count(Listing.id)).filter(
        Listing.search_id == search_id,
        Listing.created_at >= today_start
    ).scalar()
    
    # Calculate average price
    avg_price = db.query(func.avg(Listing.price)).filter(
        Listing.search_id == search_id
    ).scalar() or 0
    
    return {
        "total_listings": total_listings,
        "new_listings_today": new_today,
        "average_price": round(float(avg_price), 2),
        "price_trend": "stable"  # TODO: Calculate actual trend
    }
