# Balatro RL Bridge - Installation Guide

This guide walks you through setting up the Balatro RL harness mod on **Windows** and **macOS**.

---

## Windows Installation

Verified on Windows 11 with Lovely **v0.9.0** and Balatro **1.0.1o-FULL**. The bridge loads through Lovely
only: **no Steamodded** (game logic must stay vanilla; see `docs/DATA_CONTRACT.md`). `BalatroRLBridge/lovely.toml`
registers `main.lua` as a Lua module and calls it from `love.update`; those are the mod's only patches.

On Windows every harness instance (including the single default one on port 7777) runs from its own
directory under `%USERPROFILE%\balatro-instances\<port>`, never from the real `%APPDATA%\Balatro`:
the bridge unlocks and discovers everything on whatever profile it boots and saves it, and starting a run
overwrites that profile's `save.jkr`. Keep `BalatroRLBridge` **out** of `%APPDATA%\Balatro\Mods` so normal
play is unaffected.

### Prerequisites

- Windows 10 or later, Balatro installed via Steam, Steam running and logged in
- Git, Python 3.10+

### Step 1: Back up your saves

```powershell
Copy-Item -Recurse "$env:APPDATA\Balatro" "$env:APPDATA\Balatro_backup_$(Get-Date -Format yyyyMMdd_HHmmss)"
```

### Step 2: Install Lovely Injector

```powershell
curl.exe -L -o lovely.zip https://github.com/ethangreen-dev/lovely-injector/releases/download/v0.9.0/lovely-x86_64-pc-windows-msvc.zip
Expand-Archive lovely.zip lovely
Copy-Item lovely\version.dll "C:\Program Files (x86)\Steam\steamapps\common\Balatro\"
```

`version.dll` makes Lovely load on every launch of `Balatro.exe`. Lovely does not follow an overridden
`APPDATA` variable; without `--mod-dir` it always uses the real `%APPDATA%\Balatro\Mods`.

### Step 3: Create the instance template (optional)

New instances are copied from `%USERPROFILE%\balatro-instances\template\Balatro` when it exists (otherwise they
start empty and the game creates a fresh profile). A template with your `settings.jkr` and profile avoids
first-boot defaults. The bridge unlocks/discovers everything and marks the tutorial complete on every boot anyway.
Do not put any mods in the template: the launcher deletes everything in an instance's `Mods` except
`BalatroRLBridge` and Lovely's own `lovely` dir.

```powershell
$T = "$env:USERPROFILE\balatro-instances\template\Balatro"
New-Item -ItemType Directory -Force "$T\1" | Out-Null
Copy-Item "$env:APPDATA\Balatro\settings.jkr" $T
Copy-Item "$env:APPDATA\Balatro\1\profile.jkr", "$env:APPDATA\Balatro\1\meta.jkr" "$T\1\"   # no save.jkr
```

### Step 4: Python environment

```powershell
cd python
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
```

### Step 5: Launch an instance and verify

`game_mod\windows\launch_instance.ps1` creates `<root>\<port>` (from the template if present) on first use,
removes any other mod from the instance's `Mods`, copies the repo's `BalatroRLBridge` (`main.lua`, `lovely.toml`)
into it, then starts `Balatro.exe` with `--mod-dir <root>\<port>\Balatro\Mods` and:

| variable | value |
|---|---|
| `APPDATA` | `<root>\<port>` (LÖVE save dir) |
| `BALATRO_RL_PORT` | `<port>` |
| `BALATRO_RL_DATA_DIR` | `-DataDir`, default `<repo>\data` (trajectories go to `trajectories\<date>\`) |
| `BALATRO_RL_GIT_SHA` | `git rev-parse HEAD` of the repo, `-dirty` if the tree has changes |
| `BALATRO_RL_BRIDGE_DIR` | the deployed bridge dir (used for `bridge_hash`) |
| `BALATRO_RL_DEBUG` | `1` only with `-DebugEval` (enables test-only `POST /debug/eval`; taints recordings) |

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File game_mod\windows\launch_instance.ps1 -Port 7777
curl.exe http://127.0.0.1:7777/health
# {"status":"ok","bridge_version":"2.0.0","lovely_version":"0.9.0","recorder_ok":true,...}
```

The bridge comes up about 5 seconds after launch; the Lovely log (`<root>\<port>\Balatro\Mods\lovely\log\`)
should show only `Applied 1 patch to 'main.lua'` plus `[BalatroRLBridge]` INFO lines. Each launch redeploys the
bridge, so after editing `main.lua` you only need to kill that instance (by PID) and relaunch.

`steam.exe -applaunch 2379780` is **not** used: on this machine it stalled in Steam's launch flow
(`LaunchApp waiting for user response to ShowInterstitials` in `Steam\logs\console_log.txt`), and it cannot
set a per-instance environment. Launching `Balatro.exe` directly works because `steam_appid.txt` is in the game
directory. Steam still tracks the process as running app 2379780.

### Multiple instances

Run one launch per port. Each instance gets its own save dir, mod dir, Lovely logs, and bridge port:

```powershell
foreach ($p in 7777..7782) { powershell -NoProfile -ExecutionPolicy Bypass -File game_mod\windows\launch_instance.ps1 -Port $p }
```

```bash
BALATRO_RL_PORT=7778 python balatro_env/scripts/cli.py s   # drive a given instance
```

Two instances ran side by side, with separate runs and saves. Each used about 390 MB working set
(about 700 MB private) and 35–40% of one core while idle in a run, on a 16-thread CPU with an RTX 4070 Ti.

### Process management

```bash
tasklist -FI "IMAGENAME eq Balatro.exe"     # list instances
taskkill -F -PID <pid>                      # kill one instance (the launcher prints its PID)
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"name='Balatro.exe'\" | Select ProcessId,CommandLine"
```

Avoid `taskkill -IM Balatro.exe` while other agents run instances: it kills all of them.

### Layout and logs

```
%USERPROFILE%\balatro-instances\
├── template\Balatro\{settings.jkr, 1\}
└── 7777\Balatro\                       # APPDATA=...\7777 → LÖVE saves here
    ├── settings.jkr, 1\profile.jkr ...
    └── Mods\                            # --mod-dir
        ├── BalatroRLBridge\             # copied from the repo on every launch (main.lua, lovely.toml)
        └── lovely\log\, lovely\dump\    # per-instance Lovely log / patched source
```

---

## macOS Installation (Apple Silicon)

### Prerequisites

- macOS on Apple Silicon (M1/M2/M3/M4)
- Balatro installed via Steam
- Terminal access

### Step 1: Install Lovely Injector

#### 1.1 Download Lovely Injector

```bash
cd ~/Downloads

# Download the latest Apple Silicon release
curl -L -o lovely.tar.gz https://github.com/ethangreen-dev/lovely-injector/releases/latest/download/lovely-aarch64-apple-darwin.tar.gz

# Extract
tar -xzf lovely.tar.gz
```

#### 1.2 Install to Balatro Directory

```bash
cd ~/Library/Application\ Support/Steam/steamapps/common/Balatro

# Copy Lovely files
cp ~/Downloads/liblovely.dylib .
cp ~/Downloads/run_lovely_macos.sh .

# Make the launch script executable
chmod +x run_lovely_macos.sh
```

#### 1.3 Handle macOS Gatekeeper (if needed)

```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine liblovely.dylib

# Or allow in System Settings → Privacy & Security → "Allow Anyway"
```

### Step 2: Install the RL Bridge Mod (no Steamodded)

The bridge is Lovely-only; remove any `Steamodded` folder from the Mods dir (it changes game logic). Set
`BALATRO_RL_DATA_DIR` (data root; trajectories go to `$BALATRO_RL_DATA_DIR/trajectories/<date>/`) in the
environment that launches the game, or nothing is recorded.

```bash
mkdir -p ~/Library/Application\ Support/Balatro/Mods
# From the repo root
cp -r game_mod/BalatroRLBridge ~/Library/Application\ Support/Balatro/Mods/
```

### Step 4: Launch and Verify

**Important:** On macOS, launch via the shell script, not through Steam.

```bash
cd ~/Library/Application\ Support/Steam/steamapps/common/Balatro
./run_lovely_macos.sh
```

Test the bridge:
```bash
curl http://127.0.0.1:7777/health
```

### Directory Structure

```
~/Library/Application Support/Balatro/Mods/
└── BalatroRLBridge/
    ├── lovely.toml
    └── main.lua
```

---

## Troubleshooting

### Bridge not responding

1. Ensure the game is fully loaded (~15-20 seconds after launch)
2. Check for `[BalatroRLBridge] HTTP server started` in terminal/log output
3. Verify port 7777 is not already in use

### Port 7777 already in use

Choose another port with the `BALATRO_RL_PORT` environment variable (the bridge reads it at startup), or
on Windows run `launch_instance.ps1 -Port <port>`. `cli.py` reads the same variable; `BalatroClient` takes a `port=` argument.

### Mods not loading

1. The Lovely log must show `Applied 1 patch to 'main.lua'`; if not, check `BalatroRLBridge/lovely.toml` is in
   the mod dir Lovely reports (`Using mod directory at ...`)
2. Windows: ensure `version.dll` is in the Balatro install directory
3. macOS: ensure you launch via `./run_lovely_macos.sh`, not Steam

### Uninstalling

**Windows:**
```powershell
# Remove Lovely Injector
Remove-Item "C:\Program Files (x86)\Steam\steamapps\common\Balatro\version.dll"

# Remove harness instances and the Lovely mod dir (your saves in %APPDATA%\Balatro\<n> are untouched)
Remove-Item -Recurse "$env:USERPROFILE\balatro-instances"
Remove-Item -Recurse "$env:APPDATA\Balatro\Mods"
```

**macOS:**
```bash
rm ~/Library/Application\ Support/Steam/steamapps/common/Balatro/liblovely.dylib
rm ~/Library/Application\ Support/Steam/steamapps/common/Balatro/run_lovely_macos.sh
rm -rf ~/Library/Application\ Support/Balatro/Mods/
```

## Quick Reference

| Command | Purpose |
|---------|---------|
| `curl http://127.0.0.1:7777/health` | Test bridge connection |
| `curl http://127.0.0.1:7777/state` | Get current game state |
| `curl http://127.0.0.1:7777/legal` | Get legal actions |
| `curl -X POST -d '{"card_indices":[1,2]}' http://127.0.0.1:7777/preview` | Read-only hand preview |
