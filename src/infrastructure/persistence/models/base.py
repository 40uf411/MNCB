"""
Base SQLAlchemy model with timestamp fields and soft delete functionality.
"""
from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel:
    """Base SQLAlchemy model with timestamp fields and soft delete functionality."""
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    is_streamable = Column(Boolean, default=False, nullable=False)
    
    def is_deleted(self) -> bool:
        """Check if model is soft deleted."""
        return self.deleted_at is not None
