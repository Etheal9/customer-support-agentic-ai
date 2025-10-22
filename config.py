"""Configuration settings for the multi-agent customer care system."""

import os
from dotenv import load_dotenv

load_dotenv()

# API Keys - Set these as environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


# Model configurations
OPENAI_MODEL = "gpt-4o-mini"
GEMINI_MODEL = "models/gemini-2.5-flash"
CLAUDE_MODEL = "claude-3-haiku-20240307"

# System settings
REQUEST_TIMEOUT = 30  # seconds
MAX_CONVERSATION_HISTORY = 20
SESSION_TIMEOUT = 3600  # 1 hour

# Agent configurations
AGENT_CONFIGS = {
    "orchestrator": {
        "model": GEMINI_MODEL,
        "temperature": 0.3,
        "max_tokens": 1000
    },
    "order": {
        "model": GEMINI_MODEL,
        "temperature": 0.1,
        "max_tokens": 500
    },
    "tech_support": {
        "model": GEMINI_MODEL,
        "temperature": 0.2,
        "max_tokens": 800
    },
    "product": {
        "model": GEMINI_MODEL,
        "temperature": 0.2,
        "max_tokens": 600
    },
    "solutions": {
        "model": GEMINI_MODEL,
        "temperature": 0.3,
        "max_tokens": 700
    }
}

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"