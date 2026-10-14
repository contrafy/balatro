"""`balatro-data dashboard`: stdlib-only local HTTP status page for the swarm (no external assets).

Routes: `/` (auto-refreshing HTML), `/status.json`, `/runs/<port>_<seed>.md` (post-mortems as text).
Trajectory summaries come from `status.RunScanner` (cached by size+mtime; open files are read incrementally, so a
refresh costs one stat per file plus the bytes appended since the last refresh).
"""

from __future__ import annotations

import html
import json
import os
import threading
import time
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from balatro_env.data.status import (
    ANTE_BUCKETS,
    LIVE_WINDOW_S,
    RUNS_DIR,
    VALIDITY_KEYS,
    PostMortemIndex,
    RunInfo,
    RunScanner,
    build_status,
    deck_name,
    fmt_action,
    fmt_age,
    fmt_blind,
)
from balatro_env.data.trajectory import data_dir

CSS = """
body{font:13px/1.35 system-ui,Segoe UI,sans-serif;margin:16px;background:#111418;color:#d8dee6}
h1{font-size:18px;margin:0 0 4px} h2{font-size:15px;margin:22px 0 6px;color:#9fc3ff}
table{border-collapse:collapse;margin:4px 0} td,th{border:1px solid #2c333c;padding:3px 6px;vertical-align:top}
th{background:#1b2027;text-align:left} tr:nth-child(even) td{background:#161a20}
a{color:#7fb3ff} .muted{color:#7d8794} .warn{color:#ffb454} .bad{color:#ff6b6b} .good{color:#7ee787}
.why{max-width:420px} .bar{display:inline-block;width:80px;height:8px;background:#2c333c;margin-left:4px}
.bar>span{display:block;height:8px;background:#7ee787} .hist{display:inline-block;margin:0 18px 10px 0}
.small{font-size:11px}
"""


def _e(value: Any) -> str:
    return html.escape("-" if value is None or value == "" else str(value))


def _table(head: list[str], rows: list[list[str]]) -> str:
    th = "".join(f"<th>{h}</th>" for h in head)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table><tr>{th}</tr>{body}</table>"


def _pm_link(name: str | None) -> str:
    return f'<a href="/runs/{html.escape(name)}">{html.escape(name)}</a>' if name else "-"


def _progress(snap: dict[str, Any]) -> str:
    need, got = snap.get("chips_needed"), snap.get("chips_scored")
    text = _e(fmt_blind(snap))
    if isinstance(need, (int, float)) and need > 0 and isinstance(got, (int, float)):
        pct = max(0.0, min(100.0, 100.0 * got / need))
        text += f'<span class="bar"><span style="width:{pct:.0f}%"></span></span>'
    return text


def histogram_svg(model: str, counts: dict[str, int]) -> str:
    """Inline SVG bar chart of runs per ante reached (W = win)."""
    w, h, pad, bw = 260, 120, 18, 24
    top = max(counts.values() or [0]) or 1
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h + 2 * pad}" '
             f'role="img" aria-label="ante histogram {html.escape(model)}">',
             f'<text x="0" y="12" fill="#9fc3ff" font-size="12">{html.escape(model)}</text>']
    for k, b in enumerate(ANTE_BUCKETS):
        n = counts.get(b, 0)
        bh = round((h - pad) * n / top)
        x = 4 + k * (bw + 4)
        y = pad + (h - pad) - bh
        color = "#7ee787" if b == "W" else "#5b8def"
        parts.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" fill="{color}"/>')
        if n:
            parts.append(f'<text x="{x + bw / 2}" y="{y - 2}" fill="#d8dee6" font-size="10" '
                         f'text-anchor="middle">{n}</text>')
        parts.append(f'<text x="{x + bw / 2}" y="{h + pad - 4}" fill="#7d8794" font-size="10" '
                     f'text-anchor="middle">{b}</text>')
    parts.append("</svg>")
    return "".join(parts)


