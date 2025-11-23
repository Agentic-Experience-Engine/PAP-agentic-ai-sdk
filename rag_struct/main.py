# rag_struct/main.py

from fastapi import FastAPI
from pydantic import BaseModel

from .agents import build_search_agent

app = FastAPI()

# Create a single SearchAgent instance for the whole server
search_agent = build_search_agent()


class SearchRequest(BaseModel):
    user_id: str
    query: str


@app.post("/search")
async def search_endpoint(payload: SearchRequest):
    """
    Main API endpoint for external callers (e.g. B2C app).
    Calls the SearchAgent with user_id + query.
    """

    # Construct the agent prompt
    prompt = (
        f"User id: {payload.user_id}. "
        f"User query: {payload.query}. "
        "Use tools (RAG, user history, filters) if needed. "
        "Return a helpful, concise answer and list any found products."
    )

    result = search_agent.run(prompt)
    return {"answer": result}
