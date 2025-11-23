# rag_struct/demo_search.py
import os

from .tools import get_rag
from .agents import build_search_agent


def seed_rag():
    """
    Seed the vector store with a few sample products / texts.
    In real life you'll pull this from your product service.
    """
    rag = get_rag()

    texts = [
        "SuperSoft Black Jeans: slim fit, stretchable denim, ideal for daily wear, price 2499 INR.",
        "UltraStretch Black Jeans: skinny fit, high-rise, very soft, price 2799 INR.",
        "Classic Blue Jeans: straight fit, non-stretch, price 1999 INR.",
        "Return policy: You can return products within 30 days of delivery if unused and with tags.",
    ]
    metadatas = [
        {"type": "product", "product_id": "JEANS-BLACK-001", "color": "black"},
        {"type": "product", "product_id": "JEANS-BLACK-002", "color": "black"},
        {"type": "product", "product_id": "JEANS-BLUE-001", "color": "blue"},
        {"type": "policy", "slug": "returns"},
    ]

    chunks = rag.ingest(texts=texts, metadatas=metadatas)
    print(f"Seeded RAG with {chunks} chunks")


def run_search():
    """
    Build the SearchAgent and ask your target query.
    """
    search_agent = build_search_agent()

    user_id = "user-123"
    user_query = "Black Jeans that I searched last time"

    # You’re telling the agent explicitly what to do with user_id
    prompt = (
        f"User id: {user_id}. "
        f"User query: {user_query}. "
        "If needed, call tools to fetch user's previously viewed products, "
        "then filter for black jeans and return only those products. "
        "Respond with a concise explanation and list the product names you recommend."
    )

    result = search_agent.run(prompt)
    print("\n=== AGENT RESPONSE ===")
    print(result)


if __name__ == "__main__":
    # Make sure your OPENAI_API_KEY is set in the environment before running
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("Please set OPENAI_API_KEY in your environment")

    seed_rag()
    run_search()
