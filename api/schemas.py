# api/schemas.py
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """
    Request body for /api/v1/search.

    user_context is optional, but should include at least a user_id when available.
    """

    query: str
    user_context: Dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """
    Generic response for /api/v1/search.

    - items: list of result objects (events, products, orders, etc.).
    - source: where the results came from ("user_events", "orders", "generic_search").
    - plan: the SearchPlan as JSON, for debugging/telemetry.
    - ai_rewritten_query: optional normalized query string.
    """

    items: List[Dict[str, Any]]
    source: str
    plan: Dict[str, Any]
    ai_rewritten_query: Optional[str] = None
