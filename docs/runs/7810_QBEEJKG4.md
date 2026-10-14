# Run QBEEJKG4 (port 7810, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind Big Blind (24542/37500)

Ante 1 (Skip/Rare/The Goad 600, $4): Small: disc to a T-high Straight draw, Straight 280 + Pair KK 60 = 340/300. Shop $5: Blue Joker{RENTAL} $1 (+2 chips per DECK card = ~+105 chips, only scorer) then Buffoon pack $4 -> holo Hologram (+10 mult from the edition, x1 growth) over eternal Sock and Buskin; $0. Big: one-card High Card 1144 (est exact). Goad: High Card AH 1144 vs 600.
Ante 2 (Negative/Holo/The Flint 2000, $7): shop passed Hanging Chad / eternal Baron $8 ($1 short). Skipped Small (Negative tag -> free negative Riff-raff{P,R}, refused as a 2nd rental). Big: Two Pair QQ77 1704/1500. Jumbo Standard -> JH (Hologram x1.25). Flint: Straight A-high 2340/2000.
Ante 3 (Ethereal/Negative/The Mouth 6400, $8): Jumbo Standard -> AC bonus (x1.5). Skipped Small for Ethereal tag -> Spectral pack -> Incantation (+4 cards, Hologram x2.5). Big: Pair 99 4095 + Pair AA 4095 = 8190/4800. Mouth: locked High Card (always repeatable) 3135+3052+3850 = 10037/6400.
Ante 4 (Boss tag/D6/The Eye 18000, $6, EMERGENCY 0.34): Riff-raff{PERISHABLE} $6 -> Splash + Wrathful (Small), Green Joker (Big). Splash makes every played card score (High Card with 5 cards ~5.7k). Small: Pair 4972 + Two Pair 4260 = 9232/9000. Big: Pair 8635 + Flush 6240 = 14875/13500. Sold Riff-raff (slots full) -> Uranus. Eye: Pair 8242 + Two Pair 8150 + Straight 7362 = 23754/18000.
Ante 5 (Handy/Voucher/The Serpent 50000, $2): shop nothing affordable. Skipped Small for Handy Tag (+$18, $20) and avoided rent. Big 37500: no pair after discards; Two Pair 9085 + Flush 6412 + Full House 9045 = 24542/37500. LOSS.

## Post-mortem

Binding constraint: scaling with zero money. Rent on Blue Joker (-$3 every round) plus Small Blinds paying $0 kept the wallet at -$5..$8 the entire run, so from ante 3 on I could not afford the 2nd xMult / Baron / Mystic Summit / Misprint / any pack I saw (Baron{E} $8 at ante 2 and Mystic Summit $5 at ante 3 were each $1-$4 short). The build ended as flat chips (Blue ~+115, Splash) and +mult (Wrathful, Green) times a single growth xMult (Hologram x2.5), ~8-10k per hand at ante 5 against 37.5k/3 = 12.5k needed.

Decisions I would change:
1. Ante 1: took Blue Joker and then the Buffoon pack ($4) leaving $0 (floor said keep $4). The Hologram pick was great, but Blue Joker's rent then ate $3 per round for the whole run. Sell Blue (or any flat rental) the first time a permanent chip source exists; I never found one and the rent starved every later shop. Better: pick it up knowing it must be sold by ante 3 and having a replacement plan.
2. Ante 2/3 shops: I never fed Hologram beyond one Standard card per shop (-$6 each); Standard packs are the only reliable feed and I stopped at $0-4. Hologram stayed x2.5 for 3 antes (it needs ~8 more cards for x4.5).
3. Ante 4: spent my last $3 on Uranus for the Eye instead of a Standard pack (+0.25 Hologram is +10% on every hand, Uranus only on one type); I could not afford the pack because I had sold Riff-raff for $3 and had $0 otherwise. Selling Splash/Green for $1-2 to reach $4 would not have helped.
4. Ante 5: skipped Small for Handy ($+18, no shop because shops only come after a played blind). Handy is worthless if the next two blinds cannot be cleared; a better line would have been to play the Small (25000 reachable with 2-3 hands) to get a shop, since the Handy money could not be spent before the Big.

Reusable rules (if-then):
- IF a Buffoon pack offers a holographic joker (+10 mult edition), THEN it is a first scorer by itself even if the joker is a growth xMult at x1: Hologram holo scored 1144 on a single card at ante 1 with Blue Joker's chips.
- IF you own Hologram, THEN every Incantation / Standard pack / Familiar-type card is +0.25 xMult; an Ethereal Tag at the Small Blind (free Spectral pack, Incantation +4 cards) took it from x1.5 to x2.5 and is worth the skip.
- IF you own Splash, THEN High Card/Pair with 5 cards scores every card (5 high-chip cards: High Card 5.7-8k vs 3.2k single), so keep playing 5 cards and let chips-per-card (Blue Joker, Scary Face) multiply; a pair-family type matters little.
- IF The Mouth is the boss, THEN lock High Card (any single card, with Splash any 5) rather than Pair: guaranteed repeat, 3 x 3.1k beat 6400.
- IF The Eye is the boss and you own Splash, THEN High Card is a 3rd distinct scoring type for free; I scored 23754/18000 with Pair, Two Pair, Straight.
- IF a rental (Blue Joker) is your only chip source, THEN count -$3 per round against every shop budget: it made every shop after ante 2 unaffordable. Sell it once 2 other scorers exist or accept being poor.
- IF the Small Blind tag is Handy Tag, THEN it pays $1 per hand played this run (+$18 at ante 5, hand ~18) immediately, but a shop only follows a PLAYED blind, so only skip with a Big you can clear.

Advisor/CLI defects:
- shopadvise ante 4: recommended Riff-raff $6 (SIM +0.49) correctly, but then `shopadvise` did not mention selling Riff-raff once slots were full (it makes nothing at 6/6); I had to infer it.
- `est` for Hologram+Splash hands was exact (8242, 8150, 7362, 6412), no defects.
- The Eye `advise` PACE line said "3 distinct hand types still needed" good; but did not suggest High Card with 5 Splash cards as a distinct type.
- Advise ranked a Standard Pack (+0.25 Hologram) at 60 but `SIM` ignores Hologram growth (shows 0 gain); Standard packs were never bought because floor/SIM said nothing, yet Hologram growth was the main scaling.
- Cash-out screen: money shown as negative (e.g. $-5) after rent before cash out; fine but confusing since SHOP then shows only the post-payout number.
