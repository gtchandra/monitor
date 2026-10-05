import threading
import time

_store = {}
_inflight = set()
_lock = threading.Lock()


def _refresh(key, fetch_fn):
    try:
        data = fetch_fn()
        _store[key] = {'data': data, 'ts': time.time()}
    except Exception:
        pass   # keep serving the stale entry
    finally:
        with _lock:
            _inflight.discard(key)


def get(key, ttl, fetch_fn):
    entry = _store.get(key)
    if entry and time.time() - entry['ts'] < ttl:
        return entry['data']
    if entry:
        # stale: answer immediately, refresh in the background (one refresh per key at a time)
        with _lock:
            start = key not in _inflight
            _inflight.add(key)
        if start:
            threading.Thread(target=_refresh, args=(key, fetch_fn), daemon=True).start()
        return entry['data']
    # cold cache: nothing to serve, so block on the first fetch
    try:
        data = fetch_fn()
    except Exception:
        return None
    _store[key] = {'data': data, 'ts': time.time()}
    return data
