# agents/users_agent.py
from __future__ import annotations

from typing import Any, Dict, List

from agents.base import BaseAgent
from core.planning import StructuredQuery, UserBehaviorIntent
from tools.analytics_tool import run_analytics_query


class UsersAgent(BaseAgent):
    """
    👤 UsersAgent (Behaviorist)

    - Accepts a UserBehaviorIntent from SearchAgent.
    - Builds a StructuredQuery object based on your UserEvent schema.
    - Calls the analytics tool, which talks to Next.js.
    """

    def __init__(self) -> None:
        super().__init__(name="users_agent")

    async def run(self, **kwargs: Any) -> Any:
        """
        Not used directly in this design; SearchAgent calls the more specific
        methods below. You could implement a generic dispatcher here later.
        """
        raise NotImplementedError("Use build_structured_query + fetch_events instead.")

    async def build_structured_query(
        self,
        intent: UserBehaviorIntent,
        user_context: Dict[str, Any],
    ) -> StructuredQuery:
        """
        Translate UserBehaviorIntent into a DB-agnostic StructuredQuery targeting user_event.

        Example for:
          "Show me all the black jeans I searched for in the last 10 mins"
        → StructuredQuery(
            entity="user_event",
            filters={
              "user_id": 42,
              "type": "search",
              "product_category": "jeans",
              "meta": { "color": "black" },
              "time_window": "10m",
            },
          )
        """

        user_id = user_context.get("user_id") or user_context.get("id")

        filters: Dict[str, Any] = {}

        if user_id is not None:
            filters["user_id"] = user_id

        if intent.action and intent.action != "unknown":
            # Map to UserEvent.type
            filters["type"] = intent.action

        if intent.product_category:
            filters["product_category"] = intent.product_category

        if intent.attributes:
            # Convention: nested attributes live under "meta" (Next.js maps this to JSON filters)
            filters["meta"] = intent.attributes

        if intent.time_window:
            filters["time_window"] = intent.time_window

        structured_query = StructuredQuery(
            entity="user_event",
            filters=filters,
        )

        self.logger.debug("StructuredQuery built for user behavior: %s", structured_query)
        return structured_query

    async def fetch_events(
        self,
        structured_query: StructuredQuery,
        user_context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Executes the StructuredQuery via the analytics tool and returns the events.
        """
        events = await run_analytics_query(
            structured_query=structured_query,
            user_context=user_context,
        )
        self.logger.debug("Fetched %d user events", len(events))
        return events
