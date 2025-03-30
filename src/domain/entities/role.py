"""
Role entity for the authentication system.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

from .base import BaseEntity
from .privilege import Privilege

class Role(BaseEntity):
    """Role entity representing a user role with associated privileges."""
    
    name: str
    description: Optional[str]
    privileges: List[Privilege]
    
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        privileges: Optional[List[Privilege]] = None,
        id: Optional[uuid.UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__(id, created_at, updated_at)
        self.name = name
        self.description = description
        self.privileges = privileges or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        data = super().to_dict()
        data.update({
            "name": self.name,
            "description": self.description,
            "privileges": [str(privilege.id) for privilege in self.privileges],
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], privileges: Optional[List[Privilege]] = None) -> 'Role':
        """Create entity from dictionary."""
        return cls(
            name=data["name"],
            description=data.get("description"),
            privileges=privileges or [],
            id=uuid.UUID(data["id"]) if "id" in data else None,
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else None,
        )
    
    def has_privilege(self, privilege_name: str) -> bool:
        """Check if role has a specific privilege."""
        for privilege in self.privileges:
            if privilege.name == privilege_name:
                return True
        return False
    
    def add_privilege(self, privilege: Privilege) -> None:
        """Add a privilege to the role."""
        if privilege not in self.privileges:
            self.privileges.append(privilege)
    
    def remove_privilege(self, privilege: Privilege) -> None:
        """Remove a privilege from the role."""
        if privilege in self.privileges:
            self.privileges.remove(privilege)
