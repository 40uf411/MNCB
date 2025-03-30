"""
Repository interfaces for the authentication system.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import uuid

from src.domain.entities import User, Role, Privilege, UserRole, RolePrivilege

class UserRepository(ABC):
    """Repository interface for User entity."""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: uuid.UUID) -> bool:
        """Delete a user."""
        pass
    
    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users with pagination."""
        pass
    
    @abstractmethod
    async def add_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> UserRole:
        """Add a role to a user."""
        pass
    
    @abstractmethod
    async def remove_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        """Remove a role from a user."""
        pass
    
    @abstractmethod
    async def get_roles(self, user_id: uuid.UUID) -> List[Role]:
        """Get all roles for a user."""
        pass


class RoleRepository(ABC):
    """Repository interface for Role entity."""
    
    @abstractmethod
    async def create(self, role: Role) -> Role:
        """Create a new role."""
        pass
    
    @abstractmethod
    async def get_by_id(self, role_id: uuid.UUID) -> Optional[Role]:
        """Get role by ID."""
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        pass
    
    @abstractmethod
    async def update(self, role: Role) -> Role:
        """Update an existing role."""
        pass
    
    @abstractmethod
    async def delete(self, role_id: uuid.UUID) -> bool:
        """Delete a role."""
        pass
    
    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """List roles with pagination."""
        pass
    
    @abstractmethod
    async def add_privilege(self, role_id: uuid.UUID, privilege_id: uuid.UUID) -> RolePrivilege:
        """Add a privilege to a role."""
        pass
    
    @abstractmethod
    async def remove_privilege(self, role_id: uuid.UUID, privilege_id: uuid.UUID) -> bool:
        """Remove a privilege from a role."""
        pass
    
    @abstractmethod
    async def get_privileges(self, role_id: uuid.UUID) -> List[Privilege]:
        """Get all privileges for a role."""
        pass


class PrivilegeRepository(ABC):
    """Repository interface for Privilege entity."""
    
    @abstractmethod
    async def create(self, privilege: Privilege) -> Privilege:
        """Create a new privilege."""
        pass
    
    @abstractmethod
    async def get_by_id(self, privilege_id: uuid.UUID) -> Optional[Privilege]:
        """Get privilege by ID."""
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Privilege]:
        """Get privilege by name."""
        pass
    
    @abstractmethod
    async def update(self, privilege: Privilege) -> Privilege:
        """Update an existing privilege."""
        pass
    
    @abstractmethod
    async def delete(self, privilege_id: uuid.UUID) -> bool:
        """Delete a privilege."""
        pass
    
    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[Privilege]:
        """List privileges with pagination."""
        pass
