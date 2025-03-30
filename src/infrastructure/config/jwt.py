"""
JWT authentication configuration.
"""
from typing import Dict, Any, Optional
import os

class JWTConfig:
    """Configuration for JWT authentication."""
    
    def __init__(
        self,
        secret_key: str = "your-secret-key",
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "secret_key": self.secret_key,
            "algorithm": self.algorithm,
            "access_token_expire_minutes": self.access_token_expire_minutes,
            "refresh_token_expire_days": self.refresh_token_expire_days,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JWTConfig':
        """Create config from dictionary."""
        return cls(
            secret_key=data.get("secret_key", "your-secret-key"),
            algorithm=data.get("algorithm", "HS256"),
            access_token_expire_minutes=data.get("access_token_expire_minutes", 30),
            refresh_token_expire_days=data.get("refresh_token_expire_days", 7),
        )
    
    @classmethod
    def from_env(cls) -> 'JWTConfig':
        """Create config from environment variables."""
        return cls(
            secret_key=os.getenv("JWT_SECRET_KEY", "your-secret-key"),
            algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            access_token_expire_minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
            refresh_token_expire_days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")),
        )
