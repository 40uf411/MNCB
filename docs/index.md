# Me Need Code-Base Documentation

## Overview

The Me Need Code-Base is a powerful tool designed to streamline the development of FastAPI applications following best practices in software architecture. This documentation provides comprehensive information about the generator, its features, and how to use it effectively.

## Table of Contents

1. [Getting Started](README.md)
   - Installation
   - Basic Usage
   - Configuration Options

2. [User Guide](user_guide.md)
   - Detailed Usage Instructions
   - Configuration Options
   - Interactive Mode
   - Generated Application Structure

3. [Entity Creation and Management](entity_creation_guide.md)
   - Understanding Entity Structure
   - Adding New Entities with Terminal Tool
   - Working with Streamable Entities
   - Customizing Entities
   - Best Practices

4. [Real-Time Data Streaming Protocol](streaming_protocol.md)
   - Architecture
   - WebSocket Connection
   - Message Format
   - Operations
   - Error Codes
   - Permission Model
   - Usage Examples

5. [Developer Guide](developer_guide.md)
   - Project Structure
   - Core Components
   - Generated Application Architecture
   - Authentication System
   - Role-Based Access Control
   - Database Integration
   - Contributing

## Key Features

### Modern Architecture

The generated application follows the onion architecture pattern and domain-driven design principles:

- **Domain Layer**: Contains business entities, repository interfaces, and service interfaces
- **Application Layer**: Contains use cases that orchestrate the flow of data
- **Infrastructure Layer**: Contains implementations of repositories and services
- **Presentation Layer**: Contains API endpoints, CLI interfaces, and other user interfaces

### Authentication System

A complete authentication system with:

- **Users**: Application users with username, email, and password
- **Roles**: Groups of privileges (e.g., admin, manager, user)
- **Privileges**: Individual permissions for specific actions
- **JWT Authentication**: Secure token-based authentication

### Database Integration

- **PostgreSQL**: For persistent storage
- **DragonFlyDB**: For caching
- **SQLAlchemy**: For ORM
- **Alembic**: For database migrations

### Timestamp Fields and Soft Delete

All entities include:

- **created_at**: When the entity was created
- **updated_at**: When the entity was last updated
- **deleted_at**: When the entity was soft deleted (if applicable)

The delete behavior can be configured as:

- **Soft Delete**: Marks entities as deleted without removing them from the database
- **Hard Delete**: Permanently removes entities from the database

### Real-Time Data Streaming

Entities can be marked as streamable, enabling real-time updates via:

- **WebSockets**: For client-server communication
- **Message Brokers**: Kafka or RabbitMQ for event distribution
- **Permission-Based Access**: Integration with the role-based access control system

### Entity Management

The generator provides tools for:

- **Interactive Entity Creation**: Define entities with fields and relationships interactively
- **JSON-Based Entity Creation**: Define entities using JSON for automation
- **CRUD Operations**: Automatic generation of Create, Read, Update, Delete operations
- **Role-Based Access Control**: Permissions for each operation

## Command-Line Tools

### mncb-generator

The main tool for generating a new FastAPI application:

```bash
mncb-generator --project-name my_app --output-dir ./my_app
```

### mncb-entity

A tool for adding new entities to an existing project:

```bash
mncb-entity add-entity --project-dir ./my_app --entity-name Product
```

## Configuration

The generator and the generated application can be configured through:

- **Command-Line Options**: For the generator
- **Environment Variables**: For the generated application
- **Configuration Files**: For advanced settings

## Best Practices

1. **Entity Design**: Follow domain-driven design principles
2. **API Design**: Use RESTful conventions
3. **Authentication**: Secure all endpoints with appropriate permissions
4. **Streaming**: Use streaming only for entities that need real-time updates
5. **Testing**: Write tests for all components

## Getting Help

If you encounter issues:

1. Check the documentation for the specific component
2. Review the error messages and logs
3. File an issue on the project repository with detailed information
