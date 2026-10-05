import re
import shutil
import subprocess
import time
from itertools import zip_longest
from .cache import get as cached

_ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
_SKIP = ("Shell:", "Terminal:")   # meaningless when run under systemd


def _neofetch(*args):
    out = subprocess.run(["neofetch", *args], capture_output=True, text=True, timeout=5).stdout
    return [_ANSI.sub("", ln).rstrip() for ln in out.splitlines()]


def _fetch_rows():
    """neofetch logo and info side by side, as a list of plain-text rows (None if unavailable)."""
    try:
        logo = _neofetch("-L")
        info = [ln for ln in _neofetch("--stdout") if ln.strip() and not ln.startswith(_SKIP)]
        # neofetch 7.1 leaves an unmatched "]" on some GPU names ("Intel Graphics]")
        info = [ln[:-1] if ln.endswith("]") and "[" not in ln else ln for ln in info]
    except Exception:
        return None
    if not info:
        return None
    while logo and not logo[-1].strip():
        logo.pop()
    width = max((len(ln) for ln in logo), default=0) + 3
    return [((l or "").ljust(width) + (i or "")).rstrip() for l, i in zip_longest(logo, info)]


def _cpu_times():
    cores = []
    with open("/proc/stat") as f:
        for ln in f:
            if ln.startswith("cpu") and ln[3].isdigit():
                v = [int(x) for x in ln.split()[1:]]
                cores.append((v[3] + v[4], sum(v)))   # (idle + iowait, total)
    return cores


def _stats(disk_path):
    a = _cpu_times()
    time.sleep(0.5)
    b = _cpu_times()
    cpu = []
    for (i0, t0), (i1, t1) in zip(a, b):
        dt = t1 - t0
        cpu.append(round(100 * (1 - (i1 - i0) / dt)) if dt else 0)

    mem = {}
    with open("/proc/meminfo") as f:
        for ln in f:
            k, v = ln.split(":", 1)
            mem[k] = int(v.split()[0])   # kB
    total, used = mem["MemTotal"], mem["MemTotal"] - mem["MemAvailable"]

    du = shutil.disk_usage(disk_path)
    return {
        "cpu": cpu,
        "mem_used": round(used / 1024 ** 2, 1),
        "mem_total": round(total / 1024 ** 2, 1),
        "mem_pct": round(100 * used / total),
        "disk_path": disk_path,
        "disk_pct": round(100 * du.used / du.total),
    }


def get(disk_path="/"):
    return {
        "fetch": cached("system:fetch", ttl=600, fetch_fn=_fetch_rows),
        "stats": cached("system:stats:" + disk_path, ttl=10, fetch_fn=lambda: _stats(disk_path)),
    }
