# app/schemas/__init__.py

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from app.models import SubscriptionTier, Marketplace, AlertChannel, SearchStatus


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    is_superuser: bool
    subscription_tier: SubscriptionTier
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Search Schemas
class SearchBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    keywords: str = Field(..., min_length=1)
    marketplaces: List[Marketplace]
    location: Optional[str] = None
    radius_km: Optional[int] = Field(None, ge=1, le=500)
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    filters: Optional[Dict[str, Any]] = {}
    check_interval_minutes: int = Field(60, ge=15, le=1440)

    @validator('max_price')
    def validate_price_range(cls, v, values):
        if v is not None and 'min_price' in values and values['min_price'] is not None:
            if v < values['min_price']:
                raise ValueError('max_price must be greater than min_price')
        return v


class SearchCreate(SearchBase):
    pass


class SearchUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    keywords: Optional[str] = Field(None, min_length=1)
    marketplaces: Optional[List[Marketplace]] = None
    location: Optional[str] = None
    radius_km: Optional[int] = Field(None, ge=1, le=500)
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    filters: Optional[Dict[str, Any]] = None
    status: Optional[SearchStatus] = None
    check_interval_minutes: Optional[int] = Field(None, ge=15, le=1440)


class Search(SearchBase):
    id: int
    user_id: int
    status: SearchStatus
    last_checked_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class SearchWithStats(Search):
    listings_count: int = 0
    new_listings_today: int = 0


# Listing Schemas
class ListingBase(BaseModel):
    external_id: str
    marketplace: Marketplace
    title: str
    description: Optional[str] = None
    price: float
    currency: str = "USD"
    location: Optional[str] = None
    url: str
    image_urls: List[str] = []
    seller_name: Optional[str] = None
    seller_rating: Optional[float] = None
    metadata: Dict[str, Any] = {}
    posted_at: Optional[datetime] = None


class ListingCreate(ListingBase):
    search_id: int


class ListingUpdate(BaseModel):
    is_saved: Optional[bool] = None


class Listing(ListingBase):
    id: int
    search_id: int
    is_featured: bool
    is_saved: bool
    scraped_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Alert Schemas
class AlertBase(BaseModel):
    channel: AlertChannel
    enabled: bool = True
    config: Dict[str, Any] = {}


class AlertCreate(AlertBase):
    search_id: int


class AlertUpdate(BaseModel):
    enabled: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None


class Alert(AlertBase):
    id: int
    user_id: int
    search_id: int
    last_triggered_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Dashboard Schemas
class DashboardStats(BaseModel):
    total_searches: int
    active_searches: int
    total_listings: int
    new_listings_today: int
    saved_listings: int


class RecentActivity(BaseModel):
    search_name: str
    listings_found: int
    timestamp: datetime


# Pagination Schemas
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int


# Message Schema
class Message(BaseModel):
    message: str
