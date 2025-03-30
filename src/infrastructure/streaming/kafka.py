"""
Kafka implementation of the streaming service.
"""
from typing import Dict, Any, List, Callable, Optional, AsyncIterator
import json
import asyncio
import uuid
import logging

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError, UnknownTopicOrPartitionError

from src.domain.services.streaming import StreamingService
from src.infrastructure.config.platform import PlatformConfig


class KafkaStreamingService(StreamingService):
    """Kafka implementation of the streaming service."""
    
    def __init__(self, config: PlatformConfig):
        self.config = config
        self.bootstrap_servers = f"{config.streaming_broker_host}:{config.streaming_broker_port}"
        self.producer = None
        self.admin_client = None
        self.consumers = {}
        self.logger = logging.getLogger(__name__)
    
    async def connect(self) -> bool:
        """Connect to the Kafka broker."""
        try:
            # Initialize producer
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
            )
            await self.producer.start()
            
            # Initialize admin client
            self.admin_client = AIOKafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
            )
            
            self.logger.info(f"Connected to Kafka broker at {self.bootstrap_servers}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Kafka broker: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from the Kafka broker."""
        try:
            if self.producer:
                await self.producer.stop()
                self.producer = None
            
            if self.admin_client:
                await self.admin_client.close()
                self.admin_client = None
            
            # Stop all consumers
            for consumer in self.consumers.values():
                await consumer.stop()
            self.consumers = {}
            
            self.logger.info("Disconnected from Kafka broker")
            return True
        except Exception as e:
            self.logger.error(f"Failed to disconnect from Kafka broker: {e}")
            return False
    
    async def publish(self, topic: str, message: Dict[str, Any], key: Optional[str] = None) -> bool:
        """Publish a message to a topic."""
        try:
            if not self.producer:
                await self.connect()
            
            # Create topic if it doesn't exist
            if not await self.topic_exists(topic):
                await self.create_topic(topic)
            
            # Add timestamp to message
            message['timestamp'] = asyncio.get_event_loop().time()
            
            # Publish message
            await self.producer.send_and_wait(topic, message, key=key)
            self.logger.debug(f"Published message to topic {topic}: {message}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to publish message to topic {topic}: {e}")
            return False
    
    async def subscribe(self, topic: str, group_id: Optional[str] = None) -> AsyncIterator[Dict[str, Any]]:
        """Subscribe to a topic and yield messages."""
        try:
            # Use a random group_id if not provided
            if not group_id:
                group_id = f"group-{uuid.uuid4()}"
            
            # Create consumer if it doesn't exist for this group
            consumer_key = f"{topic}-{group_id}"
            if consumer_key not in self.consumers:
                consumer = AIOKafkaConsumer(
                    topic,
                    bootstrap_servers=self.bootstrap_servers,
                    group_id=group_id,
                    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                    auto_offset_reset='latest',
                )
                await consumer.start()
                self.consumers[consumer_key] = consumer
            else:
                consumer = self.consumers[consumer_key]
            
            self.logger.info(f"Subscribed to topic {topic} with group {group_id}")
            
            # Yield messages
            try:
                async for message in consumer:
                    yield message.value
            finally:
                # Clean up consumer when the iterator is done
                await consumer.stop()
                if consumer_key in self.consumers:
                    del self.consumers[consumer_key]
        except Exception as e:
            self.logger.error(f"Error in subscription to topic {topic}: {e}")
            raise
    
    async def create_topic(self, topic: str, partitions: int = 1, replication_factor: int = 1) -> bool:
        """Create a new topic."""
        try:
            if not self.admin_client:
                await self.connect()
            
            # Create topic
            topic_obj = NewTopic(
                name=topic,
                num_partitions=partitions,
                replication_factor=replication_factor,
            )
            await self.admin_client.create_topics([topic_obj])
            self.logger.info(f"Created topic {topic}")
            return True
        except TopicAlreadyExistsError:
            self.logger.info(f"Topic {topic} already exists")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create topic {topic}: {e}")
            return False
    
    async def delete_topic(self, topic: str) -> bool:
        """Delete a topic."""
        try:
            if not self.admin_client:
                await self.connect()
            
            # Delete topic
            await self.admin_client.delete_topics([topic])
            self.logger.info(f"Deleted topic {topic}")
            return True
        except UnknownTopicOrPartitionError:
            self.logger.info(f"Topic {topic} does not exist")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete topic {topic}: {e}")
            return False
    
    async def list_topics(self) -> List[str]:
        """List all available topics."""
        try:
            if not self.admin_client:
                await self.connect()
            
            # List topics
            topics = await self.admin_client.list_topics()
            return list(topics)
        except Exception as e:
            self.logger.error(f"Failed to list topics: {e}")
            return []
    
    async def topic_exists(self, topic: str) -> bool:
        """Check if a topic exists."""
        try:
            if not self.admin_client:
                await self.connect()
            
            # List topics
            topics = await self.admin_client.list_topics()
            return topic in topics
        except Exception as e:
            self.logger.error(f"Failed to check if topic {topic} exists: {e}")
            return False
