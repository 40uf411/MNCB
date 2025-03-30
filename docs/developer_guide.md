"""
Developer Guide for the Me Need Code-Base

This guide provides technical details for developers who want to understand
or contribute to the Me Need Code-Base.
"""

# Me Need Code-Base - Developer Guide

## Project Structure

The Me Need Code-Base follows a modular architecture to separate concerns and make the codebase maintainable:

```
fastapi_generator/
├── src/
│   ├── domain/
│   │   ├── entities/       # Domain entities
│   │   ├── repositories/   # Repository interfaces
│   │   └── services/       # Service interfaces
│   ├── application/
│   │   ├── use_cases/      # Application use cases
│   │   └── interfaces/     # Application interfaces
│   ├── infrastructure/
│   │   ├── persistence/    # Database implementations
│   │   ├── auth/           # Authentication implementations
│   │   └── config/         # Configuration classes
│   └── presentation/
│       ├── api/            # API components
│       └── cli/            # CLI components
└── docs/                   # Documentation
```

## Core Components

### Model Generator

The `ModelGenerator` class in `src/application/use_cases/model_generator.py` is responsible for generating all the necessary files for a custom model:

- Domain entities
- Repository interfaces
- SQLAlchemy models
- Repository implementations
- API schemas
- API endpoints

### CRUD Generator

The `CRUDGenerator` class in `src/application/use_cases/crud_generator.py` generates the role-based access control system:

- Privilege seeds
- Role seeds
- User seeds
- Role-privilege associations
- User-role associations
- API router updates
- Database initialization script

### Model Input Collector

The `ModelInputCollector` class in `src/presentation/cli/model_input.py` provides an interactive CLI for collecting model definitions from users:

- Model name and description
- Field definitions (name, type, description, required, unique)
- Relationship definitions (type, target model, back reference)

## Generated Application Architecture

The generated application follows the onion architecture pattern:

### Domain Layer

The core of the application containing business logic and entities:

- **Entities**: Business objects with their properties and behaviors
- **Repositories**: Interfaces for data access
- **Services**: Business logic interfaces

### Application Layer

Coordinates the application activities:

- **Use Cases**: Application-specific business rules
- **Interfaces**: Interfaces for external services

### Infrastructure Layer

Provides implementations for the interfaces defined in the inner layers:

- **Persistence**: Database models and repository implementations
- **Auth**: Authentication and authorization implementations
- **Config**: Configuration classes

### Presentation Layer

Handles the interaction with external systems:

- **API**: REST API endpoints
- **CLI**: Command-line interfaces

## Authentication System

The authentication system is built on JWT OAuth2 and includes:

### Domain Layer

- **User Entity**: Represents a system user
- **Role Entity**: Represents a user role with associated privileges
- **Privilege Entity**: Represents a system permission
- **UserRole Association**: Many-to-many relationship between users and roles
- **RolePrivilege Association**: Many-to-many relationship between roles and privileges

### Infrastructure Layer

- **PasswordServiceImpl**: Handles password hashing and verification
- **TokenServiceImpl**: Handles JWT token generation and validation
- **AuthServiceImpl**: Handles user authentication and privilege checking

### Application Layer

- **RegisterUserUseCase**: Registers a new user
- **LoginUserUseCase**: Logs in a user and returns tokens
- **RefreshTokenUseCase**: Refreshes an access token
- **GetCurrentUserUseCase**: Gets the current user from a token
- **CheckUserPrivilegeUseCase**: Checks if a user has a specific privilege

### Presentation Layer

- **Auth Endpoints**: API endpoints for authentication
- **Auth Dependencies**: FastAPI dependencies for authentication

## Role-Based Access Control

The role-based access control system is implemented as follows:

1. **Privileges**: Each action (create, read, update, delete) on each entity has a corresponding privilege
2. **Roles**: Roles are collections of privileges
3. **Users**: Users are assigned roles
4. **Endpoints**: Each endpoint checks if the user has the required privilege

The system comes with three predefined roles:

1. **Admin**: Has all privileges
2. **Manager**: Can perform CRUD operations on all entities
3. **User**: Can only read entities

## Database Integration

The generated application uses:

- **PostgreSQL**: For persistent storage
- **DragonFlyDB**: For caching
- **SQLAlchemy**: For ORM
- **Alembic**: For database migrations

## API Documentation

The generated application includes automatic API documentation using:

- **Swagger/OpenAPI**: Available at `/docs`
- **ReDoc**: Available at `/redoc`

## Testing

The generated application includes a testing framework using:

- **pytest**: For unit and integration tests
- **pytest-asyncio**: For testing async code
- **TestClient**: For testing FastAPI endpoints

## Contributing

To contribute to the Me Need Code-Base:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests for your changes
5. Submit a pull request

## Development Setup

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/yourusername/MNCB.git
cd MNCB

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Building the Package

To build the package:

```bash
# Install build dependencies
pip install build

# Build the package
python -m build
```

## Publishing the Package

To publish the package to PyPI:

```bash
# Install twine
pip install twine

# Upload the package
twine upload dist/*
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
