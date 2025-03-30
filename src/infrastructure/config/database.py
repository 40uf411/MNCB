"""
Database configuration for PostgreSQL and DragonFlyDB.
"""
from typing import Dict, Any, Optional
import os

class DatabaseConfig:
    """Configuration for PostgreSQL database."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        user: str = "postgres",
        password: str = "postgres",
        database: str = "fastapi_db",
        min_connections: int = 1,
        max_connections: int = 10,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.min_connections = min_connections
        self.max_connections = max_connections
    
    @property
    def connection_string(self) -> str:
        """Get the database connection string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "database": self.database,
            "min_connections": self.min_connections,
            "max_connections": self.max_connections,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatabaseConfig':
        """Create config from dictionary."""
        return cls(
            host=data.get("host", "localhost"),
            port=data.get("port", 5432),
            user=data.get("user", "postgres"),
            password=data.get("password", "postgres"),
            database=data.get("database", "fastapi_db"),
            min_connections=data.get("min_connections", 1),
            max_connections=data.get("max_connections", 10),
        )
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Create config from environment variables."""
        return cls(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            database=os.getenv("POSTGRES_DB", "fastapi_db"),
            min_connections=int(os.getenv("POSTGRES_MIN_CONNECTIONS", "1")),
            max_connections=int(os.getenv("POSTGRES_MAX_CONNECTIONS", "10")),
        )


class CacheConfig:
    """Configuration for DragonFlyDB cache."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        password: Optional[str] = None,
        db: int = 0,
        socket_timeout: int = 5,
    ):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.socket_timeout = socket_timeout
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "password": self.password,
            "db": self.db,
            "socket_timeout": self.socket_timeout,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheConfig':
        """Create config from dictionary."""
        return cls(
            host=data.get("host", "localhost"),
            port=data.get("port", 6379),
            password=data.get("password"),
            db=data.get("db", 0),
            socket_timeout=data.get("socket_timeout", 5),
        )
    
    @classmethod
    def from_env(cls) -> 'CacheConfig':
        """Create config from environment variables."""
        return cls(
            host=os.getenv("DRAGONFLY_HOST", "localhost"),
            port=int(os.getenv("DRAGONFLY_PORT", "6379")),
            password=os.getenv("DRAGONFLY_PASSWORD"),
            db=int(os.getenv("DRAGONFLY_DB", "0")),
            socket_timeout=int(os.getenv("DRAGONFLY_SOCKET_TIMEOUT", "5")),
        )
