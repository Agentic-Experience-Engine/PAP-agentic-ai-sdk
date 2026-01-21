from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from __api.endpoints import router

app = FastAPI(title="Product Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1", tags=["Search"])


