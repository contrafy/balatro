"""One headless Balatro instance: the real game source + the RL bridge inside an embedded LuaJIT.

The game ships LuaJIT 2.0.5 (`lua51.dll`), so the default runtime is lupa's `luajit20` module: same PRNG
(`math.random` / `math.randomseed`), same string hashing (table iteration order) and the same
CRT-backed number formatting the game's pseudorandom functions depend on. `lua="luajit21"` selects
lupa's LuaJIT 2.1 instead (see docs/HEADLESS.md for when that is equivalent).
"""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import re
import zlib
from pathlib import Path
from typing import Any, Iterable

from balatro_env.headless.source import BRIDGE_DIR, LUA_DIR, extract_source

# Fixed virtual frame time handed to love.update. 0.1 s is LOVE's own cap on the smoothed dt (a live game
# at 10 fps sees exactly this); larger steps make UI easing overshoot and never settle.
DEFAULT_DT = 0.1

# lupa runtime module: luajit20 matches the game's bundled LuaJIT 2.0.5.
LUA_FLAVORS = ("luajit20", "luajit21")
DEFAULT_LUA = "luajit20"

# Profile settings as in the swarm's instance template (game speed 4, tutorial done, English).
SETTINGS_LUA = (
    'return {["GAMESPEED"]=4,["tutorial_complete"]=true,["profile"]=1,["language"]="en-us",'
    '["skip_splash"]="Yes",["crashreports"]=false,["reduced_motion"]=false,["screenshake"]=0,'
    '["play_button_pos"]=1,["colourblind_option"]=true,["run_stake_stickers"]=true,'
    '["current_setup"]="New Run"}'
)

HEADLESS_PORT = 0


def fastpath_names() -> tuple[str, ...]:
    """Names of the fast-path optimizations (headless/lua/fastpath.lua `P.NAMES`, in order)."""
    text = (LUA_DIR / "fastpath.lua").read_text(encoding="utf-8")
    m = re.search(r"^P\.NAMES = \{([^}]*)\}", text, re.M)
    if not m:
        raise EngineError("fastpath.lua: P.NAMES not found")
    return tuple(re.findall(r'"(\w+)"', m.group(1)))


def resolve_fastpath(spec: bool | str | Iterable[str]) -> tuple[str, ...]:
    """True/'all' = every optimization, False/'none'/'' = vanilla, else names (comma-separated string or
    iterable). The replay gate must pass for the default (all)."""
    names = fastpath_names()
    if spec is True or spec == "all":
        return names
    if spec is False or spec in ("none", ""):
        return ()
    chosen = [s.strip() for s in spec.split(",")] if isinstance(spec, str) else list(spec)
    unknown = [n for n in chosen if n not in names]
    if unknown:
        raise ValueError(f"unknown fastpath optimization(s) {unknown}; known: {', '.join(names)}")
    return tuple(n for n in names if n in chosen)


class EngineError(RuntimeError):
    pass


def _b(s: str | os.PathLike) -> bytes:
    return os.fsencode(str(s).replace("\\", "/"))


class _Host:
    """Primitives the Lua side cannot do alone (bound into love.data)."""

    @staticmethod
    def gzip(data: bytes, level: float) -> bytes:
        lvl = int(level)
        return gzip.compress(data, compresslevel=9 if lvl < 0 else lvl, mtime=0)

    @staticmethod
    def deflate(data: bytes, level: float, fmt: bytes) -> bytes:
        lvl = int(level)
        wbits = {b"zlib": 15, b"gzip": 31}.get(fmt, -15)
        c = zlib.compressobj(lvl, zlib.DEFLATED, wbits)
        return c.compress(data) + c.flush()

    @staticmethod
    def inflate(data: bytes, fmt: bytes) -> bytes:
        wbits = {b"zlib": 15, b"gzip": 31}.get(fmt, -15)
        return zlib.decompress(data, wbits)

    @staticmethod
    def hash(alg: bytes, data: bytes) -> bytes:
        return hashlib.new(alg.decode().lower().replace("-", ""), data).digest()


