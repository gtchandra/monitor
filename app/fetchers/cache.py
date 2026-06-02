import time

_store = {}

def get(key, ttl, fetch_fn):
    entry = _store.get(key)
    if entry and time.time() - entry['ts'] < ttl:
        return entry['data']
    try:
        data = fetch_fn()
    except Exception:
        return entry['data'] if entry else None
    _store[key] = {'data': data, 'ts': time.time()}
    return data
