# Entity Creation and Management Guide

## Introduction

This guide explains how to create and manage entities in your FastAPI application generated with the Me Need Code-Base. It covers the structure of entities, how to add new entities using the terminal tool, and how to work with streamable entities for real-time data.

## Understanding the Entity Structure

### Domain-Driven Design and Onion Architecture

The generated application follows domain-driven design principles and onion architecture, which organizes code into concentric layers:

1. **Domain Layer** (Core)
   - Contains business entities, repository interfaces, and service interfaces
   - Independent of external frameworks and technologies

2. **Application Layer**
   - Contains use cases that orchestrate the flow of data to and from entities
   - Depends only on the domain layer

3. **Infrastructure Layer**
   - Contains implementations of repositories and services
   - Depends on the domain and application layers

4. **Presentation Layer**
   - Contains API endpoints, CLI interfaces, and other user interfaces
   - Depends on the application layer

### Entity Components

When you create an entity, the following components are generated:

1. **Domain Entity**
   - Located in `app/domain/entities/{entity_name.lower()}.py`
   - Defines the business object with its properties and behaviors
   - Inherits from `BaseEntity` which provides common fields like `id`, `created_at`, `updated_at`, `deleted_at`, and `is_streamable`

2. **Repository Interface**
   - Located in `app/domain/repositories/{entity_name.lower()}.py`
   - Defines the interface for data access operations
   - Inherits from `BaseRepository` which provides common CRUD operations

3. **SQLAlchemy Model**
   - Located in `app/infrastructure/persistence/models/{entity_name.lower()}.py`
   - Defines the database model for the entity
   - Inherits from `BaseModel` which provides common fields and behaviors

4. **Repository Implementation**
   - Located in `app/infrastructure/persistence/repositories/{entity_name.lower()}.py`
   - Implements the repository interface using SQLAlchemy
   - Inherits from `BaseSQLAlchemyRepository` which provides common CRUD implementations

5. **API Schema**
   - Located in `app/presentation/api/schemas/{entity_name.lower()}.py`
   - Defines the Pydantic models for API requests and responses

6. **API Endpoint**
   - Located in `app/presentation/api/v1/endpoints/{entity_name.lower()}.py`
   - Defines the API endpoints for CRUD operations
   - Includes role-based access control

## Adding New Entities

### Using the Terminal Tool

The Me Need Code-Base provides a terminal tool called `mncb-entity` for adding new entities to an existing project. This tool generates all the necessary files for a new entity with CRUD operations.

#### Basic Usage

```bash
mncb-entity add-entity --project-dir ./my_app --entity-name Product
```

This will start an interactive session to define fields and relationships for the new entity.

#### Command-line Options

```
--project-dir TEXT     Directory of the existing project  [default: .]
--entity-name TEXT     Name of the entity to create (PascalCase)  [required]
--streamable BOOLEAN   Whether the entity should be streamable  [default: False]
--fields-json TEXT     JSON string defining fields (alternative to interactive mode)
--relationships-json TEXT  JSON string defining relationships (alternative to interactive mode)
--interactive BOOLEAN  Run in interactive mode to input fields and relationships  [default: True]
```

#### Interactive Mode

In interactive mode, you'll be prompted to define fields and relationships for your entity:

1. **Fields**
   - Field name (snake_case, e.g., `product_name`)
   - Field type (`str`, `int`, `float`, `bool`, `datetime`, `date`, `uuid`, `list`, `dict`)
   - Field description (optional)
   - Required status (yes/no)
   - Unique constraint (yes/no)
   - Default value (optional)

2. **Relationships**
   - Relationship type (`one_to_one`, `one_to_many`, `many_to_one`, `many_to_many`)
   - Target model name (PascalCase, e.g., `Category`)
   - Back reference name (optional)

#### Non-Interactive Mode with JSON

You can also define fields and relationships using JSON:

```bash
mncb-entity add-entity \
  --project-dir ./my_app \
  --entity-name Product \
  --interactive false \
  --fields-json '[{"name":"name","type":"str","required":true,"unique":true},{"name":"price","type":"float","required":true}]' \
  --relationships-json '[{"type":"many_to_one","target_model":"Category","back_populates":"products"}]'
```

### Example: Creating a Product Entity

Here's an example of creating a Product entity with fields and relationships:

```bash
mncb-entity add-entity --project-dir ./my_app --entity-name Product
```

Interactive session:

