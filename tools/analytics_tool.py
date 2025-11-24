# tools/analytics_tool.py
from __future__ import annotations

import logging
from typing import Any, Dict, List

import httpx

from core.planning import StructuredQuery
from tools.http_client import get_http_client

logger = logging.getLogger(__name__)


class AnalyticsServiceError(RuntimeError):
    """Raised when the analytics (Next.js) service is unavailable or returns an error."""


async def run_analytics_query(
    structured_query: StructuredQuery,
    user_context: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Tool: call the Next.js internal analytics endpoint with a Structured Query Object.

    This is the TEXT-TO-API boundary:
      - Python never builds SQL.
      - It only sends structured JSON describing the query.
    """

    payload = {
        "query": structured_query.dict(),
        "user_context": user_context,
    }

    try:
        async with get_http_client() as client:
            resp = await client.post("/api/internal/analytics/query", json=payload)
            resp.raise_for_status()
    except httpx.RequestError as exc:
        logger.exception("Error calling analytics service: %s", exc)
        raise AnalyticsServiceError("Analytics service unavailable") from exc
    except httpx.HTTPStatusError as exc:
        logger.exception(
            "Analytics service returned HTTP %s: %s", exc.response.status_code, exc
        )
        raise AnalyticsServiceError(
            f"Analytics service error (status {exc.response.status_code})"
        ) from exc

    data = resp.json()
    # Convention: for user_event queries, Next.js returns { "events": [...] }
    if isinstance(data, dict) and "events" in data:
        return data["events"]

    # Fallback: if body is just a list, or some other structure
    if isinstance(data, list):
        return data

    logger.warning("Unexpected analytics response shape: %s", data)
    return []
