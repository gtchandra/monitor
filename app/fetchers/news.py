import feedparser
from .cache import get as cached

def _fetch(feeds, max_items):
    items = []
    for feed in feeds:
        try:
            parsed = feedparser.parse(feed["url"])
            for entry in parsed.entries[:max_items]:
                title = entry.get("title", "").strip()
                if title:
                    items.append({"title": title, "label": feed.get("label", "")})
        except Exception:
            pass
    return items[:max_items]

def get(feeds, max_items=10):
    key = "news:" + ",".join(f["url"] for f in feeds)
    return cached(key, ttl=300, fetch_fn=lambda: _fetch(feeds, max_items))
