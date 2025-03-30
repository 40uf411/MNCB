"""
Database connection and session management.
"""
from typing import Generator, Optional
from contextlib import contextmanager, asynccontextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.infrastructure.config import DatabaseConfig

class Database:
    """Database connection manager for PostgreSQL."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = create_engine(
            config.connection_string,
            pool_pre_ping=True,
            pool_size=config.min_connections,
            max_overflow=config.max_connections - config.min_connections,
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_tables(self, base) -> None:
        """Create all tables defined in the base."""
        base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self, base) -> None:
        """Drop all tables defined in the base."""
        base.metadata.drop_all(bind=self.engine)


class AsyncDatabase:
    """Async database connection manager for PostgreSQL."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        # Convert connection string to async format
        async_conn_string = config.connection_string.replace("postgresql://", "postgresql+asyncpg://")
        self.engine = create_async_engine(
            async_conn_string,
            pool_pre_ping=True,
            pool_size=config.min_connections,
            max_overflow=config.max_connections - config.min_connections,
        )
        self.SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    @asynccontextmanager
    async def get_session(self) -> Generator[AsyncSession, None, None]:
        """Get an async database session."""
        session = self.SessionLocal()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    async def create_tables(self, base) -> None:
        """Create all tables defined in the base."""
        async with self.engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all)
    
    async def drop_tables(self, base) -> None:
        """Drop all tables defined in the base."""
        async with self.engine.begin() as conn:
            await conn.run_sync(base.metadata.drop_all)
