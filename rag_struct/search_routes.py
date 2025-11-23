# api/search_routes.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from .agents import build_search_agent

router = APIRouter(prefix="/search", tags=["search"])

class SearchQuery(BaseModel):
    user_id: str
    query: str


def get_search_agent():
    # you may want to make this a singleton in real app
    return build_search_agent()


@router.post("/ask")
async def search_ask(payload: SearchQuery, search_agent = Depends(get_search_agent)):
    """
    Main entry point from B2C app.
    """
    # 1) You can inject user_id into the prompt so tools know what to do
    combined_query = (
        f"User id: {payload.user_id}. "
        f"User query: {payload.query}. "
        "If needed, call tools to fetch user's previous product views/events, "
        "then filter for black jeans and return only those products."
    )

    result = search_agent.run(combined_query)
    return {"answer": result}
