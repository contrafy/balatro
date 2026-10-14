"""Orchestrator bookkeeping for the LLM player swarm (state in data/swarm_state.json).

  swarm_ctl.py next <port> <tier>     ensure the port's instance is healthy, assign a fresh seed, print the task spec
  swarm_ctl.py result '<json>'        record a finished player's JSON result (needs "port" and "seed")
  swarm_ctl.py summary                per-tier outcomes so far
"""

import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
STATE = REPO / "data" / "swarm_state.json"
RESULTS = REPO / "data" / "swarm_results.jsonl"
MODEL_ID = {"fable": "claude-fable-5-1", "opus": "claude-opus-5-5", "sonnet": "claude-sonnet-5-5", "haiku": "claude-haiku-5-5"}


def load():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"used_seeds": [], "ports": {}}


def save(s):
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(s, indent=1))
    tmp.replace(STATE)


def healthy(port):
    try:
        return json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=3)).get("status") == "ok"
    except Exception:
        return False


def find_pid(port):
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "Get-CimInstance Win32_Process -Filter \"name='Balatro.exe'\" | ForEach-Object { \"$($_.ProcessId) $($_.CommandLine)\" }"],
                         capture_output=True, text=True).stdout
    for line in out.splitlines():
        if f"balatro-instances\\{port}\\" in line:
            return int(line.split()[0])
    return None


def ensure_instance(port):
    if healthy(port):
        return "ok"
    pid = find_pid(port)
    if pid:
        subprocess.run(["taskkill", "-F", "-PID", str(pid)], capture_output=True)
        time.sleep(2)
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                    str(REPO / "game_mod" / "windows" / "launch_instance.ps1"), "-Port", str(port)], capture_output=True)
    for _ in range(30):
        if healthy(port):
            return "relaunched"
        time.sleep(1)
    return "FAILED"


def fresh_seed(s):
    exe = REPO / "python" / ".venv" / "Scripts" / "python.exe"
    n = len(s["used_seeds"]) + 20
    seeds = subprocess.run([str(exe), "-m", "balatro_env.data", "seeds", "--count", str(n)], capture_output=True, text=True, cwd=REPO).stdout.split()
    used = set(s["used_seeds"])
    for sd in seeds:
        if sd not in used:
            return sd
    raise SystemExit("no fresh seed")


def cmd_next(port, tier):
    s = load()
    inst = ensure_instance(port)
    seed = fresh_seed(s)
    s["used_seeds"].append(seed)
    runs = s["ports"].setdefault(str(port), {"runs": []})["runs"]
    n = len(runs) + 1
    aid = f"{tier}-{port}-r{n}"
    runs.append({"seed": seed, "tier": tier, "agent_id": aid, "started": time.strftime("%Y-%m-%d %H:%M")})
    save(s)
    print(json.dumps({"instance": inst, "agent": f"balatro-player-{tier}", "name": f"P{port}{tier.capitalize()}R{n}",
                      "task": f"PORT={port}\nAGENT_ID={aid}\nMODEL={MODEL_ID[tier]}\nSEED={seed}\nPlay one recorded Black Deck Gold Stake (8) run on port {port} with seed {seed}. The instance is already running."}))


def cmd_result(raw):
    r = json.loads(raw)
    r.setdefault("finished", time.strftime("%Y-%m-%d %H:%M"))
    with RESULTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(r) + "\n")
    print("recorded", r.get("port"), r.get("seed"), r.get("outcome"), r.get("ante"))


def cmd_summary():
    rows = [json.loads(l) for l in RESULTS.read_text(encoding="utf-8").splitlines() if l.strip()] if RESULTS.exists() else []
    agg = {}
    for r in rows:
        m = r.get("model", "?")
        a = agg.setdefault(m, {"runs": 0, "wins": 0, "antes": []})
        a["runs"] += 1
        a["wins"] += r.get("outcome") == "win"
        if isinstance(r.get("ante"), int):
            a["antes"].append(r["ante"])
    for m, a in agg.items():
        ant = a["antes"]
        print(f"{m}: runs {a['runs']} wins {a['wins']} mean ante {sum(ant) / max(len(ant), 1):.2f} max {max(ant, default=0)}")


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "next":
        cmd_next(int(sys.argv[2]), sys.argv[3])
    elif c == "result":
        cmd_result(sys.argv[2])
    elif c == "summary":
        cmd_summary()
