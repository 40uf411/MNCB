"""
Export all entity classes for easy importing.
"""

from .base import BaseEntity
from .user import User
from .role import Role
from .privilege import Privilege
from .associations import UserRole, RolePrivilege

__all__ = [
    "BaseEntity",
    "User",
    "Role",
    "Privilege",
    "UserRole",
    "RolePrivilege",
]
