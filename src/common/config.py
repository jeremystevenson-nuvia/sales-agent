"""
Configuration management for the application.
"""

import json
import os
from typing import Optional, Any

from dotenv import load_dotenv
load_dotenv()

from pydantic import Field, model_validator, BaseModel


class Config(BaseModel):
    """Application settings loaded from environment variables.

    When a value is not provided during initialization, the corresponding
    environment variable (matching the field name in upper case) will be used
    as a default. Explicit arguments always take precedence over environment
    variables.
    """
    # Bot Configuration
    ai_prefix: Optional[str] = Field(default="assistant", description="Prefix for AI messages in the prompt")
    human_prefix: Optional[str] = Field(default="user", description="Prefix for human messages in the prompt")
    memory_key: Optional[str] = Field(default="history", description="Key to use for conversation history")
    
    # Chat Configuration
    model_type: str = Field(default="OPENAI", description="The type of model to use (OPENAI)")
    
    ## OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API Key")
    base_model_name: Optional[str] = Field(default=None, description="Base model name to use")

    ## LlamaCpp Configuration
    model_path: Optional[str] = Field(default=None, description="Path to LlamaCpp model")

    ## Vertex AI Configuration
    credentials: Optional[str] = Field(default=None, description="Path to Vertex AI credentials file")

    # Memory Configuration
    bot_memory_type: Optional[str] = Field(default="inmemory", description="Type of memory to use (inmemory)")
    memory_window_size: int = Field(default=5, description="Number of messages to include in the context window")

    # Server Configuration
    port: int = Field(default=8080, description="Server port")
    log_level: str = Field(default="INFO", description="Logging level")

    # Database Configuration
    database_url: Optional[str] = Field(default="sqlite:///./chatbot.db", description="Database URL for user information storage")
    database_echo: Optional[bool] = Field(default=False, description="Enable SQLAlchemy query logging")
    database_pool_size: Optional[int] = Field(default=5, description="Database connection pool size")
    database_max_overflow: Optional[int] = Field(default=10, description="Database connection pool max overflow")

    @model_validator(mode="before")
    @classmethod
    def validate_api_key(cls, values: Any):
        """Load missing values from environment variables."""
        for field_name in cls.model_fields:
            if values.get(field_name) is None:
                field_value = os.getenv(field_name.upper())
                if field_value is not None:
                    values[field_name] = field_value
        return values

    @classmethod
    def from_json(cls, json_path: str) -> "Config":
        """Load configuration from a JSON file."""
        with open(json_path, "r") as f:
            return cls(**json.load(f))
