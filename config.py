# config.py
from __future__ import annotations

import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Base URL for the Next.js B2C app (the "Body")
NEXTJS_BASE_URL: str = os.getenv("NEXTJS_BASE_URL", "http://localhost:3000")

# Timeout for HTTP calls to Next.js internal APIs (seconds)
HTTP_TIMEOUT_SECONDS: float = float(os.getenv("HTTP_TIMEOUT_SECONDS", "10"))

# LLM model used by the Brain (Ollama)
MODEL_NAME: str = os.getenv("MODEL_NAME", "llama3")

# Ollama base URL (docker-compose sets this)
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
