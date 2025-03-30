"""
Main entry point for the Me Need Code-Base.
"""
import os
import sys
import typer
from typing import Optional
from enum import Enum
from pathlib import Path

from src.presentation.cli.generator import CodebaseGenerator
from src.presentation.cli.model_input import generate_models
from src.presentation.cli.crud_input import generate_crud_with_rbac

app = typer.Typer(help="Me Need Code-Base - A tool to generate FastAPI applications with PostgreSQL, DragonFlyDB, and JWT OAuth2 authentication")

class DeleteType(str, Enum):
    """Delete type for entities."""
    SOFT = "soft"
    HARD = "hard"

class StreamingBroker(str, Enum):
    """Streaming broker type."""
    KAFKA = "kafka"
    RABBITMQ = "rabbitmq"
    NONE = "none"

@app.command()
def generate(
    project_name: str = typer.Option("fastapi_app", help="Name of the project"),
    output_dir: str = typer.Option("./output", help="Output directory for the generated codebase"),
    db_name: str = typer.Option("fastapi_db", help="Name of the PostgreSQL database"),
    db_user: str = typer.Option("postgres", help="PostgreSQL database user"),
    db_password: str = typer.Option("postgres", help="PostgreSQL database password"),
    db_host: str = typer.Option("localhost", help="PostgreSQL database host"),
    db_port: int = typer.Option(5432, help="PostgreSQL database port"),
    cache_host: str = typer.Option("localhost", help="DragonFlyDB cache host"),
    cache_port: int = typer.Option(6379, help="DragonFlyDB cache port"),
    jwt_secret: str = typer.Option("your-secret-key", help="Secret key for JWT token generation"),
    jwt_algorithm: str = typer.Option("HS256", help="Algorithm for JWT token generation"),
    jwt_expiration: int = typer.Option(30, help="JWT token expiration time in minutes"),
    delete_type: DeleteType = typer.Option(DeleteType.SOFT, help="Delete type for entities (soft or hard)"),
    enable_streaming: bool = typer.Option(False, help="Enable real-time data streaming"),
    streaming_broker: StreamingBroker = typer.Option(StreamingBroker.KAFKA, help="Streaming broker to use (kafka, rabbitmq, or none)"),
    streaming_broker_host: str = typer.Option("localhost", help="Streaming broker host"),
    streaming_broker_port: int = typer.Option(9092, help="Streaming broker port (default: 9092 for Kafka, 5672 for RabbitMQ)"),
    interactive: bool = typer.Option(False, help="Run in interactive mode to input custom models"),
):
    """
    Generate a FastAPI application with PostgreSQL, DragonFlyDB, and JWT OAuth2 authentication.
    
    Features:
    - Onion architecture and domain-driven design
    - JWT OAuth2 authentication with users, roles, and privileges
    - PostgreSQL for persistent storage and DragonFlyDB for caching
    - Timestamp fields (created_at, updated_at, deleted_at) with soft/hard delete
    - Real-time data streaming with WebSockets and message brokers (Kafka/RabbitMQ)
    """
    typer.echo(f"Generating FastAPI codebase for project: {project_name}")
    
    # Create output directory
    output_path = Path(output_dir).absolute()
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create generator instance
    generator = CodebaseGenerator(
        project_name=project_name,
        output_dir=str(output_path),
        db_config={
            "name": db_name,
            "user": db_user,
            "password": db_password,
            "host": db_host,
            "port": db_port,
        },
        cache_config={
            "host": cache_host,
            "port": cache_port,
        },
        jwt_config={
            "secret_key": jwt_secret,
            "algorithm": jwt_algorithm,
            "expiration_minutes": jwt_expiration,
        },
        platform_config={
            "delete_type": delete_type,
            "enable_streaming": enable_streaming,
            "streaming_broker": streaming_broker,
            "streaming_broker_host": streaming_broker_host,
            "streaming_broker_port": streaming_broker_port,
        },
        interactive=interactive,
    )
    
    # Generate the codebase
    generator.generate()
    
    # If interactive mode is enabled, generate custom models
    if interactive:
        typer.echo("\nNow let's define your custom models:")
        generate_models(str(output_path))
        
        typer.echo("\nGenerating CRUD operations with role-based access control:")
        generate_crud_with_rbac(str(output_path))
    
    typer.echo(f"\nFastAPI codebase generated successfully at: {output_path}")
    typer.echo("To run the application:")
    typer.echo(f"1. cd {output_path}")
    typer.echo("2. pip install -r requirements.txt")
    typer.echo("3. python -m app.infrastructure.persistence.init_db")
    typer.echo("4. uvicorn app.presentation.api.app:app --reload")
    
    if enable_streaming:
        typer.echo("\nStreaming is enabled. Make sure you have the following:")
        if streaming_broker == StreamingBroker.KAFKA:
            typer.echo(f"- Kafka broker running at {streaming_broker_host}:{streaming_broker_port}")
        elif streaming_broker == StreamingBroker.RABBITMQ:
            typer.echo(f"- RabbitMQ broker running at {streaming_broker_host}:{streaming_broker_port}")
        typer.echo("- See docs/streaming_protocol.md for details on the streaming protocol")

def main():
    """Main entry point for the Me Need Code-Base."""
    app()

if __name__ == "__main__":
    main()
