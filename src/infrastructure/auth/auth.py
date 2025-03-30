"""
Implementation of authentication service.
"""
from typing import Optional, List
import uuid

from src.domain.entities import User, Role, Privilege
from src.domain.services.auth import AuthService, PasswordService, TokenService
from src.domain.repositories.auth import UserRepository, RoleRepository, PrivilegeRepository

class AuthServiceImpl(AuthService):
    """Implementation of authentication service."""
    
    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        privilege_repository: PrivilegeRepository,
        password_service: PasswordService,
        token_service: TokenService,
    ):
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.privilege_repository = privilege_repository
        self.password_service = password_service
        self.token_service = token_service
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        user = await self.user_repository.get_by_username(username)
        if not user:
            # Try with email
            user = await self.user_repository.get_by_email(username)
            if not user:
                return None
        
        if not user.is_active:
            return None
        
        if not self.password_service.verify_password(password, user.hashed_password):
            return None
        
        # Load user roles
        roles = await self.user_repository.get_roles(user.id)
        user.roles = roles
        
        # Load privileges for each role
        for role in user.roles:
            privileges = await self.role_repository.get_privileges(role.id)
            role.privileges = privileges
        
        return user
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """Get the current user from a token."""
        user_id = self.token_service.get_user_id_from_token(token)
        if not user_id:
            return None
        
        user = await self.user_repository.get_by_id(user_id)
        if not user or not user.is_active:
            return None
        
        # Load user roles
        roles = await self.user_repository.get_roles(user.id)
        user.roles = roles
        
        # Load privileges for each role
        for role in user.roles:
            privileges = await self.role_repository.get_privileges(role.id)
            role.privileges = privileges
        
        return user
    
    async def check_user_privilege(self, user: User, privilege_name: str) -> bool:
        """Check if a user has a specific privilege."""
        if user.is_superuser:
            return True
        
        # If roles are not loaded, load them
        if not user.roles:
            roles = await self.user_repository.get_roles(user.id)
            user.roles = roles
            
            # Load privileges for each role
            for role in user.roles:
                privileges = await self.role_repository.get_privileges(role.id)
                role.privileges = privileges
        
        # Check if any role has the privilege
        for role in user.roles:
            for privilege in role.privileges:
                if privilege.name == privilege_name:
                    return True
        
        return False
