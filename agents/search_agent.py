# agents/search_agent.py
from __future__ import annotations

from typing import Any, Dict

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from agents.base import BaseAgent
from agents.users_agent import UsersAgent
from agents.orders_agent import OrdersAgent
from core.planning import (
    GenericSearchIntent,
    OrdersIntent,
    SearchPlan,
    UserBehaviorIntent,
)


class SearchAgent(BaseAgent):
    """
    🕵️‍♂️ SearchAgent (Lead / MCP)

    - Receives raw query + user_context from FastAPI.
    - Uses an LLM router chain to produce a SearchPlan (route + intent).
    - Delegates to UsersAgent or OrdersAgent as needed.
    - Never touches the DB: all data comes via tools (Next.js APIs).
    """

    def __init__(
        self,
        *,
        llm: BaseChatModel,
        users_agent: UsersAgent,
        orders_agent: OrdersAgent,
    ) -> None:
        super().__init__(name="search_agent")
        self.llm = llm
        self.users_agent = users_agent
        self.orders_agent = orders_agent

        self._router_parser = PydanticOutputParser(pydantic_object=SearchPlan)

        self._router_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "You are the Search Router for an e-commerce AI brain.\n"
                        "Your job is to interpret the user's natural language query and decide which "
                        "specialist agent should handle it: generic product search, user behavior "
                        "(event logs), or orders (purchases/usual items).\n\n"
                        "You MUST return JSON that matches this Pydantic schema:\n"
                        f"{self._router_parser.get_format_instructions()}\n\n"
                        "Routing guidance:\n"
                        "- If the query refers to 'I', 'my', 'last X minutes/hours/days', or behavior "
                        "  such as 'I viewed', 'I searched', 'things I looked at', choose route='user_behavior'.\n"
                        "- If the query is about order history, cart, or usual orders, choose route='orders'.\n"
                        "- Otherwise, choose route='generic_search'.\n\n"
                        "When route='user_behavior':\n"
                        "- action should be one of 'view', 'search', 'add_to_cart', 'purchase', or 'unknown'.\n"
                        "- product_category should be a concise category like 'jeans', 'noodles', etc.\n"
                        "- attributes can include filters like {'color': 'black', 'size': '32'}.\n"
                        "- time_window should be shorthand like '10m', '1h', '24h', '7d'.\n\n"
                        "Example:\n"
                        "Query: 'show me all the black jeans I searched for in the last 10 mins'\n"
                        "SearchPlan should have:\n"
                        "  route='user_behavior'\n"
                        "  user_behavior.action='search'\n"
                        "  user_behavior.product_category='jeans'\n"
                        "  user_behavior.attributes={'color': 'black'}\n"
                        "  user_behavior.time_window='10m'\n"
                    ),
                ),
                (
                    "human",
                    (
                        "User query: {query}\n"
                        "User context (JSON): {user_context}\n\n"
                        "Return ONLY the JSON for SearchPlan, no extra commentary."
                    ),
                ),
            ]
        )

        # Router chain: prompt -> LLM -> Pydantic parser
        self._router_chain = self._router_prompt | self.llm | self._router_parser

    async def run(self, query: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Entry point used by FastAPI.

        Returns a dict like:
        {
          "source": "user_events" | "orders" | "generic_search",
          "plan": <SearchPlan as dict>,
          "items": [...],
          "ai_rewritten_query": <optional normalized query>
        }
        """
        plan = await self._route(query=query, user_context=user_context)
        plan_dict = plan.dict()
        self.logger.debug("Search plan: %s", plan_dict)

        if plan.route == "user_behavior" and plan.user_behavior is not None:
            events = await self._handle_user_behavior(plan.user_behavior, user_context)
            return {
                "source": "user_events",
                "plan": plan_dict,
                "items": events,
                "ai_rewritten_query": query,  # keep original for now
            }

        if plan.route == "orders" and plan.orders is not None:
            orders_result = await self._handle_orders(plan.orders, user_context)
            return {
                "source": "orders",
                "plan": plan_dict,
                "items": orders_result,
                "ai_rewritten_query": query,
            }

        if plan.route == "generic_search" and plan.generic is not None:
            generic_result = await self._handle_generic(plan.generic, user_context)
            return {
                "source": "generic_search",
                "plan": plan_dict,
                "items": generic_result,
                "ai_rewritten_query": plan.generic.normalized_query,
            }

        # Fallback: shouldn't happen if LLM obeys the schema
        self.logger.warning("Unexpected SearchPlan shape; defaulting to generic_search.")
        fallback_generic = GenericSearchIntent(normalized_query=query)
        generic_result = await self._handle_generic(fallback_generic, user_context)
        return {
            "source": "generic_search",
            "plan": plan_dict,
            "items": generic_result,
            "ai_rewritten_query": fallback_generic.normalized_query,
        }

    async def _route(self, query: str, user_context: Dict[str, Any]) -> SearchPlan:
        return await self._router_chain.ainvoke(
            {
                "query": query,
                "user_context": user_context,
            }
        )

    async def _handle_user_behavior(
        self,
        intent: UserBehaviorIntent,
        user_context: Dict[str, Any],
    ) -> Any:
        structured_query = await self.users_agent.build_structured_query(
            intent=intent,
            user_context=user_context,
        )
        events = await self.users_agent.fetch_events(
            structured_query=structured_query,
            user_context=user_context,
        )
        return events

    async def _handle_orders(
        self,
        intent: OrdersIntent,
        user_context: Dict[str, Any],
    ) -> Any:
        return await self.orders_agent.run(intent=intent, user_context=user_context)

    async def _handle_generic(
        self,
        intent: GenericSearchIntent,
        user_context: Dict[str, Any],
    ) -> Any:
        """
        Generic product search path.

        For now, this is a stub that returns an empty list.
        Later, you'll add a ProductSearchTool that calls Next.js
        (e.g. /api/internal/products/search) and return real products.
        """
        self.logger.debug("Generic search for query=%s", intent.normalized_query)
        return []
