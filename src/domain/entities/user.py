"""
User entity for the authentication system.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

from .base import BaseEntity

class User(BaseEntity):
    """User entity representing a system user."""
    
    username: str
    email: str
    hashed_password: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    roles: List['Role']
    
    def __init__(
        self,
        username: str,
        email: str,
        hashed_password: str,
        full_name: Optional[str] = None,
        is_active: bool = True,
        is_superuser: bool = False,
        roles: Optional[List['Role']] = None,
        id: Optional[uuid.UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__(id, created_at, updated_at)
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.full_name = full_name
        self.is_active = is_active
        self.is_superuser = is_superuser
        self.roles = roles or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        data = super().to_dict()
        data.update({
            "username": self.username,
            "email": self.email,
            "hashed_password": self.hashed_password,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "roles": [str(role.id) for role in self.roles],
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], roles: Optional[List['Role']] = None) -> 'User':
        """Create entity from dictionary."""
        return cls(
            username=data["username"],
            email=data["email"],
            hashed_password=data["hashed_password"],
            full_name=data.get("full_name"),
            is_active=data.get("is_active", True),
            is_superuser=data.get("is_superuser", False),
            roles=roles or [],
            id=uuid.UUID(data["id"]) if "id" in data else None,
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else None,
        )
    
    def has_privilege(self, privilege_name: str) -> bool:
        """Check if user has a specific privilege through any of their roles."""
        if self.is_superuser:
            return True
        
        for role in self.roles:
            for privilege in role.privileges:
                if privilege.name == privilege_name:
                    return True
        
        return False
