"""
CLI interface for the CRUD generator.
"""
from typing import List, Dict, Any, Optional
import os

from src.application.use_cases.model_generator import Model
from src.application.use_cases.crud_generator import CRUDGenerator
from src.presentation.cli.model_input import ModelInputCollector

def generate_crud_with_rbac(output_dir: str) -> List[str]:
    """Generate CRUD operations with role-based access control."""
    print("Generating CRUD operations with role-based access control...")
    
    # Collect model definitions
    collector = ModelInputCollector()
    models = collector.collect_models()
    
    if not models:
        print("No models defined. Exiting.")
        return []
    
    # Generate CRUD files
    generator = CRUDGenerator(output_dir)
    generated_files = generator.generate_crud_files(models)
    
    print(f"Generated {len(generated_files)} CRUD-related files.")
    return generated_files
