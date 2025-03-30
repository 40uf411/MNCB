"""
Association classes for many-to-many relationships in the authentication system.
"""
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from .base import BaseEntity
from .user import User
from .role import Role
from .privilege import Privilege

class UserRole(BaseEntity):
    """Association class for the many-to-many relationship between User and Role."""
    
    user_id: uuid.UUID
    role_id: uuid.UUID
    
    def __init__(
        self,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
        id: Optional[uuid.UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__(id, created_at, updated_at)
        self.user_id = user_id
        self.role_id = role_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        data = super().to_dict()
        data.update({
            "user_id": str(self.user_id),
            "role_id": str(self.role_id),
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserRole':
        """Create entity from dictionary."""
        return cls(
            user_id=uuid.UUID(data["user_id"]),
            role_id=uuid.UUID(data["role_id"]),
            id=uuid.UUID(data["id"]) if "id" in data else None,
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else None,
        )


class RolePrivilege(BaseEntity):
    """Association class for the many-to-many relationship between Role and Privilege."""
    
    role_id: uuid.UUID
    privilege_id: uuid.UUID
    
    def __init__(
        self,
        role_id: uuid.UUID,
        privilege_id: uuid.UUID,
        id: Optional[uuid.UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__(id, created_at, updated_at)
        self.role_id = role_id
        self.privilege_id = privilege_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        data = super().to_dict()
        data.update({
            "role_id": str(self.role_id),
            "privilege_id": str(self.privilege_id),
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RolePrivilege':
        """Create entity from dictionary."""
        return cls(
            role_id=uuid.UUID(data["role_id"]),
            privilege_id=uuid.UUID(data["privilege_id"]),
            id=uuid.UUID(data["id"]) if "id" in data else None,
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else None,
        )
