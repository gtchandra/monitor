import subprocess
import threading
from collections import OrderedDict
import requests

# url -> list of braille rows (or None if it failed). Filled only by background threads,
# so a request never waits on a download or a chafa run.
_art = OrderedDict()
_inflight = set()
_lock = threading.Lock()
_MAX_ITEMS = 20
_MAX_BYTES = 3 * 1024 * 1024


def _render(url, cols, rows):
    rows_out = None
    try:
        r = requests.get(url, timeout=5, headers={"User-Agent": "monitor-dashboard/1.0"})
        r.raise_for_status()
        if len(r.content) <= _MAX_BYTES:
            out = subprocess.run(
                ["chafa", "--format=symbols", "--colors=none", "--symbols=braille",
                 f"--size={cols}x{rows}", "-"],
                input=r.content, capture_output=True, timeout=10,
            ).stdout.decode("utf-8", "replace")
            rows_out = [ln.rstrip() for ln in out.splitlines() if ln.strip()] or None
    except Exception:
        pass   # stored as None: don't retry this url on every request
    with _lock:
        _art[(url, cols, rows)] = rows_out
        while len(_art) > _MAX_ITEMS:
            _art.popitem(last=False)
        _inflight.discard((url, cols, rows))


def get(url, cols=60, rows=18):
    """Braille rows for the image at `url`, or None if not rendered (yet)."""
    key = (url, cols, rows)
    with _lock:
        if key in _art:
            return _art[key]
        start = key not in _inflight
        _inflight.add(key)
    if start:
        threading.Thread(target=_render, args=(url, cols, rows), daemon=True).start()
    return None
