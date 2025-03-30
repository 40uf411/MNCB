"""
Streaming service interface for real-time data streaming.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Callable, Optional, AsyncIterator
import uuid


class StreamingService(ABC):
    """Interface for real-time data streaming."""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the streaming broker."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from the streaming broker."""
        pass
    
    @abstractmethod
    async def publish(self, topic: str, message: Dict[str, Any], key: Optional[str] = None) -> bool:
        """Publish a message to a topic."""
        pass
    
    @abstractmethod
    async def subscribe(self, topic: str, group_id: Optional[str] = None) -> AsyncIterator[Dict[str, Any]]:
        """Subscribe to a topic and yield messages."""
        pass
    
    @abstractmethod
    async def create_topic(self, topic: str, partitions: int = 1, replication_factor: int = 1) -> bool:
        """Create a new topic."""
        pass
    
    @abstractmethod
    async def delete_topic(self, topic: str) -> bool:
        """Delete a topic."""
        pass
    
    @abstractmethod
    async def list_topics(self) -> List[str]:
        """List all available topics."""
        pass
    
    @abstractmethod
    async def topic_exists(self, topic: str) -> bool:
        """Check if a topic exists."""
        pass
