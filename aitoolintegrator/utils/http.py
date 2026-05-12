"""httpx async client wrapper for AiToolIntegrator HTTP requests."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import httpx

from aitoolintegrator.utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_TIMEOUT = 30.0
DEFAULT_HEADERS = {
    "User-Agent": "AiToolIntegrator/0.1.0 (https://github.com/aitoolintegrator/aitoolintegrator)",
    "Accept": "application/json",
}


@asynccontextmanager
async def get_client(
    timeout: float = DEFAULT_TIMEOUT,
    headers: dict[str, str] | None = None,
) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Yield a configured async httpx client.

    Args:
        timeout: Request timeout in seconds.
        headers: Additional headers to merge with defaults.

    Yields:
        A ready-to-use httpx.AsyncClient.
    """
    merged_headers = {**DEFAULT_HEADERS, **(headers or {})}
    async with httpx.AsyncClient(
        timeout=timeout,
        headers=merged_headers,
        follow_redirects=True,
    ) as client:
        yield client


async def get_json(url: str, params: dict[str, Any] | None = None) -> Any:  # noqa: ANN401
    """Perform a GET request and return parsed JSON.

    Args:
        url: Target URL.
        params: Optional query parameters.

    Returns:
        Parsed JSON response.

    Raises:
        httpx.HTTPError: On HTTP errors.
        RuntimeError: On non-JSON response.
    """
    async with get_client() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        try:
            return response.json()
        except Exception as exc:
            raise RuntimeError(f"Non-JSON response from {url}: {exc}") from exc


async def fetch_github_stars(repo: str) -> int:
    """Fetch the GitHub star count for a repository.

    Args:
        repo: Repository in 'owner/name' format or full GitHub URL.

    Returns:
        Star count, or 0 if the request fails.
    """
    # Normalize to owner/name
    if repo.startswith("https://github.com/"):
        repo = repo.removeprefix("https://github.com/").rstrip("/")

    url = f"https://api.github.com/repos/{repo}"
    try:
        data = await get_json(url)
        return int(data.get("stargazers_count", 0))
    except Exception as exc:
        logger.debug("Could not fetch stars for %s: %s", repo, exc)
        return 0
