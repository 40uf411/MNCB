"""
Terminal command for adding new entities with CRUD operations.
"""
import os
import typer
from typing import Optional, List, Dict, Any
import inflect
import json

from src.application.use_cases.model_generator import ModelField, ModelRelationship, Model, ModelGenerator
from src.application.use_cases.crud_generator import CRUDGenerator

# Initialize inflect engine for pluralization
p = inflect.engine()

app = typer.Typer(help="Entity Creator - Add new entities with CRUD operations to an existing project")

@app.command()
def add_entity(
    project_dir: str = typer.Option(".", help="Directory of the existing project"),
    entity_name: str = typer.Option(..., help="Name of the entity to create (PascalCase)"),
    streamable: bool = typer.Option(False, help="Whether the entity should be streamable"),
    fields_json: Optional[str] = typer.Option(None, help="JSON string defining fields (alternative to interactive mode)"),
    relationships_json: Optional[str] = typer.Option(None, help="JSON string defining relationships (alternative to interactive mode)"),
    interactive: bool = typer.Option(True, help="Run in interactive mode to input fields and relationships"),
):
    """
    Add a new entity with CRUD operations to an existing project.
    
    This command will:
    1. Create the domain entity
    2. Create the repository interface
    3. Create the SQLAlchemy model
    4. Create the repository implementation
    5. Create the API schema
    6. Create the API endpoint
    7. Update the API router
    8. Add necessary privileges
    
    You can define fields and relationships either interactively or via JSON.
    """
    typer.echo(f"Adding new entity '{entity_name}' to project at {project_dir}")
    
    # Validate project directory
    if not os.path.isdir(project_dir):
        typer.echo(f"Error: Project directory {project_dir} does not exist")
        raise typer.Exit(1)
    
    # Validate entity name
    if not entity_name[0].isupper() or not entity_name.isalnum():
        typer.echo("Error: Entity name must be in PascalCase (e.g., Product)")
        raise typer.Exit(1)
    
    # Collect fields
    fields = []
    if fields_json:
        try:
            fields_data = json.loads(fields_json)
            for field_data in fields_data:
                fields.append(ModelField(
                    name=field_data["name"],
                    type_name=field_data["type"],
                    description=field_data.get("description", ""),
                    required=field_data.get("required", True),
                    unique=field_data.get("unique", False),
                    default=field_data.get("default", None),
                ))
        except (json.JSONDecodeError, KeyError) as e:
            typer.echo(f"Error parsing fields JSON: {e}")
            raise typer.Exit(1)
    elif interactive:
        fields = collect_fields_interactive(entity_name)
    
    if not fields:
        typer.echo("Error: No fields defined for entity")
        raise typer.Exit(1)
    
    # Collect relationships
    relationships = []
    if relationships_json:
        try:
            relationships_data = json.loads(relationships_json)
            for rel_data in relationships_data:
                relationships.append(ModelRelationship(
                    type_name=rel_data["type"],
                    target_model=rel_data["target_model"],
                    back_populates=rel_data.get("back_populates", None),
                ))
        except (json.JSONDecodeError, KeyError) as e:
            typer.echo(f"Error parsing relationships JSON: {e}")
            raise typer.Exit(1)
    elif interactive:
        relationships = collect_relationships_interactive(entity_name)
    
    # Create model
    model = Model(
        name=entity_name,
        fields=fields,
        relationships=relationships,
        description=f"{entity_name} entity",
    )
    
    # Set streamable flag
    if streamable:
        # Find the is_streamable field in the model
        for field in model.fields:
            if field.name == "is_streamable":
                field.default = True
                break
        else:
            # If is_streamable field doesn't exist, add it
            model.fields.append(ModelField(
                name="is_streamable",
                type_name="bool",
                description="Whether this entity is streamable",
                required=True,
                unique=False,
                default=True,
            ))
    
    # Generate files
    try:
        generator = ModelGenerator(project_dir)
        files = generator.generate_model_files(model)
        
        # Generate CRUD files
        crud_generator = CRUDGenerator(project_dir)
        crud_files = crud_generator.generate_crud_files([model])
        
        files.extend(crud_files)
        
        typer.echo(f"Successfully created {len(files)} files for entity {entity_name}:")
        for file in files:
            typer.echo(f"  - {os.path.relpath(file, project_dir)}")
        
        typer.echo("\nNext steps:")
        typer.echo("1. Review the generated files")
        typer.echo("2. Run database migrations if needed")
        typer.echo("3. Restart your application")
        
        if streamable:
            typer.echo("\nNote: This entity is marked as streamable. Make sure streaming is enabled in your application.")
    
    except Exception as e:
        typer.echo(f"Error generating entity files: {e}")
        raise typer.Exit(1)


