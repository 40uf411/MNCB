#!/usr/bin/env python3
"""
CLI interface for the Me Need Code-Base.
"""

import os
import sys
import inquirer
from typing import List, Dict, Any, Optional

class CodebaseGenerator:
    """
    Main class for generating the FastAPI codebase with authentication system
    and custom models with CRUD operations.
    """
    
    def __init__(
        self,
        project_name: str,
        output_dir: str,
        db_config: Dict[str, Any],
        cache_config: Dict[str, Any],
        jwt_config: Dict[str, Any],
        interactive: bool = True,
    ):
        self.project_name = project_name
        self.output_dir = os.path.abspath(output_dir)
        self.db_config = db_config
        self.cache_config = cache_config
        self.jwt_config = jwt_config
        self.interactive = interactive
        self.models = []
        
    def generate(self):
        """Generate the complete FastAPI codebase."""
        print(f"Generating FastAPI codebase for project: {self.project_name}")
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Generate project structure
        self._generate_project_structure()
        
        # Generate authentication system
        self._generate_auth_system()
        
        # Get custom models from user if in interactive mode
        if self.interactive:
            self._get_custom_models()
        
        # Generate custom models and CRUD operations
        self._generate_custom_models()
        
        # Generate configuration files
        self._generate_config_files()
        
        # Generate main application
        self._generate_main_app()
        
        print(f"FastAPI codebase generated successfully at: {self.output_dir}")
        print("To run the application:")
        print(f"1. cd {self.output_dir}")
        print("2. pip install -r requirements.txt")
        print("3. python -m app.main")
    
    def _generate_project_structure(self):
        """Generate the project directory structure."""
        directories = [
            "app",
            "app/domain",
            "app/domain/entities",
            "app/domain/repositories",
            "app/domain/services",
            "app/application",
            "app/application/use_cases",
            "app/application/interfaces",
            "app/infrastructure",
            "app/infrastructure/persistence",
            "app/infrastructure/auth",
            "app/infrastructure/config",
            "app/presentation",
            "app/presentation/api",
            "app/presentation/api/v1",
            "app/presentation/api/v1/endpoints",
            "tests",
            "tests/unit",
            "tests/integration",
        ]
        
        for directory in directories:
            os.makedirs(os.path.join(self.output_dir, directory), exist_ok=True)
            # Create __init__.py files
            with open(os.path.join(self.output_dir, directory, "__init__.py"), "w") as f:
                f.write("# Auto-generated by Me Need Code-Base\n")
    
    def _generate_auth_system(self):
        """Generate the authentication system with User, Role, and Privilege entities."""
        # Implementation will be added in the next steps
        pass
    
    def _get_custom_models(self):
        """Get custom model definitions from user input."""
        print("\nLet's define your custom models:")
        
        continue_adding = True
        while continue_adding:
            model_name = input("\nEnter model name (PascalCase, e.g., Product): ")
            
            if not model_name:
                print("Model name cannot be empty. Skipping.")
                continue
            
            # Ensure first letter is uppercase
            model_name = model_name[0].upper() + model_name[1:]
            
            fields = []
            print(f"\nDefining fields for {model_name}:")
            print("Enter field definitions in format: name:type (e.g., title:str, price:float)")
            print("Available types: str, int, float, bool, datetime, date, uuid, list, dict")
            print("Enter an empty line when done.")
            
            while True:
                field_def = input("Field (name:type): ")
                if not field_def:
                    break
                
                if ":" not in field_def:
                    print("Invalid format. Use name:type format.")
                    continue
                
                name, type_name = field_def.split(":", 1)
                name = name.strip()
                type_name = type_name.strip().lower()
                
                valid_types = ["str", "int", "float", "bool", "datetime", "date", "uuid", "list", "dict"]
                if type_name not in valid_types:
                    print(f"Invalid type. Choose from: {', '.join(valid_types)}")
                    continue
                
                fields.append({"name": name, "type": type_name})
            
            # Ask for relationships
            relationships = []
            print(f"\nDefining relationships for {model_name}:")
            print("Enter relationship definitions in format: type:model (e.g., many_to_one:User)")
            print("Available types: one_to_one, one_to_many, many_to_one, many_to_many")
            print("Enter an empty line when done.")
            
            while True:
                rel_def = input("Relationship (type:model): ")
                if not rel_def:
                    break
                
                if ":" not in rel_def:
                    print("Invalid format. Use type:model format.")
                    continue
                
                rel_type, rel_model = rel_def.split(":", 1)
                rel_type = rel_type.strip().lower()
                rel_model = rel_model.strip()
                
                valid_rel_types = ["one_to_one", "one_to_many", "many_to_one", "many_to_many"]
                if rel_type not in valid_rel_types:
                    print(f"Invalid relationship type. Choose from: {', '.join(valid_rel_types)}")
                    continue
                
                relationships.append({"type": rel_type, "model": rel_model})
            
            # Add model to the list
            self.models.append({
                "name": model_name,
                "fields": fields,
                "relationships": relationships
            })
            
            # Ask if user wants to add more models
            add_more = input("\nAdd another model? (y/n): ")
            continue_adding = add_more.lower() == 'y'
    
    def _generate_custom_models(self):
        """Generate custom models and their CRUD operations."""
        # Implementation will be added in the next steps
        pass
    
    def _generate_config_files(self):
        """Generate configuration files for the application."""
        # Implementation will be added in the next steps
        pass
    
    def _generate_main_app(self):
        """Generate the main FastAPI application."""
        # Implementation will be added in the next steps
        pass
