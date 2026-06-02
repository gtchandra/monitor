# monitor

A terminal-style dashboard web app, designed for an iPad Mini. It displays the
time, weather, news headlines, stock prices, and a customisable "home" section,
all rendered with a retro serial/telex aesthetic (character-by-character typing
reveal and an end-of-cycle "video memory corruption" glitch).

Served by Flask on port **5010**.

## Features

- **Weather** — current conditions via [wttr.in](https://wttr.in) (cached 10 min)
- **News** — RSS headlines via `feedparser` (cached 5 min)
- **Stocks** — quotes via `yfinance` (cached 15 min)
- **Home** — a Markdown file (`home.md`) rendered into a custom panel
- In-memory TTL cache that serves stale data on fetch errors rather than failing
- Pure Jinja2/CSS front end — no JS framework; auto-refreshes on an interval

## Requirements

- Python ≥ 3.12
- [uv](https://github.com/astral-sh/uv) for dependency management

## Setup

```bash
# Install dependencies
uv sync

# Create your personal home panel from the example (home.md is gitignored)
cp home-example.md home.md

# Run the server (must run from app/ due to the bare `fetchers` import)
cd app && python server.py
```

Then open <http://localhost:5010>.

## Configuration

All settings live in `config.yaml`:

| Key | Description |
| --- | --- |
| `location` | City used for the weather lookup |
| `refresh_seconds` | How often the dashboard auto-refreshes |
| `home_md_path` | Path to the Markdown file rendered in the Home panel |
| `news_feeds` | List of `{url, label}` RSS feeds |
| `news_max_items` | Max headlines shown |
| `stocks` | List of `{symbol, label}` tickers |
| `typing` | Serial/telex typing-reveal animation tuning |
| `glitch` | End-of-cycle glitch animation tuning |

## Architecture

- **`app/server.py`** — entry point; loads `config.yaml`, calls the fetchers,
  renders `app/templates/dashboard.html`.
- **`app/fetchers/`** — each module exposes a single `get(...)` function wrapping
  `cache.get(key, ttl, fetch_fn)`:
  - `weather.py` — wttr.in JSON API
  - `news.py` — RSS via `feedparser`
  - `stocks.py` — `yfinance`
  - `cache.py` — shared in-memory TTL cache
- **`app/templates/dashboard.html`** — Jinja2 + CSS; staggered animations driven
  by a `randms()` Jinja2 global.

## License

No license specified.
