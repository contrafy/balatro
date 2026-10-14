"""Swarm status: per-run summaries scanned from trajectory files, aggregation over runs + manifest + post-mortems,
and the auto-generated block of docs/SWARM_STATUS.md (`balatro-data status`). Shared by the dashboard and dataops.

Scanning relies on the recorder's sorted-key JSON (docs/DATA_CONTRACT.md): the top-level `"t"` key is the last
`"t":"` occurrence on every line, so line types are found without parsing the (large) step lines; only the first
and last step of a file, rejects, header and end are decoded.
"""

from __future__ import annotations

import gzip
import json
import os
import re
import time
import zlib
from collections import Counter
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any

from balatro_env.data.manifest import load_manifest, manifest_path, migrate_legacy, replace_file
from balatro_env.data.trajectory import data_dir, dataset_files, run_key

REPO_ROOT = Path(__file__).resolve().parents[3]
DOCS_DIR = REPO_ROOT / "docs"
STATUS_PATH = DOCS_DIR / "SWARM_STATUS.md"
RUNS_DIR = DOCS_DIR / "runs"
BEGIN, END = "<!-- AUTO:BEGIN -->", "<!-- AUTO:END -->"
# An open (.jsonl, end-less) file counts as live while it is its port's newest file and was written this recently.
LIVE_WINDOW_S = 1800.0
CACHE_NAME = ".status_cache.json"
CACHE_VERSION = 2
UNKNOWN_MODEL = "(unknown)"
ANTE_BUCKETS = ("1", "2", "3", "4", "5", "6", "7", "8", "W")

_TYPE_MARK = b'"t":"'
_KEY_RE = re.compile(r"^(?P<seed>[^_]+)_(?P<port>\d+)_(?P<ms>\d+)$")
_PM_RE = re.compile(r"^(?P<port>\d+)_(?P<seed>[A-Za-z0-9]+)\.md$")
_PM_MODEL_RE = re.compile(r"\(port \d+,\s*([^)]+)\)")

STATUS_TEMPLATE = f"""# Swarm status

## Morning summary

_Orchestrator: summarize the night here._

## Auto-generated status

{BEGIN}
{END}

## Orchestrator log

"""


def _loads(raw: bytes | None) -> dict[str, Any] | None:
    if not raw:
        return None
    try:
        obj = json.loads(raw)
    except ValueError:
        return None
    return obj if isinstance(obj, dict) else None


def joker_label(j: dict[str, Any]) -> str:
    if j.get("facing") == "back":
        return "(face-down)"
    name = str(j.get("name") or j.get("key") or "?")
    return f"{name} ({j['edition']})" if j.get("edition") else name


def snapshot(step: dict[str, Any]) -> dict[str, Any]:
    """The decision state recorded with a step (obs is taken before the step's action executes)."""
    o = step.get("obs") or {}
    b = o.get("blind") or {}
    bs = o.get("blind_select") or {}
    choice = (bs.get("choices") or {}).get(bs.get("on_deck") or "") or {}
    act = step.get("action") or {}
    meta = step.get("meta") or {}
    return {
        "i": step.get("i"),
        "ts_ms": step.get("ts_ms"),
        "phase": o.get("phase"),
        "ante": o.get("ante"),
        "round": o.get("round"),
        "money": o.get("money"),
        "hands_left": o.get("hands_remaining"),
        "discards_left": o.get("discards_remaining"),
        "blind": b.get("name") or choice.get("name"),
        "chips_scored": b.get("chips_scored") if b else None,
        "chips_needed": b.get("chips_needed") if b else choice.get("chips"),
        "jokers": [joker_label(j) for j in o.get("jokers") or [] if isinstance(j, dict)],
        "action": act.get("type"),
        "params": act.get("params") or {},
        "why": meta.get("why"),
    }


