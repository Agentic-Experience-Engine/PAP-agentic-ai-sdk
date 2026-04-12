from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel, Field


class IntentType(str, Enum):
    PRODUCT_SEARCH = "product_search"
    FETCH_USER_HISTORY = "fetch_user_history"
    MODIFY_CART = "modify_cart"
    CHECKOUT_ACTION = "checkout_action"
    DIRECT_CHAT_REPLY = "direct_chat_reply"


class ContextDependencies(BaseModel):
    requires_user_context: bool = Field(default=False)


class IntentDSL(BaseModel):
    intent_type: IntentType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    context_dependencies: ContextDependencies = Field(default_factory=ContextDependencies)
    response_format: str
    ai_reasoning: str
