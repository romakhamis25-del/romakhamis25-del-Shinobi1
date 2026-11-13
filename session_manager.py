"""
SHINOBI :: Session Manager
HTTP session with rate-limiting, UA rotation, exponential backoff.
"""

import asyncio
import logging
import random
from typing import List, Optional

import httpx


DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Firefox/123.0 Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/17.3 Safari/605.1.15",
]

RETRYABLE_STATUS = {429, 503, 502, 504}


class SessionManager:
    def __init__(
        self,
        user_agents: Optional[List[str]] = None,
        rate_limit_delay: float = 1.5,
        timeout: float = 15.0,
        max_retries: int = 3,
        base_backoff: float = 2.0,
        verify_ssl: bool = False,
    ):
        self.user_agents = user_agents or DEFAULT_USER_AGENTS
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        self.logger = logging.getLogger("shinobi.session")

        limits = httpx.Limits(max_connections=20, max_keepalive_connections=10)
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout, connect=10.0),
            limits=limits,
            verify=verify_ssl,
            follow_redirects=True,
            headers={"Accept": "text/html,application/json;q=0.9,*/*;q=0.8"},
        )
        self._last_request_time = 0.0

    def _rotate_user_agent(self) -> str:
        return random.choice(self.user_agents)

    async def _apply_rate_limit(self) -> None:
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()

    @staticmethod
    def _synthetic_response(url: str, error: str) -> httpx.Response:
        req = httpx.Request("GET", url)
        return httpx.Response(
            status_code=0,
            request=req,
            headers={"x-shinobi-error": error},
            content=b"",
        )

    async def fetch(self, url: str, method: str = "GET", **kwargs) -> httpx.Response:
        await self._apply_rate_limit()

        last_error: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                headers = kwargs.pop("headers", {})
                headers.setdefault("User-Agent", self._rotate_user_agent())
                response = await self._client.request(
                    method, url, headers=headers, **kwargs
                )
                if response.status_code in RETRYABLE_STATUS and attempt < self.max_retries:
                    backoff = self.base_backoff ** attempt + random.uniform(0, 1)
                    retry_after = response.headers.get("Retry-After")
                    if retry_after and retry_after.isdigit():
                        backoff = max(backoff, float(retry_after))
                    self.logger.warning(
                        f"[{response.status_code}] {url} — retry "
                        f"{attempt}/{self.max_retries} in {backoff:.1f}s"
                    )
                    await asyncio.sleep(backoff)
                    continue
                return response

            except (httpx.ConnectError, httpx.ReadTimeout,
                    httpx.RemoteProtocolError, httpx.ConnectTimeout) as exc:
                last_error = exc
                backoff = self.base_backoff ** attempt
                self.logger.warning(
                    f"Network error ({type(exc).__name__}) on {url} — "
                    f"retry {attempt}/{self.max_retries} in {backoff:.1f}s"
                )
                await asyncio.sleep(backoff)
            except httpx.HTTPError as exc:
                self.logger.error(f"HTTP error for {url}: {exc}")
                return self._synthetic_response(url, str(exc))

        self.logger.error(f"All retries exhausted for {url}: {last_error}")
        return self._synthetic_response(url, f"retries_exhausted: {last_error}")

    async def close(self) -> None:
        try:
            await self._client.aclose()
        except Exception:  # noqa: BLE001
            pass
