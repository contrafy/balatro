# Balatro RL Bridge - macOS Installation Guide

This guide walks you through setting up the Balatro RL harness mod on macOS (Apple Silicon M1/M2/M3).

## Prerequisites

- macOS on Apple Silicon (M1/M2/M3)
- Balatro installed via Steam
- Terminal access

## Step 1: Install Lovely Injector

Lovely Injector is the runtime Lua injector that allows us to run custom code inside Balatro.

### 1.1 Download Lovely Injector

```bash
# Create a temporary directory for downloads
cd ~/Downloads

# Download the latest Apple Silicon release
curl -L -o lovely.tar.gz https://github.com/ethangreen-dev/lovely-injector/releases/latest/download/lovely-aarch64-apple-darwin.tar.gz

# Extract
tar -xzf lovely.tar.gz
```

### 1.2 Install to Balatro Directory

```bash
# Navigate to your Balatro installation
cd ~/Library/Application\ Support/Steam/steamapps/common/Balatro

# Copy Lovely files
cp ~/Downloads/liblovely.dylib .
cp ~/Downloads/run_lovely_macos.sh .

# Make the launch script executable
chmod +x run_lovely_macos.sh
```

### 1.3 Handle macOS Gatekeeper (if needed)

If macOS blocks the library, you'll need to allow it:

```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine liblovely.dylib

# Or allow in System Settings:
# System Settings → Privacy & Security → scroll down to Security
# Look for "liblovely.dylib was blocked" and click "Allow Anyway"
```

## Step 2: Install Steamodded (Mod Framework)

Steamodded provides the modding framework infrastructure.

### 2.1 Create Mods Directory

```bash
mkdir -p ~/Library/Application\ Support/Balatro/Mods
```

### 2.2 Download Steamodded

```bash
cd ~/Library/Application\ Support/Balatro/Mods

# Clone Steamodded
git clone https://github.com/Steamodded/smods.git Steamodded

# Or download and extract manually from:
# https://github.com/Steamodded/smods/releases
```

## Step 3: Install the RL Bridge Mod

### 3.1 Copy the Bridge Mod

From this repository, copy the mod to your Balatro mods folder:

```bash
# From the repo root
cp -r game_mod/BalatroRLBridge ~/Library/Application\ Support/Balatro/Mods/
```

### 3.2 Verify Directory Structure

Your mods folder should look like:

```
~/Library/Application Support/Balatro/Mods/
├── Steamodded/
│   ├── mod.json
│   └── ...
└── BalatroRLBridge/
    ├── mod.json
    └── main.lua
```

## Step 4: Launch Balatro with Mods

**Important:** On macOS, you must launch via the shell script, not through Steam.

```bash
cd ~/Library/Application\ Support/Steam/steamapps/common/Balatro
./run_lovely_macos.sh
```

### First Launch Verification

1. Launch the game using the command above
2. Press `M` or `Alt+F5` to open the mod manager
3. Verify you see both "Steamodded" and "BalatroRLBridge" in the list
4. Check the terminal - you should see log output including:
   ```
   [BalatroRLBridge] HTTP server starting on 127.0.0.1:7777
   ```

### Test the Bridge

Open a new terminal and test the health endpoint:

```bash
curl http://127.0.0.1:7777/health
```

Expected response:
```json
{"status":"ok","version":"1.0.0","uptime_ms":12345}
```

## Troubleshooting

### "liblovely.dylib" cannot be opened

1. Go to **System Settings → Privacy & Security**
2. Scroll down to the Security section
3. Click "Allow Anyway" next to the blocked file message
4. Try launching again and click "Open" when prompted

### Mods not loading

1. Ensure Steamodded is installed in the Mods folder
2. Check that mod.json files are valid JSON
3. Look at terminal output for error messages
4. Verify you're launching via `./run_lovely_macos.sh`, not Steam

### Port 7777 already in use

Edit `main.lua` in the BalatroRLBridge mod and change the port:

```lua
local CONFIG = {
    port = 7778,  -- Change this
    ...
}
```

### Game freezes when connecting

The HTTP server uses non-blocking sockets. If the game freezes:
1. The socket library may not be loading correctly
2. Check terminal for "socket" related errors
3. Ensure Lovely Injector is properly installed

## Uninstalling

To remove the modding setup:

```bash
# Remove Lovely Injector
rm ~/Library/Application\ Support/Steam/steamapps/common/Balatro/liblovely.dylib
rm ~/Library/Application\ Support/Steam/steamapps/common/Balatro/run_lovely_macos.sh

# Remove mods
rm -rf ~/Library/Application\ Support/Balatro/Mods/

# Game will run vanilla when launched through Steam
```

## Quick Reference

| Command | Purpose |
|---------|---------|
| `./run_lovely_macos.sh` | Launch modded Balatro |
| `curl http://127.0.0.1:7777/health` | Test bridge connection |
| `curl http://127.0.0.1:7777/state` | Get current game state |
| `curl http://127.0.0.1:7777/legal` | Get legal actions |
| Press `M` in-game | Open mod manager |