@dataclass
class RunInfo:
    run_key: str
    path: str
    seed: str | None = None
    port: int | None = None
    deck: str | None = None
    stake: int | None = None
    start_agent: str | None = None
    agent: str | None = None
    model: str | None = None
    replay_of: str | None = None
    ended: bool = False  # has an `end` line
    outcome: str | None = None  # end-line outcome (win/loss/abandoned); None while open or after a crash
    tainted: bool = False
    ante: int | None = None
    round: int | None = None
    blind: str | None = None
    steps: int = 0
    rejects: dict[str, int] = field(default_factory=dict)  # reject lines per meta.agent
    started_ms: int | None = None
    last_ts_ms: int | None = None
    mtime: float = 0.0
    last: dict[str, Any] | None = None  # snapshot() of the last recorded step

    @property
    def compressed(self) -> bool:
        return self.path.endswith(".gz")

    @property
    def is_fuzz(self) -> bool:
        return (self.seed or "").upper().startswith("FUZZ")

    @property
    def is_test(self) -> bool:
        return any((a or "").startswith("test-") for a in (self.agent, self.start_agent))

    @property
    def is_replay(self) -> bool:
        return bool(self.replay_of) or "replay" in (self.agent, self.start_agent)

    @property
    def is_player(self) -> bool:
        """A real player run: not a fuzz seed, test agent, replay verification or debug-tainted run."""
        return not (self.is_fuzz or self.is_test or self.is_replay or self.tainted)

    @property
    def result(self) -> str:
        return self.outcome or "unfinished"

    @property
    def total_rejects(self) -> int:
        return sum(self.rejects.values())


class _Parse:
    """Incremental line accumulator for one trajectory file."""

    def __init__(self) -> None:
        self.header: dict[str, Any] | None = None
        self.end: dict[str, Any] | None = None
        self.first_step: dict[str, Any] | None = None
        self.last_step: bytes | None = None
        self.steps = 0
        self.rejects: Counter[str | None] = Counter()
        self.debug = False

    def feed(self, raw: bytes) -> None:
        raw = raw.strip()
        if not raw:
            return
        k = raw.rfind(_TYPE_MARK)
        if k < 0:
            return
        t = raw[k + 5: raw.find(b'"', k + 5)]
        if t == b"step":
            self.steps += 1
            if self.first_step is None:
                self.first_step = _loads(raw)
            self.last_step = raw
        elif t == b"reject":
            obj = _loads(raw) or {}
            self.rejects[(obj.get("meta") or {}).get("agent")] += 1
        elif t == b"header" and self.header is None:
            self.header = _loads(raw)
        elif t == b"end" and self.end is None:
            self.end = _loads(raw)
        elif t == b"debug":
            self.debug = True

    def info(self, path: Path, mtime: float, root: Path) -> RunInfo:
        h = self.header or {}
        sm = h.get("start_meta") or {}
        sp = h.get("start_params") or {}
        key = run_key(path)
        m = _KEY_RE.match(key)
        last = _loads(self.last_step)
        lmeta = (last or {}).get("meta") or {}
        fmeta = (self.first_step or {}).get("meta") or {}
        agent = lmeta.get("agent") or fmeta.get("agent") or sm.get("agent")
        snap = snapshot(last) if last else None
        end = self.end or {}
        final = end.get("final_obs") if isinstance(end.get("final_obs"), dict) else {}
        port = h.get("port") if h.get("port") is not None else (int(m["port"]) if m else None)
        fb = final.get("blind") or {}
        where = {"blind": fb.get("name"), "chips_scored": fb.get("chips_scored"),
                 "chips_needed": fb.get("chips_needed")} if fb.get("name") else snap
        try:
            rel = path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            rel = path.as_posix()
        return RunInfo(
            run_key=key,
            path=rel,
            seed=h.get("seed") or sp.get("seed") or (m["seed"] if m else None),
            port=port,
            deck=h.get("deck_key") or sp.get("deck"),
            stake=h.get("stake") or sp.get("stake"),
            start_agent=sm.get("agent"),
            agent=agent,
            model=lmeta.get("model") or fmeta.get("model") or sm.get("model"),
            replay_of=sm.get("replay_of"),
            ended=self.end is not None,
            outcome=end.get("outcome") if self.end is not None else None,
            tainted=bool(end.get("tainted")) or self.debug,
            ante=end.get("ante") if end.get("ante") is not None else (snap or {}).get("ante"),
            round=end.get("round") if end.get("round") is not None else (snap or {}).get("round"),
            blind=fmt_blind(where) if where and where.get("blind") else None,
            steps=self.steps,
            rejects={str(a or agent or "?"): n for a, n in self.rejects.items()},
            started_ms=h.get("started_at_ms") or (int(m["ms"]) if m else None),
            last_ts_ms=(snap or {}).get("ts_ms") or end.get("ts_ms"),
            mtime=mtime,
            last=snap,
        )


