"""
Configuration file for GPT-4 fine-tuning project
Modify these settings to customize your fine-tuning process
"""

# OpenAI Configuration
OPENAI_MODEL = "gpt-4.1-2025-04-14"  # Base model to fine-tune (Most reliable for fine-tuning)
OPENAI_MAX_TOKENS = 1000  # Maximum tokens for responses
OPENAI_TEMPERATURE = 0.5  # Response creativity (0.0 = deterministic, 1.0 = creative)

# Document Processing Configuration
CHUNK_SIZE = 1000  # Size of each training chunk in tokens
CHUNK_OVERLAP = 200  # Overlap between chunks in tokens
DOCS_DIRECTORY = "docs"  # Directory containing your documents

# Fine-tuning Configuration
TRAINING_DATA_FILE = "fine_tuning_data.jsonl"  # Output file for training data
SYSTEM_PROMPT = "You are a helpful AI assistant trained on specific documents."

# File Extensions to Process
SUPPORTED_EXTENSIONS = [".txt", ".md", ".markdown"]

# Monitoring Configuration
MONITORING_INTERVAL = 60  # Seconds between status checks during fine-tuning

# Chat Configuration
CHAT_HISTORY_FILE = "chat_history.json"  # File to save chat history
BATCH_DELAY = 0.1  # Delay between batch requests to avoid rate limiting
