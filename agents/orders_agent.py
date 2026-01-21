# agents/orders_agent.py
from __future__ import annotations

from typing import Any, Dict

from agents.base import BaseAgent
from core.planning import OrdersIntent


class OrdersAgent(BaseAgent):
    """
    📦 OrdersAgent (Clerk)

    - Future home for cart/order logic.
    - For now, it's a stub so SearchAgent can route to it.
    """

    def __init__(self) -> None:
        super().__init__(name="orders_agent")

    async def run(
        self,
        intent: OrdersIntent,
        user_context: Dict[str, Any],
    ) -> Any:
        self.logger.debug("OrdersAgent got intent=%s user_context=%s", intent, user_context)
        # TODO: implement calls to Next.js orders/cart internal APIs.
        return []