class Engine:
    """Boots the game to the main menu (profile unlocked by the bridge) and exposes the bridge's HTTP API
    in-process. `request()` goes through the bridge's own server loop, so bodies are byte-identical to a
    live instance's."""

    def __init__(self, exe: str | None = None, data_dir: str | os.PathLike | None = None,
                 port: int = HEADLESS_PORT, dt: float = DEFAULT_DT, git_sha: str | None = None,
                 quiet: bool = True, boot_frames: int = 2000, lua: str = DEFAULT_LUA,
                 fastpath: bool | str | Iterable[str] = True):
        import importlib

        if lua not in LUA_FLAVORS:
            raise ValueError(f"lua must be one of {LUA_FLAVORS}, not {lua!r}")
        runtime = importlib.import_module(f"lupa.{lua}")
        self.source_dir = extract_source(exe)
        self.dt = dt
        self.data_dir = Path(data_dir) if data_dir else None
        self.lua = runtime.LuaRuntime(encoding=None, unpack_returned_tuples=True)
        g = self.lua.globals()
        self.H = g.dofile(_b(LUA_DIR / "runtime.lua"))
        self.fastpath = resolve_fastpath(fastpath)
        env = {b"BALATRO_RL_PORT": str(port).encode(), b"BALATRO_RL_BRIDGE_DIR": _b(BRIDGE_DIR)}
        if self.data_dir is not None:
            env[b"BALATRO_RL_DATA_DIR"] = _b(self.data_dir.resolve())
        if git_sha:
            env[b"BALATRO_RL_GIT_SHA"] = git_sha.encode()
        host = self.lua.table_from({
            b"gzip": _Host.gzip, b"deflate": _Host.deflate, b"inflate": _Host.inflate, b"hash": _Host.hash,
        })
        cfg = self.lua.table_from({
            b"lua_dir": _b(LUA_DIR),
            b"source_dir": _b(self.source_dir),
            b"bridge_dir": _b(BRIDGE_DIR),
            b"dt": float(dt),
            b"quiet": bool(quiet),
            b"fastpath": self.lua.table_from([n.encode() for n in self.fastpath]),
            b"env": self.lua.table_from(env),
            b"save_files": self.lua.table_from({b"settings.jkr": SETTINGS_LUA.encode()}),
        })
        self.H.boot(cfg, host)
        frames, ok, phase, reason = self.H.settle(boot_frames, 0)
        if not ok:
            raise EngineError(f"boot did not reach a settled menu after {frames} frames: {phase} {reason}")

    # -- raw bridge API -------------------------------------------------------------------------------

    def request_raw(self, method: str, path: str, body: bytes = b"") -> bytes:
        status, out = self.H.request(method.encode(), path.encode(), body)
        if status != 200:
            raise EngineError(f"{method} {path}: HTTP {status}: {out[:300]!r}")
        return out

    def request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        data = json.dumps(body).encode() if body is not None else b""
        return json.loads(self.request_raw(method, path, data))

    def state(self) -> dict[str, Any]:
        return self.request("GET", "/state")

    def legal(self) -> dict[str, Any]:
        return self.request("GET", "/legal")

    def health(self) -> dict[str, Any]:
        return self.request("GET", "/health")

    def action(self, atype: str, params: dict[str, Any] | None = None,
               meta: dict[str, Any] | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"type": atype, "params": params or {}}
        if meta:
            body["meta"] = meta
        return self.request("POST", "/action", body)

    # -- clock ----------------------------------------------------------------------------------------

    def settle(self, max_frames: int = 20000, extra: int = 0) -> tuple[int, bool, str, str | None]:
        """Advance the virtual clock until the bridge reports settled. Returns (frames, ok, phase, reason)."""
        frames, ok, phase, reason = self.H.settle(max_frames, extra)
        return int(frames), bool(ok), _s(phase), _s(reason)

    def status(self) -> tuple[bool, str, str | None]:
        ok, phase, reason = self.H.status()
        return bool(ok), _s(phase), _s(reason)

    def frames(self, n: int) -> int:
        return int(self.H.frames(n))

    def close(self) -> None:
        """Close trajectory files of a run that never ended (they stay open in the Lua state otherwise:
        lupa's Lua<->Python reference cycle keeps the runtime alive past the last Python reference)."""
        if self.H is not None:
            self.H.close()
            self.H = None
            self.lua = None


def _s(v: Any) -> Any:
    return v.decode() if isinstance(v, bytes) else v
