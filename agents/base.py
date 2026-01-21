# agents/base.py
from __future__ import annotations

from abc import ABC, abstractmethod
import logging
from typing import Any

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Shared base class for all agents (SearchAgent, UsersAgent, OrdersAgent, etc.).
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.logger = logger.getChild(name)

    @abstractmethod
    async def run(self, **kwargs: Any) -> Any:  # pragma: no cover - interface only
        raise NotImplementedError
