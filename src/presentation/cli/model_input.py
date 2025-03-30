"""
CLI interface for collecting model definitions from users.
"""
from typing import List, Dict, Any, Optional
import os
import re
import inquirer
from inquirer import errors

from src.application.use_cases.model_generator import ModelField, ModelRelationship, Model, ModelGenerator

class ModelInputCollector:
    """Collects model definitions from user input."""
    
    def __init__(self):
        self.models = []
        self.valid_types = ["str", "int", "float", "bool", "datetime", "date", "uuid", "list", "dict"]
        self.valid_relationship_types = ["one_to_one", "one_to_many", "many_to_one", "many_to_many"]
    
    def validate_model_name(self, answers, current):
        """Validate model name."""
        if not current:
            raise errors.ValidationError('', reason="Model name cannot be empty")
        
        # Check if name starts with uppercase letter
        if not current[0].isupper():
            raise errors.ValidationError('', reason="Model name must start with an uppercase letter (PascalCase)")
        
        # Check if name contains only alphanumeric characters
        if not re.match(r'^[a-zA-Z0-9]+$', current):
            raise errors.ValidationError('', reason="Model name must contain only alphanumeric characters")
        
        # Check if name already exists
        for model in self.models:
            if model.name.lower() == current.lower():
                raise errors.ValidationError('', reason=f"Model with name '{current}' already exists")
        
        return True
    
    def validate_field_name(self, answers, current):
        """Validate field name."""
        if not current:
            raise errors.ValidationError('', reason="Field name cannot be empty")
        
        # Check if name starts with lowercase letter
        if not current[0].islower():
            raise errors.ValidationError('', reason="Field name must start with a lowercase letter")
        
        # Check if name contains only alphanumeric characters and underscores
        if not re.match(r'^[a-z][a-zA-Z0-9_]*$', current):
            raise errors.ValidationError('', reason="Field name must contain only alphanumeric characters and underscores")
        
        # Check if name already exists in current fields
        for field in answers.get('fields', []):
            if field['name'] == current:
                raise errors.ValidationError('', reason=f"Field with name '{current}' already exists in this model")
        
        return True
    
    def validate_field_type(self, answers, current):
        """Validate field type."""
        if not current:
            raise errors.ValidationError('', reason="Field type cannot be empty")
        
        if current not in self.valid_types:
            raise errors.ValidationError('', reason=f"Invalid field type. Choose from: {', '.join(self.valid_types)}")
        
        return True
    
    def validate_relationship_type(self, answers, current):
        """Validate relationship type."""
        if not current:
            raise errors.ValidationError('', reason="Relationship type cannot be empty")
        
        if current not in self.valid_relationship_types:
            raise errors.ValidationError('', reason=f"Invalid relationship type. Choose from: {', '.join(self.valid_relationship_types)}")
        
        return True
    
    def validate_relationship_model(self, answers, current):
        """Validate relationship target model."""
        if not current:
            raise errors.ValidationError('', reason="Target model cannot be empty")
        
        # Check if model exists or is the current model (self-reference)
        model_names = [model.name for model in self.models]
        if current != answers.get('name') and current not in model_names:
            raise errors.ValidationError('', reason=f"Model '{current}' does not exist. Available models: {', '.join(model_names)}")
        
        return True
    
    def collect_field(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Collect a single field definition."""
        questions = [
            inquirer.Text('name',
                          message=f"Enter field name for {model_name} (empty to finish):",
                          validate=self.validate_field_name),
            inquirer.List('type',
                         message="Select field type:",
                         choices=self.valid_types),
            inquirer.Text('description',
                         message="Enter field description (optional):"),
            inquirer.Confirm('required',
                            message="Is this field required?",
                            default=True),
            inquirer.Confirm('unique',
                            message="Is this field unique?",
                            default=False),
        ]
        
        # Get field name first to check if user wants to finish
        name_question = questions[0]
        name_answer = inquirer.prompt([name_question])
        
        if not name_answer or not name_answer['name']:
            return None
        
        # Get the rest of the field details
        answers = inquirer.prompt(questions[1:])
        answers['name'] = name_answer['name']
        
        return answers
    
    def collect_relationship(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Collect a single relationship definition."""
        questions = [
            inquirer.List('type',
                         message=f"Select relationship type for {model_name} (empty to finish):",
                         choices=self.valid_relationship_types + ['<Done>'],
                         default='<Done>'),
            inquirer.Text('target_model',
                         message="Enter target model name:",
                         validate=lambda answers, current: self.validate_relationship_model({'name': model_name}, current)),
            inquirer.Text('back_populates',
                         message="Enter back reference name (optional):"),
        ]
        
        # Get relationship type first to check if user wants to finish
        type_question = questions[0]
        type_answer = inquirer.prompt([type_question])
        
        if not type_answer or type_answer['type'] == '<Done>':
            return None
        
        # Get the rest of the relationship details
        answers = inquirer.prompt(questions[1:])
        answers['type'] = type_answer['type']
        
        return answers
    
    def collect_model(self) -> Optional[Model]:
        """Collect a single model definition."""
        questions = [
            inquirer.Text('name',
                          message="Enter model name (PascalCase, e.g., Product) (empty to finish):",
                          validate=self.validate_model_name),
            inquirer.Text('description',
                         message="Enter model description (optional):"),
        ]
        
        # Get model name first to check if user wants to finish
        name_question = questions[0]
        name_answer = inquirer.prompt([name_question])
        
        if not name_answer or not name_answer['name']:
            return None
        
        # Get the rest of the model details
        answers = inquirer.prompt(questions[1:])
        answers['name'] = name_answer['name']
        
        # Collect fields
        print(f"\nDefining fields for {answers['name']}:")
        fields = []
        while True:
            field_data = self.collect_field(answers['name'])
            if not field_data:
                break
            
            field = ModelField(
                name=field_data['name'],
                type_name=field_data['type'],
                description=field_data['description'],
                required=field_data['required'],
                unique=field_data['unique'],
            )
            fields.append(field)
        
        # Collect relationships
        print(f"\nDefining relationships for {answers['name']}:")
        relationships = []
        while True:
            relationship_data = self.collect_relationship(answers['name'])
            if not relationship_data:
                break
            
            relationship = ModelRelationship(
                type_name=relationship_data['type'],
                target_model=relationship_data['target_model'],
                back_populates=relationship_data['back_populates'] or None,
            )
            relationships.append(relationship)
        
        # Create model
        model = Model(
            name=answers['name'],
            description=answers['description'],
            fields=fields,
            relationships=relationships,
        )
        
        return model
    
    def collect_models(self) -> List[Model]:
        """Collect multiple model definitions."""
        print("Let's define your custom models:")
        
        while True:
            model = self.collect_model()
            if not model:
                break
            
            self.models.append(model)
            print(f"Model {model.name} added successfully!")
            
            # Ask if user wants to add more models
            add_more = inquirer.prompt([
                inquirer.Confirm('add_more',
                                message="Add another model?",
                                default=True),
            ])
            
            if not add_more or not add_more['add_more']:
                break
        
        return self.models


def generate_models(output_dir: str) -> List[str]:
    """Generate models from user input."""
    collector = ModelInputCollector()
    models = collector.collect_models()
    
    if not models:
        print("No models defined. Exiting.")
        return []
    
    generator = ModelGenerator(output_dir)
    generated_files = []
    
    for model in models:
        print(f"Generating files for model {model.name}...")
        model_files = generator.generate_model_files(model)
        generated_files.extend(model_files)
        print(f"Generated {len(model_files)} files for model {model.name}.")
    
    return generated_files
