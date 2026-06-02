import os
import random
import yaml
from datetime import datetime
from flask import Flask, render_template, send_from_directory
from fetchers import weather, news, stocks

app = Flask(__name__)
app.jinja_env.globals['randms'] = lambda: random.uniform(0.12, 0.50)

_cfg_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
with open(_cfg_path) as f:
    cfg = yaml.safe_load(f)

_home_md_path = os.path.join(os.path.dirname(__file__), "..", cfg.get("home_md_path", "./home.md"))


def _read_home():
    try:
        with open(_home_md_path, encoding="utf-8") as f:
            return f.read().splitlines()
    except Exception:
        return None


def _is_quiet(hour, start, end):
    """True if `hour` falls in the quiet window, which may wrap past midnight."""
    if start == end:
        return False
    if start < end:
        return start <= hour < end
    return hour >= start or hour < end


_static_dir = os.path.join(os.path.dirname(__file__), 'static')

@app.route('/apple-touch-icon<path:suffix>.png')
def touch_icon(suffix):
    return send_from_directory(_static_dir, 'apple-touch-icon.png')


@app.route("/")
def index():
    now = datetime.now()

    crt = cfg.get("crt") or {}
    quiet = cfg.get("quiet_hours") or {}
    if quiet.get("enabled", True) and _is_quiet(now.hour, quiet.get("start", 22), quiet.get("end", 6)):
        ss = cfg.get("screensaver") or {}
        return render_template(
            "screensaver.html",
            ss_count=ss.get("count", 40),
            ss_fade_min=ss.get("fade_min_seconds", 6),
            ss_fade_max=ss.get("fade_max_seconds", 16),
            ss_randomness=ss.get("randomness", 0.5),
            crt_enabled=crt.get("enabled", True),
            crt_opacity=crt.get("opacity", 0.25),
            crt_gap=crt.get("gap_px", 2),
        )

    bar_time = now.strftime("%a %d %b %Y ■ %H:%M")

    wx = weather.get(cfg["location"])
    headlines = news.get(cfg["news_feeds"], cfg.get("news_max_items", 10))
    home_lines = _read_home()
    stock_quotes = stocks.get(cfg.get("stocks", []))

    bar_weather = f"{wx['temp_c']}°C  {wx['desc']}" if wx else "[unavailable]"

    typing = cfg.get("typing") or {}
    glitch = cfg.get("glitch") or {}

    return render_template(
        "dashboard.html",
        bar_time=bar_time,
        bar_weather=bar_weather,
        location=cfg["location"],
        refresh_seconds=cfg.get("refresh_seconds", 60),
        wx=wx,
        headlines=headlines,
        home_lines=home_lines,
        stock_quotes=stock_quotes,
        typing_cps=typing.get("cps", 45),
        typing_jitter=typing.get("jitter", 0.7),
        typing_lf=typing.get("lf_pause_ms", 150),
        glitch_idle=glitch.get("idle_seconds", 15),
        glitch_duration=glitch.get("duration_seconds", 5),
        glitch_churn=glitch.get("churn_ms", 120),
        glitch_blank=glitch.get("blank_ratio", 0.4),
        crt_enabled=crt.get("enabled", True),
        crt_opacity=crt.get("opacity", 0.25),
        crt_gap=crt.get("gap_px", 2),
    )


def main():
    app.run(host="0.0.0.0", port=5010, debug=False)


if __name__ == "__main__":
    main()
