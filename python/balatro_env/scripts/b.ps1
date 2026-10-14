# Swarm wrapper for cli.py (PowerShell): b.ps1 <port> <cmd> [args...] [--why "one-line rationale"]
#   powershell -NoProfile -File python\balatro_env\scripts\b.ps1 7778 s
#   powershell -NoProfile -File python\balatro_env\scripts\b.ps1 7778 blind --why "Small Blind, tag not worth a skip"
# Agent identity for the trajectory meta comes from BALATRO_AGENT_ID / BALATRO_AGENT_MODEL (default agent: port-<port>).
if ($args.Count -lt 1 -or "$($args[0])" -notmatch '^\d+$') {
    Write-Error 'usage: b.ps1 <port> <cmd> [args...] [--why "..."]'
    exit 1
}
$root = Resolve-Path (Join-Path $PSScriptRoot '..\..\..')
$env:BALATRO_RL_PORT = "$($args[0])"
$env:PYTHONIOENCODING = 'utf-8'
$rest = @($args | Select-Object -Skip 1)
& (Join-Path $root 'python\.venv\Scripts\python.exe') (Join-Path $PSScriptRoot 'cli.py') @rest
exit $LASTEXITCODE
