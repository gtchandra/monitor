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
- `system.py` — neofetch logo + info side by side (TTL 600 s) and per-core CPU / memory / disk usage read from `/proc` (TTL 10 s); shown as a boot banner with btop-style gauges before the news, followed by a `system.hold_seconds` pause. Not included in `/feed.txt`.
- `cache.py` — shared TTL in-memory cache; a stale entry is returned immediately while a background thread refreshes it, and only a cold cache blocks. On fetch error the stale data is kept.

**Configuration:** `config.yaml` controls location, refresh interval, `home_md_path`, news feeds, and stock symbols. `home.md` is rendered as Markdown and injected into the dashboard as the "Home" section.

**Recurring tasks:** `tasks.json` (gitignored; see `tasks-example.json`) holds chore tasks with `interval_days` + `last_check`. A task is due when `today - last_check >= interval_days`; `server.py` shows the first due task in a "message from system:" overlay, and `POST /task/<id>/done` stamps `last_check` to today. Rotation among people is modelled as separate tasks with staggered `last_check`.

**Template:** `app/templates/dashboard.html` — Jinja2/CSS plus small ES5 scripts (the target is a first-gen iPad Mini on iOS 9, so no `fetch`, no flex `gap`, and keep DOM churn and timers minimal). Cycle: telex-style typing, an idle pause, a glitch, then the typing replays in place; a full `location.reload()` happens only once `refresh_seconds` has elapsed. `screensaver.html` is served during `quiet_hours`; it uses a fixed pool of glyph spans driven by one timer and reloads at the wake hour (`ss_wake_ms`).
