"""Locate the user's Balatro.exe and extract its Lua source into a local cache (never redistributed).

Balatro.exe is a fused LOVE executable: a zip archive appended to the LOVE runtime, so `zipfile` reads it
directly. Only the Lua source, localization and version file are extracted; images/sounds/fonts are
listed in `.manifest` (the headless love.filesystem needs directory listings) but not written.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
LUA_DIR = REPO_ROOT / "headless" / "lua"
BRIDGE_DIR = REPO_ROOT / "game_mod" / "BalatroRLBridge"

_STEAM_SUFFIX = Path("steamapps") / "common" / "Balatro" / "Balatro.exe"


def candidate_exes() -> list[Path]:
    out: list[Path] = []
    if os.environ.get("BALATRO_EXE"):
        out.append(Path(os.environ["BALATRO_EXE"]))
    if sys.platform == "win32":
        for base in (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles"), "C:/Program Files (x86)"):
            if base:
                out.append(Path(base) / "Steam" / _STEAM_SUFFIX)
    else:
        home = Path.home()
        for base in (home / ".steam" / "steam", home / ".local" / "share" / "Steam",
                     home / "Library" / "Application Support" / "Steam"):
            out.append(base / _STEAM_SUFFIX)
    return out


def find_exe(exe: str | os.PathLike | None = None) -> Path | None:
    """The game executable: explicit path, $BALATRO_EXE, or the default Steam install locations."""
    if exe:
        p = Path(exe)
        return p if p.is_file() else None
    for p in candidate_exes():
        if p.is_file():
            return p
    return None


def cache_root() -> Path:
    return Path(os.environ.get("BALATRO_HEADLESS_CACHE") or REPO_ROOT / "headless" / ".cache")


def _keep(name: str) -> bool:
    return not name.startswith("resources/") and not name.endswith("/")


def extract_source(exe: str | os.PathLike | None = None, cache: Path | None = None) -> Path:
    """Extract (once) and return the directory holding the game's Lua source for this exe."""
    path = find_exe(exe)
    if path is None:
        raise FileNotFoundError(
            "Balatro.exe not found; set BALATRO_EXE or pass exe= (tried: "
            + ", ".join(str(p) for p in candidate_exes()) + ")")
    st = path.stat()
    cache = cache or cache_root()
    stamp = f"{st.st_size}-{st.st_mtime_ns}"
    index = cache / "index.json"
    try:
        known = json.loads(index.read_text()) if index.is_file() else {}
    except ValueError:  # unreadable index: only a cache of exe hashes, rebuild it
        known = {}
    digest = known.get(str(path), {}).get(stamp)
    known_before = digest is not None
    if digest is None:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        digest = h.hexdigest()
    out = cache / f"game-{digest[:16]}"
    if not (out / ".manifest").is_file():
        tmp = cache / f".tmp-{digest[:16]}-{os.getpid()}"
        shutil.rmtree(tmp, ignore_errors=True)
        with zipfile.ZipFile(path) as z:
            names = [n for n in z.namelist() if not n.endswith("/")]
            for n in names:
                if _keep(n):
                    z.extract(n, tmp)
        (tmp / ".manifest").write_text("\n".join(names) + "\n", encoding="utf-8")
        (tmp / ".source.json").write_text(json.dumps({"exe": str(path), "sha256": digest}), encoding="utf-8")
        try:
            tmp.rename(out)
        except OSError:  # another worker won the race
            shutil.rmtree(tmp, ignore_errors=True)
    if not known_before:
        known.setdefault(str(path), {})[stamp] = digest
        cache.mkdir(parents=True, exist_ok=True)
        # Parallel workers boot at once: write a private file and rename it into place, so a reader
        # never sees a partial index.
        tmp_index = cache / f".index-{os.getpid()}.json"
        try:
            tmp_index.write_text(json.dumps(known))
            os.replace(tmp_index, index)
        except OSError:
            tmp_index.unlink(missing_ok=True)
    return out


def game_version(source_dir: Path) -> str:
    return (source_dir / "version.jkr").read_text(encoding="utf-8").splitlines()[0].strip()
