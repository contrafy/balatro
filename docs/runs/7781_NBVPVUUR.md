# Run NBVPVUUR (port 7781) - IN PROGRESS

Bridge issue: first `start Black Deck` produced run 9DYK1589 but `G.GAME.blind_on_deck` stayed nil through
3 retries of `blind` plus ~15s of sleeps (state showed "Blinds (on deck None)" and SELECT_BLIND kept failing
with "blind_on_deck not set yet, retry"). Re-issued `start Black Deck` per known workaround (see run
7784_8FC3SMNC.md) - fixed immediately, but discarded 9DYK1589 before a single blind was played and produced
this new run_id NBVPVUUR. No log entry needed for 9DYK1589 since nothing happened in it.

Ante 1: Small 300 tag Boss Tag, Big 450 tag Economy Tag, Boss The Pillar (600, cards played earlier this ante
get debuffed at boss) - keep Small/Big card usage minimal/non-engine per playbook section 6.
- Small Blind (300): advise -> discarded 1 4 5 8 (kept Two Pair QQ55 base), redrew into FULL HOUSE QQQ55, advise
  said PLAY FULLHOUSE 2 3 4 6 7 est320 >= need 300. Issued `play FULLHOUSE 2 3 4 6 7`. CLI printed
  "Playing Full House ... est 320" and "ok: Hand played", then the CLI process crashed with a Python traceback
  (ConnectionRefusedError / ConnectionError contacting 127.0.0.1:7781/state) while polling the follow-up state.
  Bridge has been unreachable (Connection refused) on every subsequent `s` call, ~60+ seconds of retries so far.
  Per instructions this instance's process is never to be killed/restarted by me; polling in background until it
  recovers. Unclear whether the Full House hand actually resolved server-side before the crash (CLI said
  "ok: Hand played" before losing the connection, so likely committed) - will verify via `s`/`raw` once reachable.
- Bridge still unreachable after ~5 minutes of polling (60 attempts x 5s) following the Full House play above.
  Started a second, longer background poll (90 attempts x 5s, ~7.5min) rather than restarting the process myself
  (explicitly forbidden by task instructions). Will keep waiting/escalating in poll duration if needed.

RUN ABORTED (not a loss): bridge reconnected after ~115s but game state was [SPLASH] (fresh boot) - the
coordinator confirmed this instance's process was killed by another agent's restart, unrelated to any action
taken here. The Full House QQQ55 play against Small Blind (300) had been submitted successfully ("ok: Hand
played" printed before the connection dropped) but the whole run state was lost with the process, so we never
learned whether it would have won ante 1. No post-mortem applies since this was an external process kill, not
gameplay. Continuing with a fresh run: see 7781_DERK8VD7.md.
