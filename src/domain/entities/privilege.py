"""
Privilege entity for the authentication system.
"""
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from .base import BaseEntity

class Privilege(BaseEntity):
    """Privilege entity representing a system permission."""
    
    name: str
    description: Optional[str]
    
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        id: Optional[uuid.UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__(id, created_at, updated_at)
        self.name = name
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        data = super().to_dict()
        data.update({
            "name": self.name,
            "description": self.description,
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Privilege':
        """Create entity from dictionary."""
        return cls(
            name=data["name"],
            description=data.get("description"),
            id=uuid.UUID(data["id"]) if "id" in data else None,
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else None,
        )
