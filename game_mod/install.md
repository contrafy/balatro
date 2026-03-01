# Balatro RL Bridge - Installation Guide

This guide walks you through setting up the Balatro RL harness mod on **Windows** and **macOS**.

---

## Windows Installation

### Prerequisites

- Windows 10 or later
- Balatro installed via Steam
- Git (for Steamodded)

### Step 1: Install Lovely Injector

1. Download the latest Windows release from [lovely-injector releases](https://github.com/ethangreen-dev/lovely-injector/releases/latest) — you need `lovely-x86_64-pc-windows-msvc.zip`
2. Extract `version.dll` from the zip
3. Copy `version.dll` to your Balatro install directory:
   ```
   C:\Program Files (x86)\Steam\steamapps\common\Balatro\
   ```

Lovely hooks in automatically when Balatro launches via Steam — no special launch script needed.

### Step 2: Install Steamodded

```powershell
# Create mods directory
mkdir "$env:APPDATA\Balatro\Mods" -Force

# Clone Steamodded
cd "$env:APPDATA\Balatro\Mods"
git clone https://github.com/Steamodded/smods.git Steamodded
```

### Step 3: Install the RL Bridge Mod

From this repository, copy the mod folder:

```powershell
# From the repo root
Copy-Item -Recurse game_mod\BalatroRLBridge "$env:APPDATA\Balatro\Mods\BalatroRLBridge"
```

### Step 4: Launch and Verify

1. Launch Balatro through Steam (Lovely hooks in via `version.dll`)
2. Wait ~15-20 seconds for the game to fully load
3. Test the bridge:
   ```powershell
   curl http://127.0.0.1:7777/health
   ```
   Expected: `{"status":"ok","version":"1.0.0","uptime_ms":...}`

### Directory Structure

```
%APPDATA%\Balatro\Mods\
├── Steamodded\
│   ├── mod.json
│   └── ...
└── BalatroRLBridge\
    ├── mod.json
    └── main.lua
```

### Logs

- Lovely logs: `%APPDATA%\Balatro\Mods\lovely\log\`
- Lovely dump (patched game source): `%APPDATA%\Balatro\Mods\lovely\dump\`

### Deploying Mod Changes (Development)

When editing `main.lua` during development:
```powershell
Copy-Item game_mod\BalatroRLBridge\main.lua "$env:APPDATA\Balatro\Mods\BalatroRLBridge\main.lua"
```
Then kill and relaunch the game for changes to take effect.

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

### Step 2: Install Steamodded

```bash
mkdir -p ~/Library/Application\ Support/Balatro/Mods
cd ~/Library/Application\ Support/Balatro/Mods
git clone https://github.com/Steamodded/smods.git Steamodded
```

### Step 3: Install the RL Bridge Mod

```bash
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
├── Steamodded/
│   ├── mod.json
│   └── ...
└── BalatroRLBridge/
    ├── mod.json
    └── main.lua
```

---

## Troubleshooting

### Bridge not responding

1. Ensure the game is fully loaded (~15-20 seconds after launch)
2. Check for `[BalatroRLBridge] HTTP server started` in terminal/log output
3. Verify port 7777 is not already in use

### Port 7777 already in use

Edit `main.lua` in the BalatroRLBridge mod and change the port:

```lua
local CONFIG = {
    port = 7778,  -- Change this
    ...
}
```

### Mods not loading

1. Verify Steamodded is in the Mods folder with a valid `mod.json`
2. Windows: ensure `version.dll` is in the Balatro install directory
3. macOS: ensure you launch via `./run_lovely_macos.sh`, not Steam
4. Press `M` or `Alt+F5` in-game to open the mod manager and verify mods appear

### Uninstalling

**Windows:**
```powershell
# Remove Lovely Injector
Remove-Item "C:\Program Files (x86)\Steam\steamapps\common\Balatro\version.dll"

# Remove mods
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
| Press `M` in-game | Open mod manager |