@dataclass
class _Entry:
    size: int
    mtime_ns: int
    info: RunInfo
    parse: _Parse | None = None  # kept for open .jsonl files (incremental reads)
    offset: int = 0


class RunScanner:
    """RunInfo per trajectory file, cached by (size, mtime). Growing .jsonl files are read incrementally (only
    new complete lines); finished .jsonl.gz files are parsed once and persisted in `<data>/.status_cache.json`."""

    def __init__(self, root: str | os.PathLike | None = None, persist: bool = True) -> None:
        self.root = data_dir(root)
        self.persist = persist
        self.entries: dict[str, _Entry] = {}
        self._cache_path = self.root / CACHE_NAME
        if persist:
            self._load_cache()

    def _load_cache(self) -> None:
        try:
            doc = json.loads(self._cache_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if doc.get("version") != CACHE_VERSION:
            return
        names = {f.name for f in fields(RunInfo)}
        for key, e in (doc.get("files") or {}).items():
            try:
                info = RunInfo(**{k: v for k, v in e["info"].items() if k in names})
                self.entries[key] = _Entry(int(e["size"]), int(e["mtime_ns"]), info)
            except (KeyError, TypeError, ValueError):
                continue

    def _save_cache(self) -> None:
        files = {k: {"size": e.size, "mtime_ns": e.mtime_ns, "info": asdict(e.info)}
                 for k, e in self.entries.items() if k.endswith(".gz")}
        tmp = self._cache_path.with_name(CACHE_NAME + f".{os.getpid()}.tmp")
        try:
            tmp.write_text(json.dumps({"version": CACHE_VERSION, "files": files}), encoding="utf-8")
            replace_file(tmp, self._cache_path)
        except OSError:
            tmp.unlink(missing_ok=True)

    def scan(self) -> list[RunInfo]:
        files = dataset_files(self.root)
        out: list[RunInfo] = []
        seen: set[str] = set()
        dirty = False
        for path in files:
            key = path.relative_to(self.root).as_posix() if path.is_relative_to(self.root) else str(path)
            try:
                st = path.stat()
            except FileNotFoundError:  # gzipped/removed between listing and stat
                continue
            seen.add(key)
            entry = self.entries.get(key)
            if entry and entry.size == st.st_size and entry.mtime_ns == st.st_mtime_ns:
                out.append(entry.info)
                continue
            try:
                entry = self._read(path, st, entry)
            except OSError:
                continue
            self.entries[key] = entry
            dirty |= key.endswith(".gz")
            out.append(entry.info)
        for key in [k for k in self.entries if k not in seen]:
            dirty |= key.endswith(".gz")
            del self.entries[key]
        if dirty and self.persist:
            self._save_cache()
        return out

    def _read(self, path: Path, st: os.stat_result, prev: _Entry | None) -> _Entry:
        if path.name.endswith(".gz"):
            parse = _Parse()
            try:
                with gzip.open(path, "rb") as fh:
                    for raw in fh:
                        parse.feed(raw)
            except (EOFError, gzip.BadGzipFile, zlib.error):
                pass  # truncated/corrupt stream: keep what decoded; validate reports it
            return _Entry(st.st_size, st.st_mtime_ns, parse.info(path, st.st_mtime, self.root))
        if prev is not None and prev.parse is not None and st.st_size >= prev.offset:
            parse, offset = prev.parse, prev.offset
        else:
            parse, offset = _Parse(), 0
        with open(path, "rb") as fh:
            fh.seek(offset)
            data = fh.read()
        cut = data.rfind(b"\n") + 1  # only complete lines; a partial last line is read next time
        for raw in data[:cut].split(b"\n"):
            parse.feed(raw)
        return _Entry(st.st_size, st.st_mtime_ns, parse.info(path, st.st_mtime, self.root), parse, offset + cut)


@dataclass
class PostMortem:
    name: str
    port: int
    seed: str
    title: str
    mtime: float

    @property
    def model(self) -> str | None:
        m = _PM_MODEL_RE.search(self.title)
        return m.group(1).strip() if m else None


class PostMortemIndex:
    """docs/runs/<port>_<seed>.md files (title = first heading), cached by mtime."""

    def __init__(self, runs_dir: str | os.PathLike = RUNS_DIR) -> None:
        self.dir = Path(runs_dir)
        self._cache: dict[str, PostMortem] = {}

    def scan(self) -> list[PostMortem]:
        out: list[PostMortem] = []
        if not self.dir.is_dir():
            return out
        for path in self.dir.iterdir():
            m = _PM_RE.match(path.name)
            if not m:
                continue
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue
            pm = self._cache.get(path.name)
            if pm is None or pm.mtime != mtime:
                title = ""
                try:
                    with open(path, encoding="utf-8", errors="replace") as fh:
                        for line in fh:
                            if line.strip():
                                title = line.strip().lstrip("#").strip()
                                break
                except OSError:
                    pass
                pm = PostMortem(path.name, int(m["port"]), m["seed"].upper(), title, mtime)
                self._cache[path.name] = pm
            out.append(pm)
        out.sort(key=lambda p: p.mtime, reverse=True)
        return out


def find_postmortem(pms: dict[tuple[int | None, str], PostMortem], run: RunInfo) -> PostMortem | None:
    seed = (run.seed or "").upper()
    return pms.get((run.port, seed)) or pms.get((None, seed))


def deck_name(deck: str | None) -> str:
    if not deck:
        return "?"
    return deck[2:].replace("_", " ").title() if deck.startswith("b_") else deck


def ante_bucket(run: RunInfo) -> str:
    if run.outcome == "win":
        return "W"
    return str(min(max(int(run.ante or 1), 1), 8))


def is_live(run: RunInfo, newest_by_port: dict[int, str], now_s: float, window_s: float) -> bool:
    return (not run.ended and not run.compressed and now_s - run.mtime <= window_s
            and run.port is not None and newest_by_port.get(run.port) == run.run_key)


def _row_is_player(row: dict[str, Any], run: RunInfo | None) -> bool:
    if run is not None:
        return run.is_player
    agent = row.get("agent") or ""
    return not (str(row.get("seed") or "").upper().startswith("FUZZ") or agent.startswith("test-")
                or agent == "replay" or row.get("replay_of"))


VALIDITY_KEYS = ("files", "schema_ok", "schema_bad", "replay_ok", "replay_failed", "awaiting_replay", "open",
                 "gui_ok", "gui_failed", "headless_ok", "headless_failed", "cross_checked", "disagree")


def _validity(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Manifest counts. replay_ok/replay_failed = combined verdict; gui_*/headless_* = per-host verdicts;
    cross_checked = runs verified by both hosts, disagree = of those, verdicts that differ."""
    c = Counter()
    quarantined: list[tuple[str, str]] = []
    for row in rows:
        c["files"] += 1
        closed = str(row.get("path") or "").endswith(".gz")
        if row.get("schema_ok"):
            c["schema_ok"] += 1
            if row.get("replay_ok") is True:
                c["replay_ok"] += 1
            elif row.get("replay_ok") is False:
                c["replay_failed"] += 1
            elif closed:
                c["awaiting_replay"] += 1
            else:
                c["open"] += 1
            host = dict(row)
            migrate_legacy(host)
            gui, hl = host.get("gui_replay_ok"), host.get("headless_replay_ok")
            for name, v in (("gui", gui), ("headless", hl)):
                if v is not None:
                    c[f"{name}_{'ok' if v else 'failed'}"] += 1
            if gui is not None and hl is not None:
                c["cross_checked"] += 1
                c["disagree"] += gui != hl
        else:
            c["schema_bad"] += 1
        if row.get("quarantined_reason"):
            quarantined.append((row["run_key"], str(row["quarantined_reason"])))
    out: dict[str, Any] = {k: c[k] for k in VALIDITY_KEYS}
    out["quarantined"] = sorted(quarantined)
    return out


def aggregate(runs: list[RunInfo], manifest_rows: dict[str, dict[str, Any]], postmortems: list[PostMortem],
              now_s: float | None = None, live_window_s: float = LIVE_WINDOW_S) -> dict[str, Any]:
    """Everything `status` and the dashboard show. Fuzz seeds, `test-*` agents and replay verifications are
    excluded from results/live/rejects; validity counts cover player runs (plus an all-files line without tests)."""
    now_s = time.time() if now_s is None else now_s
    pm_by: dict[tuple[int | None, str], PostMortem] = {}
    for pm in sorted(postmortems, key=lambda p: p.mtime):
        pm_by[(pm.port, pm.seed)] = pm
        pm_by[(None, pm.seed)] = pm
    newest: dict[int, tuple[int, str]] = {}
    for r in runs:
        if r.port is not None:
            cand = (r.started_ms or 0, r.run_key)
            if r.port not in newest or cand > newest[r.port]:
                newest[r.port] = cand
    newest_by_port = {p: k for p, (_, k) in newest.items()}

    def model_of(r: RunInfo) -> str:
        pm = find_postmortem(pm_by, r)
        return r.model or (pm.model if pm else None) or UNKNOWN_MODEL

    players = [r for r in runs if r.is_player]
    live = sorted((r for r in players if is_live(r, newest_by_port, now_s, live_window_s)),
                  key=lambda r: (r.port or 0))
    live_keys = {r.run_key for r in live}
    done = [r for r in players if r.run_key not in live_keys]

    groups: dict[tuple[str, int, str], list[RunInfo]] = {}
    for r in done:
        groups.setdefault((model_of(r), int(r.stake or 0), r.deck or "?"), []).append(r)
    results = []
    for (model, stake, deck), rs in sorted(groups.items()):
        antes = [int(r.ante) for r in rs if r.ante is not None]
        oc = Counter(r.result for r in rs)
        results.append({
            "model": model, "stake": stake, "deck": deck, "runs": len(rs), "wins": oc["win"],
            "losses": oc["loss"], "abandoned": oc["abandoned"], "unfinished": oc["unfinished"],
            "mean_ante": round(sum(antes) / len(antes), 2) if antes else None,
            "max_ante": max(antes) if antes else None,
        })

    def depth(r: RunInfo) -> tuple:
        return (r.outcome == "win", r.ante or 0, r.round or 0, r.started_ms or 0)

    def row(r: RunInfo) -> dict[str, Any]:
        pm = find_postmortem(pm_by, r)
        return {"run": r, "model": model_of(r), "postmortem": pm.name if pm else None}

    hist: dict[str, Counter] = {}
    for r in done:
        hist.setdefault(model_of(r), Counter())[ante_bucket(r)] += 1

    rej = Counter()
    rej_runs: dict[str, set[str]] = {}
    steps_by_agent = Counter()
    for r in players:
        steps_by_agent[r.agent or "?"] += r.steps
        for agent, n in r.rejects.items():
            rej[agent] += n
            rej_runs.setdefault(agent, set()).add(r.run_key)
    agents = sorted(set(rej) | set(steps_by_agent), key=lambda a: (-rej[a], a))
    rejects = [{"agent": a, "rejects": rej[a], "runs_with_rejects": len(rej_runs.get(a, ())),
                "steps": steps_by_agent[a]} for a in agents]

    by_key = {r.run_key: r for r in runs}
    rows = [row_ for k, row_ in manifest_rows.items()
            if not (k in by_key and by_key[k].is_test) and not str(row_.get("agent") or "").startswith("test-")]
    player_rows = [r_ for r_ in rows if _row_is_player(r_, by_key.get(r_["run_key"]))]
    validity = _validity(player_rows)
    validity["not_in_manifest"] = sum(1 for r in players if r.run_key not in manifest_rows)

    return {
        "generated_s": now_s,
        "live": [row(r) for r in live],
        "results": results,
        "deepest": [row(r) for r in sorted(done, key=depth, reverse=True)[:10]],
        "wins": [row(r) for r in sorted((r for r in done if r.outcome == "win"),
                                        key=lambda r: r.started_ms or 0)],
        "histogram": {m: {b: c[b] for b in ANTE_BUCKETS} for m, c in sorted(hist.items())},
        "validity": validity,
        "validity_all": _validity(rows),
        "rejects": rejects,
        "postmortems": postmortems,
        "counts": {"player_runs": len(players), "finished": len(done), "live": len(live), "files": len(runs)},
    }


def build_status(root: str | os.PathLike | None = None, runs_dir: str | os.PathLike = RUNS_DIR,
                 scanner: RunScanner | None = None, pm_index: PostMortemIndex | None = None,
                 now_s: float | None = None, live_window_s: float = LIVE_WINDOW_S) -> dict[str, Any]:
    root = data_dir(root)
    scanner = scanner or RunScanner(root)
    pm_index = pm_index or PostMortemIndex(runs_dir)
    return aggregate(scanner.scan(), load_manifest(root) if manifest_path(root).exists() else {},
                     pm_index.scan(), now_s, live_window_s)


# ---------------------------------------------------------------------------------------------- formatting

def fmt_age(seconds: float | None) -> str:
    if seconds is None:
        return "?"
    s = int(max(seconds, 0))
    if s < 120:
        return f"{s}s"
    if s < 7200:
        return f"{s // 60}m"
    return f"{s // 3600}h{(s % 3600) // 60:02d}m"


def fmt_action(snap: dict[str, Any] | None) -> str:
    if not snap or not snap.get("action"):
        return "-"
    params = snap.get("params") or {}
    if not params:
        return str(snap["action"])
    return f"{snap['action']} {json.dumps(params, separators=(',', ':'), sort_keys=True)}"


def fmt_blind(snap: dict[str, Any] | None) -> str:
    if not snap or not snap.get("blind"):
        return "-"
    need, got = snap.get("chips_needed"), snap.get("chips_scored")
    if need is not None and got is not None:
        return f"{snap['blind']} {got}/{need}"
    return f"{snap['blind']} ({need})" if need is not None else str(snap["blind"])


def _md(value: Any, limit: int = 0) -> str:
    text = "-" if value is None or value == "" else str(value)
    text = " ".join(text.split()).replace("|", "\\|")
    return text[: limit - 1] + "…" if limit and len(text) > limit else text


def render_markdown(st: dict[str, Any], runs_link: str = "runs") -> str:
    """The text between the AUTO markers. `runs_link` = docs/runs relative to the status file."""
    now_s = st["generated_s"]
    c = st["counts"]
    out = [f"_Generated {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now_s))} by `balatro-data status` "
           f"(edits inside this block are overwritten). Player runs: {c['player_runs']} "
           f"({c['finished']} finished, {c['live']} live); fuzz seeds, `test-*` agents and replays excluded._", ""]

    def pm_link(item: dict[str, Any]) -> str:
        return f"[{item['postmortem']}]({runs_link}/{item['postmortem']})" if item["postmortem"] else "-"

    out += [f"### Live runs ({len(st['live'])})", ""]
    if st["live"]:
        out += ["| port | agent | model | seed | stake | phase | ante | round | $ | blind | last action | why | idle |",
                "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for item in st["live"]:
            r: RunInfo = item["run"]
            s = r.last or {}
            idle = now_s - (r.last_ts_ms / 1000 if r.last_ts_ms else r.mtime)
            out.append(f"| {r.port} | {_md(r.agent)} | {_md(item['model'])} | {r.seed} | {r.stake} | "
                       f"{_md(s.get('phase'))} | {_md(s.get('ante'))} | {_md(s.get('round'))} | "
                       f"{_md(s.get('money'))} | {_md(fmt_blind(s))} | {_md(fmt_action(s), 60)} | "
                       f"{_md(s.get('why'), 100)} | {fmt_age(idle)} |")
    else:
        out.append("No live runs.")

    out += ["", "### Results by model x stake x deck", ""]
    if st["results"]:
        out += ["| model | stake | deck | runs | wins | losses | abandoned | unfinished | mean ante | max ante |",
                "|---|---|---|---|---|---|---|---|---|---|"]
        for g in st["results"]:
            out.append(f"| {_md(g['model'])} | {g['stake']} | {deck_name(g['deck'])} | {g['runs']} | {g['wins']} | "
                       f"{g['losses']} | {g['abandoned']} | {g['unfinished']} | {_md(g['mean_ante'])} | "
                       f"{_md(g['max_ante'])} |")
    else:
        out.append("No finished player runs yet.")

    out += ["", "### Deepest runs", ""]
    if st["deepest"]:
        out += ["| # | seed | model | stake | deck | outcome | ante | blind | post-mortem |",
                "|---|---|---|---|---|---|---|---|---|"]
        for n, item in enumerate(st["deepest"], 1):
            r = item["run"]
            out.append(f"| {n} | {r.seed} | {_md(item['model'])} | {r.stake} | {deck_name(r.deck)} | {r.result} | "
                       f"{_md(r.ante)} | {_md(r.blind)} | {pm_link(item)} |")
    else:
        out.append("None yet.")

    v, va = st["validity"], st["validity_all"]
    out += ["", "### Data validity", "",
            f"- Player runs: {v['files']} files in manifest; schema_ok {v['schema_ok']}, schema invalid "
            f"{v['schema_bad']}; replay_ok {v['replay_ok']}, replay failed {v['replay_failed']}, awaiting replay "
            f"{v['awaiting_replay']}, open/unended {v['open']}; quarantined {len(v['quarantined'])}; "
            f"not yet in manifest {v['not_in_manifest']}.",
            f"- Player-run replay verdicts by host: headless ok {v['headless_ok']} / failed {v['headless_failed']}; "
            f"gui (live) ok {v['gui_ok']} / failed {v['gui_failed']}; cross-checked by both {v['cross_checked']}, "
            f"disagreeing {v['disagree']}.",
            f"- All files (incl. fuzz + replays): {va['files']}; schema_ok {va['schema_ok']}; replay_ok "
            f"{va['replay_ok']} (headless {va['headless_ok']}, gui {va['gui_ok']}); replay failed "
            f"{va['replay_failed']}; awaiting replay {va['awaiting_replay']}; quarantined {len(va['quarantined'])}."]
    if v["quarantined"]:
        out += ["", "Quarantined player runs:", ""]
        out += [f"- `{k}`: {_md(reason, 200)}" for k, reason in v["quarantined"]]

    out += ["", "### Rejects per agent", ""]
    if st["rejects"]:
        out += ["| agent | rejects | runs with rejects | steps |", "|---|---|---|---|"]
        out += [f"| {_md(x['agent'])} | {x['rejects']} | {x['runs_with_rejects']} | {x['steps']} |"
                for x in st["rejects"]]
    else:
        out.append("No player runs.")
    return "\n".join(out)


def write_status(path: str | os.PathLike, block: str) -> Path:
    """Replace the text between the AUTO markers (create the file from the template if missing)."""
    path = Path(path)
    text = path.read_text(encoding="utf-8") if path.exists() else STATUS_TEMPLATE
    b, e = text.find(BEGIN), text.find(END)
    if b < 0 or e < b:
        text = text.rstrip("\n") + f"\n\n## Auto-generated status\n\n{BEGIN}\n{END}\n"
        b, e = text.find(BEGIN), text.find(END)
    new = text[: b + len(BEGIN)] + "\n" + block.strip("\n") + "\n" + text[e:]
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".{os.getpid()}.tmp")
    tmp.write_text(new, encoding="utf-8", newline="\n")
    replace_file(tmp, path)
    return path


def update_status_file(root: str | os.PathLike | None = None, out: str | os.PathLike = STATUS_PATH,
                       runs_dir: str | os.PathLike = RUNS_DIR, scanner: RunScanner | None = None,
                       pm_index: PostMortemIndex | None = None,
                       live_window_s: float = LIVE_WINDOW_S) -> tuple[Path, str, dict[str, Any]]:
    out = Path(out)
    st = build_status(root, runs_dir, scanner, pm_index, live_window_s=live_window_s)
    link = os.path.relpath(Path(runs_dir).resolve(), out.resolve().parent).replace(os.sep, "/")
    block = render_markdown(st, link)
    return write_status(out, block), block, st
