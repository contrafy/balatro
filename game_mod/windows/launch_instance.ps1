# Launch an isolated Balatro instance with the RL bridge on its own port (Windows, Lovely only).
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File game_mod\windows\launch_instance.ps1 -Port 7777
#
# Each instance lives in <Root>\<Port>: LOVE saves to %APPDATA%\Balatro, so the instance gets
# APPDATA=<Root>\<Port>; Lovely ignores APPDATA, so its mod dir is passed with --mod-dir.
# A new instance is seeded from <Root>\template\Balatro (settings.jkr + profile) when present.
# The instance's Mods dir holds only BalatroRLBridge (copied from the repo on every launch: this is the
# deploy step) and Lovely's own lovely\ dir; anything else (e.g. a leftover Steamodded) is removed so
# game logic stays vanilla.
param(
    [Parameter(Mandatory = $true)][int]$Port,
    [string]$Root = (Join-Path $env:USERPROFILE 'balatro-instances'),
    [string]$GameDir = 'C:\Program Files (x86)\Steam\steamapps\common\Balatro',
    [string]$DataDir = '',
    # Test-only: enables POST /debug/eval (taints any trajectory it touches). Never for data collection.
    [switch]$DebugEval
)
$ErrorActionPreference = 'Stop'

$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$instance = Join-Path $Root $Port
$saveDir = Join-Path $instance 'Balatro'
$modDir = Join-Path $saveDir 'Mods'
if (-not (Test-Path $saveDir)) {
    New-Item -ItemType Directory -Force $instance | Out-Null
    $template = Join-Path $Root 'template\Balatro'
    if (Test-Path $template) {
        Copy-Item -Recurse $template $saveDir
    } else {
        New-Item -ItemType Directory -Force $saveDir | Out-Null
    }
}
New-Item -ItemType Directory -Force $modDir | Out-Null

# Lovely-only: keep just the bridge and Lovely's log/dump dir
Get-ChildItem $modDir -Force | Where-Object { $_.Name -ne 'lovely' -and $_.Name -ne 'BalatroRLBridge' } |
    ForEach-Object { Remove-Item -Recurse -Force $_.FullName }

$bridgeSrc = Join-Path $repo 'game_mod\BalatroRLBridge'
$bridgeDst = Join-Path $modDir 'BalatroRLBridge'
if (Test-Path $bridgeDst) { Remove-Item -Recurse -Force $bridgeDst }
Copy-Item -Recurse $bridgeSrc $bridgeDst

if (-not $DataDir) { $DataDir = Join-Path $repo 'data' }
New-Item -ItemType Directory -Force $DataDir | Out-Null

$gitSha = 'unknown'
try {
    $sha = (& git -C $repo rev-parse HEAD 2>$null)
    if ($LASTEXITCODE -eq 0 -and $sha) {
        $gitSha = $sha.Trim()
        $dirty = (& git -C $repo status --porcelain 2>$null)
        if ($dirty) { $gitSha = "$gitSha-dirty" }
    }
} catch { }

$env:APPDATA = $instance
$env:BALATRO_RL_PORT = "$Port"
$env:BALATRO_RL_DATA_DIR = $DataDir
$env:BALATRO_RL_GIT_SHA = $gitSha
$env:BALATRO_RL_BRIDGE_DIR = $bridgeDst
$env:BALATRO_RL_DEBUG = if ($DebugEval) { '1' } else { '' }
$p = Start-Process -FilePath (Join-Path $GameDir 'Balatro.exe') -WorkingDirectory $GameDir `
    -ArgumentList @('--mod-dir', "`"$modDir`"") -PassThru
# Many instances run at once: keep them below the desktop so the machine stays responsive.
try { $p.PriorityClass = 'BelowNormal' } catch { }
"Balatro PID $($p.Id) on port $Port (save dir $saveDir, data dir $DataDir, git $gitSha)"
