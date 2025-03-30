"""
Base entity with timestamp fields and soft delete functionality.
"""
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


class BaseEntity:
    """Base entity with timestamp fields and soft delete functionality."""
    
    def __init__(
        self,
        id: Optional[uuid.UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        deleted_at: Optional[datetime] = None,
        is_streamable: bool = False,
    ):
        self.id = id or uuid.uuid4()
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted_at = deleted_at
        self.is_streamable = is_streamable
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        return {
            "id": str(self.id),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "is_streamable": self.is_streamable,
        }
    
    def is_deleted(self) -> bool:
        """Check if entity is soft deleted."""
        return self.deleted_at is not None
