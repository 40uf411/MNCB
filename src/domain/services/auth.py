"""
Authentication service interfaces for the domain layer.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import uuid

from src.domain.entities import User

class PasswordService(ABC):
    """Service interface for password hashing and verification."""
    
    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Hash a password."""
        pass
    
    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        pass


class TokenService(ABC):
    """Service interface for token generation and validation."""
    
    @abstractmethod
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
        """Create an access token."""
        pass
    
    @abstractmethod
    def create_refresh_token(self, data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
        """Create a refresh token."""
        pass
    
    @abstractmethod
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify a token and return its payload."""
        pass
    
    @abstractmethod
    def get_user_id_from_token(self, token: str) -> Optional[uuid.UUID]:
        """Extract user ID from a token."""
        pass


class AuthService(ABC):
    """Service interface for authentication operations."""
    
    @abstractmethod
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        pass
    
    @abstractmethod
    async def get_current_user(self, token: str) -> Optional[User]:
        """Get the current user from a token."""
        pass
    
    @abstractmethod
    async def check_user_privilege(self, user: User, privilege_name: str) -> bool:
        """Check if a user has a specific privilege."""
        pass
