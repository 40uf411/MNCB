"""
Model generator for creating custom models based on user input.
"""
from typing import List, Dict, Any, Optional
import os
import re
import inflect

# Initialize inflect engine for pluralization
p = inflect.engine()

class ModelField:
    """Represents a field in a model."""
    
    def __init__(
        self,
        name: str,
        type_name: str,
        description: Optional[str] = None,
        required: bool = True,
        unique: bool = False,
        default: Any = None,
    ):
        self.name = name
        self.type_name = type_name
        self.description = description
        self.required = required
        self.unique = unique
        self.default = default
    
    @property
    def python_type(self) -> str:
        """Get the Python type for this field."""
        type_mapping = {
            "str": "str",
            "int": "int",
            "float": "float",
            "bool": "bool",
            "datetime": "datetime",
            "date": "date",
            "uuid": "uuid.UUID",
            "list": "List[Any]",
            "dict": "Dict[str, Any]",
        }
        return type_mapping.get(self.type_name, "Any")
    
    @property
    def sqlalchemy_type(self) -> str:
        """Get the SQLAlchemy type for this field."""
        type_mapping = {
            "str": "String",
            "int": "Integer",
            "float": "Float",
            "bool": "Boolean",
            "datetime": "DateTime",
            "date": "Date",
            "uuid": "UUID(as_uuid=True)",
            "list": "JSON",
            "dict": "JSON",
        }
        return type_mapping.get(self.type_name, "String")
    
    @property
    def pydantic_type(self) -> str:
        """Get the Pydantic type for this field."""
        type_mapping = {
            "str": "str",
            "int": "int",
            "float": "float",
            "bool": "bool",
            "datetime": "datetime",
            "date": "date",
            "uuid": "uuid.UUID",
            "list": "List[Any]",
            "dict": "Dict[str, Any]",
        }
        return type_mapping.get(self.type_name, "Any")
    
    @property
    def pydantic_field(self) -> str:
        """Get the Pydantic field definition for this field."""
        if self.default is not None:
            return f"{self.name}: {self.pydantic_type} = {self.default}"
        elif not self.required:
            return f"{self.name}: Optional[{self.pydantic_type}] = None"
        else:
            return f"{self.name}: {self.pydantic_type}"


class ModelRelationship:
    """Represents a relationship between models."""
    
    def __init__(
        self,
        type_name: str,
        target_model: str,
        back_populates: Optional[str] = None,
    ):
        self.type_name = type_name
        self.target_model = target_model
        self.back_populates = back_populates
    
    @property
    def is_to_many(self) -> bool:
        """Check if this is a to-many relationship."""
        return self.type_name in ["one_to_many", "many_to_many"]
    
    @property
    def foreign_key_name(self) -> str:
        """Get the foreign key name for this relationship."""
        if self.type_name in ["one_to_one", "many_to_one"]:
            return f"{self.target_model.lower()}_id"
        return None
    
    @property
    def relationship_name(self) -> str:
        """Get the relationship name for this relationship."""
        if self.type_name in ["one_to_one", "many_to_one"]:
            return self.target_model.lower()
        else:
            return p.plural(self.target_model.lower())


class Model:
    """Represents a model to be generated."""
    
    def __init__(
        self,
        name: str,
        fields: List[ModelField],
        relationships: List[ModelRelationship] = None,
        description: Optional[str] = None,
    ):
        self.name = name
        self.fields = fields
        self.relationships = relationships or []
        self.description = description
    
    @property
    def table_name(self) -> str:
        """Get the table name for this model."""
        # Convert CamelCase to snake_case and pluralize
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', self.name)
        snake_case = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        return p.plural(snake_case)


