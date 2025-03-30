# Me Need Code-Base

A command-line tool to generate a FastAPI application with PostgreSQL, DragonFlyDB, and JWT OAuth2 authentication following onion architecture and domain-driven design principles.

## Features

- **Modern Architecture**: Follows onion architecture and domain-driven design principles
- **Authentication System**: Built-in JWT OAuth2 authentication with users, roles, and privileges
- **Database Integration**: PostgreSQL for persistent storage and DragonFlyDB for caching
- **Custom Models**: Interactive CLI for defining custom models with relationships
- **CRUD Operations**: Automatic generation of CRUD endpoints with role-based access control
- **API Documentation**: Automatic Swagger/OpenAPI documentation

## Installation

```bash
# Clone the repository
git clone https://github.com/40uf411/MNCB.git
cd MCNB

# Install the package
pip install -e .
```

## Usage

### Basic Usage

```bash
# Generate a new FastAPI application
mncb-generator --project-name my_app --output-dir ./my_app
```

### Command-line Options

```
--project-name      Name of the project (default: fastapi_app)
--output-dir        Output directory for the generated codebase (default: ./output)
--db-name           Name of the PostgreSQL database (default: fastapi_db)
--db-user           PostgreSQL database user (default: postgres)
--db-password       PostgreSQL database password (default: postgres)
--db-host           PostgreSQL database host (default: localhost)
--db-port           PostgreSQL database port (default: 5432)
--cache-host        DragonFlyDB cache host (default: localhost)
--cache-port        DragonFlyDB cache port (default: 6379)
--jwt-secret        Secret key for JWT token generation (default: your-secret-key)
--jwt-algorithm     Algorithm for JWT token generation (default: HS256)
--jwt-expiration    JWT token expiration time in minutes (default: 30)
--interactive       Run in interactive mode to input custom models
```

## Architecture

The generated application follows the onion architecture pattern with the following layers:

### Domain Layer

The core of the application containing business logic and entities.

- **Entities**: Business objects with their properties and behaviors
- **Repositories**: Interfaces for data access
- **Services**: Business logic interfaces

### Application Layer

Coordinates the application activities and doesn't contain business logic.

- **Use Cases**: Application-specific business rules
- **Interfaces**: Interfaces for external services

### Infrastructure Layer

Provides implementations for the interfaces defined in the inner layers.

- **Persistence**: Database models and repository implementations
- **Auth**: Authentication and authorization implementations
- **Config**: Configuration classes

### Presentation Layer

Handles the interaction with external systems.

- **API**: REST API endpoints
- **CLI**: Command-line interfaces

## Authentication System

The generated application includes a complete authentication system with:

- **Users**: Application users with username, email, and password
- **Roles**: Groups of privileges (e.g., admin, manager, user)
- **Privileges**: Individual permissions for specific actions
- **JWT Authentication**: Secure token-based authentication

### Default Roles and Privileges

The system comes with three predefined roles:

1. **Admin**: Has all privileges
2. **Manager**: Can perform CRUD operations on all entities
3. **User**: Can only read entities

### Default Users

The system creates the following default users:

1. **Admin**: Username: `admin`, Password: `admin`
2. **Manager**: Username: `manager`, Password: `manager`
3. **User**: Username: `user`, Password: `user`

## Custom Models

The generator allows you to define custom models with:

- **Fields**: Various data types (string, integer, boolean, etc.)
- **Relationships**: One-to-one, one-to-many, many-to-one, many-to-many
- **Validation**: Required fields, unique constraints, etc.

### Example Model Definition

When running in interactive mode, you'll be prompted to define your models:

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

## Generated Files

The generator creates the following structure:

```
app/
├── domain/
│   ├── entities/
│   ├── repositories/
│   └── services/
├── application/
│   ├── use_cases/
│   └── interfaces/
├── infrastructure/
│   ├── persistence/
│   ├── auth/
│   └── config/
└── presentation/
    ├── api/
    └── cli/
```

## Running the Generated Application

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

## Development

### Prerequisites

- Python 3.8+
- PostgreSQL
- DragonFlyDB (or Redis as an alternative)

### Testing

```bash
# Run tests
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
