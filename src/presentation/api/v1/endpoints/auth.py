"""
API endpoints for authentication.
"""
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src.domain.entities import User
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
from src.presentation.api.schemas import (
    UserCreate,
    UserResponse,
    RoleCreate,
    RoleResponse,
    PrivilegeCreate,
    PrivilegeResponse,
    Token,
    RefreshToken,
    UserRoleCreate,
    RolePrivilegeCreate,
    LoginRequest,
)
from src.presentation.api.dependencies import (
    get_register_user_use_case,
    get_login_user_use_case,
    get_refresh_token_use_case,
    get_current_user_use_case,
    get_create_role_use_case,
    get_create_privilege_use_case,
    get_assign_role_to_user_use_case,
    get_assign_privilege_to_role_use_case,
    get_check_user_privilege_use_case,
    get_current_user,
    get_current_active_user,
    get_current_active_superuser,
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    register_user_use_case: RegisterUserUseCase = Depends(get_register_user_use_case),
):
    """Register a new user."""
    try:
        user = await register_user_use_case.execute(
            username=user_in.username,
            email=user_in.email,
            password=user_in.password,
            full_name=user_in.full_name,
            is_active=user_in.is_active,
            is_superuser=user_in.is_superuser,
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    login_user_use_case: LoginUserUseCase = Depends(get_login_user_use_case),
):
    """Login a user and return tokens."""
    result = await login_user_use_case.execute(
        username=login_data.username,
        password=login_data.password,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return result


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    login_user_use_case: LoginUserUseCase = Depends(get_login_user_use_case),
):
    """OAuth2 compatible token login, get an access token for future requests."""
    result = await login_user_use_case.execute(
        username=form_data.username,
        password=form_data.password,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return result


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token_data: RefreshToken,
    refresh_token_use_case: RefreshTokenUseCase = Depends(get_refresh_token_use_case),
):
    """Refresh an access token."""
    result = await refresh_token_use_case.execute(
        refresh_token=refresh_token_data.refresh_token,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return result


@router.get("/users/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
):
    """Get current user."""
    return current_user


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_in: RoleCreate,
    create_role_use_case: CreateRoleUseCase = Depends(get_create_role_use_case),
    current_user: User = Depends(get_current_active_superuser),
):
    """Create a new role."""
    try:
        role = await create_role_use_case.execute(
            name=role_in.name,
            description=role_in.description,
        )
        return role
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/privileges", response_model=PrivilegeResponse, status_code=status.HTTP_201_CREATED)
async def create_privilege(
    privilege_in: PrivilegeCreate,
    create_privilege_use_case: CreatePrivilegeUseCase = Depends(get_create_privilege_use_case),
    current_user: User = Depends(get_current_active_superuser),
):
    """Create a new privilege."""
    try:
        privilege = await create_privilege_use_case.execute(
            name=privilege_in.name,
            description=privilege_in.description,
        )
        return privilege
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/users/{user_id}/roles", response_model=UserResponse)
async def assign_role_to_user(
    user_id: str,
    role_in: UserRoleCreate,
    assign_role_to_user_use_case: AssignRoleToUserUseCase = Depends(get_assign_role_to_user_use_case),
    current_user: User = Depends(get_current_active_superuser),
):
    """Assign a role to a user."""
    try:
        user = await assign_role_to_user_use_case.execute(
            user_id=uuid.UUID(user_id),
            role_id=role_in.role_id,
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/roles/{role_id}/privileges", response_model=RoleResponse)
async def assign_privilege_to_role(
    role_id: str,
    privilege_in: RolePrivilegeCreate,
    assign_privilege_to_role_use_case: AssignPrivilegeToRoleUseCase = Depends(get_assign_privilege_to_role_use_case),
    current_user: User = Depends(get_current_active_superuser),
):
    """Assign a privilege to a role."""
    try:
        role = await assign_privilege_to_role_use_case.execute(
            role_id=uuid.UUID(role_id),
            privilege_id=privilege_in.privilege_id,
        )
        return role
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