def render_html(st: dict[str, Any], refresh_s: int) -> str:
    now_s = st["generated_s"]
    c = st["counts"]
    out = [f'<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="{refresh_s}">'
           f"<title>Balatro swarm ({c['live']} live)</title><style>{CSS}</style></head><body>",
           "<h1>Balatro swarm</h1>",
           f'<div class="muted">{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now_s))} - '
           f"{c['player_runs']} player runs ({c['finished']} finished, {c['live']} live), {c['files']} trajectory "
           f"files; refresh every {refresh_s}s; <a href=\"/status.json\">status.json</a></div>"]

    out.append(f"<h2>Live runs ({len(st['live'])})</h2>")
    rows = []
    for item in st["live"]:
        r: RunInfo = item["run"]
        s = r.last or {}
        idle = now_s - (r.last_ts_ms / 1000 if r.last_ts_ms else r.mtime)
        idle_cls = "bad" if idle > 600 else "warn" if idle > 180 else ""
        rows.append([
            _e(r.port), _e(r.agent), _e(item["model"]), _e(r.seed),
            f"{_e(deck_name(r.deck))} / {_e(r.stake)}", _e(s.get("phase")), _e(s.get("ante")), _e(s.get("round")),
            f"${_e(s.get('money'))}", _progress(s),
            f"{_e(s.get('hands_left'))} / {_e(s.get('discards_left'))}",
            f'<span class="small">{_e(", ".join(s.get("jokers") or []))}</span>',
            f"<code>{_e(fmt_action(s))}</code>", f'<span class="why">{_e(s.get("why"))}</span>',
            f'<span class="{idle_cls}">{fmt_age(idle)}</span>', _e(r.steps), _e(r.total_rejects),
            _pm_link(item["postmortem"]),
        ])
    out.append(_table(["port", "agent", "model", "seed", "deck / stake", "phase", "ante", "round", "money",
                       "blind", "hands / discards", "jokers", "last action", "why", "idle", "steps", "rejects",
                       "log"], rows) if rows else '<div class="muted">No live runs.</div>')
    out.append('<div class="muted small">Values are the last recorded decision state (obs before the last '
               "action).</div>")

    out.append("<h2>Results by model x stake x deck</h2>")
    out.append(_table(
        ["model", "stake", "deck", "runs", "wins", "losses", "abandoned", "unfinished", "mean ante", "max ante"],
        [[_e(g["model"]), _e(g["stake"]), _e(deck_name(g["deck"])), _e(g["runs"]),
          f'<span class="good">{g["wins"]}</span>' if g["wins"] else "0", _e(g["losses"]), _e(g["abandoned"]),
          _e(g["unfinished"]), _e(g["mean_ante"]), _e(g["max_ante"])] for g in st["results"]])
        if st["results"] else '<div class="muted">No finished player runs yet.</div>')

    out.append(f"<h2>Wins ({len(st['wins'])})</h2>")
    out.append(_table(["seed", "model", "agent", "deck / stake", "steps", "started", "post-mortem"],
                      [[_e(i["run"].seed), _e(i["model"]), _e(i["run"].agent),
                        f"{_e(deck_name(i['run'].deck))} / {_e(i['run'].stake)}", _e(i["run"].steps),
                        _e(time.strftime("%m-%d %H:%M", time.localtime((i["run"].started_ms or 0) / 1000))),
                        _pm_link(i["postmortem"])] for i in st["wins"]])
               if st["wins"] else '<div class="muted">No wins yet.</div>')

    out.append("<h2>Ante reached per model (finished runs; W = win)</h2>")
    out.append("".join(f'<div class="hist">{histogram_svg(m, h)}</div>' for m, h in st["histogram"].items())
               or '<div class="muted">No finished player runs yet.</div>')

    out.append("<h2>Deepest runs</h2>")
    out.append(_table(["#", "seed", "model", "deck / stake", "outcome", "ante", "round", "blind", "post-mortem"],
                      [[str(n), _e(i["run"].seed), _e(i["model"]),
                        f"{_e(deck_name(i['run'].deck))} / {_e(i['run'].stake)}", _e(i["run"].result),
                        _e(i["run"].ante), _e(i["run"].round), _e(i["run"].blind), _pm_link(i["postmortem"])]
                       for n, i in enumerate(st["deepest"], 1)]) if st["deepest"] else
               '<div class="muted">None yet.</div>')

    out.append("<h2>Data validity (manifest)</h2>")
    keys = list(VALIDITY_KEYS)
    v, va = st["validity"], st["validity_all"]
    out.append(_table(["scope"] + keys + ["quarantined", "not in manifest"],
                      [["player runs"] + [_e(v[k]) for k in keys] + [_e(len(v["quarantined"])),
                                                                     _e(v["not_in_manifest"])],
                       ["all files"] + [_e(va[k]) for k in keys] + [_e(len(va["quarantined"])), "-"]]))
    if va["quarantined"]:
        out.append(_table(["quarantined run", "reason"],
                          [[_e(k), f'<span class="bad small">{_e(reason)}</span>'] for k, reason in va["quarantined"]]))

    out.append("<h2>Rejects per agent</h2>")
    out.append(_table(["agent", "rejects", "runs with rejects", "steps"],
                      [[_e(x["agent"]), f'<span class="warn">{x["rejects"]}</span>' if x["rejects"] else "0",
                        _e(x["runs_with_rejects"]), _e(x["steps"])] for x in st["rejects"]])
               if st["rejects"] else '<div class="muted">No player runs.</div>')

    out.append(f"<h2>Post-mortems ({len(st['postmortems'])})</h2>")
    out.append(_table(["file", "title", "updated"],
                      [[_pm_link(p.name), _e(p.title),
                        _e(time.strftime("%m-%d %H:%M", time.localtime(p.mtime)))] for p in st["postmortems"]])
               if st["postmortems"] else '<div class="muted">None.</div>')
    out.append("</body></html>")
    return "\n".join(out)


