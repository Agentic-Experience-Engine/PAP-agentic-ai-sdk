# core/llm.py
from __future__ import annotations

from functools import lru_cache
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_ollama.chat_models import ChatOllama

import config


@lru_cache()
def get_default_chat_model(*, temperature: float = 0.1) -> BaseChatModel:
    """
    Central factory for the chat model used by all agents.

    - Uses Ollama via langchain-ollama.
    - Reads MODEL_NAME and OLLAMA_BASE_URL from config.py.
    - Cached so we don't re-instantiate the model per request.
    """
    return ChatOllama(
        model=config.MODEL_NAME,
        temperature=temperature,
        base_url=config.OLLAMA_BASE_URL,
    )
