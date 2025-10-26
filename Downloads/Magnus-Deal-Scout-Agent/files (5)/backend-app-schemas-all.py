# app/schemas/__init__.py

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums (matching database)
class SubscriptionTier(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    BUSINESS = "business"


class Marketplace(str, Enum):
    EBAY = "ebay"
    FACEBOOK = "facebook"
    GUMTREE = "gumtree"
    CRAIGSLIST = "craigslist"


class AlertChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"


class SearchStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


# Base Schemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True


# User Schemas
class UserBase(BaseSchema):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


class UserInDB(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    subscription_tier: SubscriptionTier
    created_at: datetime
    updated_at: Optional[datetime]


class User(UserInDB):
    pass


# Authentication Schemas
class Token(BaseSchema):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseSchema):
    sub: Optional[int] = None
    exp: Optional[int] = None


# Search Schemas
class SearchBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    keywords: str = Field(..., min_length=1)
    marketplaces: List[Marketplace] = Field(..., min_items=1)
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


class SearchUpdate(BaseSchema):
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


class SearchInDB(SearchBase):
    id: int
    user_id: int
    status: SearchStatus
    last_checked_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]


class Search(SearchInDB):
    pass


class SearchWithCount(Search):
    listing_count: int = 0


# Listing Schemas
class ListingBase(BaseSchema):
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
    is_featured: bool = False
    metadata: Dict[str, Any] = {}
    posted_at: Optional[datetime] = None


class ListingCreate(ListingBase):
    search_id: int


class ListingUpdate(BaseSchema):
    is_saved: Optional[bool] = None


class ListingInDB(ListingBase):
    id: int
    search_id: int
    is_saved: bool
    scraped_at: datetime
    created_at: datetime


class Listing(ListingInDB):
    pass


class ListingWithSearch(Listing):
    search: Optional[Search] = None


# Alert Schemas
class AlertBase(BaseSchema):
    search_id: int
    channel: AlertChannel
    config: Optional[Dict[str, Any]] = {}


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseSchema):
    enabled: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None


class AlertInDB(AlertBase):
    id: int
    user_id: int
    enabled: bool
    last_triggered_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]


class Alert(AlertInDB):
    pass


# Pagination Schema
class PaginatedResponse(BaseSchema):
    items: List[Any]
    total: int
    page: int
    per_page: int
    total_pages: int


# Dashboard Schemas
class DashboardStats(BaseSchema):
    total_searches: int
    active_searches: int
    total_listings: int
    new_listings_today: int
    saved_listings: int


# Task Schemas
class TaskResponse(BaseSchema):
    message: str
    task_id: str


# Response Messages
class Message(BaseSchema):
    message: str