def status_json(st: dict[str, Any]) -> dict[str, Any]:
    def item(i: dict[str, Any]) -> dict[str, Any]:
        return {**asdict(i["run"]), "model": i["model"], "postmortem": i["postmortem"],
                "result": i["run"].result}

    out = {k: v for k, v in st.items() if k not in ("live", "deepest", "wins", "postmortems")}
    for k in ("live", "deepest", "wins"):
        out[k] = [item(i) for i in st[k]]
    out["postmortems"] = [asdict(p) for p in st["postmortems"]]
    return out


class Dashboard:
    """Shared state for request threads: one scanner (mtime cache), status memoized for `min_age_s`."""

    def __init__(self, root: str | os.PathLike | None, runs_dir: str | os.PathLike = RUNS_DIR,
                 live_window_s: float = LIVE_WINDOW_S, refresh_s: int = 15, min_age_s: float = 2.0) -> None:
        self.root = data_dir(root)
        self.runs_dir = Path(runs_dir)
        self.scanner = RunScanner(self.root)
        self.pm_index = PostMortemIndex(self.runs_dir)
        self.live_window_s = live_window_s
        self.refresh_s = refresh_s
        self.min_age_s = min_age_s
        self._lock = threading.Lock()
        self._st: dict[str, Any] | None = None
        self._at = 0.0

    def status(self) -> dict[str, Any]:
        with self._lock:
            if self._st is None or time.monotonic() - self._at > self.min_age_s:
                self._st = build_status(self.root, self.runs_dir, self.scanner, self.pm_index,
                                        live_window_s=self.live_window_s)
                self._at = time.monotonic()
            return self._st

    def postmortem(self, name: str) -> bytes | None:
        if "/" in name or "\\" in name or not name.endswith(".md") or name.startswith("."):
            return None
        path = self.runs_dir / name
        try:
            return path.read_bytes() if path.is_file() else None
        except OSError:
            return None


def make_handler(dash: Dashboard) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, body: bytes, ctype: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            try:
                if path in ("/", "/index.html"):
                    body = render_html(dash.status(), dash.refresh_s).encode("utf-8")
                    self._send(200, body, "text/html; charset=utf-8")
                elif path == "/status.json":
                    body = json.dumps(status_json(dash.status()), default=str).encode("utf-8")
                    self._send(200, body, "application/json")
                elif path.startswith("/runs/"):
                    data = dash.postmortem(path[len("/runs/"):])
                    if data is None:
                        self._send(404, b"not found", "text/plain")
                    else:
                        self._send(200, data, "text/plain; charset=utf-8")
                else:
                    self._send(404, b"not found", "text/plain")
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass
            except Exception as exc:  # keep serving; show the error instead of dropping the connection
                self._send(HTTPStatus.INTERNAL_SERVER_ERROR, f"{type(exc).__name__}: {exc}".encode(), "text/plain")

        def log_message(self, fmt: str, *args: Any) -> None:
            pass

    return Handler


def serve(root: str | os.PathLike | None, host: str, port: int, runs_dir: str | os.PathLike = RUNS_DIR,
          live_window_s: float = LIVE_WINDOW_S, refresh_s: int = 15) -> None:
    dash = Dashboard(root, runs_dir, live_window_s, refresh_s)
    dash.status()  # warm the cache before accepting requests
    server = ThreadingHTTPServer((host, port), make_handler(dash))
    server.daemon_threads = True
    print(f"dashboard on http://{host}:{port}/ (data {dash.root}, post-mortems {dash.runs_dir})", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
