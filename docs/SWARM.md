# Swarm Runbook (Windows)

How the orchestrator runs N LLM player agents, each on its own Balatro instance, so every game becomes a valid
training trajectory (`docs/DATA_CONTRACT.md`). One-time machine setup (Lovely, instance template, venv) is in
`game_mod/install.md` (Windows section). Strategy and CLI rules for players are in `docs/PLAYBOOK.md`.

Shell notes: commands below are for Git Bash from the repo root unless marked PowerShell. The GitHub CLI (`gh`) is
not installed on this machine; nothing in the swarm needs it.

## 1. Ports and instances

- One port per player agent; one instance per port (~400 MB RAM each). Keep a table of `port -> agent id -> seed(s)`.
- Never reuse a port that another live agent owns, and never touch ports you didn't launch.
- Launch (also redeploys the repo's bridge into that instance):

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File game_mod/windows/launch_instance.ps1 -Port 7801
# -> "Balatro PID 12345 on port 7801 (save dir ...)"   <- record the PID
```

- Wait for the bridge (about 5 s), then check it:

```bash
for i in $(seq 1 30); do curl -s -m 2 http://127.0.0.1:7801/health && break; sleep 1; done
bash python/balatro_env/scripts/b.sh 7801 s
```

- Instances live in `%USERPROFILE%\balatro-instances\<port>`; the user's real saves in `%APPDATA%\Balatro` are never
  used. Every instance profile is fully unlocked/discovered (a requirement for valid data).
- Trajectories are written by the bridge to `data/trajectories/<YYYY-MM-DD>/<seed>_<port>_<unix_ms>.jsonl`
  (`BALATRO_RL_DATA_DIR`, default `<repo>/data`; gitignored).

## 2. Seeds

Every run starts from an assigned seed so it can be replayed. Never play a held-out evaluation seed.

- Held-out eval seeds: `python/balatro_env/data/eval_seeds.txt` (500 seeds; never give these to the swarm). Seeds
  starting with `FUZZ` are reserved for the fuzzer.
- Draw fresh swarm seeds (already excludes eval + `FUZZ*`):

```bash
python/.venv/Scripts/balatro-data seeds --count 20      # one seed per line
python/.venv/Scripts/balatro-data seeds --check 7K3P9QXA # exit 1 if reserved
```

- Give each agent its own list (one seed per run, including the next-stake run after a win). Never hand the same
  seed+deck+stake to two agents unless you deliberately want a duplicate.

## 3. Player-agent prompt template

Fill in `<PORT>`, `<AGENT_ID>`, `<MODEL>`, `<SEEDS>`, `<STAKE>`:

```text
You are a Balatro player agent. Your game instance is on port <PORT>; it is the only one you may touch.
1. Read docs/PLAYBOOK.md fully before acting. Follow its ground rules (section 0) exactly.
2. Control the game only through:  bash python/balatro_env/scripts/b.sh <PORT> <cmd> [args] --why "<reason>"
   Set these once per shell command: BALATRO_AGENT_ID=<AGENT_ID> BALATRO_AGENT_MODEL=<MODEL>
   (e.g.  BALATRO_AGENT_ID=<AGENT_ID> BALATRO_AGENT_MODEL=<MODEL> bash python/balatro_env/scripts/b.sh <PORT> s)
3. Every state-changing command needs --why '...' (one line, <=300 chars, concrete numbers). Use SINGLE quotes:
   inside double quotes bash expands "$6" to "" and silently corrupts the rationale. Use Git Bash, not WSL bash
   (WSL drops the BALATRO_AGENT_* variables). Every action you send is recorded as training data: no
   exploratory or test actions. s/hands/advise/shopadvise/legal/raw/sel are free.
4. Start with: b.sh <PORT> start Black Deck <STAKE> --seed <first seed> --why "assigned seed"
   Your seeds, in order (one per run; after a WIN use the next one at stake+1): <SEEDS>
5. Write your run log and post-mortem to docs/runs/<PORT>_<seed>.md (PLAYBOOK section 9).
6. Never run git, never kill/launch/restart processes, never edit files outside docs/runs/.
   If the CLI prints BRIDGE OFFLINE, or the state does not settle for 2 minutes, write your log and stop.
```

## 4. Between runs (orchestrator)

From the repo root, after an agent finishes a run (`GAME_OVER` or win):

```bash
D=python/.venv/Scripts/balatro-data
$D validate data/trajectories/<date>/<file>.jsonl     # schema + legality; exit 1 on error
$D compress                                           # gzip every ended *.jsonl (skips files still being written)
$D manifest                                           # rebuild data/manifest.jsonl (keeps prior replay_ok)
$D replay data/trajectories/<date>/<file>.jsonl.gz --port <idle port> --update-manifest
```

- `replay` needs an instance that no agent is using (launch a spare port for it). It prints `REPLAY_OK` or the first
  diverging step with a JSON diff. Only manifest rows with `schema_ok && replay_ok` feed training.
- Read the agent's `docs/runs/<port>_<seed>.md` post-mortem; fold verified lessons into PLAYBOOK strategy sections.
- `reject` lines in a trajectory mean the bridge refused an action. A few are fine; many from one agent mean its
  prompt or the CLI needs fixing.

Unattended alternative (run as long-lived services; the replay port must not belong to any player):

```bash
python/.venv/Scripts/python -m balatro_env.data dataops --replay-port 7820 --headless-workers 3 --interval 300   # compress/validate/manifest/replay (headless + live spot-check)/status -> data/dataops.log
python/.venv/Scripts/balatro-data dashboard --port 8765                       # http://127.0.0.1:8765/
python/.venv/Scripts/balatro-data status --print                              # one-off refresh of docs/SWARM_STATUS.md
```

## 5. Crash handling

A crashed instance can keep its process alive while the bridge is gone. Check both:

```bash
curl -s -m 3 http://127.0.0.1:<port>/health || echo OFFLINE
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"name='Balatro.exe'\" | Select ProcessId,CommandLine | Format-List"
```

The command line contains `--mod-dir ...\balatro-instances\<port>\Balatro\Mods`, which identifies the port's PID.
If the bridge is offline for more than ~10 s:

1. Read the instance's newest Lovely log for the error:
   `%USERPROFILE%\balatro-instances\<port>\Balatro\Mods\lovely\log\` (grep `ERROR`).
2. Kill that instance only, by PID (never by image name: `taskkill -IM Balatro.exe` kills every agent's game):
   `taskkill -F -PID <pid>`
3. Relaunch the same port with the launcher. The interrupted trajectory stays incomplete (no `end` line);
   `manifest` marks it invalid. Start the agent on its next seed rather than continuing.

## 6. Shutdown

Kill each instance you launched by PID (`taskkill -F -PID <pid>`), then run `compress` and `manifest`.