class ModelGenerator:
    """Generator for creating model files based on user input."""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
    
    def generate_domain_entity(self, model: Model, output_dir: Optional[str] = None) -> str:
        """Generate a domain entity file for the model."""
        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "app", "domain", "entities")
        
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{model.name.lower()}.py")
        
        imports = [
            "from datetime import datetime",
            "from typing import Optional, List, Dict, Any",
            "import uuid",
            "",
            "from .base import BaseEntity",
        ]
        
        # Add imports for relationships
        for relationship in model.relationships:
            if relationship.target_model != model.name:
                imports.append(f"from .{relationship.target_model.lower()} import {relationship.target_model}")
        
        class_def = [
            f"class {model.name}(BaseEntity):",
            f'    """{model.description or f"{model.name} entity."}"""',
            "",
        ]
        
        # Add field declarations
        for field in model.fields:
            field_type = field.python_type
            if not field.required:
                field_type = f"Optional[{field_type}]"
            class_def.append(f"    {field.name}: {field_type}")
        
        # Add relationship declarations
        for relationship in model.relationships:
            if relationship.is_to_many:
                class_def.append(f"    {relationship.relationship_name}: List['{relationship.target_model}']")
            else:
                class_def.append(f"    {relationship.relationship_name}: Optional['{relationship.target_model}']")
        
        class_def.append("")
        
        # Add __init__ method
        init_params = ["self"]
        for field in model.fields:
            if field.default is not None:
                init_params.append(f"{field.name}: {field.python_type} = {field.default}")
            elif not field.required:
                init_params.append(f"{field.name}: Optional[{field.python_type}] = None")
            else:
                init_params.append(f"{field.name}: {field.python_type}")
        
        for relationship in model.relationships:
            if relationship.is_to_many:
                init_params.append(f"{relationship.relationship_name}: Optional[List['{relationship.target_model}']] = None")
            else:
                init_params.append(f"{relationship.relationship_name}: Optional['{relationship.target_model}'] = None")
        
        init_params.extend([
            "id: Optional[uuid.UUID] = None",
            "created_at: Optional[datetime] = None",
            "updated_at: Optional[datetime] = None",
        ])
        
        init_method = [
            "    def __init__(",
            ",\n        ".join(init_params),
            "    ):",
            "        super().__init__(id, created_at, updated_at)",
        ]
        
        for field in model.fields:
            init_method.append(f"        self.{field.name} = {field.name}")
        
        for relationship in model.relationships:
            if relationship.is_to_many:
                init_method.append(f"        self.{relationship.relationship_name} = {relationship.relationship_name} or []")
            else:
                init_method.append(f"        self.{relationship.relationship_name} = {relationship.relationship_name}")
        
        init_method.append("")
        
        # Add to_dict method
        to_dict_method = [
            "    def to_dict(self) -> Dict[str, Any]:",
            '        """Convert entity to dictionary."""',
            "        data = super().to_dict()",
            "        data.update({",
        ]
        
        for field in model.fields:
            to_dict_method.append(f'            "{field.name}": self.{field.name},')
        
        for relationship in model.relationships:
            if relationship.is_to_many:
                to_dict_method.append(f'            "{relationship.relationship_name}": [str(item.id) for item in self.{relationship.relationship_name}],')
            else:
                to_dict_method.append(f'            "{relationship.relationship_name}": str(self.{relationship.relationship_name}.id) if self.{relationship.relationship_name} else None,')
        
        to_dict_method.extend([
            "        })",
            "        return data",
            "",
        ])
        
        # Add from_dict method
        from_dict_params = ["cls", "data: Dict[str, Any]"]
        for relationship in model.relationships:
            if relationship.is_to_many:
                from_dict_params.append(f"{relationship.relationship_name}: Optional[List['{relationship.target_model}']] = None")
            else:
                from_dict_params.append(f"{relationship.relationship_name}: Optional['{relationship.target_model}'] = None")
        
        from_dict_method = [
            "    @classmethod",
            "    def from_dict(",
            ",\n        ".join(from_dict_params),
            "    ) -> 'Model':",
            '        """Create entity from dictionary."""',
            "        return cls(",
        ]
        
        for field in model.fields:
            from_dict_method.append(f'            {field.name}=data["{field.name}"],')
        
        for relationship in model.relationships:
            if relationship.is_to_many:
                from_dict_method.append(f"            {relationship.relationship_name}={relationship.relationship_name} or [],")
            else:
                from_dict_method.append(f"            {relationship.relationship_name}={relationship.relationship_name},")
        
        from_dict_method.extend([
            '            id=uuid.UUID(data["id"]) if "id" in data else None,',
            '            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else None,',
            '            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else None,',
            "        )",
        ])
        
        # Combine all parts
        content = "\n".join(imports) + "\n\n\n" + "\n".join(class_def) + "\n".join(init_method) + "\n".join(to_dict_method) + "\n".join(from_dict_method)
        
        with open(file_path, "w") as f:
            f.write(content)
        
        return file_path
    
    def generate_sqlalchemy_model(self, model: Model, output_dir: Optional[str] = None) -> str:
        """Generate a SQLAlchemy model file for the model."""
        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "app", "infrastructure", "persistence", "models")
        
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{model.name.lower()}.py")
        
        imports = [
            "from datetime import datetime",
            "from typing import List, Optional",
            "import uuid",
            "",
            "from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, ForeignKey, Table, JSON",
            "from sqlalchemy.dialects.postgresql import UUID",
            "from sqlalchemy.orm import relationship",
            "",
            "from .base import Base",
        ]
        
        # Add imports for relationships
        for relationship in model.relationships:
            if relationship.target_model != model.name:
                imports.append(f"from .{relationship.target_model.lower()} import {relationship.target_model}Model")
        
        # Add association tables for many-to-many relationships
        association_tables = []
        for relationship in model.relationships:
            if relationship.type_name == "many_to_many":
                source_table = model.table_name
                target_table = p.plural(relationship.target_model.lower())
                assoc_table_name = f"{model.name.lower()}_{relationship.target_model.lower()}_association"
                
                association_tables.append(f"""
{assoc_table_name} = Table(
    "{source_table}_{target_table}",
    Base.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("{model.name.lower()}_id", UUID(as_uuid=True), ForeignKey("{source_table}.id")),
    Column("{relationship.target_model.lower()}_id", UUID(as_uuid=True), ForeignKey("{target_table}.id")),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
)""")
        
        class_def = [
            f"class {model.name}Model(Base):",
            f'    """{model.description or f"SQLAlchemy model for {model.name} entity."}"""',
            "",
            f'    __tablename__ = "{model.table_name}"',
            "",
            '    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)',
        ]
        
        # Add field columns
        for field in model.fields:
            column_args = []
            if field.unique:
                column_args.append("unique=True")
            if field.required:
                column_args.append("nullable=False")
            else:
                column_args.append("nullable=True")
            
            if field.default is not None:
                column_args.append(f"default={field.default}")
            
            class_def.append(f"    {field.name} = Column({field.sqlalchemy_type}, {', '.join(column_args)})")
        
        # Add foreign keys for relationships
        for relationship in model.relationships:
            if relationship.type_name in ["one_to_one", "many_to_one"]:
                target_table = p.plural(relationship.target_model.lower())
                class_def.append(f"    {relationship.foreign_key_name} = Column(UUID(as_uuid=True), ForeignKey(\"{target_table}.id\"), nullable=True)")
        
        # Add timestamp columns
        class_def.extend([
            "    created_at = Column(DateTime, default=datetime.utcnow)",
            "    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)",
            "",
            "    # Relationships",
        ])
        
        # Add relationship definitions
        for relationship in model.relationships:
            if relationship.type_name == "one_to_one":
                class_def.append(f"    {relationship.relationship_name} = relationship(\"{relationship.target_model}Model\", uselist=False, foreign_keys=[{relationship.foreign_key_name}])")
            elif relationship.type_name == "many_to_one":
                class_def.append(f"    {relationship.relationship_name} = relationship(\"{relationship.target_model}Model\", foreign_keys=[{relationship.foreign_key_name}])")
            elif relationship.type_name == "one_to_many":
                back_populates = f", back_populates=\"{relationship.back_populates}\"" if relationship.back_populates else ""
                class_def.append(f"    {relationship.relationship_name} = relationship(\"{relationship.target_model}Model\"{back_populates})")
            elif relationship.type_name == "many_to_many":
                assoc_table_name = f"{model.name.lower()}_{relationship.target_model.lower()}_association"
                back_populates = f", back_populates=\"{relationship.back_populates}\"" if relationship.back_populates else ""
                class_def.append(f"    {relationship.relationship_name} = relationship(\"{relationship.target_model}Model\", secondary={assoc_table_name}{back_populates})")
        
        # Combine all parts
        content = "\n".join(imports) + "\n\n" + "\n".join(association_tables) + "\n\n\n" + "\n".join(class_def)
        
        with open(file_path, "w") as f:
            f.write(content)
        
        return file_path
    
    def generate_repository_interface(self, model: Model, output_dir: Optional[str] = None) -> str:
        """Generate a repository interface file for the model."""
        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "app", "domain", "repositories")
        
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{model.name.lower()}.py")
        
        imports = [
            "from abc import ABC, abstractmethod",
            "from typing import List, Optional, Dict, Any",
            "import uuid",
            "",
            f"from src.domain.entities import {model.name}",
        ]
        
        class_def = [
            f"class {model.name}Repository(ABC):",
            f'    """Repository interface for {model.name} entity."""',
            "",
            "    @abstractmethod",
            f"    async def create(self, {model.name.lower()}: {model.name}) -> {model.name}:",
            f'        """Create a new {model.name.lower()}."""',
            "        pass",
            "",
            "    @abstractmethod",
            f"    async def get_by_id(self, {model.name.lower()}_id: uuid.UUID) -> Optional[{model.name}]:",
            f'        """Get {model.name.lower()} by ID."""',
            "        pass",
            "",
            "    @abstractmethod",
            f"    async def update(self, {model.name.lower()}: {model.name}) -> {model.name}:",
            f'        """Update an existing {model.name.lower()}."""',
            "        pass",
            "",
            "    @abstractmethod",
            f"    async def delete(self, {model.name.lower()}_id: uuid.UUID) -> bool:",
            f'        """Delete a {model.name.lower()}."""',
            "        pass",
            "",
            "    @abstractmethod",
            f"    async def list(self, skip: int = 0, limit: int = 100) -> List[{model.name}]:",
            f'        """List {p.plural(model.name.lower())} with pagination."""',
            "        pass",
        ]
        
        # Add methods for relationships
        for relationship in model.relationships:
            if relationship.type_name in ["one_to_many", "many_to_many"]:
                target_name = relationship.target_model
                target_var = target_name.lower()
                
                class_def.extend([
                    "",
                    "    @abstractmethod",
                    f"    async def add_{target_var}(self, {model.name.lower()}_id: uuid.UUID, {target_var}_id: uuid.UUID) -> bool:",
                    f'        """Add a {target_var} to a {model.name.lower()}."""',
                    "        pass",
                    "",
                    "    @abstractmethod",
                    f"    async def remove_{target_var}(self, {model.name.lower()}_id: uuid.UUID, {target_var}_id: uuid.UUID) -> bool:",
                    f'        """Remove a {target_var} from a {model.name.lower()}."""',
                    "        pass",
                    "",
                    "    @abstractmethod",
                    f"    async def get_{relationship.relationship_name}(self, {model.name.lower()}_id: uuid.UUID) -> List[{target_name}]:",
                    f'        """Get all {relationship.relationship_name} for a {model.name.lower()}."""',
                    "        pass",
                ])
        
        # Combine all parts
        content = "\n".join(imports) + "\n\n\n" + "\n".join(class_def)
        
        with open(file_path, "w") as f:
            f.write(content)
        
        return file_path
    
    def generate_repository_implementation(self, model: Model, output_dir: Optional[str] = None) -> str:
        """Generate a repository implementation file for the model."""
        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "app", "infrastructure", "persistence", "repositories")
        
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{model.name.lower()}.py")
        
        imports = [
            "from typing import List, Optional, Dict, Any",
            "import uuid",
            "",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "from sqlalchemy.future import select",
            "from sqlalchemy import update, delete",
            "",
            f"from src.domain.entities import {model.name}",
            f"from src.domain.repositories.{model.name.lower()} import {model.name}Repository",
            f"from src.infrastructure.persistence.models import {model.name}Model",
            "from src.infrastructure.persistence.database import AsyncDatabase",
        ]
        
        # Add imports for relationships
        for relationship in model.relationships:
            if relationship.target_model != model.name:
                imports.append(f"from src.domain.entities import {relationship.target_model}")
                imports.append(f"from src.infrastructure.persistence.models import {relationship.target_model}Model")
        
        class_def = [
            f"class SQLAlchemy{model.name}Repository({model.name}Repository):",
            f'    """SQLAlchemy implementation of {model.name}Repository."""',
            "",
            "    def __init__(self, db: AsyncDatabase):",
            "        self.db = db",
            "",
            f"    async def create(self, {model.name.lower()}: {model.name}) -> {model.name}:",
            f'        """Create a new {model.name.lower()}."""',
            f"        {model.name.lower()}_model = {model.name}Model(",
            "            id={model.name.lower()}.id,",
        ]
        
        # Add field assignments for create method
        for field in model.fields:
            class_def.append(f"            {field.name}={model.name.lower()}.{field.name},")
        
        # Add foreign key assignments for relationships
        for relationship in model.relationships:
            if relationship.type_name in ["one_to_one", "many_to_one"]:
                rel_name = relationship.relationship_name
                fk_name = relationship.foreign_key_name
                class_def.append(f"            {fk_name}={model.name.lower()}.{rel_name}.id if {model.name.lower()}.{rel_name} else None,")
        
        class_def.extend([
            "            created_at={model.name.lower()}.created_at,",
            "            updated_at={model.name.lower()}.updated_at,",
            "        )",
            "",
            "        async with self.db.get_session() as session:",
            f"            session.add({model.name.lower()}_model)",
            "            await session.flush()",
        ])
        
        # Add relationship handling for create method
        for relationship in model.relationships:
            if relationship.type_name in ["one_to_many", "many_to_many"]:
                rel_name = relationship.relationship_name
                target_model = relationship.target_model
                class_def.extend([
                    f"            # Add {rel_name} if any",
                    f"            if {model.name.lower()}.{rel_name}:",
                    f"                for item in {model.name.lower()}.{rel_name}:",
                    "                    item_result = await session.execute(",
                    f"                        select({target_model}Model).where({target_model}Model.id == item.id)",
                    "                    )",
                    "                    item_model = item_result.scalar_one_or_none()",
                    "                    if item_model:",
                    f"                        {model.name.lower()}_model.{rel_name}.append(item_model)",
                ])
        
        class_def.extend([
            "",
            "            await session.commit()",
            f"            await session.refresh({model.name.lower()}_model)",
            "",
            "            # Convert back to domain entity",
            f"            return self._model_to_entity({model.name.lower()}_model)",
            "",
            f"    async def get_by_id(self, {model.name.lower()}_id: uuid.UUID) -> Optional[{model.name}]:",
            f'        """Get {model.name.lower()} by ID."""',
            "        async with self.db.get_session() as session:",
            "            result = await session.execute(",
            f"                select({model.name}Model).where({model.name}Model.id == {model.name.lower()}_id)",
            "            )",
            f"            {model.name.lower()}_model = result.scalar_one_or_none()",
            "",
            f"            if not {model.name.lower()}_model:",
            "                return None",
            "",
            f"            return self._model_to_entity({model.name.lower()}_model)",
            "",
            f"    async def update(self, {model.name.lower()}: {model.name}) -> {model.name}:",
            f'        """Update an existing {model.name.lower()}."""',
            "        async with self.db.get_session() as session:",
            "            result = await session.execute(",
            f"                select({model.name}Model).where({model.name}Model.id == {model.name.lower()}.id)",
            "            )",
            f"            {model.name.lower()}_model = result.scalar_one_or_none()",
            "",
            f"            if not {model.name.lower()}_model:",
            f"                raise ValueError(f\"{model.name} with ID {{{model.name.lower()}.id}} not found\")",
            "",
            "            # Update fields",
        ])
        
        # Add field updates for update method
        for field in model.fields:
            class_def.append(f"            {model.name.lower()}_model.{field.name} = {model.name.lower()}.{field.name}")
        
        # Add foreign key updates for relationships
        for relationship in model.relationships:
            if relationship.type_name in ["one_to_one", "many_to_one"]:
                rel_name = relationship.relationship_name
                fk_name = relationship.foreign_key_name
                class_def.append(f"            {model.name.lower()}_model.{fk_name} = {model.name.lower()}.{rel_name}.id if {model.name.lower()}.{rel_name} else None")
        
        class_def.append(f"            {model.name.lower()}_model.updated_at = {model.name.lower()}.updated_at")
        
        # Add relationship handling for update method
        for relationship in model.relationships:
            if relationship.type_name in ["one_to_many", "many_to_many"]:
                rel_name = relationship.relationship_name
                target_model = relationship.target_model
                class_def.extend([
                    "",
                    f"            # Update {rel_name} if provided",
                    f"            if {model.name.lower()}.{rel_name}:",
                    f"                # Clear existing {rel_name}",
                    f"                {model.name.lower()}_model.{rel_name} = []",
                    "",
                    f"                # Add new {rel_name}",
                    f"                for item in {model.name.lower()}.{rel_name}:",
                    "                    item_result = await session.execute(",
                    f"                        select({target_model}Model).where({target_model}Model.id == item.id)",
                    "                    )",
                    "                    item_model = item_result.scalar_one_or_none()",
                    "                    if item_model:",
                    f"                        {model.name.lower()}_model.{rel_name}.append(item_model)",
                ])
        
        class_def.extend([
            "",
            "            await session.commit()",
            f"            await session.refresh({model.name.lower()}_model)",
            "",
            f"            return self._model_to_entity({model.name.lower()}_model)",
            "",
            f"    async def delete(self, {model.name.lower()}_id: uuid.UUID) -> bool:",
            f'        """Delete a {model.name.lower()}."""',
            "        async with self.db.get_session() as session:",
            "            result = await session.execute(",
            f"                delete({model.name}Model).where({model.name}Model.id == {model.name.lower()}_id)",
            "            )",
            "",
            "            return result.rowcount > 0",
            "",
            f"    async def list(self, skip: int = 0, limit: int = 100) -> List[{model.name}]:",
            f'        """List {p.plural(model.name.lower())} with pagination."""',
            "        async with self.db.get_session() as session:",
            "            result = await session.execute(",
            f"                select({model.name}Model).offset(skip).limit(limit)",
            "            )",
            f"            {model.name.lower()}_models = result.scalars().all()",
            "",
            f"            return [self._model_to_entity({model.name.lower()}_model) for {model.name.lower()}_model in {model.name.lower()}_models]",
        ])
        
        # Add methods for relationships
        for relationship in model.relationships:
            if relationship.type_name in ["one_to_many", "many_to_many"]:
                target_name = relationship.target_model
                target_var = target_name.lower()
                rel_name = relationship.relationship_name
                
                class_def.extend([
                    "",
                    f"    async def add_{target_var}(self, {model.name.lower()}_id: uuid.UUID, {target_var}_id: uuid.UUID) -> bool:",
                    f'        """Add a {target_var} to a {model.name.lower()}."""',
                    "        async with self.db.get_session() as session:",
                    f"            {model.name.lower()}_result = await session.execute(",
                    f"                select({model.name}Model).where({model.name}Model.id == {model.name.lower()}_id)",
                    "            )",
                    f"            {model.name.lower()}_model = {model.name.lower()}_result.scalar_one_or_none()",
                    "",
                    f"            if not {model.name.lower()}_model:",
                    "                return False",
                    "",
                    f"            {target_var}_result = await session.execute(",
                    f"                select({target_name}Model).where({target_name}Model.id == {target_var}_id)",
                    "            )",
                    f"            {target_var}_model = {target_var}_result.scalar_one_or_none()",
                    "",
                    f"            if not {target_var}_model:",
                    "                return False",
                    "",
                    f"            {model.name.lower()}_model.{rel_name}.append({target_var}_model)",
                    "            await session.commit()",
                    "",
                    "            return True",
                    "",
                    f"    async def remove_{target_var}(self, {model.name.lower()}_id: uuid.UUID, {target_var}_id: uuid.UUID) -> bool:",
                    f'        """Remove a {target_var} from a {model.name.lower()}."""',
                    "        async with self.db.get_session() as session:",
                    f"            {model.name.lower()}_result = await session.execute(",
                    f"                select({model.name}Model).where({model.name}Model.id == {model.name.lower()}_id)",
                    "            )",
                    f"            {model.name.lower()}_model = {model.name.lower()}_result.scalar_one_or_none()",
                    "",
                    f"            if not {model.name.lower()}_model:",
                    "                return False",
                    "",
                    f"            {target_var}_result = await session.execute(",
                    f"                select({target_name}Model).where({target_name}Model.id == {target_var}_id)",
                    "            )",
                    f"            {target_var}_model = {target_var}_result.scalar_one_or_none()",
                    "",
                    f"            if not {target_var}_model or {target_var}_model not in {model.name.lower()}_model.{rel_name}:",
                    "                return False",
                    "",
                    f"            {model.name.lower()}_model.{rel_name}.remove({target_var}_model)",
                    "            await session.commit()",
                    "",
                    "            return True",
                    "",
                    f"    async def get_{rel_name}(self, {model.name.lower()}_id: uuid.UUID) -> List[{target_name}]:",
                    f'        """Get all {rel_name} for a {model.name.lower()}."""',
                    "        async with self.db.get_session() as session:",
                    f"            {model.name.lower()}_result = await session.execute(",
                    f"                select({model.name}Model).where({model.name}Model.id == {model.name.lower()}_id)",
                    "            )",
                    f"            {model.name.lower()}_model = {model.name.lower()}_result.scalar_one_or_none()",
                    "",
                    f"            if not {model.name.lower()}_model:",
                    "                return []",
                    "",
                    "            return [",
                    f"                {target_name}(",
                    "                    id=item.id,",
                ])
                
                # Add fields for target model
                for field in model.fields:
                    class_def.append(f"                    {field.name}=item.{field.name},")
                
                class_def.extend([
                    "                    created_at=item.created_at,",
                    "                    updated_at=item.updated_at,",
                    "                )",
                    f"                for item in {model.name.lower()}_model.{rel_name}",
                    "            ]",
                ])
        
        # Add model_to_entity method
        class_def.extend([
            "",
            f"    def _model_to_entity(self, model: {model.name}Model) -> {model.name}:",
            f'        """Convert a {model.name}Model to a {model.name} entity."""',
            f"        return {model.name}(",
            "            id=model.id,",
        ])
        
        # Add field assignments for model_to_entity method
        for field in model.fields:
            class_def.append(f"            {field.name}=model.{field.name},")
        
        # Add relationship assignments for model_to_entity method
        for relationship in model.relationships:
            if relationship.type_name in ["one_to_one", "many_to_one"]:
                rel_name = relationship.relationship_name
                target_model = relationship.target_model
                class_def.append(f"            {rel_name}={target_model}(")
                class_def.append(f"                id=model.{rel_name}.id,")
                # Add fields for target model
                for field in model.fields:
                    class_def.append(f"                {field.name}=model.{rel_name}.{field.name},")
                class_def.append("                created_at=model.{rel_name}.created_at,")
                class_def.append("                updated_at=model.{rel_name}.updated_at,")
                class_def.append(f"            ) if model.{rel_name} else None,")
            elif relationship.type_name in ["one_to_many", "many_to_many"]:
                rel_name = relationship.relationship_name
                target_model = relationship.target_model
                class_def.append(f"            {rel_name}=[")
                class_def.append(f"                {target_model}(")
                class_def.append("                    id=item.id,")
                # Add fields for target model
                for field in model.fields:
                    class_def.append(f"                    {field.name}=item.{field.name},")
                class_def.append("                    created_at=item.created_at,")
                class_def.append("                    updated_at=item.updated_at,")
                class_def.append("                )")
                class_def.append(f"                for item in model.{rel_name}")
                class_def.append("            ],")
        
        class_def.extend([
            "            created_at=model.created_at,",
            "            updated_at=model.updated_at,",
            "        )",
        ])
        
        # Combine all parts
        content = "\n".join(imports) + "\n\n\n" + "\n".join(class_def)
        
        with open(file_path, "w") as f:
            f.write(content)
        
        return file_path
    
    def generate_api_schema(self, model: Model, output_dir: Optional[str] = None) -> str:
        """Generate API schema file for the model."""
        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "app", "presentation", "api", "schemas")
        
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{model.name.lower()}.py")
        
        imports = [
            "from datetime import datetime",
            "from typing import List, Optional, Dict, Any",
            "import uuid",
            "",
            "from pydantic import BaseModel, Field",
        ]
        
        # Add imports for relationships
        for relationship in model.relationships:
            if relationship.target_model != model.name:
                imports.append(f"from .{relationship.target_model.lower()} import {relationship.target_model}Response")
        
        class_def = [
            f"class {model.name}Base(BaseModel):",
            f'    """{model.description or f"Base schema for {model.name}."}"""',
        ]
        
        # Add fields for base schema
        for field in model.fields:
            if field.default is not None:
                class_def.append(f"    {field.pydantic_field}")
            elif not field.required:
                class_def.append(f"    {field.name}: Optional[{field.pydantic_type}] = None")
            else:
                class_def.append(f"    {field.name}: {field.pydantic_type}")
        
        class_def.extend([
            "",
            "",
            f"class {model.name}Create({model.name}Base):",
            f'    """{model.description or f"Schema for creating a {model.name}."}"""',
            "    pass",
            "",
            "",
            f"class {model.name}Update(BaseModel):",
            f'    """{model.description or f"Schema for updating a {model.name}."}"""',
        ])
        
        # Add fields for update schema
        for field in model.fields:
            class_def.append(f"    {field.name}: Optional[{field.pydantic_type}] = None")
        
        class_def.extend([
            "",
            "",
            f"class {model.name}Response({model.name}Base):",
            f'    """{model.description or f"Schema for {model.name} response."}"""',
            "    id: uuid.UUID",
            "    created_at: datetime",
            "    updated_at: datetime",
        ])
        
        # Add relationship fields for response schema
        for relationship in model.relationships:
            if relationship.is_to_many:
                class_def.append(f"    {relationship.relationship_name}: List[{relationship.target_model}Response] = []")
            else:
                class_def.append(f"    {relationship.relationship_name}: Optional[{relationship.target_model}Response] = None")
        
        class_def.extend([
            "",
            "    class Config:",
            "        orm_mode = True",
        ])
        
        # Combine all parts
        content = "\n".join(imports) + "\n\n\n" + "\n".join(class_def)
        
        with open(file_path, "w") as f:
            f.write(content)
        
        return file_path
    
    def generate_api_endpoint(self, model: Model, output_dir: Optional[str] = None) -> str:
        """Generate API endpoint file for the model."""
        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "app", "presentation", "api", "v1", "endpoints")
        
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{model.name.lower()}.py")
        
        model_var = model.name.lower()
        model_plural = p.plural(model_var)
        
        imports = [
            "from typing import List, Optional, Any",
            "import uuid",
            "",
            "from fastapi import APIRouter, Depends, HTTPException, status, Query, Path",
            "",
            f"from src.domain.entities import {model.name}, User",
            f"from src.domain.repositories.{model.name.lower()} import {model.name}Repository",
            f"from src.presentation.api.schemas.{model.name.lower()} import {model.name}Create, {model.name}Update, {model.name}Response",
            "from src.presentation.api.dependencies import get_current_active_user, require_privilege",
        ]
        
        router_def = [
            "router = APIRouter()",
            "",
            "",
            f"@router.post(\"/\", response_model={model.name}Response, status_code=status.HTTP_201_CREATED)",
            f"async def create_{model_var}(",
            f"    {model_var}_in: {model.name}Create,",
            f"    {model_var}_repository: {model.name}Repository = Depends(),",
            f"    current_user: User = Depends(require_privilege(\"create_{model_var}\")),",
            "):",
            f'    """Create a new {model_var}."""',
            "    try:",
            f"        {model_var} = {model.name}(",
            "            **{model_var}_in.dict(),",
            "        )",
            f"        return await {model_var}_repository.create({model_var})",
            "    except ValueError as e:",
            "        raise HTTPException(",
            "            status_code=status.HTTP_400_BAD_REQUEST,",
            "            detail=str(e),",
            "        )",
            "",
            "",
            f"@router.get(\"/{{{model_var}_id}}\", response_model={model.name}Response)",
            f"async def read_{model_var}(",
            f"    {model_var}_id: uuid.UUID = Path(..., title=\"The ID of the {model_var} to get\"),",
            f"    {model_var}_repository: {model.name}Repository = Depends(),",
            f"    current_user: User = Depends(require_privilege(\"read_{model_var}\")),",
            "):",
            f'    """Get a specific {model_var} by ID."""',
            f"    {model_var} = await {model_var}_repository.get_by_id({model_var}_id)",
            f"    if {model_var} is None:",
            "        raise HTTPException(",
            "            status_code=status.HTTP_404_NOT_FOUND,",
            f"            detail=\"{model.name} not found\",",
            "        )",
            f"    return {model_var}",
            "",
            "",
            f"@router.get(\"/\", response_model=List[{model.name}Response])",
            f"async def read_{model_plural}(",
            "    skip: int = Query(0, ge=0, title=\"Skip N items\"),",
            "    limit: int = Query(100, ge=1, le=100, title=\"Limit the number of items returned\"),",
            f"    {model_var}_repository: {model.name}Repository = Depends(),",
            f"    current_user: User = Depends(require_privilege(\"read_{model_var}\")),",
            "):",
            f'    """List {model_plural} with pagination."""',
            f"    return await {model_var}_repository.list(skip=skip, limit=limit)",
            "",
            "",
            f"@router.put(\"/{{{model_var}_id}}\", response_model={model.name}Response)",
            f"async def update_{model_var}(",
            f"    {model_var}_id: uuid.UUID = Path(..., title=\"The ID of the {model_var} to update\"),",
            f"    {model_var}_in: {model.name}Update,",
            f"    {model_var}_repository: {model.name}Repository = Depends(),",
            f"    current_user: User = Depends(require_privilege(\"update_{model_var}\")),",
            "):",
            f'    """Update a {model_var}."""',
            "    try:",
            f"        {model_var} = await {model_var}_repository.get_by_id({model_var}_id)",
            f"        if {model_var} is None:",
            "            raise HTTPException(",
            "                status_code=status.HTTP_404_NOT_FOUND,",
            f"                detail=\"{model.name} not found\",",
            "            )",
            "",
            "        # Update fields if provided",
            "        update_data = {model_var}_in.dict(exclude_unset=True)",
            "        for field, value in update_data.items():",
            f"            setattr({model_var}, field, value)",
            "",
            f"        return await {model_var}_repository.update({model_var})",
            "    except ValueError as e:",
            "        raise HTTPException(",
            "            status_code=status.HTTP_400_BAD_REQUEST,",
            "            detail=str(e),",
            "        )",
            "",
            "",
            f"@router.delete(\"/{{{model_var}_id}}\", status_code=status.HTTP_204_NO_CONTENT)",
            f"async def delete_{model_var}(",
            f"    {model_var}_id: uuid.UUID = Path(..., title=\"The ID of the {model_var} to delete\"),",
            f"    {model_var}_repository: {model.name}Repository = Depends(),",
            f"    current_user: User = Depends(require_privilege(\"delete_{model_var}\")),",
            "):",
            f'    """Delete a {model_var}."""',
            f"    {model_var} = await {model_var}_repository.get_by_id({model_var}_id)",
            f"    if {model_var} is None:",
            "        raise HTTPException(",
            "            status_code=status.HTTP_404_NOT_FOUND,",
            f"            detail=\"{model.name} not found\",",
            "        )",
            "",
            f"    deleted = await {model_var}_repository.delete({model_var}_id)",
            "    if not deleted:",
            "        raise HTTPException(",
            "            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,",
            f"            detail=\"Failed to delete {model_var}\",",
            "        )",
        ]
        
        # Add endpoints for relationships
        for relationship in model.relationships:
            if relationship.type_name in ["one_to_many", "many_to_many"]:
                target_name = relationship.target_model
                target_var = target_name.lower()
                rel_name = relationship.relationship_name
                
                router_def.extend([
                    "",
                    "",
                    f"@router.post(\"/{{{model_var}_id}}/{rel_name}/{{{target_var}_id}}\", status_code=status.HTTP_204_NO_CONTENT)",
                    f"async def add_{target_var}_to_{model_var}(",
                    f"    {model_var}_id: uuid.UUID = Path(..., title=\"The ID of the {model_var}\"),",
                    f"    {target_var}_id: uuid.UUID = Path(..., title=\"The ID of the {target_var} to add\"),",
                    f"    {model_var}_repository: {model.name}Repository = Depends(),",
                    f"    current_user: User = Depends(require_privilege(\"update_{model_var}\")),",
                    "):",
                    f'    """Add a {target_var} to a {model_var}."""',
                    f"    {model_var} = await {model_var}_repository.get_by_id({model_var}_id)",
                    f"    if {model_var} is None:",
                    "        raise HTTPException(",
                    "            status_code=status.HTTP_404_NOT_FOUND,",
                    f"            detail=\"{model.name} not found\",",
                    "        )",
                    "",
                    f"    success = await {model_var}_repository.add_{target_var}({model_var}_id, {target_var}_id)",
                    "    if not success:",
                    "        raise HTTPException(",
                    "            status_code=status.HTTP_400_BAD_REQUEST,",
                    f"            detail=\"Failed to add {target_var} to {model_var}\",",
                    "        )",
                    "",
                    "",
                    f"@router.delete(\"/{{{model_var}_id}}/{rel_name}/{{{target_var}_id}}\", status_code=status.HTTP_204_NO_CONTENT)",
                    f"async def remove_{target_var}_from_{model_var}(",
                    f"    {model_var}_id: uuid.UUID = Path(..., title=\"The ID of the {model_var}\"),",
                    f"    {target_var}_id: uuid.UUID = Path(..., title=\"The ID of the {target_var} to remove\"),",
                    f"    {model_var}_repository: {model.name}Repository = Depends(),",
                    f"    current_user: User = Depends(require_privilege(\"update_{model_var}\")),",
                    "):",
                    f'    """Remove a {target_var} from a {model_var}."""',
                    f"    {model_var} = await {model_var}_repository.get_by_id({model_var}_id)",
                    f"    if {model_var} is None:",
                    "        raise HTTPException(",
                    "            status_code=status.HTTP_404_NOT_FOUND,",
                    f"            detail=\"{model.name} not found\",",
                    "        )",
                    "",
                    f"    success = await {model_var}_repository.remove_{target_var}({model_var}_id, {target_var}_id)",
                    "    if not success:",
                    "        raise HTTPException(",
                    "            status_code=status.HTTP_400_BAD_REQUEST,",
                    f"            detail=\"Failed to remove {target_var} from {model_var}\",",
                    "        )",
                    "",
                    "",
                    f"@router.get(\"/{{{model_var}_id}}/{rel_name}\", response_model=List[{target_name}Response])",
                    f"async def read_{model_var}_{rel_name}(",
                    f"    {model_var}_id: uuid.UUID = Path(..., title=\"The ID of the {model_var}\"),",
                    f"    {model_var}_repository: {model.name}Repository = Depends(),",
                    f"    current_user: User = Depends(require_privilege(\"read_{model_var}\")),",
                    "):",
                    f'    """Get all {rel_name} for a {model_var}."""',
                    f"    {model_var} = await {model_var}_repository.get_by_id({model_var}_id)",
                    f"    if {model_var} is None:",
                    "        raise HTTPException(",
                    "            status_code=status.HTTP_404_NOT_FOUND,",
                    f"            detail=\"{model.name} not found\",",
                    "        )",
                    "",
                    f"    return await {model_var}_repository.get_{rel_name}({model_var}_id)",
                ])
        
        # Combine all parts
        content = "\n".join(imports) + "\n\n\n" + "\n".join(router_def)
        
        with open(file_path, "w") as f:
            f.write(content)
        
        return file_path
    
    def generate_model_files(self, model: Model) -> List[str]:
        """Generate all files for a model."""
        files = []
        
        # Generate domain entity
        entity_file = self.generate_domain_entity(model)
        files.append(entity_file)
        
        # Generate repository interface
        repo_interface_file = self.generate_repository_interface(model)
        files.append(repo_interface_file)
        
        # Generate SQLAlchemy model
        sqlalchemy_model_file = self.generate_sqlalchemy_model(model)
        files.append(sqlalchemy_model_file)
        
        # Generate repository implementation
        repo_impl_file = self.generate_repository_implementation(model)
        files.append(repo_impl_file)
        
        # Generate API schema
        api_schema_file = self.generate_api_schema(model)
        files.append(api_schema_file)
        
        # Generate API endpoint
        api_endpoint_file = self.generate_api_endpoint(model)
        files.append(api_endpoint_file)
        
        return files
