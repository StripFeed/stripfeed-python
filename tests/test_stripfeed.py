"""Tests for the StripFeed Python SDK."""

from __future__ import annotations

import json
import urllib.error
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from stripfeed import StripFeed, StripFeedError


def _mock_response(data: dict, status: int = 200) -> MagicMock:
    """Create a mock urllib response."""
    body = json.dumps(data).encode()
    resp = MagicMock()
    resp.read.return_value = body
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def _mock_http_error(data: dict, status: int) -> urllib.error.HTTPError:
    """Create a mock HTTPError."""
    body = json.dumps(data).encode()
    return urllib.error.HTTPError(
        url="https://www.stripfeed.dev/api/v1/fetch",
        code=status,
        msg=f"HTTP {status}",
        hdrs={},  # type: ignore[arg-type]
        fp=BytesIO(body),
    )


class TestConstructor:
    def test_accepts_api_key(self) -> None:
        sf = StripFeed("sf_live_test123")
        assert sf._api_key == "sf_live_test123"

    def test_accepts_custom_config(self) -> None:
        sf = StripFeed(
            "sf_live_test123",
            base_url="https://custom.api/v1",
            timeout=5,
        )
        assert sf._base_url == "https://custom.api/v1"
        assert sf._timeout == 5

    def test_raises_on_empty_key(self) -> None:
        with pytest.raises(ValueError, match="api_key is required"):
            StripFeed("")


class TestFetch:
    @patch("stripfeed.urllib.request.urlopen")
    def test_calls_fetch_endpoint(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response(
            {
                "markdown": "# Hello",
                "title": "Hello",
                "tokens": 5,
                "originalTokens": 50,
                "savingsPercent": 90.0,
                "cached": False,
                "fetchMs": 100,
                "format": "json",
                "model": None,
                "url": "https://example.com",
            }
        )

        sf = StripFeed("sf_live_test123")
        result = sf.fetch("https://example.com")

        assert result["markdown"] == "# Hello"
        assert result["tokens"] == 5
        assert result["savingsPercent"] == 90.0

        req = mock_urlopen.call_args[0][0]
        assert "/fetch?" in req.full_url
        assert "url=https" in req.full_url
        assert "format=json" in req.full_url
        assert req.get_header("Authorization") == "Bearer sf_live_test123"

    @patch("stripfeed.urllib.request.urlopen")
    def test_passes_optional_params(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response({"markdown": ""})

        sf = StripFeed("sf_live_test123")
        sf.fetch(
            "https://example.com",
            selector="article",
            model="claude-sonnet-4-6",
            cache=False,
            ttl=7200,
        )

        req = mock_urlopen.call_args[0][0]
        assert "selector=article" in req.full_url
        assert "model=claude-sonnet-4-6" in req.full_url
        assert "cache=false" in req.full_url
        assert "ttl=7200" in req.full_url

    @patch("stripfeed.urllib.request.urlopen")
    def test_raises_on_401(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.side_effect = _mock_http_error(
            {"error": "Invalid API key"}, 401
        )

        sf = StripFeed("sf_live_bad")
        with pytest.raises(StripFeedError) as exc_info:
            sf.fetch("https://example.com")
        assert exc_info.value.status == 401
        assert "Invalid API key" in str(exc_info.value)

    @patch("stripfeed.urllib.request.urlopen")
    def test_raises_on_429(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.side_effect = _mock_http_error(
            {"error": "Rate limit exceeded"}, 429
        )

        sf = StripFeed("sf_live_test123")
        with pytest.raises(StripFeedError) as exc_info:
            sf.fetch("https://example.com")
        assert exc_info.value.status == 429

    @patch("stripfeed.urllib.request.urlopen")
    def test_uses_custom_base_url(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response({"markdown": ""})

        sf = StripFeed("sf_live_test123", base_url="https://custom.api/v1")
        sf.fetch("https://example.com")

        req = mock_urlopen.call_args[0][0]
        assert req.full_url.startswith("https://custom.api/v1/fetch?")


class TestFetchMarkdown:
    @patch("stripfeed.urllib.request.urlopen")
    def test_returns_only_markdown(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response(
            {"markdown": "# Hello World\n\nContent here.", "tokens": 10}
        )

        sf = StripFeed("sf_live_test123")
        md = sf.fetch_markdown("https://example.com")

        assert md == "# Hello World\n\nContent here."
        assert isinstance(md, str)


class TestBatch:
    @patch("stripfeed.urllib.request.urlopen")
    def test_sends_string_urls(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response(
            {"results": [], "total": 2, "success": 2, "failed": 0, "model": None}
        )

        sf = StripFeed("sf_live_test123")
        sf.batch(["https://a.com", "https://b.com"])

        req = mock_urlopen.call_args[0][0]
        assert "/batch" in req.full_url
        assert req.get_method() == "POST"

        body = json.loads(req.data)
        assert body["urls"] == ["https://a.com", "https://b.com"]

    @patch("stripfeed.urllib.request.urlopen")
    def test_sends_mixed_urls(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response(
            {"results": [], "total": 2, "success": 2, "failed": 0, "model": "gpt-4o"}
        )

        sf = StripFeed("sf_live_test123")
        sf.batch(
            [
                "https://a.com",
                {"url": "https://b.com", "selector": "article"},
            ],
            model="gpt-4o",
        )

        body = json.loads(mock_urlopen.call_args[0][0].data)
        assert body["urls"] == [
            "https://a.com",
            {"url": "https://b.com", "selector": "article"},
        ]
        assert body["model"] == "gpt-4o"

    @patch("stripfeed.urllib.request.urlopen")
    def test_raises_on_403(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.side_effect = _mock_http_error(
            {"error": "Batch endpoint requires a Pro plan"}, 403
        )

        sf = StripFeed("sf_live_free")
        with pytest.raises(StripFeedError) as exc_info:
            sf.batch(["https://a.com"])
        assert exc_info.value.status == 403

    @patch("stripfeed.urllib.request.urlopen")
    def test_returns_batch_result(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_response(
            {
                "results": [
                    {"url": "https://a.com", "status": 200, "markdown": "# A", "tokens": 5},
                    {"url": "https://bad.com", "status": 502, "error": "Unreachable"},
                ],
                "total": 2,
                "success": 1,
                "failed": 1,
                "model": None,
            }
        )

        sf = StripFeed("sf_live_test123")
        result = sf.batch(["https://a.com", "https://bad.com"])

        assert result["total"] == 2
        assert result["success"] == 1
        assert result["failed"] == 1
        assert result["results"][0]["status"] == 200
        assert result["results"][1]["status"] == 502


class TestStripFeedError:
    def test_has_correct_properties(self) -> None:
        err = StripFeedError(429, "Rate limit exceeded")
        assert err.status == 429
        assert str(err) == "Rate limit exceeded"
        assert isinstance(err, Exception)
