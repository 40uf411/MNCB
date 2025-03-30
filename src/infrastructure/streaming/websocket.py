"""
WebSocket manager for real-time data streaming.
"""
from typing import Dict, Any, List, Set, Optional, Callable, Awaitable
import json
import asyncio
import logging
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect, status, Depends
from pydantic import BaseModel, ValidationError

from src.domain.entities import User
from src.domain.services.streaming import StreamingService
from src.infrastructure.config.platform import PlatformConfig


class StreamingError(Exception):
    """Exception raised for streaming errors."""
    
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


class StreamingRequest(BaseModel):
    """Request model for streaming operations."""
    
    operation: str  # "subscribe", "unsubscribe", "publish"
    topic: str
    data: Optional[Dict[str, Any]] = None
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None


class StreamingResponse(BaseModel):
    """Response model for streaming operations."""
    
    status: str  # "success", "error"
    operation: str
    topic: Optional[str] = None
    message: Optional[str] = None
    error_code: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class WebSocketManager:
    """Manager for WebSocket connections and streaming."""
    
    def __init__(self, streaming_service: StreamingService, platform_config: PlatformConfig):
        self.streaming_service = streaming_service
        self.platform_config = platform_config
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_subscriptions: Dict[str, Set[str]] = {}  # user_id -> set of topics
        self.logger = logging.getLogger(__name__)
    
    async def connect(self, websocket: WebSocket, user: User) -> None:
        """Accept a WebSocket connection."""
        await websocket.accept()
        user_id = str(user.id)
        self.active_connections[user_id] = websocket
        self.user_subscriptions[user_id] = set()
        
        # Send welcome message
        await self.send_response(
            websocket,
            StreamingResponse(
                status="success",
                operation="connect",
                message=f"Connected to streaming service as {user.username}"
            )
        )
        
        self.logger.info(f"User {user.username} ({user_id}) connected to WebSocket")
    
    async def disconnect(self, user_id: str) -> None:
        """Handle WebSocket disconnection."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        # Unsubscribe from all topics
        if user_id in self.user_subscriptions:
            del self.user_subscriptions[user_id]
        
        self.logger.info(f"User {user_id} disconnected from WebSocket")
    
    async def handle_message(self, websocket: WebSocket, user: User, message: str) -> None:
        """Handle incoming WebSocket message."""
        user_id = str(user.id)
        
        try:
            # Parse request
            request_data = json.loads(message)
            request = StreamingRequest(**request_data)
            
            # Handle request based on operation
            if request.operation == "subscribe":
                await self.handle_subscribe(websocket, user, request)
            elif request.operation == "unsubscribe":
                await self.handle_unsubscribe(websocket, user, request)
            elif request.operation == "publish":
                await self.handle_publish(websocket, user, request)
            else:
                raise StreamingError("INVALID_OPERATION", f"Unknown operation: {request.operation}")
        
        except json.JSONDecodeError:
            await self.send_error(websocket, "INVALID_JSON", "Invalid JSON format")
        except ValidationError as e:
            await self.send_error(websocket, "VALIDATION_ERROR", str(e))
        except StreamingError as e:
            await self.send_error(websocket, e.code, e.message)
        except Exception as e:
            self.logger.error(f"Error handling WebSocket message: {e}")
            await self.send_error(websocket, "INTERNAL_ERROR", "Internal server error")
    
    async def handle_subscribe(self, websocket: WebSocket, user: User, request: StreamingRequest) -> None:
        """Handle subscribe operation."""
        user_id = str(user.id)
        topic = request.topic
        
        # Check if user has permission to subscribe to this topic
        if not await self.check_subscribe_permission(user, topic, request.entity_type, request.entity_id):
            raise StreamingError("PERMISSION_DENIED", f"No permission to subscribe to topic: {topic}")
        
        # Add to user subscriptions
        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = set()
        self.user_subscriptions[user_id].add(topic)
        
        # Start subscription task
        asyncio.create_task(self.subscription_task(user, topic))
        
        # Send success response
        await self.send_response(
            websocket,
            StreamingResponse(
                status="success",
                operation="subscribe",
                topic=topic,
                message=f"Subscribed to topic: {topic}"
            )
        )
        
        self.logger.info(f"User {user.username} ({user_id}) subscribed to topic: {topic}")
    
    async def handle_unsubscribe(self, websocket: WebSocket, user: User, request: StreamingRequest) -> None:
        """Handle unsubscribe operation."""
        user_id = str(user.id)
        topic = request.topic
        
        # Remove from user subscriptions
        if user_id in self.user_subscriptions and topic in self.user_subscriptions[user_id]:
            self.user_subscriptions[user_id].remove(topic)
        
        # Send success response
        await self.send_response(
            websocket,
            StreamingResponse(
                status="success",
                operation="unsubscribe",
                topic=topic,
                message=f"Unsubscribed from topic: {topic}"
            )
        )
        
        self.logger.info(f"User {user.username} ({user_id}) unsubscribed from topic: {topic}")
    
    async def handle_publish(self, websocket: WebSocket, user: User, request: StreamingRequest) -> None:
        """Handle publish operation."""
        user_id = str(user.id)
        topic = request.topic
        data = request.data or {}
        
        # Check if user has permission to publish to this topic
        if not await self.check_publish_permission(user, topic, request.entity_type, request.entity_id):
            raise StreamingError("PERMISSION_DENIED", f"No permission to publish to topic: {topic}")
        
        # Add user info to data
        data["user_id"] = str(user.id)
        data["username"] = user.username
        
        # Publish to streaming service
        success = await self.streaming_service.publish(topic, data)
        
        if not success:
            raise StreamingError("PUBLISH_FAILED", f"Failed to publish to topic: {topic}")
        
        # Send success response
        await self.send_response(
            websocket,
            StreamingResponse(
                status="success",
                operation="publish",
                topic=topic,
                message=f"Published to topic: {topic}"
            )
        )
        
        self.logger.info(f"User {user.username} ({user_id}) published to topic: {topic}")
    
    async def subscription_task(self, user: User, topic: str) -> None:
        """Task to handle subscription to a topic and forward messages to WebSocket."""
        user_id = str(user.id)
        
        try:
            async for message in self.streaming_service.subscribe(topic):
                # Check if user is still subscribed and connected
                if (user_id in self.user_subscriptions and 
                    topic in self.user_subscriptions[user_id] and
                    user_id in self.active_connections):
                    
                    websocket = self.active_connections[user_id]
                    
                    # Send message to WebSocket
                    await self.send_response(
                        websocket,
                        StreamingResponse(
                            status="success",
                            operation="message",
                            topic=topic,
                            data=message
                        )
                    )
                else:
                    # User unsubscribed or disconnected
                    break
        except Exception as e:
            self.logger.error(f"Error in subscription task for topic {topic}: {e}")
            
            # Try to send error to user if still connected
            if user_id in self.active_connections:
                websocket = self.active_connections[user_id]
                await self.send_error(
                    websocket,
                    "SUBSCRIPTION_ERROR",
                    f"Error in subscription to topic {topic}: {str(e)}"
                )
    
    async def check_subscribe_permission(
        self, user: User, topic: str, entity_type: Optional[str], entity_id: Optional[UUID]
    ) -> bool:
        """Check if user has permission to subscribe to a topic."""
        # Admin can subscribe to any topic
        if user.is_superuser:
            return True
        
        # Check if topic is for an entity
        if entity_type and entity_id:
            # Check if user has read permission for this entity type
            privilege_name = f"read_{entity_type.lower()}"
            has_privilege = False
            
            for role in user.roles:
                for privilege in role.privileges:
                    if privilege.name == privilege_name:
                        has_privilege = True
                        break
                if has_privilege:
                    break
            
            return has_privilege
        
        # For non-entity topics, check if it's a public topic or user-specific topic
        if topic.startswith("public."):
            return True
        
        if topic.startswith(f"user.{user.id}."):
            return True
        
        # Default to deny
        return False
    
    async def check_publish_permission(
        self, user: User, topic: str, entity_type: Optional[str], entity_id: Optional[UUID]
    ) -> bool:
        """Check if user has permission to publish to a topic."""
        # Admin can publish to any topic
        if user.is_superuser:
            return True
        
        # Check if topic is for an entity
        if entity_type and entity_id:
            # Check if user has update permission for this entity type
            privilege_name = f"update_{entity_type.lower()}"
            has_privilege = False
            
            for role in user.roles:
                for privilege in role.privileges:
                    if privilege.name == privilege_name:
                        has_privilege = True
                        break
                if has_privilege:
                    break
            
            return has_privilege
        
        # For non-entity topics, check if it's a user-specific topic
        if topic.startswith(f"user.{user.id}."):
            return True
        
        # Default to deny
        return False
    
    async def send_response(self, websocket: WebSocket, response: StreamingResponse) -> None:
        """Send a response to the WebSocket."""
        await websocket.send_text(response.json())
    
    async def send_error(self, websocket: WebSocket, code: str, message: str) -> None:
        """Send an error response to the WebSocket."""
        response = StreamingResponse(
            status="error",
            operation="error",
            error_code=code,
            message=message
        )
        await websocket.send_text(response.json())
    
    async def broadcast(self, topic: str, message: Dict[str, Any]) -> None:
        """Broadcast a message to all users subscribed to a topic."""
        for user_id, topics in self.user_subscriptions.items():
            if topic in topics and user_id in self.active_connections:
                websocket = self.active_connections[user_id]
                await self.send_response(
                    websocket,
                    StreamingResponse(
                        status="success",
                        operation="message",
                        topic=topic,
                        data=message
                    )
                )
    
    async def publish_entity_event(
        self, entity_type: str, entity_id: UUID, event_type: str, data: Dict[str, Any]
    ) -> bool:
        """Publish an entity event to the streaming service."""
        topic = f"entity.{entity_type.lower()}.{entity_id}"
        
        # Add event type to data
        data["event_type"] = event_type
        data["entity_type"] = entity_type
        data["entity_id"] = str(entity_id)
        
        # Publish to streaming service
        return await self.streaming_service.publish(topic, data)
