from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal

class SearchRequest(BaseModel):
    query: str
    user_id: Optional[str] = None

class PapActionRequest(BaseModel):
    query: str
    userId: Optional[str]
    action: Literal["list_products"]
    metadata: Dict[str, Optional[Any]]
