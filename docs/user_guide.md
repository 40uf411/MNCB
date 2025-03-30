# FastAPI Codebase Generator User Guide

## Introduction

The FastAPI Codebase Generator is a powerful tool designed to streamline the development of FastAPI applications following best practices in software architecture. This guide will walk you through the process of using the tool to generate a complete FastAPI application with authentication, database integration, and custom models.

## Getting Started

### Installation

Before using the FastAPI Codebase Generator, ensure you have the following prerequisites installed:

- Python 3.8 or higher
- PostgreSQL
- DragonFlyDB (or Redis as an alternative)

To install the FastAPI Codebase Generator:

```bash
# Clone the repository
git clone https://github.com/yourusername/fastapi-generator.git
cd fastapi-generator

# Install the package
pip install -e .
```

### Basic Usage

The simplest way to use the generator is with the default settings:

```bash
fastapi-generator --project-name my_app --output-dir ./my_app
```

This will create a new FastAPI application in the `./my_app` directory with the default configuration.

## Configuration Options

The FastAPI Codebase Generator provides several configuration options to customize your application:

### Database Configuration

```bash
fastapi-generator \
  --db-name my_database \
  --db-user my_user \
  --db-password my_password \
  --db-host localhost \
  --db-port 5432
```

### Cache Configuration

```bash
fastapi-generator \
  --cache-host localhost \
  --cache-port 6379
```

### JWT Authentication Configuration

```bash
fastapi-generator \
  --jwt-secret my-secret-key \
  --jwt-algorithm HS256 \
  --jwt-expiration 60
```

## Interactive Mode

The interactive mode allows you to define custom models for your application:

```bash
fastapi-generator --interactive
```

### Defining Models

When running in interactive mode, you'll be prompted to define your models:

1. Enter the model name in PascalCase (e.g., Product)
2. Provide an optional description for the model
3. Define fields for the model:
   - Field name
   - Field type (str, int, float, bool, datetime, date, uuid, list, dict)
   - Field description (optional)
   - Required status
   - Unique constraint
4. Define relationships between models:
   - Relationship type (one_to_one, one_to_many, many_to_one, many_to_many)
   - Target model
   - Back reference name (optional)

### Example Model Definition

Here's an example of defining a Product model with a relationship to a Category model:

```
Enter model name (PascalCase, e.g., Product): Product
Enter model description (optional): Product entity for e-commerce

Defining fields for Product:
Enter field name for Product: name
Select field type: str
Enter field description (optional): Product name
Is this field required? [Y/n]: Y
Is this field unique? [y/N]: Y

Enter field name for Product: price
Select field type: float
Enter field description (optional): Product price
Is this field required? [Y/n]: Y
Is this field unique? [y/N]: N

Defining relationships for Product:
Select relationship type for Product: many_to_one
Enter target model name: Category
Enter back reference name (optional): products
```

## Generated Application Structure

The generator creates an application with the following structure:

```
app/
├── domain/
│   ├── entities/          # Domain entities (User, Role, Privilege, etc.)
│   ├── repositories/      # Repository interfaces
│   └── services/          # Service interfaces
├── application/
│   ├── use_cases/         # Application use cases
│   └── interfaces/        # Application interfaces
├── infrastructure/
│   ├── persistence/       # Database models and repository implementations
│   │   └── seeds/         # Seed data for the database
│   ├── auth/              # Authentication implementations
│   └── config/            # Configuration classes
└── presentation/
    ├── api/               # API endpoints
    │   └── v1/            # API version 1
    │       └── endpoints/ # API endpoint implementations
    └── cli/               # Command-line interfaces
```

## Authentication System

The generated application includes a complete authentication system with:

### Users, Roles, and Privileges

- **Users**: Application users with username, email, and password
- **Roles**: Groups of privileges (e.g., admin, manager, user)
- **Privileges**: Individual permissions for specific actions

### Default Users

The system creates the following default users:

1. **Admin**: Username: `admin`, Password: `admin`
   - Has all privileges
2. **Manager**: Username: `manager`, Password: `manager`
   - Can perform CRUD operations on all entities
3. **User**: Username: `user`, Password: `user`
   - Can only read entities

### Authentication Endpoints

The generated application includes the following authentication endpoints:

- `POST /api/v1/auth/register`: Register a new user
- `POST /api/v1/auth/login`: Login a user and get access token
- `POST /api/v1/auth/token`: OAuth2 compatible token login
- `POST /api/v1/auth/refresh`: Refresh an access token
- `GET /api/v1/auth/users/me`: Get current user information

## Running the Generated Application

To run the generated application:

```bash
# Navigate to the output directory
cd ./output

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python -m app.infrastructure.persistence.init_db

# Run the application
uvicorn app.presentation.api.app:app --reload
```

## API Documentation

Once the application is running, you can access the Swagger documentation at:

```
http://localhost:8000/docs
```

And the ReDoc documentation at:

```
http://localhost:8000/redoc
```

## Customizing the Generated Application

The generated application is designed to be easily customizable:

### Adding New Models

You can add new models to the application by:

1. Creating a new entity in the `app/domain/entities` directory
2. Creating a new repository interface in the `app/domain/repositories` directory
3. Creating a new SQLAlchemy model in the `app/infrastructure/persistence/models` directory
4. Creating a new repository implementation in the `app/infrastructure/persistence/repositories` directory
5. Creating new API schemas in the `app/presentation/api/schemas` directory
6. Creating new API endpoints in the `app/presentation/api/v1/endpoints` directory
7. Adding the new endpoints to the API router in `app/presentation/api/v1/api.py`

### Modifying Authentication

You can modify the authentication system by:

1. Updating the authentication services in the `app/infrastructure/auth` directory
2. Modifying the authentication use cases in the `app/application/use_cases/auth.py`
3. Updating the authentication endpoints in the `app/presentation/api/v1/endpoints/auth.py`

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:

1. Ensure PostgreSQL is running
2. Verify the database credentials in the environment variables
3. Check if the database exists and is accessible

### Authentication Issues

If you encounter authentication issues:

1. Verify the JWT secret key in the environment variables
2. Check if the user exists and is active
3. Ensure the user has the required privileges

## Conclusion

The FastAPI Codebase Generator provides a solid foundation for building FastAPI applications following best practices in software architecture. By using this tool, you can quickly set up a new project with authentication, database integration, and custom models, allowing you to focus on implementing your business logic rather than setting up the infrastructure.
