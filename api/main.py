from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from langchain_ollama.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# 1. Create an instance of the FastAPI class (our main application object)
app = FastAPI()

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


# Models for the /search endpoint
class SearchRequest(BaseModel):
    query: str


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


@app.post("/api/v1/search")
async def process_search(search_request: SearchRequest):
    llm = ChatOllama(model="phi3:mini")

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert at refining e-commerce search queries. Take the user's input and rephrase it to be a clear, concise search term.",
            ),
            ("human", "User search input query: {query}"),
        ]
    )

    chain = prompt | llm
    response = chain.invoke({"query": search_request.query})
    ai_query = response.content
    print(f"AI Refined Query: {ai_query}")

    fake_products = [
        ProductResult(id=1, title=f"Result for '{ai_query}' 1", imageUrl=""),
        ProductResult(id=2, title=f"Result for '{ai_query}' 2", imageUrl=""),
    ]
    return SearchResponse(result=fake_products, ai_rewritten_query=ai_query)
