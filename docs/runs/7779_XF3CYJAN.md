# Run XF3CYJAN (port 7779) - LOSS at ante 1, Big Blind

Deck: Black Deck, Stake: White (1). Started fresh after bridge restart (unlocked all jokers/decks); prior run 4SPXA6NF
was healthy (won ante 1 comfortably) but lost to the restart, not a game loss - see docs/runs/7779_4SPXA6NF.md.

Ante 1: blind select - Small tag=Polychrome Tag, Big tag=Economy Tag, Boss=The Goad 600 (a suit debuffed).
Small (need 300): no jokers, played FULLHOUSE TTTQQ est360 actual360 (1 hand, 0 discards used). Won.
Shop ($9): shopadvise recommended buy Rocket ($6, econ +$1/round). Overrode per playbook section 5 ante1-2 rule
  ("buy the FIRST affordable joker that adds mult/chips... two by end of ante2") since Rocket is pure economy with
  zero ante-1 scoring impact and we had 0 jokers. Bought Buffoon Pack ($4) instead; pack offered only Ceremonial
  Dagger and Fortune Teller (both scaling/utility, no direct +mult/+chips option existed in this shop at all).
  Picked Ceremonial Dagger (destroys joker to right at blind start, gains 2x its sell value as mult) for long-run
  scaling potential. Money after: $5, too low for Rocket ($6); endshop.
Big Blind (need 450): only had Ceremonial Dagger (zero score effect while it's the only joker - nothing to its
  right to sacrifice). Used both discards chasing two-pair upgrades (T-pair -> T6 two pair -> best draw was still
  two pair), ran out of discards with best available Two Pair est 104 (need 450). Played 3 forced hands with
  filler cards: TWOPAIR T6 (scored 104), TWOPAIR 62 (scored 72, cum 176), PAIR Q (scored 60, cum 236). All three
  `est` values matched actual scored deltas exactly (0% deviation). Final: 236/450. LOST -> GAME_OVER.

Post-mortem: binding constraint = misplay/luck combo. No +mult/+chips joker was ever offered in the ante-1 shop
(Buffoon Pack only contained scaling jokers with no immediate payoff), so Big Blind had to be cleared on bare
card value alone; the deal never produced a third pair or better after the first Full House used up the good
cards. This looks like an unwinnable draw given the shop RNG, not a clear misplay - but the one decision I would
reconsider: with 0 jokers and $9, going for Buffoon Pack (a gamble on pack contents) instead of saving toward a
guaranteed scoring joker later, or rerolling once ($5) to see if a flat +mult joker appeared, may have been worse
than expected value suggested. No `est` vs actual mismatch >20% occurred this run (all hands matched exactly).

Bridge issues: mid-run-planning (previous run 4SPXA6NF) the bridge was intentionally restarted by the orchestrator
to deploy an unlock update; `s` returned `[SPLASH]` with empty `Legal:` for several minutes after restart while
`raw` already reported `"phase": "MENU"` - worth noting `raw` may reflect the true phase before `s` catches up
after a restart. No `ACTION FAILED` or other errors occurred during actual play.

Playbook suggestions:
1. Section 5 ante1-2: add explicit guidance for when a Buffoon Pack's contents (once opened) contain no direct
   +mult/+chips joker - state whether to still take a scaling joker (as I did) or whether econ (Rocket/Credit
   Card) would have been the better prior. Current text assumes packs will contain a scoring joker; not always true.
2. Consider a rule: reserve at least 1 discard for the final hand of Small/Big blind (not just boss) when no
   jokers are owned yet, so the last hand isn't forced blind - though in this run more discards weren't the
   bottleneck (the deal itself never produced better than two pair after the Full House).
