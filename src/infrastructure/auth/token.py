"""
Implementation of token service for authentication using JWT.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import uuid
import jwt

from src.domain.services.auth import TokenService

class TokenServiceImpl(TokenService):
    """Implementation of token service using PyJWT."""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256", access_token_expire_minutes: int = 30):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
        """Create an access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            minutes=expires_delta if expires_delta else self.access_token_expire_minutes
        )
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
        """Create a refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            days=7 if expires_delta is None else expires_delta
        )
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify a token and return its payload."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            return None
    
    def get_user_id_from_token(self, token: str) -> Optional[uuid.UUID]:
        """Extract user ID from a token."""
        payload = self.verify_token(token)
        if payload and "sub" in payload:
            try:
                return uuid.UUID(payload["sub"])
            except ValueError:
                return None
        return None
