# CLAUDE.md

## Overview

Official Python SDK for StripFeed. Thin wrapper over the StripFeed API with full type hints.

## Stack

- Python 3.9+
- pytest for testing
- No runtime dependencies (uses urllib from stdlib)

## Commands

```bash
pip install -e ".[dev]"   # Install in dev mode with test deps
pytest                     # Run tests
python -m build            # Build sdist + wheel
```

## Architecture

Single file (`stripfeed/__init__.py`). Exports:
- `StripFeed` class with `fetch()`, `fetch_markdown()`, `batch()`, `usage()`
- `StripFeedError` for API errors
- Types via TypedDict: `FetchResult`, `BatchResultItem`, `BatchResult`

Uses `urllib.request` from stdlib. No external dependencies.

## CI/CD

GitHub Actions workflow (`.github/workflows/release.yml`):
- Triggers on push to main
- Runs tests, builds, checks if version tag exists
- If new version: publishes to PyPI, creates git tag + GitHub Release
- Requires `PYPI_API_TOKEN` secret

To release: bump version in `stripfeed/__init__.py`, push to main.

## Git Rules

- All commits must use Claude as author:
  ```bash
  GIT_COMMITTER_NAME="Claude" GIT_COMMITTER_EMAIL="noreply@anthropic.com" git commit --author="Claude <noreply@anthropic.com>" -m "message"
  ```
- Never push without approval
- PyPI package: `stripfeed`
