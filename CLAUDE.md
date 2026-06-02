# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Terminal-style dashboard web app for iPad Mini. Displays time, weather, news headlines, stock prices, and a customisable home section. Served by Flask on port 5010.

## Commands

```bash
# Install dependencies (uses uv)
uv sync

# Run the server (must run from app/ due to bare `fetchers` import)
cd app && python server.py
# Accessible at http://localhost:5010
```

No tests or linter are configured.

## Architecture

**Entry point:** `app/server.py` — loads `config.yaml` at startup, handles `GET /`, calls all fetchers, renders `app/templates/dashboard.html`.

**Fetchers** (`app/fetchers/`): each module exposes a single `get(...)` function that wraps `cache.get(key, ttl, fetch_fn)`:
- `weather.py` — hits `wttr.in` (JSON API), TTL 600 s
- `news.py` — parses RSS feeds via `feedparser`, TTL 300 s
- `stocks.py` — queries `yfinance`, TTL 900 s
- `cache.py` — shared TTL in-memory cache; returns stale data on fetch error rather than raising

**Configuration:** `config.yaml` controls location, refresh interval, `home_md_path`, news feeds, and stock symbols. `home.md` is rendered as Markdown and injected into the dashboard as the "Home" section.

**Template:** `app/templates/dashboard.html` — pure Jinja2/CSS, no JS framework. Auto-refreshes every `refresh_seconds`. Staggered CSS animations are driven by `randms()` (a Jinja2 global set in `server.py`).
