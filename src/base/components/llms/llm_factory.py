from src.common.config import Config
from .base import BaseLLMClient

def create_llm_client(config: Config) -> BaseLLMClient:
    """Create a LLM client based on the configuration."""
    model_type = config.model_type.upper() if config.model_type else None
    if model_type == "OPENAI":
        from src.base.components.llms.variants.openai_client import OpenAIClient
        return OpenAIClient(config)
    else:
        raise ValueError(f"Invalid model type: {model_type}")
