# Run YNCL1ZEH (port 7808, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind The Fish (48177/50000)

Ante 1 (D6/Economy/The Window 600, $4): Small flush AD KD QD 9D 4D 316 (one hand). Shop: Buffoon pack -> Shoot the Moon (+13 mult per Queen HELD, the run engine). Big: Pair 55 with QH QD held 560. Shop $8: Sly{RENTAL} $1 (+50 chips, sold at ante 4). Window: Pair 22 960.
Ante 2 (Standard/Economy/The Head 2000, $11): foil Riff-raff $8 (2 commons per blind with free slots: Credit Card, Even Steven, 8 Ball, Delayed Gratification). Small 2P 1460, Big Pair 22 4104, Head Pair 66 1220 + 2P TT44 1340.
Ante 3 (Buffoon/Juggle/The Manacle 6400, $14): bought Hanging Chad (sold Credit Card). Skipped Small for the Buffoon tag: pack was junk (Ride the Bus, eternal Wily/To the Moon, perishable rental Joker) = a wasted skip. Big Pair AA 2310 + TT 6600, Manacle Pair 55/66/44 = 1950+4154+3906.
Ante 4 (Coupon/Handy/The House 18000, $18): EMERGENCY ratio 0.28 with 0 xMult. Sold Delayed Grat -> Supernova; Arcana -> Judgement (sold Sly for slot) -> Abstract Joker; sold Riff-raff -> foil Misprint from Jumbo Buffoon; sold Supernova -> foil Gros Michel; Mercury (Pair L2). Small FH KKK66 7488 + High 3015; Big Flush 7622 + Flush 7350; House: disc facedown, High TC 9450 + Pair 88 12010 (QC held).
Ante 5 (Standard/Orbital/The Fish 50000, $10): Mercury x3 (Pair L4 55x5). Small: Pair 66 10578 + FH JJJ22 11481 + FH 8293 = 25k+ (cleared with last hand). Sold Even Steven -> Banner (+30 chips per unused discard); Arcana -> Death (AH->QH, 5 Queens). Big: Pair JJ 14640, Pair 44 15120, High AS 14157 (QH QD held). Fish 50000: Pair KK 15810 + facedown play 14742 + facedown play 17625 = 48177. LOST by 1823.

## Post-mortem

Binding constraint: scaling. 0 xMult all run (never saw a reliable one; Shoot the Moon + flat adds topped out ~15k/hand at ante 5 vs 16.7k/hand needed for the boss). Lost by 3.6%.

Decisions I would change:
1. Ante 3 Small skip for the Buffoon tag (B ~ boss/2 borderline, 0 xMult): the Jumbo pack held nothing usable and I lost a shop visit (~$7-10 + planet). Should have played the Small.
2. Ante 4-5: spent ~$20 on Celestial packs/Mercury and Arcana for +1 Pair level each; fine, but I never reached the reroll hunt for xMult because money stayed $0-10 (Sly rental rent + Riff-raff $8 bought at ante 2 cost my ante-2/3 interest). A Gold run without any xMult by ante 4 is a coin flip at ante 5.
3. Fish final hand: I sold nothing/held $1; could have sold Banner/Hanging Chad is wrong, but I could have used the 2 discards BEFORE the first Fish play (face-up draws) to set up Queens; I judged Banner (-30 chips/discard ~ -2k/hand) too expensive. In hindsight 1823 short = one more held Queen (+~2.7k); a discard digging for a Queen would have been about break-even.

Reusable rules (if-then):
- IF you own Shoot the Moon (+13 mult per Queen HELD), THEN play pairs/high cards of non-Queen ranks and keep Queens in hand: a single held Queen is worth ~+2.7k per hand at ante 5; use Death/Strength on the rank to add Queens (Death: left selected card becomes a copy of the RIGHT one; AH->QH worked with targets 1 2).
- IF a hand contains a Queen and the hand type is irrelevant, THEN a 1-card High Card with 2 Queens held scored 14k at ante 5; the Pair/FH levels matter less than Queens held.
- IF Banner (+30 chips per unused discard) is owned, THEN each discard costs ~30 chips x mult on every later hand: do not discard unless the draw is >60% to improve; Banner + 2 unused discards was worth ~+3k/hand.
- IF The Fish/House cards are face down, THEN the hand display is sorted by rank descending: positions give rank bounds (top 3 cards were Q/K/A), so hold the top cards (Queens for Shoot the Moon) and play the low bound cards as a likely pair.
- IF Riff-raff is owned and slots are full, THEN it only gives +50 chips (foil); sell it when a real scorer (Misprint foil) needs the slot.
- IF EMERGENCY (ratio <0.35) at ante 4 with 0 xMult, THEN Judgement/Buffoon packs with a sold flat joker gave +mult (Abstract +18, Gros Michel +15): worth it, but flat +mult alone cleared ante 4 and fell 4% short at ante 5.

Advisor/CLI defects:
- shopadvise/advise commands took 30-120 s each under swarm load (backgrounded); no content defect.
- advise at ante 5 Fish: "PACE ... discard toward a bigger hand" ignored that each discard costs Banner chips (the SOLVER p 0.00-0.22 for all lines).
- Pack advice ranked Wily Joker{ETERNAL} as the ADVICE pick in the junk Buffoon pack (SIM +0.06, 'sell Delayed Gratification'): an eternal conditional trips joker is a bad pick; I skipped.
