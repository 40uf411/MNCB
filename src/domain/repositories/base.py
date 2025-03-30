"""
Base repository interface with soft delete functionality.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic
from datetime import datetime
import uuid

from src.domain.entities.base import BaseEntity
from src.infrastructure.config.platform import PlatformConfig, DeleteType

T = TypeVar('T', bound=BaseEntity)


class BaseRepository(Generic[T], ABC):
    """Base repository interface with soft delete functionality."""
    
    def __init__(self, platform_config: PlatformConfig):
        self.platform_config = platform_config
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity."""
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: uuid.UUID, include_deleted: bool = False) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an existing entity."""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: uuid.UUID) -> bool:
        """Delete an entity.
        
        If platform_config.delete_type is DeleteType.SOFT, this will perform a soft delete.
        If platform_config.delete_type is DeleteType.HARD, this will perform a hard delete.
        """
        pass
    
    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100, include_deleted: bool = False) -> List[T]:
        """List entities with pagination."""
        pass
    
    @abstractmethod
    async def restore(self, entity_id: uuid.UUID) -> bool:
        """Restore a soft-deleted entity."""
        pass
    
    async def perform_delete(self, entity_id: uuid.UUID) -> bool:
        """Perform delete operation based on platform configuration."""
        if self.platform_config.delete_type == DeleteType.SOFT:
            return await self.soft_delete(entity_id)
        else:
            return await self.hard_delete(entity_id)
    
    @abstractmethod
    async def soft_delete(self, entity_id: uuid.UUID) -> bool:
        """Perform a soft delete by setting deleted_at timestamp."""
        pass
    
    @abstractmethod
    async def hard_delete(self, entity_id: uuid.UUID) -> bool:
        """Perform a hard delete by removing the entity from the database."""
        pass
