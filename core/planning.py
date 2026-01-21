# core/planning.py
from __future__ import annotations

from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field


class UserBehaviorIntent(BaseModel):
    """
    Semantic interpretation for user-behavior-based queries.

    Example:
      "show me all the black jeans I searched for in the last 10 mins"

    Might produce:
      route='user_behavior'
      action='search'
      product_category='jeans'
      attributes={'color': 'black'}
      time_window='10m'
    """

    route: Literal["user_behavior"] = "user_behavior"

    # High-level action mapped to UserEvent.type
    action: Literal["view", "search", "add_to_cart", "purchase", "unknown"] = "unknown"

    # Semantic category name ("jeans", "noodles", etc.)
    product_category: Optional[str] = None

    # Additional filters ("color": "black", "size": "32")
    attributes: Dict[str, str] = Field(default_factory=dict)

    # Relative window in shorthand: "10m", "1h", "24h", "7d", etc.
    time_window: Optional[str] = None


class OrdersIntent(BaseModel):
    """
    Intent for order/cart related queries.
    """

    route: Literal["orders"] = "orders"
    purpose: Literal["view_history", "reorder_usual", "add_usual_to_cart", "unknown"] = "unknown"
    product_category: Optional[str] = None


class GenericSearchIntent(BaseModel):
    """
    Generic search intent (not user-personalized).
    """

    route: Literal["generic_search"] = "generic_search"
    normalized_query: str


class SearchPlan(BaseModel):
    """
    Top-level routing decision from the SearchAgent's router chain.

    Exactly one of {generic, user_behavior, orders} should be non-null.
    """

    route: Literal["generic_search", "user_behavior", "orders"]
    generic: Optional[GenericSearchIntent] = None
    user_behavior: Optional[UserBehaviorIntent] = None
    orders: Optional[OrdersIntent] = None
    rationale: str


class StructuredQuery(BaseModel):
    """
    Safe, DB-agnostic query representation sent from the Brain (Python) to the Body (Next.js).

    Example payload for user events:
      {
        "entity": "user_event",
        "filters": {
          "user_id": 42,
          "type": "search",
          "product_category": "jeans",
          "meta": { "color": "black" },
          "time_window": "10m"
        }
      }

    Next.js is the *only* component allowed to turn this into Prisma/SQL.
    """

    entity: Literal["user_event", "order", "product"] = "user_event"
    filters: Dict[str, Any] = Field(
        default_factory=dict,
        description="High-level filters that the Next.js backend will translate into Prisma queries.",
    )
