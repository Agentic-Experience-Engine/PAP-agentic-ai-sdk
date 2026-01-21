# agentic_ai_sdk/tools.py
from typing import List, Dict, Any
from langchain.tools import tool

from .core import RAG


# Singleton-ish RAG instance (configure properly in your app)
_rag: RAG | None = None


def get_rag() -> RAG:
    global _rag
    if _rag is None:
        import os
        _rag = RAG(
            openai_api_key=os.environ["OPENAI_API_KEY"],
            openai_base_url=os.getenv("OPENAI_BASE_URL"),
            persist_directory="./.rag_db",
            collection_name="agentic_rag",
        )
    return _rag


# ---------- RAG tool (SearchAgent will use this) ----------

@tool("product_rag_search")
def product_rag_search(query: str) -> str:
    """
    Semantic search over product descriptions, categories, and other text.
    Use this when the user describes products in natural language
    (e.g. 'black jeans I saw last time', 'stretchable slim denim').
    Returns a textual summary of relevant items.
    """
    rag = get_rag()
    result = rag.ask(query)
    return result["answer"]


# ---------- UserAgent-related tools (stubs for now) ----------

@tool("get_user_previous_product_views")
def get_user_previous_product_views(user_id: str) -> List[Dict[str, Any]]:
    """
    Return a list of products that this user has previously viewed / searched.
    Each item should at least contain product_id and any useful metadata.
    CURRENTLY STUB: replace with real DB/API call.
    """
    # TODO: plug into your Warehouse Manager / user events DB
    # This is just a placeholder shape.
    return [
        {"product_id": "JEANS-BLACK-001", "name": "SuperSoft Black Jeans"},
        {"product_id": "JEANS-BLACK-002", "name": "UltraStretch Black Jeans"},
    ]


# ---------- OrdersAgent-related tools (stubs) ----------

@tool("get_user_orders")
def get_user_orders(user_id: str) -> List[Dict[str, Any]]:
    """
    Return a list of orders for this user.
    CURRENTLY STUB: replace with real orders DB/API call.
    """
    return []


# ---------- Product search tool (structured, non-RAG) ----------

@tool("search_products_by_filters")
def search_products_by_filters(
    color: str,
    category: str,
) -> List[Dict[str, Any]]:
    """
    Search products via structured filters (color, category) from your product service.
    Use when filters are clear like color='black' and category='jeans'.
    CURRENTLY STUB: replace with real product search API.
    """
    # This is where you'd call Warehouse Manager's search endpoint.
    return [
        {
            "product_id": "JEANS-BLACK-001",
            "name": "SuperSoft Black Jeans",
            "color": "black",
            "category": "jeans",
        },
        {
            "product_id": "JEANS-BLACK-002",
            "name": "UltraStretch Black Jeans",
            "color": "black",
            "category": "jeans",
        },
    ]