import yfinance as yf
from .cache import get as cached


def _fetch(tickers):
    results = []
    for t in tickers:
        label = t.get("label", t["symbol"])
        try:
            ticker = yf.Ticker(t["symbol"])
            fi = ticker.fast_info
            price = fi.last_price
            prev = fi.previous_close
            if price is None:
                hist = ticker.history(period="2d")
                if len(hist) >= 2:
                    price, prev = hist["Close"].iloc[-1], hist["Close"].iloc[-2]
                elif len(hist) == 1:
                    price, prev = hist["Close"].iloc[0], hist["Close"].iloc[0]
                else:
                    raise ValueError("no data")
            change = price - prev
            pct = (change / prev) * 100 if prev else 0
            results.append({
                "label": label,
                "price": round(price, 2),
                "change": round(change, 2),
                "pct": round(pct, 2),
                "currency": fi.currency or "",
            })
        except Exception:
            results.append({"label": label, "error": True})
    return results


def get(tickers):
    key = "stocks:" + ",".join(t["symbol"] for t in tickers)
    return cached(key, ttl=900, fetch_fn=lambda: _fetch(tickers))
