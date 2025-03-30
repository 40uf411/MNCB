"""
Setup script for the FastAPI Codebase Generator.
"""
from setuptools import setup, find_packages

with open("docs/README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fastapi-generator",
    version="0.1.0",
    author="FastAPI Generator Team",
    author_email="author@example.com",
    description="A tool to generate FastAPI applications with PostgreSQL, DragonFlyDB, and JWT OAuth2 authentication",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fastapi-generator",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "sqlalchemy>=1.4.23",
        "pydantic>=1.8.2",
        "passlib>=1.7.4",
        "python-jose>=3.3.0",
        "python-multipart>=0.0.5",
        "asyncpg>=0.24.0",
        "redis>=4.0.2",
        "alembic>=1.7.3",
        "inquirer>=2.7.0",
        "inflect>=5.3.0",
        "typer>=0.4.0",
        "colorama>=0.4.4",
        "aiokafka>=0.7.2",
        "aio-pika>=8.0.0",
        "websockets>=10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.5",
            "pytest-asyncio>=0.15.1",
            "black>=21.8b0",
            "isort>=5.9.3",
            "flake8>=3.9.2",
            "mypy>=0.910",
        ],
    },
    entry_points={
        "console_scripts": [
            "fastapi-generator=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["templates/**/*"],
    },
)
