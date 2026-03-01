# StripFeed Python SDK

Official Python SDK for [StripFeed](https://www.stripfeed.dev) - convert any URL to clean, token-efficient Markdown for AI agents, RAG pipelines, and LLM workflows.

## Install

```bash
pip install stripfeed
```

## Quick Start

```python
from stripfeed import StripFeed

sf = StripFeed("sf_live_your_api_key")

# Full result with metadata
result = sf.fetch("https://news.ycombinator.com")
print(result["markdown"])
print(f"Tokens: {result['tokens']} (saved {result['savingsPercent']}%)")

# Just the Markdown string
md = sf.fetch_markdown("https://news.ycombinator.com")
```

## With Options

```python
result = sf.fetch(
    "https://example.com",
    selector="article",           # CSS selector (Pro)
    format="json",                # json, text, html (Pro)
    model="claude-sonnet-4-6",    # cost tracking
    cache=False,                  # bypass cache
    ttl=7200,                     # custom cache TTL
)
```

## Batch (Pro plan)

```python
result = sf.batch(
    [
        "https://example.com",
        {"url": "https://docs.anthropic.com", "selector": "article"},
    ],
    model="claude-sonnet-4-6",
)

for item in result["results"]:
    print(f"{item['url']}: {item['tokens']} tokens")
```

## Error Handling

```python
from stripfeed import StripFeed, StripFeedError

try:
    result = sf.fetch("https://example.com")
except StripFeedError as e:
    print(f"API error {e.status}: {e}")
```

## Configuration

```python
sf = StripFeed(
    "sf_live_your_api_key",
    base_url="https://custom.api/v1",  # optional
    timeout=10,                         # optional, default 30s
)
```

## Methods

- `sf.fetch(url, **options)` - Fetch URL, return full result dict (markdown, tokens, metadata)
- `sf.fetch_markdown(url, **options)` - Fetch URL, return only Markdown string
- `sf.batch(urls, model=None)` - Fetch up to 10 URLs in parallel (Pro plan)

## Requirements

- Python 3.9+
- No external dependencies

## Links

- [Documentation](https://www.stripfeed.dev/docs)
- [Dashboard](https://www.stripfeed.dev/dashboard)
- [GitHub](https://github.com/StripFeed/stripfeed-python)
- [TypeScript SDK](https://www.npmjs.com/package/stripfeed)