def collect_fields_interactive(entity_name: str) -> List[ModelField]:
    """Collect fields interactively."""
    fields = []
    typer.echo(f"\nDefining fields for {entity_name}:")
    
    valid_types = ["str", "int", "float", "bool", "datetime", "date", "uuid", "list", "dict"]
    
    while True:
        field_name = typer.prompt("Field name (empty to finish)", default="")
        if not field_name:
            break
        
        # Validate field name
        if not field_name[0].islower() or not field_name.replace("_", "").isalnum():
            typer.echo("Field name must be in snake_case (e.g., first_name)")
            continue
        
        # Check if field name already exists
        if any(f.name == field_name for f in fields):
            typer.echo(f"Field {field_name} already exists")
            continue
        
        # Get field type
        field_type = typer.prompt(
            "Field type",
            type=str,
            default="str",
            show_choices=True,
            show_default=True,
            choices=valid_types
        )
        
        # Get field description
        field_description = typer.prompt("Field description (optional)", default="")
        
        # Get required status
        field_required = typer.confirm("Is this field required?", default=True)
        
        # Get unique status
        field_unique = typer.confirm("Is this field unique?", default=False)
        
        # Get default value
        field_default = None
        has_default = typer.confirm("Does this field have a default value?", default=False)
        if has_default:
            field_default = typer.prompt("Default value", default="None")
            if field_default == "None":
                field_default = None
            elif field_type == "bool":
                field_default = field_default.lower() == "true"
            elif field_type == "int":
                field_default = int(field_default)
            elif field_type == "float":
                field_default = float(field_default)
        
        # Create field
        field = ModelField(
            name=field_name,
            type_name=field_type,
            description=field_description,
            required=field_required,
            unique=field_unique,
            default=field_default,
        )
        fields.append(field)
        
        typer.echo(f"Added field: {field_name} ({field_type})")
    
    return fields


def collect_relationships_interactive(entity_name: str) -> List[ModelRelationship]:
    """Collect relationships interactively."""
    relationships = []
    typer.echo(f"\nDefining relationships for {entity_name}:")
    
    valid_types = ["one_to_one", "one_to_many", "many_to_one", "many_to_many"]
    
    while True:
        # Get relationship type
        rel_type = typer.prompt(
            "Relationship type (empty to finish)",
            type=str,
            default="",
            show_choices=True,
            choices=valid_types + [""]
        )
        
        if not rel_type:
            break
        
        # Get target model
        target_model = typer.prompt("Target model name (PascalCase)")
        
        # Validate target model name
        if not target_model[0].isupper() or not target_model.isalnum():
            typer.echo("Target model name must be in PascalCase (e.g., Product)")
            continue
        
        # Get back populates
        back_populates = typer.prompt("Back reference name (optional)", default="")
        if not back_populates:
            back_populates = None
        
        # Create relationship
        relationship = ModelRelationship(
            type_name=rel_type,
            target_model=target_model,
            back_populates=back_populates,
        )
        relationships.append(relationship)
        
        typer.echo(f"Added relationship: {rel_type} to {target_model}")
    
    return relationships


if __name__ == "__main__":
    app()
