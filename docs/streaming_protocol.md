# Real-Time Data Streaming Protocol Documentation

## Overview

The FastAPI Codebase Generator includes a comprehensive real-time data streaming system that allows entities to be streamed in real-time using WebSockets and message brokers (Kafka or RabbitMQ). This document describes the streaming protocol, error codes, and usage patterns.

## Architecture

The streaming system consists of the following components:

1. **StreamingService**: An interface for interacting with message brokers
   - KafkaStreamingService: Implementation for Apache Kafka
   - RabbitMQStreamingService: Implementation for RabbitMQ

2. **WebSocketManager**: Manages WebSocket connections and integrates with the StreamingService

3. **Entity Streaming**: Entities marked with `is_streamable=True` are automatically published to the message broker when created, updated, or deleted

## Streaming Protocol

### WebSocket Connection

To establish a WebSocket connection:

```
GET /api/v1/ws
```

This endpoint requires authentication. The user must be logged in and the request must include a valid JWT token.

### Message Format

All messages exchanged over WebSockets follow a standard JSON format:

#### Client to Server (Requests)

```json
{
  "operation": "subscribe|unsubscribe|publish",
  "topic": "topic_name",
  "data": {}, // Optional, only for publish
  "entity_type": "entity_type", // Optional, for entity-related operations
  "entity_id": "uuid" // Optional, for entity-related operations
}
```

#### Server to Client (Responses)

```json
{
  "status": "success|error",
  "operation": "connect|subscribe|unsubscribe|publish|message|error",
  "topic": "topic_name", // Optional
  "message": "Human-readable message", // Optional
  "error_code": "ERROR_CODE", // Only for errors
  "data": {} // Optional, contains message data for "message" operation
}
```

### Operations

#### Subscribe

Subscribe to a topic to receive real-time updates:

```json
{
  "operation": "subscribe",
  "topic": "entity.product.123e4567-e89b-12d3-a456-426614174000"
}
```

#### Unsubscribe

Unsubscribe from a topic:

```json
{
  "operation": "unsubscribe",
  "topic": "entity.product.123e4567-e89b-12d3-a456-426614174000"
}
```

#### Publish

Publish a message to a topic:

```json
{
  "operation": "publish",
  "topic": "entity.product.123e4567-e89b-12d3-a456-426614174000",
  "data": {
    "key": "value"
  }
}
```

### Topic Naming Conventions

Topics follow these naming conventions:

- `entity.{entity_type}.{entity_id}`: For entity-specific events
- `entity.{entity_type}`: For all events of a specific entity type
- `user.{user_id}.{custom}`: For user-specific topics
- `public.{custom}`: For public topics accessible to all users

### Entity Events

When an entity with `is_streamable=True` is modified, the system automatically publishes events with the following format:

```json
{
  "event_type": "created|updated|deleted",
  "entity_type": "entity_type",
  "entity_id": "uuid",
  "timestamp": 1648756800.0,
  "data": {
    // Entity data
  }
}
```

## Error Codes

| Error Code | Description | Possible Causes |
|------------|-------------|----------------|
| `INVALID_JSON` | Invalid JSON format | The client sent a message that is not valid JSON |
| `VALIDATION_ERROR` | Message validation failed | The message format does not match the expected schema |
| `INVALID_OPERATION` | Unknown operation | The operation is not one of: subscribe, unsubscribe, publish |
| `PERMISSION_DENIED` | No permission for the operation | The user does not have the required privileges |
| `PUBLISH_FAILED` | Failed to publish message | The message broker rejected the message or is unavailable |
| `SUBSCRIPTION_ERROR` | Error in subscription | The subscription to the message broker failed |
| `TOPIC_NOT_FOUND` | Topic does not exist | The requested topic does not exist |
| `INTERNAL_ERROR` | Internal server error | An unexpected error occurred on the server |

## Permission Model

The streaming system integrates with the role-based access control system:

1. **Subscribe Permission**:
   - Admin users can subscribe to any topic
   - Users can subscribe to entity topics if they have the `read_{entity_type}` privilege
   - Users can subscribe to their own user-specific topics (`user.{user_id}.*`)
   - All users can subscribe to public topics (`public.*`)

2. **Publish Permission**:
   - Admin users can publish to any topic
   - Users can publish to entity topics if they have the `update_{entity_type}` privilege
   - Users can publish to their own user-specific topics (`user.{user_id}.*`)

## Usage Examples

### Subscribing to Entity Updates

```javascript
// Connect to WebSocket
const ws = new WebSocket('wss://api.example.com/api/v1/ws');

// Subscribe to a specific product
ws.onopen = () => {
  ws.send(JSON.stringify({
    operation: 'subscribe',
    topic: 'entity.product.123e4567-e89b-12d3-a456-426614174000'
  }));
};

// Handle incoming messages
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.status === 'success' && message.operation === 'message') {
    console.log('Received update:', message.data);
  }
};
```

### Publishing an Update

```javascript
// Publish an update to a product
ws.send(JSON.stringify({
  operation: 'publish',
  topic: 'entity.product.123e4567-e89b-12d3-a456-426614174000',
  data: {
    price: 99.99,
    inStock: true
  }
}));
```

## Configuration

The streaming system can be configured through environment variables:

- `DELETE_TYPE`: `soft` or `hard` (default: `soft`)
- `ENABLE_STREAMING`: `true` or `false` (default: `false`)
- `STREAMING_BROKER`: `kafka` or `rabbitmq` (default: `kafka`)
- `STREAMING_BROKER_HOST`: Hostname of the broker (default: `localhost`)
- `STREAMING_BROKER_PORT`: Port of the broker (default: `9092` for Kafka, `5672` for RabbitMQ)

## Best Practices

1. **Topic Subscription**: Subscribe only to the topics you need to minimize network traffic
2. **Error Handling**: Always handle error responses from the server
3. **Reconnection**: Implement reconnection logic in case the WebSocket connection is lost
4. **Message Size**: Keep message sizes small to ensure efficient transmission
5. **Security**: Never include sensitive information in messages as they may be stored in the message broker

## Limitations

1. The current implementation does not support message persistence beyond the capabilities provided by the message broker
2. WebSocket connections may time out after prolonged inactivity; clients should implement ping/pong mechanisms
3. Message order is not guaranteed across different topics
4. Maximum message size is limited by the WebSocket protocol and the message broker configuration
