import feedparser
from .cache import get as cached

def _image(entry):
    """Best image URL for an entry (None if the feed has none). BBC: ask for the 976px rendition."""
    for key in ("media_thumbnail", "media_content"):
        media = entry.get(key) or []
        if media and media[0].get("url"):
            return media[0]["url"].replace("/standard/240/", "/standard/976/")
    return None


def _fetch(feeds, max_items):
    items = []
    for feed in feeds:
        try:
            parsed = feedparser.parse(feed["url"])
            for entry in parsed.entries[:max_items]:
                title = entry.get("title", "").strip()
                if title:
                    items.append({"title": title, "label": feed.get("label", ""), "image": _image(entry)})
        except Exception:
            pass
    return items[:max_items]

def get(feeds, max_items=10):
    key = "news:" + ",".join(f["url"] for f in feeds)
    return cached(key, ttl=300, fetch_fn=lambda: _fetch(feeds, max_items))