```
Defining fields for Product:
Field name (empty to finish): name
Field type [str]: str
Field description (optional): Product name
Is this field required? [Y/n]: Y
Is this field unique? [y/N]: Y
Does this field have a default value? [y/N]: N
Added field: name (str)

Field name (empty to finish): price
Field type [str]: float
Field description (optional): Product price
Is this field required? [Y/n]: Y
Is this field unique? [y/N]: N
Does this field have a default value? [y/N]: N
Added field: price (float)

Field name (empty to finish): in_stock
Field type [str]: bool
Field description (optional): Whether the product is in stock
Is this field required? [Y/n]: Y
Is this field unique? [y/N]: N
Does this field have a default value? [y/N]: Y
Default value [None]: true
Added field: in_stock (bool)

Field name (empty to finish): 

Defining relationships for Product:
Relationship type (empty to finish) [one_to_one, one_to_many, many_to_one, many_to_many]: many_to_one
Target model name (PascalCase): Category
Back reference name (optional): products
Added relationship: many_to_one to Category

Relationship type (empty to finish) [one_to_one, one_to_many, many_to_one, many_to_many]: 

Successfully created 6 files for entity Product:
  - app/domain/entities/product.py
  - app/domain/repositories/product.py
  - app/infrastructure/persistence/models/product.py
  - app/infrastructure/persistence/repositories/product.py
  - app/presentation/api/schemas/product.py
  - app/presentation/api/v1/endpoints/product.py
```

## Working with Streamable Entities

### What are Streamable Entities?

Streamable entities are entities that can be streamed in real-time using WebSockets and message brokers. When an entity is marked as streamable, any changes to it (create, update, delete) are automatically published to the message broker and can be consumed by clients via WebSockets.

### Creating a Streamable Entity

To create a streamable entity, use the `--streamable` flag:

```bash
mncb-entity add-entity --project-dir ./my_app --entity-name ChatMessage --streamable
```

This will set the `is_streamable` field to `true` for the entity.

### Streaming Protocol

The streaming protocol is documented in detail in [streaming_protocol.md](streaming_protocol.md). Here's a brief overview:

1. **WebSocket Connection**
   - Connect to `/api/v1/ws` with a valid JWT token

2. **Subscribe to Entity Updates**
   - Send a subscription request for a specific entity:
     ```json
     {
       "operation": "subscribe",
       "topic": "entity.chat_message.{id}",
       "entity_type": "ChatMessage",
       "entity_id": "{id}"
     }
     ```

3. **Receive Updates**
   - Receive real-time updates when the entity changes:
     ```json
     {
       "status": "success",
       "operation": "message",
       "topic": "entity.chat_message.{id}",
       "data": {
         "event_type": "updated",
         "entity_type": "ChatMessage",
         "entity_id": "{id}",
         "timestamp": 1648756800.0,
         "data": {
           // Entity data
         }
       }
     }
     ```

### Permission Model for Streaming

The streaming system integrates with the role-based access control system:

1. **Subscribe Permission**
   - Users can subscribe to entity topics if they have the `read_{entity_type}` privilege

2. **Publish Permission**
   - Users can publish to entity topics if they have the `update_{entity_type}` privilege

## Customizing Entities

### Adding Custom Methods

You can add custom methods to your entities by editing the generated files. For example, to add a custom method to the Product entity:

```python
# app/domain/entities/product.py
def calculate_discount(self, percentage: float) -> float:
    """Calculate the discounted price."""
    return self.price * (1 - percentage / 100)
```

### Adding Custom Endpoints

You can add custom endpoints by editing the API endpoint file:

```python
# app/presentation/api/v1/endpoints/product.py
@router.get("/{product_id}/discount/{percentage}")
async def calculate_product_discount(
    product_id: uuid.UUID,
    percentage: float,
    product_repository: ProductRepository = Depends(),
    current_user: User = Depends(require_privilege("read_product")),
):
    """Calculate the discounted price of a product."""
    product = await product_repository.get_by_id(product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    discounted_price = product.calculate_discount(percentage)
    return {"original_price": product.price, "discount_percentage": percentage, "discounted_price": discounted_price}
```

## Best Practices

1. **Entity Naming**
   - Use PascalCase for entity names (e.g., `Product`, `OrderItem`)
   - Use singular nouns for entity names

2. **Field Naming**
   - Use snake_case for field names (e.g., `product_name`, `unit_price`)
   - Use descriptive names that reflect the business domain

3. **Relationships**
   - Define relationships carefully to ensure proper database schema generation
   - Use back references to enable bidirectional navigation

4. **Streamable Entities**
   - Only mark entities as streamable if they need real-time updates
   - Consider the performance implications of streaming high-volume entities

5. **Soft Delete**
   - Use soft delete for entities that might need to be restored
   - Use hard delete for transient data or when required by regulations

## Troubleshooting

### Common Issues

1. **Entity Creation Fails**
   - Ensure the project directory is correct
   - Ensure the entity name is in PascalCase
   - Ensure field names are in snake_case

2. **Relationship Issues**
   - Ensure the target model exists or will be created
   - Ensure the relationship type is appropriate for the domain model

3. **Streaming Issues**
   - Ensure the streaming broker is running
   - Check the streaming configuration in the environment variables
   - Verify that the user has the necessary privileges

### Getting Help

If you encounter issues not covered in this guide, please:

1. Check the error messages for specific details
2. Review the documentation for the specific component
3. Check the logs for more information
4. File an issue on the project repository with detailed information about the problem
