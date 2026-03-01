"""Official Python SDK for StripFeed - convert any URL to clean Markdown."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Sequence, TypedDict, Union

__version__ = "1.0.0"
__all__ = [
    "StripFeed",
    "StripFeedError",
    "FetchResult",
    "BatchResultItem",
    "BatchResult",
]

BASE_URL = "https://www.stripfeed.dev/api/v1"


# --- Types ---


class FetchResult(TypedDict, total=False):
    """Result from fetching a single URL."""

    markdown: str
    title: str
    tokens: int
    originalTokens: int
    savingsPercent: float
    cached: bool
    fetchMs: int
    format: str
    model: Optional[str]
    url: str
    html: Optional[str]
    text: Optional[str]


class BatchResultItem(TypedDict, total=False):
    """Single item in a batch result."""

    url: str
    title: str
    markdown: str
    tokens: int
    originalTokens: int
    savingsPercent: float
    cached: bool
    fetchMs: int
    status: int
    error: str


class BatchResult(TypedDict):
    """Result from batch fetching multiple URLs."""

    results: List[BatchResultItem]
    total: int
    success: int
    failed: int
    model: Optional[str]


class BatchItem(TypedDict, total=False):
    """Input item for batch requests."""

    url: str
    selector: str


# --- Error ---


class StripFeedError(Exception):
    """Error returned by the StripFeed API."""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status


# --- Client ---


class StripFeed:
    """StripFeed API client.

    Args:
        api_key: Your StripFeed API key (sf_live_...).
        base_url: Custom base URL (default: https://www.stripfeed.dev/api/v1).
        timeout: Request timeout in seconds (default: 30).

    Example::

        sf = StripFeed("sf_live_your_key")
        result = sf.fetch("https://example.com")
        print(result["markdown"])
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = BASE_URL,
        timeout: int = 30,
    ) -> None:
        if not api_key:
            raise ValueError("StripFeed: api_key is required")
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout

    def fetch(
        self,
        url: str,
        *,
        selector: Optional[str] = None,
        format: Optional[str] = None,
        model: Optional[str] = None,
        cache: Optional[bool] = None,
        ttl: Optional[int] = None,
    ) -> FetchResult:
        """Convert a single URL to clean Markdown.

        Args:
            url: The URL to fetch and convert.
            selector: CSS selector to extract specific elements (Pro plan).
            format: Output format: "markdown", "json", "text", "html".
            model: AI model ID for cost tracking (e.g. "claude-sonnet-4-6").
            cache: Set to False to bypass cache.
            ttl: Custom cache TTL in seconds (default: 3600, max: 86400).

        Returns:
            A FetchResult dict with markdown, tokens, savings, and metadata.

        Raises:
            StripFeedError: If the API returns an error.
        """
        params: Dict[str, str] = {"url": url, "format": format or "json"}
        if selector is not None:
            params["selector"] = selector
        if model is not None:
            params["model"] = model
        if cache is False:
            params["cache"] = "false"
        if ttl is not None:
            params["ttl"] = str(ttl)

        query = urllib.parse.urlencode(params)
        return self._request(f"{self._base_url}/fetch?{query}")

    def fetch_markdown(
        self,
        url: str,
        *,
        selector: Optional[str] = None,
        model: Optional[str] = None,
        cache: Optional[bool] = None,
        ttl: Optional[int] = None,
    ) -> str:
        """Fetch a URL and return only the Markdown string.

        Args:
            url: The URL to fetch and convert.
            selector: CSS selector to extract specific elements (Pro plan).
            model: AI model ID for cost tracking.
            cache: Set to False to bypass cache.
            ttl: Custom cache TTL in seconds.

        Returns:
            Clean Markdown string.
        """
        result = self.fetch(
            url,
            selector=selector,
            format="json",
            model=model,
            cache=cache,
            ttl=ttl,
        )
        return result.get("markdown", "")

    def batch(
        self,
        urls: Sequence[Union[str, BatchItem]],
        *,
        model: Optional[str] = None,
    ) -> BatchResult:
        """Process up to 10 URLs in parallel (Pro plan required).

        Args:
            urls: List of URLs (strings or BatchItem dicts with url + selector).
            model: AI model ID for cost tracking.

        Returns:
            A BatchResult dict with results, total, success, and failed counts.

        Raises:
            StripFeedError: If the API returns an error.
        """
        body: Dict[str, Any] = {
            "urls": [
                u if isinstance(u, str) else {"url": u["url"], "selector": u.get("selector")}
                for u in urls
            ],
        }
        if model is not None:
            body["model"] = model

        return self._request(
            f"{self._base_url}/batch",
            method="POST",
            body=body,
        )

    def _request(
        self,
        url: str,
        *,
        method: str = "GET",
        body: Optional[Dict[str, Any]] = None,
    ) -> Any:
        headers = {"Authorization": f"Bearer {self._api_key}"}
        data = None

        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode()

        req = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            try:
                error_body = json.loads(e.read().decode())
                message = error_body.get("error", f"HTTP {e.code}")
            except Exception:
                message = f"HTTP {e.code}"
            raise StripFeedError(e.code, message) from e
        except urllib.error.URLError as e:
            if "timed out" in str(e.reason):
                raise StripFeedError(0, "Request timed out") from e
            raise
