# StripFeed Python SDK

[![PyPI version](https://img.shields.io/pypi/v/stripfeed)](https://pypi.org/project/stripfeed/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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

## Output Formats

By default, `sf.fetch()` returns Markdown. Use the `format` parameter to get structured JSON, plain text, or HTML instead:

### JSON format

```python
# Get structured JSON with all metadata fields
result = sf.fetch("https://news.ycombinator.com", format="json")

print(result["markdown"])        # Clean Markdown content
print(result["html"])            # Clean HTML content
print(result["text"])            # Plain text (no formatting)
print(result["title"])           # Page title
print(result["tokens"])          # Token count of clean output
print(result["originalTokens"])  # Token count of original HTML
print(result["savingsPercent"])  # Percentage of tokens saved
print(result["cached"])          # True if served from cache
print(result["fetchMs"])         # Processing time in ms
print(result["truncated"])       # True if max_tokens caused truncation
```

### Plain text format

```python
# Get plain text with all Markdown formatting stripped
result = sf.fetch("https://news.ycombinator.com", format="text")
print(result["text"])  # No headings, bold, links, etc.
```

### HTML format

```python
# Get clean HTML (after Readability extraction)
result = sf.fetch("https://news.ycombinator.com", format="html")
print(result["html"])  # Clean <article> HTML
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
    max_tokens=5000,              # truncate to token budget
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

## Check Usage

```python
usage = sf.usage()
print(f"Plan: {usage['plan']}")
print(f"Used: {usage['usage']} / {usage['limit']}")
print(f"Remaining: {usage['remaining']}")
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
- `sf.usage()` - Check current monthly API usage and plan limits

## Requirements

- Python 3.9+
- No external dependencies

## Links

- [Documentation](https://www.stripfeed.dev/docs)
- [Dashboard](https://www.stripfeed.dev/dashboard)
- [TypeScript SDK](https://www.npmjs.com/package/stripfeed)
- [MCP Server](https://www.npmjs.com/package/@stripfeed/mcp-server)
- [GitHub](https://github.com/StripFeed/stripfeed-python)
