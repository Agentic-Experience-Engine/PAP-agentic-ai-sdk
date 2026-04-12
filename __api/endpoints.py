from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

router = APIRouter()


class UserContext(BaseModel):
    user_id: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    user_context: Optional[UserContext] = None


class SearchResponse(BaseModel):
    query: str
    userId: Optional[str]
    action: str
    metadata: Dict[str, Any]


@router.post("/search", response_model=SearchResponse)
async def search_products(payload: SearchRequest):
    """
    Receives search requests from B2C app.
    """

    # return {
    #     "query": payload.query,
    #     "userId": payload.user_context.user_id if payload.user_context else None,
    #     "action": "list_products",
    #     "metadata": {
    #         "source": "pap-agentic",
    #     },
    # }

    return {
        "query": payload.query,
        "userId": payload.user_context.user_id if payload.user_context else None,
        "action": "search",
        "metadata": {
            "source": "b2c-web",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    }
