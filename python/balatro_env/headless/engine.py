"""One headless Balatro instance: the real game source + the RL bridge inside an embedded LuaJIT 2.0.

The game ships LuaJIT 2.0.5 (`lua51.dll`), so the runtime is lupa's `luajit20` module: same PRNG
(`math.random` / `math.randomseed`), same string hashing (table iteration order) and the same
CRT-backed number formatting the game's pseudorandom functions depend on.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import zlib
from pathlib import Path
from typing import Any

from balatro_env.headless.source import BRIDGE_DIR, LUA_DIR, extract_source

# Fixed virtual frame time handed to love.update (LOVE caps its smoothed dt at 0.1 s).
DEFAULT_DT = 1 / 60

# Profile settings as in the swarm's instance template (game speed 4, tutorial done, English).
SETTINGS_LUA = (
    'return {["GAMESPEED"]=4,["tutorial_complete"]=true,["profile"]=1,["language"]="en-us",'
    '["skip_splash"]="Yes",["crashreports"]=false,["reduced_motion"]=false,["screenshake"]=0,'
    '["play_button_pos"]=1,["colourblind_option"]=true,["run_stake_stickers"]=true,'
    '["current_setup"]="New Run"}'
)

HEADLESS_PORT = 0


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
                 quiet: bool = True, boot_frames: int = 2000):
        from lupa import luajit20

        self.source_dir = extract_source(exe)
        self.dt = dt
        self.data_dir = Path(data_dir) if data_dir else None
        self.lua = luajit20.LuaRuntime(encoding=None, unpack_returned_tuples=True)
        g = self.lua.globals()
        self.H = g.dofile(_b(LUA_DIR / "runtime.lua"))
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


def _s(v: Any) -> Any:
    return v.decode() if isinstance(v, bytes) else v
