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
    "User-Agent": "AiToolIntegrator/0.1.0 (https://github.com/domlemay/AiToolIntegrator)",
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


async def fetch_github_stars(repo: str, token: str | None = None) -> int | None:
    """Fetch the current star count for a GitHub repository.

    Args:
        repo: Repository in 'owner/name' format or full GitHub URL.
        token: Optional GitHub personal access token (raises rate limit from
            60 to 5 000 requests/hour).

    Returns:
        Star count, or None if the request fails (e.g. private repo, network error).
    """
    if repo.startswith("https://github.com/"):
        repo = repo.removeprefix("https://github.com/").rstrip("/")

    url = f"https://api.github.com/repos/{repo}"
    headers: dict[str, str] = {"X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        async with get_client(headers=headers) as client:
            response = await client.get(url)
            if response.status_code == 404:
                logger.debug("Repository not found: %s", repo)
                return None
            response.raise_for_status()
            data = response.json()
            return int(data["stargazers_count"])
    except Exception as exc:
        logger.debug("Could not fetch stars for %s: %s", repo, exc)
        return None
