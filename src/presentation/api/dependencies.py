"""
API dependencies for authentication.
"""
from typing import Generator, Optional
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.domain.entities import User
from src.domain.repositories.auth import UserRepository, RoleRepository, PrivilegeRepository
from src.domain.services.auth import PasswordService, TokenService, AuthService
from src.application.use_cases.auth import (
    RegisterUserUseCase,
    LoginUserUseCase,
    RefreshTokenUseCase,
    GetCurrentUserUseCase,
    CreateRoleUseCase,
    CreatePrivilegeUseCase,
    AssignRoleToUserUseCase,
    AssignPrivilegeToRoleUseCase,
    CheckUserPrivilegeUseCase,
)
from src.infrastructure.persistence import (
    AsyncDatabase,
    SQLAlchemyUserRepository,
    SQLAlchemyRoleRepository,
    SQLAlchemyPrivilegeRepository,
)
from src.infrastructure.auth import (
    PasswordServiceImpl,
    TokenServiceImpl,
    AuthServiceImpl,
)
from src.infrastructure.config import DatabaseConfig, JWTConfig

# OAuth2 token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# Configuration
def get_db_config() -> DatabaseConfig:
    """Get database configuration."""
    return DatabaseConfig.from_env()

def get_jwt_config() -> JWTConfig:
    """Get JWT configuration."""
    return JWTConfig.from_env()

# Database
def get_db() -> AsyncDatabase:
    """Get database connection."""
    return AsyncDatabase(get_db_config())

# Repositories
def get_user_repository(db: AsyncDatabase = Depends(get_db)) -> UserRepository:
    """Get user repository."""
    return SQLAlchemyUserRepository(db)

def get_role_repository(db: AsyncDatabase = Depends(get_db)) -> RoleRepository:
    """Get role repository."""
    return SQLAlchemyRoleRepository(db)

def get_privilege_repository(db: AsyncDatabase = Depends(get_db)) -> PrivilegeRepository:
    """Get privilege repository."""
    return SQLAlchemyPrivilegeRepository(db)

# Services
def get_password_service() -> PasswordService:
    """Get password service."""
    return PasswordServiceImpl()

def get_token_service(jwt_config: JWTConfig = Depends(get_jwt_config)) -> TokenService:
    """Get token service."""
    return TokenServiceImpl(
        secret_key=jwt_config.secret_key,
        algorithm=jwt_config.algorithm,
        access_token_expire_minutes=jwt_config.access_token_expire_minutes,
    )

def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    role_repository: RoleRepository = Depends(get_role_repository),
    privilege_repository: PrivilegeRepository = Depends(get_privilege_repository),
    password_service: PasswordService = Depends(get_password_service),
    token_service: TokenService = Depends(get_token_service),
) -> AuthService:
    """Get authentication service."""
    return AuthServiceImpl(
        user_repository=user_repository,
        role_repository=role_repository,
        privilege_repository=privilege_repository,
        password_service=password_service,
        token_service=token_service,
    )

# Use cases
def get_register_user_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    password_service: PasswordService = Depends(get_password_service),
) -> RegisterUserUseCase:
    """Get register user use case."""
    return RegisterUserUseCase(
        user_repository=user_repository,
        password_service=password_service,
    )

def get_login_user_use_case(
    auth_service: AuthService = Depends(get_auth_service),
    token_service: TokenService = Depends(get_token_service),
) -> LoginUserUseCase:
    """Get login user use case."""
    return LoginUserUseCase(
        auth_service=auth_service,
        token_service=token_service,
    )

def get_refresh_token_use_case(
    token_service: TokenService = Depends(get_token_service),
    user_repository: UserRepository = Depends(get_user_repository),
) -> RefreshTokenUseCase:
    """Get refresh token use case."""
    return RefreshTokenUseCase(
        token_service=token_service,
        user_repository=user_repository,
    )

def get_current_user_use_case(
    auth_service: AuthService = Depends(get_auth_service),
) -> GetCurrentUserUseCase:
    """Get current user use case."""
    return GetCurrentUserUseCase(
        auth_service=auth_service,
    )

def get_create_role_use_case(
    role_repository: RoleRepository = Depends(get_role_repository),
) -> CreateRoleUseCase:
    """Get create role use case."""
    return CreateRoleUseCase(
        role_repository=role_repository,
    )

def get_create_privilege_use_case(
    privilege_repository: PrivilegeRepository = Depends(get_privilege_repository),
) -> CreatePrivilegeUseCase:
    """Get create privilege use case."""
    return CreatePrivilegeUseCase(
        privilege_repository=privilege_repository,
    )

def get_assign_role_to_user_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    role_repository: RoleRepository = Depends(get_role_repository),
) -> AssignRoleToUserUseCase:
    """Get assign role to user use case."""
    return AssignRoleToUserUseCase(
        user_repository=user_repository,
        role_repository=role_repository,
    )

def get_assign_privilege_to_role_use_case(
    role_repository: RoleRepository = Depends(get_role_repository),
    privilege_repository: PrivilegeRepository = Depends(get_privilege_repository),
) -> AssignPrivilegeToRoleUseCase:
    """Get assign privilege to role use case."""
    return AssignPrivilegeToRoleUseCase(
        role_repository=role_repository,
        privilege_repository=privilege_repository,
    )

def get_check_user_privilege_use_case(
    auth_service: AuthService = Depends(get_auth_service),
) -> CheckUserPrivilegeUseCase:
    """Get check user privilege use case."""
    return CheckUserPrivilegeUseCase(
        auth_service=auth_service,
    )

# Current user dependencies
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    current_user_use_case: GetCurrentUserUseCase = Depends(get_current_user_use_case),
) -> User:
    """Get current user from token."""
    user = await current_user_use_case.execute(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user

async def get_current_active_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get current active superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user

# Privilege check dependency
def require_privilege(privilege_name: str):
    """Dependency factory for checking if a user has a specific privilege."""
    
    async def check_privilege(
        current_user: User = Depends(get_current_active_user),
        check_user_privilege_use_case: CheckUserPrivilegeUseCase = Depends(get_check_user_privilege_use_case),
    ) -> User:
        """Check if current user has the required privilege."""
        has_privilege = await check_user_privilege_use_case.execute(current_user, privilege_name)
        if not has_privilege:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"The user doesn't have the required privilege: {privilege_name}",
            )
        return current_user
    
    return check_privilege
