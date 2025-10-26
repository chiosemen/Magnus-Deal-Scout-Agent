# app/models/__init__.py

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, 
    JSON, Enum as SQLEnum, Text, Float, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.database import Base


# Enums
class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    BUSINESS = "business"


class Marketplace(str, enum.Enum):
    EBAY = "ebay"
    FACEBOOK = "facebook"
    GUMTREE = "gumtree"
    CRAIGSLIST = "craigslist"


class AlertChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"


class SearchStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


# Models
class User(Base):
    """User accounts and authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    searches = relationship("Search", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")


class Search(Base):
    """User-defined marketplace searches"""
    __tablename__ = "searches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    keywords = Column(Text, nullable=False)
    marketplaces = Column(JSON, nullable=False)  # List of marketplace enums
    location = Column(String(255))
    radius_km = Column(Integer)
    min_price = Column(Float)
    max_price = Column(Float)
    filters = Column(JSON, default={})  # Additional filters
    status = Column(SQLEnum(SearchStatus), default=SearchStatus.ACTIVE, index=True)
    check_interval_minutes = Column(Integer, default=60)
    last_checked_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="searches")
    listings = relationship("Listing", back_populates="search", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="search", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
    )


class Listing(Base):
    """Scraped marketplace listings"""
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    search_id = Column(Integer, ForeignKey("searches.id", ondelete="CASCADE"), nullable=False)
    external_id = Column(String(255), nullable=False)  # ID from marketplace
    marketplace = Column(SQLEnum(Marketplace), nullable=False, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False, index=True)
    currency = Column(String(10), default="USD")
    location = Column(String(255))
    url = Column(Text, nullable=False)
    image_urls = Column(JSON, default=[])
    seller_name = Column(String(255))
    seller_rating = Column(Float)
    is_featured = Column(Boolean, default=False)
    is_saved = Column(Boolean, default=False, index=True)
    metadata = Column(JSON, default={})
    posted_at = Column(DateTime(timezone=True))
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    search = relationship("Search", back_populates="listings")

    # Indexes and Constraints
    __table_args__ = (
        Index('idx_search_marketplace', 'search_id', 'marketplace'),
        Index('idx_marketplace_external', 'marketplace', 'external_id'),
        Index('idx_price', 'price'),
        Index('idx_posted_at', 'posted_at'),
        UniqueConstraint('marketplace', 'external_id', name='uq_marketplace_external_id'),
    )


class Alert(Base):
    """User notification preferences for searches"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    search_id = Column(Integer, ForeignKey("searches.id", ondelete="CASCADE"), nullable=False)
    channel = Column(SQLEnum(AlertChannel), nullable=False)
    enabled = Column(Boolean, default=True, index=True)
    config = Column(JSON, default={})  # Channel-specific configuration
    last_triggered_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="alerts")
    search = relationship("Search", back_populates="alerts")

    # Indexes
    __table_args__ = (
        Index('idx_user_search', 'user_id', 'search_id'),
        Index('idx_enabled', 'enabled'),
    )


class TaskLog(Base):
    """Celery task execution logs"""
    __tablename__ = "task_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), unique=True, index=True)
    task_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, index=True)
    search_id = Column(Integer, ForeignKey("searches.id", ondelete="SET NULL"))
    result = Column(JSON)
    error = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_task_status', 'task_name', 'status'),
        Index('idx_created_at', 'created_at'),
    )
