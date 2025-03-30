"""
CRUD generator with role-based access control.
"""
from typing import List, Dict, Any, Optional
import os
import re
import inflect

from src.application.use_cases.model_generator import ModelField, ModelRelationship, Model, ModelGenerator

# Initialize inflect engine for pluralization
p = inflect.engine()

class CRUDGenerator:
    """Generator for creating CRUD operations with role-based access control."""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.model_generator = ModelGenerator(output_dir)
    
    def generate_privilege_seeds(self, models: List[Model], output_dir: Optional[str] = None) -> str:
        """Generate privilege seed data for all models."""
        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "app", "infrastructure", "persistence", "seeds")
        
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, "privileges.py")
        
        privileges = []
        
        # Add standard CRUD privileges for each model
        for model in models:
            model_name = model.name.lower()
            privileges.extend([
                f'    # {model.name} privileges',
                f'    Privilege(name="create_{model_name}", description="Can create {model_name}"),',
                f'    Privilege(name="read_{model_name}", description="Can read {model_name}"),',
                f'    Privilege(name="update_{model_name}", description="Can update {model_name}"),',
                f'    Privilege(name="delete_{model_name}", description="Can delete {model_name}"),',
            ])
            
            # Add relationship privileges
            for relationship in model.relationships:
                if relationship.type_name in ["one_to_many", "many_to_many"]:
                    rel_name = relationship.relationship_name
                    target_name = relationship.target_model.lower()
                    privileges.extend([
                        f'    Privilege(name="add_{target_name}_to_{model_name}", description="Can add {target_name} to {model_name}"),',
                        f'    Privilege(name="remove_{target_name}_from_{model_name}", description="Can remove {target_name} from {model_name}"),',
                    ])
        
        content = f"""\"\"\"
Privilege seed data for the application.
\"\"\"
from src.domain.entities import Privilege

# Define privileges
privileges = [
    # Authentication privileges
    Privilege(name="manage_users", description="Can manage users"),
    Privilege(name="manage_roles", description="Can manage roles"),
    Privilege(name="manage_privileges", description="Can manage privileges"),
    
{os.linesep.join(privileges)}
]

def seed_privileges(privilege_repository):
    \"\"\"Seed privileges into the database.\"\"\"
    for privilege in privileges:
        try:
            existing = privilege_repository.get_by_name(privilege.name)
            if not existing:
                privilege_repository.create(privilege)
        except Exception as e:
            print(f"Error seeding privilege {{privilege.name}}: {{e}}")
"""
        
        with open(file_path, "w") as f:
            f.write(content)
        
        return file_path
    
    def generate_role_seeds(self, output_dir: Optional[str] = None) -> str:
        """Generate role seed data."""
        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "app", "infrastructure", "persistence", "seeds")
        
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, "roles.py")
        
        content = """\"\"\"
Role seed data for the application.
\"\"\"
from src.domain.entities import Role

# Define roles
roles = [
    Role(name="admin", description="Administrator with all privileges"),
    Role(name="manager", description="Manager with limited administrative privileges"),
    Role(name="user", description="Regular user with basic privileges"),
]

def seed_roles(role_repository):
    \"\"\"Seed roles into the database.\"\"\"
    for role in roles:
        try:
            existing = role_repository.get_by_name(role.name)
            if not existing:
                role_repository.create(role)
        except Exception as e:
            print(f"Error seeding role {role.name}: {e}")
"""
        
        with open(file_path, "w") as f:
            f.write(content)
        
        return file_path
    
    def generate_role_privilege_seeds(self, models: List[Model], output_dir: Optional[str] = None) -> str:
        """Generate role-privilege association seed data."""
        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "app", "infrastructure", "persistence", "seeds")
        
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, "role_privileges.py")
        
        # Generate privilege assignments for each role
        admin_privileges = []
        manager_privileges = []
        user_privileges = []
        
        # Admin gets all privileges
        admin_privileges.append("    # Admin gets all privileges")
        admin_privileges.append("    admin_role = role_repository.get_by_name('admin')")
        admin_privileges.append("    if admin_role:")
        admin_privileges.append("        for privilege in privilege_repository.list(limit=1000):")
        admin_privileges.append("            try:")
        admin_privileges.append("                role_repository.add_privilege(admin_role.id, privilege.id)")
        admin_privileges.append("            except Exception as e:")
        admin_privileges.append("                print(f\"Error assigning privilege {privilege.name} to admin: {e}\")")
        
        # Manager gets specific privileges
        manager_privileges.append("    # Manager privileges")
        manager_privileges.append("    manager_role = role_repository.get_by_name('manager')")
        manager_privileges.append("    if manager_role:")
        
        # User gets specific privileges
        user_privileges.append("    # User privileges")
        user_privileges.append("    user_role = role_repository.get_by_name('user')")
        user_privileges.append("    if user_role:")
        
        # Add model-specific privileges
        for model in models:
            model_name = model.name.lower()
            
            # Managers can do all CRUD operations
            manager_privileges.extend([
                f"        # {model.name} privileges for manager",
                f"        for privilege_name in ['create_{model_name}', 'read_{model_name}', 'update_{model_name}', 'delete_{model_name}']:",
                f"            privilege = privilege_repository.get_by_name(privilege_name)",
                f"            if privilege:",
                f"                try:",
                f"                    role_repository.add_privilege(manager_role.id, privilege.id)",
                f"                except Exception as e:",
                f"                    print(f\"Error assigning {{privilege_name}} to manager: {{e}}\")",
            ])
            
            # Users can only read
            user_privileges.extend([
                f"        # {model.name} privileges for user",
                f"        read_privilege = privilege_repository.get_by_name('read_{model_name}')",
                f"        if read_privilege:",
                f"            try:",
                f"                role_repository.add_privilege(user_role.id, read_privilege.id)",
                f"            except Exception as e:",
                f"                print(f\"Error assigning read_{model_name} to user: {{e}}\")",
            ])
            
            # Add relationship privileges for manager
            for relationship in model.relationships:
                if relationship.type_name in ["one_to_many", "many_to_many"]:
                    rel_name = relationship.relationship_name
                    target_name = relationship.target_model.lower()
                    manager_privileges.extend([
                        f"        # {model.name}-{relationship.target_model} relationship privileges for manager",
                        f"        for privilege_name in ['add_{target_name}_to_{model_name}', 'remove_{target_name}_from_{model_name}']:",
                        f"            privilege = privilege_repository.get_by_name(privilege_name)",
                        f"            if privilege:",
                        f"                try:",
                        f"                    role_repository.add_privilege(manager_role.id, privilege.id)",
                        f"                except Exception as e:",
                        f"                    print(f\"Error assigning {{privilege_name}} to manager: {{e}}\")",
                    ])
        
        content = f"""\"\"\"
Role-privilege association seed data for the application.
\"\"\"

def seed_role_privileges(role_repository, privilege_repository):
    \"\"\"Seed role-privilege associations into the database.\"\"\"
{os.linesep.join(admin_privileges)}

{os.linesep.join(manager_privileges)}

{os.linesep.join(user_privileges)}
"""
        
        with open(file_path, "w") as f:
            f.write(content)
        
        return file_path
    
    def generate_user_seeds(self, output_dir: Optional[str] = None) -> str:
        """Generate user seed data."""
        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "app", "infrastructure", "persistence", "seeds")
        
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, "users.py")
        
        content = """\"\"\"
User seed data for the application.
\"\"\"
from src.domain.entities import User

def seed_users(user_repository, password_service):
    \"\"\"Seed users into the database.\"\"\"
    # Create admin user
    try:
        admin_user = user_repository.get_by_username('admin')
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                hashed_password=password_service.hash_password('admin'),
                full_name='Admin User',
                is_active=True,
                is_superuser=True,
            )
            user_repository.create(admin_user)
    except Exception as e:
        print(f"Error seeding admin user: {e}")
    
    # Create manager user
    try:
        manager_user = user_repository.get_by_username('manager')
        if not manager_user:
            manager_user = User(
                username='manager',
                email='manager@example.com',
                hashed_password=password_service.hash_password('manager'),
                full_name='Manager User',
                is_active=True,
                is_superuser=False,
            )
            user_repository.create(manager_user)
    except Exception as e:
        print(f"Error seeding manager user: {e}")
    
    # Create regular user
    try:
        regular_user = user_repository.get_by_username('user')
        if not regular_user:
            regular_user = User(
                username='user',
                email='user@example.com',
                hashed_password=password_service.hash_password('user'),
                full_name='Regular User',
                is_active=True,
                is_superuser=False,
            )
            user_repository.create(regular_user)
    except Exception as e:
        print(f"Error seeding regular user: {e}")
"""
        
        with open(file_path, "w") as f:
            f.write(content)
        
        return file_path
    
    def generate_user_role_seeds(self, output_dir: Optional[str] = None) -> str:
        """Generate user-role association seed data."""
        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "app", "infrastructure", "persistence", "seeds")
        
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, "user_roles.py")
        
        content = """\"\"\"
User-role association seed data for the application.
\"\"\"

def seed_user_roles(user_repository, role_repository):
    \"\"\"Seed user-role associations into the database.\"\"\"
    # Assign admin role to admin user
    try:
        admin_user = user_repository.get_by_username('admin')
        admin_role = role_repository.get_by_name('admin')
        if admin_user and admin_role:
            user_repository.add_role(admin_user.id, admin_role.id)
    except Exception as e:
        print(f"Error assigning admin role to admin user: {e}")
    
    # Assign manager role to manager user
    try:
        manager_user = user_repository.get_by_username('manager')
        manager_role = role_repository.get_by_name('manager')
        if manager_user and manager_role:
            user_repository.add_role(manager_user.id, manager_role.id)
    except Exception as e:
        print(f"Error assigning manager role to manager user: {e}")
    
    # Assign user role to regular user
    try:
        regular_user = user_repository.get_by_username('user')
        user_role = role_repository.get_by_name('user')
        if regular_user and user_role:
            user_repository.add_role(regular_user.id, user_role.id)
    except Exception as e:
        print(f"Error assigning user role to regular user: {e}")
"""
        
        with open(file_path, "w") as f:
            f.write(content)
        
        return file_path
    
    def generate_seed_main(self, output_dir: Optional[str] = None) -> str:
        """Generate main seed file."""
        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "app", "infrastructure", "persistence", "seeds")
        
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, "__init__.py")
        
        content = """\"\"\"
Database seed data for the application.
\"\"\"
from .privileges import seed_privileges
from .roles import seed_roles
from .role_privileges import seed_role_privileges
from .users import seed_users
from .user_roles import seed_user_roles

async def seed_database(
    user_repository,
    role_repository,
    privilege_repository,
    password_service,
):
    \"\"\"Seed the database with initial data.\"\"\"
    # Seed privileges first
    await seed_privileges(privilege_repository)
    
    # Seed roles
    await seed_roles(role_repository)
    
    # Seed role-privilege associations
    await seed_role_privileges(role_repository, privilege_repository)
    
    # Seed users
    await seed_users(user_repository, password_service)
    
    # Seed user-role associations
    await seed_user_roles(user_repository, role_repository)
"""
        
        with open(file_path, "w") as f:
            f.write(content)
        
        return file_path
    
    def generate_api_router_updates(self, models: List[Model], output_dir: Optional[str] = None) -> str:
        """Generate updates to the API router to include new model endpoints."""
        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "app", "presentation", "api", "v1")
        
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, "api.py")
        
        imports = ["from fastapi import APIRouter", "", "from src.presentation.api.v1.endpoints import auth"]
        
        # Add imports for model endpoints
        for model in models:
            model_name = model.name.lower()
            imports.append(f"from src.presentation.api.v1.endpoints import {model_name}")
        
        router_setup = ["", "", "api_router = APIRouter()", "api_router.include_router(auth.router, prefix=\"/auth\", tags=[\"auth\"])"]
        
        # Add router includes for model endpoints
        for model in models:
            model_name = model.name.lower()
            model_plural = p.plural(model_name)
            router_setup.append(f"api_router.include_router({model_name}.router, prefix=\"/{model_plural}\", tags=[\"{model_name}\"])")
        
        content = "\n".join(imports + router_setup)
        
        with open(file_path, "w") as f:
            f.write(content)
        
        return file_path
    
    def generate_database_init_script(self, models: List[Model], output_dir: Optional[str] = None) -> str:
        """Generate database initialization script."""
        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "app", "infrastructure", "persistence")
        
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, "init_db.py")
        
        imports = [
            "\"\"\"",
            "Database initialization script.",
            "\"\"\"",
            "import asyncio",
            "import logging",
            "",
            "from src.infrastructure.persistence.database import AsyncDatabase",
            "from src.infrastructure.persistence.models import Base",
            "from src.infrastructure.persistence import (",
            "    SQLAlchemyUserRepository,",
            "    SQLAlchemyRoleRepository,",
            "    SQLAlchemyPrivilegeRepository,",
            ")",
            "from src.infrastructure.auth import PasswordServiceImpl",
            "from src.infrastructure.config import DatabaseConfig",
            "from src.infrastructure.persistence.seeds import seed_database",
        ]
        
        # Add imports for model repositories
        for model in models:
            imports.append(f"from src.infrastructure.persistence.repositories.{model.name.lower()} import SQLAlchemy{model.name}Repository")
        
        init_function = [
            "",
            "",
            "async def init_db():",
            "    \"\"\"Initialize the database.\"\"\"",
            "    logging.info(\"Initializing database\")",
            "    ",
            "    # Create database connection",
            "    db_config = DatabaseConfig.from_env()",
            "    db = AsyncDatabase(db_config)",
            "    ",
            "    # Create tables",
            "    logging.info(\"Creating database tables\")",
            "    await db.create_tables(Base)",
            "    ",
            "    # Create repositories",
            "    user_repository = SQLAlchemyUserRepository(db)",
            "    role_repository = SQLAlchemyRoleRepository(db)",
            "    privilege_repository = SQLAlchemyPrivilegeRepository(db)",
            "    password_service = PasswordServiceImpl()",
            "    ",
            "    # Seed database",
            "    logging.info(\"Seeding database\")",
            "    await seed_database(",
            "        user_repository=user_repository,",
            "        role_repository=role_repository,",
            "        privilege_repository=privilege_repository,",
            "        password_service=password_service,",
            "    )",
            "    ",
            "    logging.info(\"Database initialization complete\")",
            "",
            "",
            "if __name__ == \"__main__\":",
            "    logging.basicConfig(level=logging.INFO)",
            "    asyncio.run(init_db())",
        ]
        
        content = "\n".join(imports + init_function)
        
        with open(file_path, "w") as f:
            f.write(content)
        
        return file_path
    
    def generate_crud_files(self, models: List[Model]) -> List[str]:
        """Generate all CRUD-related files for the models."""
        files = []
        
        # Generate seed files
        files.append(self.generate_privilege_seeds(models))
        files.append(self.generate_role_seeds())
        files.append(self.generate_role_privilege_seeds(models))
        files.append(self.generate_user_seeds())
        files.append(self.generate_user_role_seeds())
        files.append(self.generate_seed_main())
        
        # Generate API router updates
        files.append(self.generate_api_router_updates(models))
        
        # Generate database initialization script
        files.append(self.generate_database_init_script(models))
        
        return files
