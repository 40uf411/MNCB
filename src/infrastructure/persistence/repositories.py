"""
Repository implementations for the authentication system.
"""
from typing import List, Optional, Dict, Any
import uuid

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from src.domain.entities import User, Role, Privilege, UserRole, RolePrivilege
from src.domain.repositories.auth import UserRepository, RoleRepository, PrivilegeRepository
from src.infrastructure.persistence.models import UserModel, RoleModel, PrivilegeModel
from src.infrastructure.persistence.database import AsyncDatabase

class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository."""
    
    def __init__(self, db: AsyncDatabase):
        self.db = db
    
    async def create(self, user: User) -> User:
        """Create a new user."""
        user_model = UserModel(
            id=user.id,
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        
        async with self.db.get_session() as session:
            session.add(user_model)
            await session.flush()
            
            # Add roles if any
            if user.roles:
                for role in user.roles:
                    role_model = await session.execute(
                        select(RoleModel).where(RoleModel.id == role.id)
                    )
                    role_model = role_model.scalar_one_or_none()
                    if role_model:
                        user_model.roles.append(role_model)
            
            await session.commit()
            await session.refresh(user_model)
            
            # Convert back to domain entity
            return self._model_to_entity(user_model)
    
    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID."""
        async with self.db.get_session() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user_model = result.scalar_one_or_none()
            
            if not user_model:
                return None
            
            return self._model_to_entity(user_model)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        async with self.db.get_session() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.username == username)
            )
            user_model = result.scalar_one_or_none()
            
            if not user_model:
                return None
            
            return self._model_to_entity(user_model)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        async with self.db.get_session() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            user_model = result.scalar_one_or_none()
            
            if not user_model:
                return None
            
            return self._model_to_entity(user_model)
    
    async def update(self, user: User) -> User:
        """Update an existing user."""
        async with self.db.get_session() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.id == user.id)
            )
            user_model = result.scalar_one_or_none()
            
            if not user_model:
                raise ValueError(f"User with ID {user.id} not found")
            
            # Update fields
            user_model.username = user.username
            user_model.email = user.email
            user_model.hashed_password = user.hashed_password
            user_model.full_name = user.full_name
            user_model.is_active = user.is_active
            user_model.is_superuser = user.is_superuser
            user_model.updated_at = user.updated_at
            
            # Update roles if provided
            if user.roles:
                # Clear existing roles
                user_model.roles = []
                
                # Add new roles
                for role in user.roles:
                    role_result = await session.execute(
                        select(RoleModel).where(RoleModel.id == role.id)
                    )
                    role_model = role_result.scalar_one_or_none()
                    if role_model:
                        user_model.roles.append(role_model)
            
            await session.commit()
            await session.refresh(user_model)
            
            return self._model_to_entity(user_model)
    
    async def delete(self, user_id: uuid.UUID) -> bool:
        """Delete a user."""
        async with self.db.get_session() as session:
            result = await session.execute(
                delete(UserModel).where(UserModel.id == user_id)
            )
            
            return result.rowcount > 0
    
    async def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users with pagination."""
        async with self.db.get_session() as session:
            result = await session.execute(
                select(UserModel).offset(skip).limit(limit)
            )
            user_models = result.scalars().all()
            
            return [self._model_to_entity(user_model) for user_model in user_models]
    
    async def add_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> UserRole:
        """Add a role to a user."""
        async with self.db.get_session() as session:
            user_result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user_model = user_result.scalar_one_or_none()
            
            if not user_model:
                raise ValueError(f"User with ID {user_id} not found")
            
            role_result = await session.execute(
                select(RoleModel).where(RoleModel.id == role_id)
            )
            role_model = role_result.scalar_one_or_none()
            
            if not role_model:
                raise ValueError(f"Role with ID {role_id} not found")
            
            user_model.roles.append(role_model)
            await session.commit()
            
            return UserRole(user_id=user_id, role_id=role_id)
    
    async def remove_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        """Remove a role from a user."""
        async with self.db.get_session() as session:
            user_result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user_model = user_result.scalar_one_or_none()
            
            if not user_model:
                return False
            
            role_result = await session.execute(
                select(RoleModel).where(RoleModel.id == role_id)
            )
            role_model = role_result.scalar_one_or_none()
            
            if not role_model or role_model not in user_model.roles:
                return False
            
            user_model.roles.remove(role_model)
            await session.commit()
            
            return True
    
    async def get_roles(self, user_id: uuid.UUID) -> List[Role]:
        """Get all roles for a user."""
        async with self.db.get_session() as session:
            user_result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user_model = user_result.scalar_one_or_none()
            
            if not user_model:
                return []
            
            return [
                Role(
                    id=role.id,
                    name=role.name,
                    description=role.description,
                    created_at=role.created_at,
                    updated_at=role.updated_at,
                )
                for role in user_model.roles
            ]
    
    def _model_to_entity(self, model: UserModel) -> User:
        """Convert a UserModel to a User entity."""
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            hashed_password=model.hashed_password,
            full_name=model.full_name,
            is_active=model.is_active,
            is_superuser=model.is_superuser,
            created_at=model.created_at,
            updated_at=model.updated_at,
            roles=[
                Role(
                    id=role.id,
                    name=role.name,
                    description=role.description,
                    created_at=role.created_at,
                    updated_at=role.updated_at,
                )
                for role in model.roles
            ],
        )


class SQLAlchemyRoleRepository(RoleRepository):
    """SQLAlchemy implementation of RoleRepository."""
    
    def __init__(self, db: AsyncDatabase):
        self.db = db
    
    async def create(self, role: Role) -> Role:
        """Create a new role."""
        role_model = RoleModel(
            id=role.id,
            name=role.name,
            description=role.description,
            created_at=role.created_at,
            updated_at=role.updated_at,
        )
        
        async with self.db.get_session() as session:
            session.add(role_model)
            await session.flush()
            
            # Add privileges if any
            if role.privileges:
                for privilege in role.privileges:
                    privilege_model = await session.execute(
                        select(PrivilegeModel).where(PrivilegeModel.id == privilege.id)
                    )
                    privilege_model = privilege_model.scalar_one_or_none()
                    if privilege_model:
                        role_model.privileges.append(privilege_model)
            
            await session.commit()
            await session.refresh(role_model)
            
            # Convert back to domain entity
            return self._model_to_entity(role_model)
    
    async def get_by_id(self, role_id: uuid.UUID) -> Optional[Role]:
        """Get role by ID."""
        async with self.db.get_session() as session:
            result = await session.execute(
                select(RoleModel).where(RoleModel.id == role_id)
            )
            role_model = result.scalar_one_or_none()
            
            if not role_model:
                return None
            
            return self._model_to_entity(role_model)
    
    async def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        async with self.db.get_session() as session:
            result = await session.execute(
                select(RoleModel).where(RoleModel.name == name)
            )
            role_model = result.scalar_one_or_none()
            
            if not role_model:
                return None
            
            return self._model_to_entity(role_model)
    
    async def update(self, role: Role) -> Role:
        """Update an existing role."""
        async with self.db.get_session() as session:
            result = await session.execute(
                select(RoleModel).where(RoleModel.id == role.id)
            )
            role_model = result.scalar_one_or_none()
            
            if not role_model:
                raise ValueError(f"Role with ID {role.id} not found")
            
            # Update fields
            role_model.name = role.name
            role_model.description = role.description
            role_model.updated_at = role.updated_at
            
            # Update privileges if provided
            if role.privileges:
                # Clear existing privileges
                role_model.privileges = []
                
                # Add new privileges
                for privilege in role.privileges:
                    privilege_result = await session.execute(
                        select(PrivilegeModel).where(PrivilegeModel.id == privilege.id)
                    )
                    privilege_model = privilege_result.scalar_one_or_none()
                    if privilege_model:
                        role_model.privileges.append(privilege_model)
            
            await session.commit()
            await session.refresh(role_model)
            
            return self._model_to_entity(role_model)
    
    async def delete(self, role_id: uuid.UUID) -> bool:
        """Delete a role."""
        async with self.db.get_session() as session:
            result = await session.execute(
                delete(RoleModel).where(RoleModel.id == role_id)
            )
            
            return result.rowcount > 0
    
    async def list(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """List roles with pagination."""
        async with self.db.get_session() as session:
            result = await session.execute(
                select(RoleModel).offset(skip).limit(limit)
            )
            role_models = result.scalars().all()
            
            return [self._model_to_entity(role_model) for role_model in role_models]
    
    async def add_privilege(self, role_id: uuid.UUID, privilege_id: uuid.UUID) -> RolePrivilege:
        """Add a privilege to a role."""
        async with self.db.get_session() as session:
            role_result = await session.execute(
                select(RoleModel).where(RoleModel.id == role_id)
            )
            role_model = role_result.scalar_one_or_none()
            
            if not role_model:
                raise ValueError(f"Role with ID {role_id} not found")
            
            privilege_result = await session.execute(
                select(PrivilegeModel).where(PrivilegeModel.id == privilege_id)
            )
            privilege_model = privilege_result.scalar_one_or_none()
            
            if not privilege_model:
                raise ValueError(f"Privilege with ID {privilege_id} not found")
            
            role_model.privileges.append(privilege_model)
            await session.commit()
            
            return RolePrivilege(role_id=role_id, privilege_id=privilege_id)
    
    async def remove_privilege(self, role_id: uuid.UUID, privilege_id: uuid.UUID) -> bool:
        """Remove a privilege from a role."""
        async with self.db.get_session() as session:
            role_result = await session.execute(
                select(RoleModel).where(RoleModel.id == role_id)
            )
            role_model = role_result.scalar_one_or_none()
            
            if not role_model:
                return False
            
            privilege_result = await session.execute(
                select(PrivilegeModel).where(PrivilegeModel.id == privilege_id)
            )
            privilege_model = privilege_result.scalar_one_or_none()
            
            if not privilege_model or privilege_model not in role_model.privileges:
                return False
            
            role_model.privileges.remove(privilege_model)
            await session.commit()
            
            return True
    
    async def get_privileges(self, role_id: uuid.UUID) -> List[Privilege]:
        """Get all privileges for a role."""
        async with self.db.get_session() as session:
            role_result = await session.execute(
                select(RoleModel).where(RoleModel.id == role_id)
            )
            role_model = role_result.scalar_one_or_none()
            
            if not role_model:
                return []
            
            return [
                Privilege(
                    id=privilege.id,
                    name=privilege.name,
                    description=privilege.description,
                    created_at=privilege.created_at,
                    updated_at=privilege.updated_at,
                )
                for privilege in role_model.privileges
            ]
    
    def _model_to_entity(self, model: RoleModel) -> Role:
        """Convert a RoleModel to a Role entity."""
        return Role(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
            privileges=[
                Privilege(
                    id=privilege.id,
                    name=privilege.name,
                    description=privilege.description,
                    created_at=privilege.created_at,
                    updated_at=privilege.updated_at,
                )
                for privilege in model.privileges
            ],
        )


class SQLAlchemyPrivilegeRepository(PrivilegeRepository):
    """SQLAlchemy implementation of PrivilegeRepository."""
    
    def __init__(self, db: AsyncDatabase):
        self.db = db
    
    async def create(self, privilege: Privilege) -> Privilege:
        """Create a new privilege."""
        privilege_model = PrivilegeModel(
            id=privilege.id,
            name=privilege.name,
            description=privilege.description,
            created_at=privilege.created_at,
            updated_at=privilege.updated_at,
        )
        
        async with self.db.get_session() as session:
            session.add(privilege_model)
            await session.commit()
            await session.refresh(privilege_model)
            
            # Convert back to domain entity
            return self._model_to_entity(privilege_model)
    
    async def get_by_id(self, privilege_id: uuid.UUID) -> Optional[Privilege]:
        """Get privilege by ID."""
        async with self.db.get_session() as session:
            result = await session.execute(
                select(PrivilegeModel).where(PrivilegeModel.id == privilege_id)
            )
            privilege_model = result.scalar_one_or_none()
            
            if not privilege_model:
                return None
            
            return self._model_to_entity(privilege_model)
    
    async def get_by_name(self, name: str) -> Optional[Privilege]:
        """Get privilege by name."""
        async with self.db.get_session() as session:
            result = await session.execute(
                select(PrivilegeModel).where(PrivilegeModel.name == name)
            )
            privilege_model = result.scalar_one_or_none()
            
            if not privilege_model:
                return None
            
            return self._model_to_entity(privilege_model)
    
    async def update(self, privilege: Privilege) -> Privilege:
        """Update an existing privilege."""
        async with self.db.get_session() as session:
            result = await session.execute(
                select(PrivilegeModel).where(PrivilegeModel.id == privilege.id)
            )
            privilege_model = result.scalar_one_or_none()
            
            if not privilege_model:
                raise ValueError(f"Privilege with ID {privilege.id} not found")
            
            # Update fields
            privilege_model.name = privilege.name
            privilege_model.description = privilege.description
            privilege_model.updated_at = privilege.updated_at
            
            await session.commit()
            await session.refresh(privilege_model)
            
            return self._model_to_entity(privilege_model)
    
    async def delete(self, privilege_id: uuid.UUID) -> bool:
        """Delete a privilege."""
        async with self.db.get_session() as session:
            result = await session.execute(
                delete(PrivilegeModel).where(PrivilegeModel.id == privilege_id)
            )
            
            return result.rowcount > 0
    
    async def list(self, skip: int = 0, limit: int = 100) -> List[Privilege]:
        """List privileges with pagination."""
        async with self.db.get_session() as session:
            result = await session.execute(
                select(PrivilegeModel).offset(skip).limit(limit)
            )
            privilege_models = result.scalars().all()
            
            return [self._model_to_entity(privilege_model) for privilege_model in privilege_models]
    
    def _model_to_entity(self, model: PrivilegeModel) -> Privilege:
        """Convert a PrivilegeModel to a Privilege entity."""
        return Privilege(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
