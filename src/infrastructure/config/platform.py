"""
Platform configuration for the application.
"""
from typing import Dict, Any, Optional
from enum import Enum
import os


class DeleteType(str, Enum):
    """Delete type for entities."""
    SOFT = "soft"
    HARD = "hard"


class PlatformConfig:
    """Platform configuration for the application."""
    
    def __init__(
        self,
        delete_type: DeleteType = DeleteType.SOFT,
        enable_streaming: bool = False,
        streaming_broker: str = "kafka",
        streaming_broker_host: str = "localhost",
        streaming_broker_port: int = 9092,
    ):
        self.delete_type = delete_type
        self.enable_streaming = enable_streaming
        self.streaming_broker = streaming_broker
        self.streaming_broker_host = streaming_broker_host
        self.streaming_broker_port = streaming_broker_port
    
    @classmethod
    def from_env(cls) -> "PlatformConfig":
        """Create platform configuration from environment variables."""
        return cls(
            delete_type=DeleteType(os.getenv("DELETE_TYPE", DeleteType.SOFT)),
            enable_streaming=os.getenv("ENABLE_STREAMING", "false").lower() == "true",
            streaming_broker=os.getenv("STREAMING_BROKER", "kafka"),
            streaming_broker_host=os.getenv("STREAMING_BROKER_HOST", "localhost"),
            streaming_broker_port=int(os.getenv("STREAMING_BROKER_PORT", "9092")),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "delete_type": self.delete_type,
            "enable_streaming": self.enable_streaming,
            "streaming_broker": self.streaming_broker,
            "streaming_broker_host": self.streaming_broker_host,
            "streaming_broker_port": self.streaming_broker_port,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlatformConfig":
        """Create configuration from dictionary."""
        return cls(
            delete_type=DeleteType(data.get("delete_type", DeleteType.SOFT)),
            enable_streaming=data.get("enable_streaming", False),
            streaming_broker=data.get("streaming_broker", "kafka"),
            streaming_broker_host=data.get("streaming_broker_host", "localhost"),
            streaming_broker_port=data.get("streaming_broker_port", 9092),
        )
