# tools/http_client.py
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

import httpx

import config


@asynccontextmanager
async def get_http_client() -> AsyncIterator[httpx.AsyncClient]:
    """
    Shared async HTTP client for talking to the Next.js B2C app.

    Uses:
      - base_url from config.NEXTJS_BASE_URL
      - timeout from config.HTTP_TIMEOUT_SECONDS
    """
    async with httpx.AsyncClient(
        base_url=config.NEXTJS_BASE_URL,
        timeout=config.HTTP_TIMEOUT_SECONDS,
    ) as client:
        yield client
