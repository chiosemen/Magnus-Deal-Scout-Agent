# app/api/v1/searches.py

from typing import Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.database import get_db
from app.models import User, Search, Listing, SearchStatus
from app.schemas import (
    SearchCreate,
    SearchUpdate,
    Search as SearchSchema,
    Message
)
from app.api.deps import get_current_active_user

router = APIRouter()


@router.get("", response_model=List[SearchSchema])
def get_searches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """Get all searches for current user"""
    searches = db.query(Search).filter(
        Search.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return searches


@router.get("/{search_id}", response_model=SearchSchema)
def get_search(
    search_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get specific search by ID"""
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
    """Create new search"""
    search = Search(
        user_id=current_user.id,
        **search_in.model_dump()
    )

    db.add(search)
    db.commit()
    db.refresh(search)

    return search


@router.put("/{search_id}", response_model=SearchSchema)
def update_search(
    search_id: int,
    search_in: SearchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Update existing search"""
    search = db.query(Search).filter(
        Search.id == search_id,
        Search.user_id == current_user.id
    ).first()

    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found"
        )

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
    """Delete search"""
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


@router.post("/{search_id}/trigger", response_model=Message)
def trigger_search(
    search_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Manually trigger a search to run immediately"""
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
    # from app.tasks.scraping import run_search_task
    # task = run_search_task.delay(search.id)

    return {"message": "Search triggered successfully"}
