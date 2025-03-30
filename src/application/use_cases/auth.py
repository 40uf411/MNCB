"""
Application use cases for authentication.
"""
from typing import Optional, Dict, Any, Tuple
import uuid

from src.domain.entities import User, Role, Privilege
from src.domain.repositories.auth import UserRepository, RoleRepository, PrivilegeRepository
from src.domain.services.auth import PasswordService, TokenService, AuthService

class RegisterUserUseCase:
    """Use case for registering a new user."""
    
    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
    ):
        self.user_repository = user_repository
        self.password_service = password_service
    
    async def execute(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> User:
        """Register a new user."""
        # Check if username already exists
        existing_user = await self.user_repository.get_by_username(username)
        if existing_user:
            raise ValueError(f"Username '{username}' already exists")
        
        # Check if email already exists
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user:
            raise ValueError(f"Email '{email}' already exists")
        
        # Hash password
        hashed_password = self.password_service.hash_password(password)
        
        # Create user entity
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=is_active,
            is_superuser=is_superuser,
        )
        
        # Save user to repository
        return await self.user_repository.create(user)


class LoginUserUseCase:
    """Use case for logging in a user."""
    
    def __init__(
        self,
        auth_service: AuthService,
        token_service: TokenService,
    ):
        self.auth_service = auth_service
        self.token_service = token_service
    
    async def execute(
        self,
        username: str,
        password: str,
    ) -> Optional[Dict[str, Any]]:
        """Login a user and return tokens."""
        # Authenticate user
        user = await self.auth_service.authenticate_user(username, password)
        if not user:
            return None
        
        # Generate tokens
        access_token = self.token_service.create_access_token({"sub": str(user.id)})
        refresh_token = self.token_service.create_refresh_token({"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "roles": [{"id": str(role.id), "name": role.name} for role in user.roles],
            },
        }


class RefreshTokenUseCase:
    """Use case for refreshing an access token."""
    
    def __init__(
        self,
        token_service: TokenService,
        user_repository: UserRepository,
    ):
        self.token_service = token_service
        self.user_repository = user_repository
    
    async def execute(
        self,
        refresh_token: str,
    ) -> Optional[Dict[str, Any]]:
        """Refresh an access token."""
        # Verify refresh token
        payload = self.token_service.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        
        # Get user ID from token
        user_id_str = payload.get("sub")
        if not user_id_str:
            return None
        
        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            return None
        
        # Get user from repository
        user = await self.user_repository.get_by_id(user_id)
        if not user or not user.is_active:
            return None
        
        # Generate new access token
        access_token = self.token_service.create_access_token({"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }


class GetCurrentUserUseCase:
    """Use case for getting the current user from a token."""
    
    def __init__(
        self,
        auth_service: AuthService,
    ):
        self.auth_service = auth_service
    
    async def execute(
        self,
        token: str,
    ) -> Optional[User]:
        """Get the current user from a token."""
        return await self.auth_service.get_current_user(token)


class CreateRoleUseCase:
    """Use case for creating a new role."""
    
    def __init__(
        self,
        role_repository: RoleRepository,
    ):
        self.role_repository = role_repository
    
    async def execute(
        self,
        name: str,
        description: Optional[str] = None,
    ) -> Role:
        """Create a new role."""
        # Check if role already exists
        existing_role = await self.role_repository.get_by_name(name)
        if existing_role:
            raise ValueError(f"Role '{name}' already exists")
        
        # Create role entity
        role = Role(
            name=name,
            description=description,
        )
        
        # Save role to repository
        return await self.role_repository.create(role)


class CreatePrivilegeUseCase:
    """Use case for creating a new privilege."""
    
    def __init__(
        self,
        privilege_repository: PrivilegeRepository,
    ):
        self.privilege_repository = privilege_repository
    
    async def execute(
        self,
        name: str,
        description: Optional[str] = None,
    ) -> Privilege:
        """Create a new privilege."""
        # Check if privilege already exists
        existing_privilege = await self.privilege_repository.get_by_name(name)
        if existing_privilege:
            raise ValueError(f"Privilege '{name}' already exists")
        
        # Create privilege entity
        privilege = Privilege(
            name=name,
            description=description,
        )
        
        # Save privilege to repository
        return await self.privilege_repository.create(privilege)


class AssignRoleToUserUseCase:
    """Use case for assigning a role to a user."""
    
    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
    ):
        self.user_repository = user_repository
        self.role_repository = role_repository
    
    async def execute(
        self,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
    ) -> User:
        """Assign a role to a user."""
        # Check if user exists
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Check if role exists
        role = await self.role_repository.get_by_id(role_id)
        if not role:
            raise ValueError(f"Role with ID {role_id} not found")
        
        # Add role to user
        await self.user_repository.add_role(user_id, role_id)
        
        # Get updated user
        updated_user = await self.user_repository.get_by_id(user_id)
        if not updated_user:
            raise ValueError(f"User with ID {user_id} not found after update")
        
        return updated_user


class AssignPrivilegeToRoleUseCase:
    """Use case for assigning a privilege to a role."""
    
    def __init__(
        self,
        role_repository: RoleRepository,
        privilege_repository: PrivilegeRepository,
    ):
        self.role_repository = role_repository
        self.privilege_repository = privilege_repository
    
    async def execute(
        self,
        role_id: uuid.UUID,
        privilege_id: uuid.UUID,
    ) -> Role:
        """Assign a privilege to a role."""
        # Check if role exists
        role = await self.role_repository.get_by_id(role_id)
        if not role:
            raise ValueError(f"Role with ID {role_id} not found")
        
        # Check if privilege exists
        privilege = await self.privilege_repository.get_by_id(privilege_id)
        if not privilege:
            raise ValueError(f"Privilege with ID {privilege_id} not found")
        
        # Add privilege to role
        await self.role_repository.add_privilege(role_id, privilege_id)
        
        # Get updated role
        updated_role = await self.role_repository.get_by_id(role_id)
        if not updated_role:
            raise ValueError(f"Role with ID {role_id} not found after update")
        
        return updated_role


class CheckUserPrivilegeUseCase:
    """Use case for checking if a user has a specific privilege."""
    
    def __init__(
        self,
        auth_service: AuthService,
    ):
        self.auth_service = auth_service
    
    async def execute(
        self,
        user: User,
        privilege_name: str,
    ) -> bool:
        """Check if a user has a specific privilege."""
        return await self.auth_service.check_user_privilege(user, privilege_name)
