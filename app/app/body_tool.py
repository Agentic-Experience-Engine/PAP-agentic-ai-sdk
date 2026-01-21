import httpx
from app.search import PapActionRequest

B2C_INTERNAL_URL = "http://localhost:3000/api/internal/pap/execute"
INTERNAL_API_KEY = "CHANGE_ME"

class BodyTool:
    async def execute(self, payload: PapActionRequest):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                B2C_INTERNAL_URL,
                json=payload.dict(),
                headers={
                    "x-internal-key": INTERNAL_API_KEY,
                },
                timeout=10,
            )
        response.raise_for_status()
        return response.json()
