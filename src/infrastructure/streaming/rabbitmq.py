"""
RabbitMQ implementation of the streaming service.
"""
from typing import Dict, Any, List, Callable, Optional, AsyncIterator
import json
import asyncio
import uuid
import logging

import aio_pika
from aio_pika import connect_robust, Message, ExchangeType

from src.domain.services.streaming import StreamingService
from src.infrastructure.config.platform import PlatformConfig


class RabbitMQStreamingService(StreamingService):
    """RabbitMQ implementation of the streaming service."""
    
    def __init__(self, config: PlatformConfig):
        self.config = config
        self.connection_string = f"amqp://guest:guest@{config.streaming_broker_host}:{config.streaming_broker_port}/"
        self.connection = None
        self.channel = None
        self.exchanges = {}
        self.queues = {}
        self.logger = logging.getLogger(__name__)
    
    async def connect(self) -> bool:
        """Connect to the RabbitMQ broker."""
        try:
            # Connect to RabbitMQ
            self.connection = await connect_robust(self.connection_string)
            self.channel = await self.connection.channel()
            
            self.logger.info(f"Connected to RabbitMQ broker at {self.connection_string}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to RabbitMQ broker: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from the RabbitMQ broker."""
        try:
            if self.connection:
                await self.connection.close()
                self.connection = None
                self.channel = None
                self.exchanges = {}
                self.queues = {}
            
            self.logger.info("Disconnected from RabbitMQ broker")
            return True
        except Exception as e:
            self.logger.error(f"Failed to disconnect from RabbitMQ broker: {e}")
            return False
    
    async def publish(self, topic: str, message: Dict[str, Any], key: Optional[str] = None) -> bool:
        """Publish a message to a topic."""
        try:
            if not self.channel:
                await self.connect()
            
            # Get or create exchange
            if topic not in self.exchanges:
                exchange = await self.channel.declare_exchange(
                    topic,
                    ExchangeType.FANOUT,
                    durable=True,
                )
                self.exchanges[topic] = exchange
            else:
                exchange = self.exchanges[topic]
            
            # Add timestamp to message
            message['timestamp'] = asyncio.get_event_loop().time()
            
            # Create message
            routing_key = key or ""
            message_body = json.dumps(message).encode('utf-8')
            message_obj = Message(
                body=message_body,
                content_type='application/json',
            )
            
            # Publish message
            await exchange.publish(message_obj, routing_key=routing_key)
            self.logger.debug(f"Published message to topic {topic}: {message}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to publish message to topic {topic}: {e}")
            return False
    
    async def subscribe(self, topic: str, group_id: Optional[str] = None) -> AsyncIterator[Dict[str, Any]]:
        """Subscribe to a topic and yield messages."""
        try:
            if not self.channel:
                await self.connect()
            
            # Use a random queue name if group_id is not provided
            queue_name = group_id or f"queue-{uuid.uuid4()}"
            
            # Get or create exchange
            if topic not in self.exchanges:
                exchange = await self.channel.declare_exchange(
                    topic,
                    ExchangeType.FANOUT,
                    durable=True,
                )
                self.exchanges[topic] = exchange
            else:
                exchange = self.exchanges[topic]
            
            # Declare queue
            queue = await self.channel.declare_queue(queue_name, durable=True)
            await queue.bind(exchange)
            
            # Store queue for cleanup
            self.queues[queue_name] = queue
            
            self.logger.info(f"Subscribed to topic {topic} with queue {queue_name}")
            
            # Create message queue
            message_queue = asyncio.Queue()
            
            # Define message handler
            async def message_handler(message):
                async with message.process():
                    try:
                        body = message.body.decode('utf-8')
                        data = json.loads(body)
                        await message_queue.put(data)
                    except Exception as e:
                        self.logger.error(f"Error processing message: {e}")
            
            # Start consuming
            consumer_tag = await queue.consume(message_handler)
            
            try:
                # Yield messages from the queue
                while True:
                    message = await message_queue.get()
                    yield message
            finally:
                # Clean up
                await queue.cancel(consumer_tag)
                if queue_name in self.queues:
                    del self.queues[queue_name]
        except Exception as e:
            self.logger.error(f"Error in subscription to topic {topic}: {e}")
            raise
    
    async def create_topic(self, topic: str, partitions: int = 1, replication_factor: int = 1) -> bool:
        """Create a new topic (exchange in RabbitMQ)."""
        try:
            if not self.channel:
                await self.connect()
            
            # Create exchange
            exchange = await self.channel.declare_exchange(
                topic,
                ExchangeType.FANOUT,
                durable=True,
            )
            self.exchanges[topic] = exchange
            
            self.logger.info(f"Created topic (exchange) {topic}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create topic (exchange) {topic}: {e}")
            return False
    
    async def delete_topic(self, topic: str) -> bool:
        """Delete a topic (exchange in RabbitMQ)."""
        try:
            if not self.channel:
                await self.connect()
            
            # Delete exchange
            await self.channel.exchange_delete(topic)
            
            if topic in self.exchanges:
                del self.exchanges[topic]
            
            self.logger.info(f"Deleted topic (exchange) {topic}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete topic (exchange) {topic}: {e}")
            return False
    
    async def list_topics(self) -> List[str]:
        """List all available topics (exchanges in RabbitMQ)."""
        # Note: RabbitMQ doesn't provide a direct way to list exchanges via AMQP
        # This would typically require management API access
        # For now, we'll just return the exchanges we've created in this session
        return list(self.exchanges.keys())
    
    async def topic_exists(self, topic: str) -> bool:
        """Check if a topic (exchange in RabbitMQ) exists."""
        # Similar to list_topics, this would typically require management API
        # For now, we'll just check if we've created this exchange in this session
        return topic in self.exchanges
