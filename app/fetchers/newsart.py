import re
import subprocess
import threading
from collections import OrderedDict
import requests

# Render styles (config `news_image.style`):
#   braille        1-bit braille, one amber tone — the "teleprinter" look
#   braille_tones  braille dots coloured in 9 amber tones
#   blocks         half blocks (▀) with fg + bg tones: 2 pixels per cell, most recognizable
_CHAFA_ARGS = {
    "braille":       ["--colors=none", "--symbols=braille"],
    "braille_tones": ["--colors=full", "--fg-only", "--symbols=braille"],
    "blocks":        ["--colors=full", "--symbols=half"],
}

_NON_SGR = re.compile(r"\x1b\[[0-9;?]*[A-Za-ln-z]")   # cursor show/hide etc.
_SGR = re.compile(r"\x1b\[([0-9;]*)m")

# (url, cols, rows, style) -> rows of [(text, css_class), ...] (or None if it failed).
# Filled only by background threads, so a request never waits on a download or a chafa run.
_art = OrderedDict()
_inflight = set()
_lock = threading.Lock()
_MAX_ITEMS = 20
_MAX_BYTES = 3 * 1024 * 1024


def _tone(rgb):
    """Luminance → amber tone 0 (black) .. 8 (brightest)."""
    r, g, b = rgb
    return min(8, int((0.2126 * r + 0.7152 * g + 0.0722 * b) / 256 * 9))


def _segments(line, with_bg):
    """One line of chafa truecolor output → [(text, "tN uM"), ...] with equal-class runs merged."""
    segs, fg, bg, pos = [], 8, 0, 0

    def emit(text):
        if not text:
            return
        cls = "t%d" % fg + (" u%d" % bg if with_bg else "")
        if segs and segs[-1][1] == cls:
            segs[-1] = (segs[-1][0] + text, cls)
        else:
            segs.append((text, cls))

    for m in _SGR.finditer(line):
        emit(line[pos:m.start()])
        p = [int(x) for x in m.group(1).split(";") if x] or [0]
        i = 0
        while i < len(p):
            if p[i] == 0:
                fg, bg = 8, 0
            elif p[i] in (38, 48) and i + 4 < len(p) and p[i + 1] == 2:
                tone = _tone(p[i + 2:i + 5])
                if p[i] == 38:
                    fg = tone
                else:
                    bg = tone
                i += 4
            elif p[i] == 39:
                fg = 8
            elif p[i] == 49:
                bg = 0
            i += 1
        pos = m.end()
    emit(line[pos:])
    return segs


def _render(url, cols, rows, style):
    key = (url, cols, rows, style)
    rows_out = None
    try:
        r = requests.get(url, timeout=5, headers={"User-Agent": "monitor-dashboard/1.0"})
        r.raise_for_status()
        if len(r.content) <= _MAX_BYTES:
            out = subprocess.run(
                ["chafa", "--format=symbols", f"--size={cols}x{rows}",
                 *_CHAFA_ARGS.get(style, _CHAFA_ARGS["blocks"]), "-"],
                input=r.content, capture_output=True, timeout=10,
            ).stdout.decode("utf-8", "replace")
            out = _NON_SGR.sub("", out)
            if style == "braille":
                lines = [_SGR.sub("", ln).rstrip() for ln in out.splitlines()]
                rows_out = [[(ln, "")] for ln in lines if ln.strip()]
            else:
                rows_out = [s for s in (_segments(ln, style == "blocks") for ln in out.splitlines()) if s]
            rows_out = rows_out or None
    except Exception:
        pass   # stored as None: don't retry this url on every request
    with _lock:
        _art[key] = rows_out
        while len(_art) > _MAX_ITEMS:
            _art.popitem(last=False)
        _inflight.discard(key)


def get(url, cols=60, rows=18, style="blocks"):
    """Rows of (text, css_class) segments for the image at `url`, or None if not rendered (yet)."""
    key = (url, cols, rows, style)
    with _lock:
        if key in _art:
            return _art[key]
        start = key not in _inflight
        _inflight.add(key)
    if start:
        threading.Thread(target=_render, args=key, daemon=True).start()
    return None
