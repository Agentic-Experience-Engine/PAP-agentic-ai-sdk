# model for the user_context need to create on later on for the personlaisation of the request done by the user.
from typing import Optional, Dict
from typing import Any
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api.schemas import SearchRequest, SearchResponse
from core.llm import get_default_chat_model
from agents.search_agent import SearchAgent
from agents.users_agent import UsersAgent
from agents.orders_agent import OrdersAgent
from tools.analytics_tool import AnalyticsServiceError


# 1. Create an instance of the FastAPI class (our main application object)
app = FastAPI()

# Instantiate core agents once per process (not per request).
_llm = get_default_chat_model()
_users_agent = UsersAgent()
_orders_agent = OrdersAgent()
_search_agent = SearchAgent(
    llm=_llm,
    users_agent=_users_agent,
    orders_agent=_orders_agent,
)


origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models for the /user-events endpoint
class EventMessage(BaseModel):
    eventType: str
    categoryId: int
    categoryName: str
    timestamp: datetime


class UserEvent(BaseModel):
    topic: str
    message: EventMessage

class UserContext(BaseModel):
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# Models for the /search endpoint
class SearchRequest(BaseModel):
    query: str
    user_context: Optional[UserContext] = None


class ProductResult(BaseModel):
    id: int
    title: str
    imageUrl: str


class SearchResponse(BaseModel):
    result: list[ProductResult]
    ai_rewritten_query: str


# 2. Define an endpoint for the root URL ("/")
@app.get("/")
async def read_root():
    # 3. Return a simple JSON response
    return {"message": "Welcome to the Agentic AI SDK!"}


@app.post("/api/v1/user-events")
async def process_user_event(event: UserEvent):
    print(f"Received event for topic '{event.topic}'")
    print(f"     - Event Type '{event.message.eventType}'")
    print(f"     - Category '{event.message.categoryName}'")
    return {"status": "success", "event_received": event.message.eventType}


# @app.post("/api/v1/search")
# async def process_search(search_request: SearchRequest):
#     llm = ChatOllama(model="phi3:mini")

#     prompt = ChatPromptTemplate.from_messages(
#         [
#             (
#                 "system",
#                 "You are an expert at refining e-commerce search queries. Take the user's input and rephrase it to be a clear, concise search term.",
#             ),
#             ("human", "User search input query: {query}"),
#         ]
#     )

#     chain = prompt | llm
#     response = chain.invoke({"query": search_request.query})
#     ai_query = response.content
#     print(f"AI Refined Query: {ai_query}")

#     fake_products = [
#         ProductResult(id=1, title=f"Result for '{ai_query}' 1", imageUrl=""),
#         ProductResult(id=2, title=f"Result for '{ai_query}' 2", imageUrl=""),
#     ]
#     return SearchResponse(result=fake_products, ai_rewritten_query=ai_query)

@app.post("/api/v1/search", response_model=SearchResponse)
async def process_search(search_request: SearchRequest) -> SearchResponse:
    """
    Multi-agent search entrypoint.

    - Uses SearchAgent to:
      - Route query to generic search / user behavior / orders.
      - In the 'black jeans last 10 mins' case, it will:
        * create a UserBehaviorIntent
        * UsersAgent produces a StructuredQuery
        * call Next.js /api/internal/analytics/query via tools.analytics_tool
    """
    try:
        result: Dict[str, Any] = await _search_agent.run(
            query=search_request.query,
            user_context=search_request.user_context,
        )
    except AnalyticsServiceError as exc:
        # Translate downstream service errors into a clean HTTP 502
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return SearchResponse(
        items=result.get("items", []),
        source=result.get("source", "unknown"),
        plan=result.get("plan", {}),
        ai_rewritten_query=result.get("ai_rewritten_query"),
    )

