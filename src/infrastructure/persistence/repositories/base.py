"""
Base SQLAlchemy repository implementation with soft delete functionality.
"""
from typing import List, Optional, Dict, Any, TypeVar, Generic, Type
from datetime import datetime
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, and_, or_

from src.domain.entities.base import BaseEntity
from src.domain.repositories.base import BaseRepository
from src.infrastructure.config.platform import PlatformConfig, DeleteType
from src.infrastructure.persistence.models.base import BaseModel
from src.infrastructure.persistence.database import AsyncDatabase

T = TypeVar('T', bound=BaseEntity)
M = TypeVar('M', bound=BaseModel)


class BaseSQLAlchemyRepository(BaseRepository[T], Generic[T, M]):
    """Base SQLAlchemy repository implementation with soft delete functionality."""
    
    def __init__(self, db: AsyncDatabase, platform_config: PlatformConfig, entity_class: Type[T], model_class: Type[M]):
        super().__init__(platform_config)
        self.db = db
        self.entity_class = entity_class
        self.model_class = model_class
    
    async def create(self, entity: T) -> T:
        """Create a new entity."""
        model = self._entity_to_model(entity)
        
        async with self.db.get_session() as session:
            session.add(model)
            await session.commit()
            await session.refresh(model)
            
            return self._model_to_entity(model)
    
    async def get_by_id(self, entity_id: uuid.UUID, include_deleted: bool = False) -> Optional[T]:
        """Get entity by ID."""
        async with self.db.get_session() as session:
            query = select(self.model_class).where(self.model_class.id == entity_id)
            
            if not include_deleted:
                query = query.where(or_(self.model_class.deleted_at == None, self.model_class.deleted_at > datetime.utcnow()))
            
            result = await session.execute(query)
            model = result.scalar_one_or_none()
            
            if not model:
                return None
            
            return self._model_to_entity(model)
    
    async def update(self, entity: T) -> T:
        """Update an existing entity."""
        async with self.db.get_session() as session:
            query = select(self.model_class).where(self.model_class.id == entity.id)
            
            # Don't allow updating deleted entities
            query = query.where(or_(self.model_class.deleted_at == None, self.model_class.deleted_at > datetime.utcnow()))
            
            result = await session.execute(query)
            model = result.scalar_one_or_none()
            
            if not model:
                raise ValueError(f"Entity with ID {entity.id} not found or is deleted")
            
            # Update model from entity
            self._update_model_from_entity(model, entity)
            model.updated_at = datetime.utcnow()
            
            await session.commit()
            await session.refresh(model)
            
            return self._model_to_entity(model)
    
    async def delete(self, entity_id: uuid.UUID) -> bool:
        """Delete an entity based on platform configuration."""
        return await self.perform_delete(entity_id)
    
    async def soft_delete(self, entity_id: uuid.UUID) -> bool:
        """Perform a soft delete by setting deleted_at timestamp."""
        async with self.db.get_session() as session:
            query = select(self.model_class).where(self.model_class.id == entity_id)
            
            # Don't allow deleting already deleted entities
            query = query.where(or_(self.model_class.deleted_at == None, self.model_class.deleted_at > datetime.utcnow()))
            
            result = await session.execute(query)
            model = result.scalar_one_or_none()
            
            if not model:
                return False
            
            model.deleted_at = datetime.utcnow()
            await session.commit()
            
            return True
    
    async def hard_delete(self, entity_id: uuid.UUID) -> bool:
        """Perform a hard delete by removing the entity from the database."""
        async with self.db.get_session() as session:
            result = await session.execute(
                delete(self.model_class).where(self.model_class.id == entity_id)
            )
            
            await session.commit()
            
            return result.rowcount > 0
    
    async def list(self, skip: int = 0, limit: int = 100, include_deleted: bool = False) -> List[T]:
        """List entities with pagination."""
        async with self.db.get_session() as session:
            query = select(self.model_class)
            
            if not include_deleted:
                query = query.where(or_(self.model_class.deleted_at == None, self.model_class.deleted_at > datetime.utcnow()))
            
            query = query.offset(skip).limit(limit)
            
            result = await session.execute(query)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
    
    async def restore(self, entity_id: uuid.UUID) -> bool:
        """Restore a soft-deleted entity."""
        async with self.db.get_session() as session:
            query = select(self.model_class).where(self.model_class.id == entity_id)
            
            # Only allow restoring deleted entities
            query = query.where(self.model_class.deleted_at != None)
            
            result = await session.execute(query)
            model = result.scalar_one_or_none()
            
            if not model:
                return False
            
            model.deleted_at = None
            model.updated_at = datetime.utcnow()
            await session.commit()
            
            return True
    
    def _entity_to_model(self, entity: T) -> M:
        """Convert entity to model. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _entity_to_model")
    
    def _model_to_entity(self, model: M) -> T:
        """Convert model to entity. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _model_to_entity")
    
    def _update_model_from_entity(self, model: M, entity: T) -> None:
        """Update model from entity. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _update_model_from_entity")
