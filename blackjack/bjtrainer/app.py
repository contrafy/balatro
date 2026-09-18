"""The trainer itself: menu and screens."""

from __future__ import annotations

import curses
import random

from . import ui
from .cards import Card, Hand, Shoe
from .config import Settings
from .counting import (
    SYSTEMS,
    Counter,
    bet_units,
    counting_action,
    should_insure,
)
from .drills import Scenario, dealt_scenario, deviation_scenario, weighted_scenario
from .game import DEALER, DONE, INSURANCE, PLAYER, Round
from .stats import Stats
from .strategy import (
    ACTION_NAMES,
    CODE_NAMES,
    DOUBLE,
    HIT,
    SPLIT,
    STAND,
    SURRENDER,
    UP_LABELS,
    chart_code,
    chart_rows,
    legality,
    upcard_index,
)

ACTION_KEYS = {"h": HIT, "s": STAND, "d": DOUBLE, "p": SPLIT, "r": SURRENDER}


class App:
    def __init__(self, stdscr) -> None:
        self.scr = stdscr
        self.theme = ui.make_theme()
        self.settings = Settings.load()
        self.stats = Stats.load()
        self.rng = random.Random()
        curses.curs_set(0)
        stdscr.keypad(True)

    # -- chrome ------------------------------------------------------------
    def header(self, title: str, right: str = "") -> None:
        _, w = self.scr.getmaxyx()
        ui.safe_addstr(self.scr, 0, 2, title.upper(), self.theme.title)
        if right:
            ui.safe_addstr(self.scr, 0, max(2, w - len(right) - 2), right, self.theme.dim)
        ui.hline(self.scr, 1, 1, w - 2, self.theme)

    def wait_key(self, timeout: int | None = None) -> int:
        self.scr.timeout(-1 if timeout is None else timeout)
        return self.scr.getch()

    def message(self, y: int, text: str, attr: int = 0) -> None:
        ui.safe_addstr(self.scr, y, 4, text, attr)

    # -- main loop ---------------------------------------------------------
    def run(self) -> None:
        items = [
            ("1", "Basic strategy drill", "Hands one at a time, instant feedback.",
             self.basic_drill),
            ("2", "Count drill", "Cards flash by; call the running and true count.",
             self.count_drill),
            ("3", "Deviation drill", "The Illustrious 18 and Fab 4 index plays.",
             self.deviation_drill),
            ("4", "Play a shoe", "Real hands, real count, bet sizing, bankroll.",
             self.play_shoe),
            ("5", "Strategy chart", "The whole chart, colour coded.", self.chart_screen),
            ("6", "Stats", "What you keep getting wrong.", self.stats_screen),
            ("7", "Settings", "Rules, count system, drill behaviour.",
             self.settings_screen),
        ]
        selected = 0
        while True:
            if ui.too_small(self.scr, self.theme):
                if self.wait_key() == ord("q"):
                    return
                continue
            self.scr.erase()
            self.header("Blackjack trainer", self.settings.rules.label)
            _, w = self.scr.getmaxyx()
            ui.center(self.scr, 3, "Perfect strategy and card counting, offline.",
                      self.theme.dim)

            top = 5
            for i, (key, label, blurb, _) in enumerate(items):
                attr = self.theme.accent if i == selected else 0
                marker = ">" if i == selected else " "
                ui.safe_addstr(self.scr, top + i * 2, 6,
                               f"{marker} {key}  {label}", attr | curses.A_BOLD)
                ui.safe_addstr(self.scr, top + i * 2, 6 + 28, blurb, self.theme.dim)

            h, _ = self.scr.getmaxyx()
            ui.safe_addstr(self.scr, h - 3, 6,
                           f"Counting with {self.settings.count_system.name}"
                           f"  ·  index plays "
                           f"{'on' if self.settings.use_deviations else 'off'}"
                           if self.theme.unicode else
                           f"Counting with {self.settings.count_system.name}",
                           self.theme.dim)
            ui.footer(self.scr, [("1-7/enter", "choose"), ("up/down", "move"),
                                 ("q", "quit")], self.theme)
            self.scr.refresh()

            key = self.wait_key()
            if key in (ord("q"), 27):
                return
            if key in (curses.KEY_DOWN, ord("j")):
                selected = (selected + 1) % len(items)
            elif key in (curses.KEY_UP, ord("k")):
                selected = (selected - 1) % len(items)
            elif key in (curses.KEY_ENTER, 10, 13):
                items[selected][3]()
            elif 0 < key < 256 and chr(key) in {i[0] for i in items}:
                for item in items:
                    if item[0] == chr(key):
                        item[3]()
                        break

    # ------------------------------------------------------------------
    # Drill screens
    # ------------------------------------------------------------------
    def _draw_scenario(self, scenario: Scenario, show_count: bool) -> int:
        """Render dealer upcard and player hand. Returns the next free row."""
        t = self.theme
        ui.safe_addstr(self.scr, 3, 6, "Dealer shows", t.dim)
        ui.draw_hand(self.scr, 4, 6, [scenario.upcard], t)
        if show_count:
            tc = scenario.true_count
            ui.safe_addstr(self.scr, 4, 20, f"True count {tc:+.0f}", t.warn)
            ui.safe_addstr(self.scr, 5, 20, "(index plays apply)", t.dim)

        ui.safe_addstr(self.scr, 8, 6, "Your hand", t.dim)
        ui.safe_addstr(self.scr, 8, 20, scenario.player.describe(), t.accent)
        ui.draw_hand(self.scr, 9, 6, scenario.player.cards, t)
        return 13

    def _action_prompt(self, legal: dict[str, bool]) -> str:
        bits = ["[h]it", "[s]tand"]
        bits.append("[d]ouble" if legal["can_double"] else " d ouble")
        bits.append("s[p]lit" if legal["can_split"] else "s p lit")
        bits.append("su[r]render" if legal["can_surrender"] else "su r render")
        return "   ".join(bits)

    def _feedback(self, row: int, correct: str, given: str, detail: str) -> None:
        t = self.theme
        ok = correct == given
        mark = ("✓" if t.unicode else "OK") if ok else ("✗" if t.unicode else "X")
        if ok:
            self.message(row, f"{mark}  {ACTION_NAMES[correct]} — correct."
                         if t.unicode else f"{mark}  {ACTION_NAMES[correct]} - correct.",
                         t.good)
        else:
            self.message(row, f"{mark}  {ACTION_NAMES[correct]}"
                              f"  (you said {ACTION_NAMES[given]})", t.bad)
        if detail:
            self.message(row + 1, detail, t.dim)

    def _cell_detail(self, scenario: Scenario, rules) -> str:
        code = chart_code(scenario.player, scenario.upcard, rules)
        up = UP_LABELS[upcard_index(scenario.upcard)]
        return (f"{scenario.player.describe()} vs {up}: chart says "
                f"{CODE_NAMES.get(code, code)}.")

    def basic_drill(self) -> None:
        self._drill_loop(deviations=self.settings.use_deviations, title="Basic strategy drill")

    def deviation_drill(self) -> None:
        self._drill_loop(deviations=True, title="Deviation drill", only_deviations=True)

    def _drill_loop(self, deviations: bool, title: str,
                    only_deviations: bool = False) -> None:
        rules = self.settings.rules
        section = "deviation" if only_deviations else "basic"
        counter = Counter(self.settings.count_system, rules.decks)
        shoe = Shoe(rules.decks, rules.penetration, self.rng)
        right = 0
        total = 0
        streak = 0
        best_streak = 0
        scenario: Scenario | None = None
        feedback: tuple[str, str, str] | None = None

        while True:
            if ui.too_small(self.scr, self.theme):
                if self.wait_key() == ord("q"):
                    return
                continue
            if scenario is None:
                if only_deviations:
                    scenario = deviation_scenario(self.rng, rules,
                                                  include_fab4=rules.surrender)
                elif self.settings.drill_source == "dealt":
                    scenario = dealt_scenario(shoe, counter)
                else:
                    scenario = weighted_scenario(self.stats, self.rng)
                    if deviations:
                        # Synthetic hands have no shoe behind them, so give them
                        # a count worth reasoning about.
                        scenario.true_count = float(self.rng.randint(-4, 6))
                feedback = None

            self.scr.erase()
            pct = f"{right}/{total}" + (f" ({right * 100 // total}%)" if total else "")
            self.header(title, f"{pct}   streak {streak} (best {best_streak})")
            show_count = deviations
            row = self._draw_scenario(scenario, show_count)

            legal = legality(scenario.player, rules, 1)
            if feedback:
                self._feedback(row, *feedback)
                ui.footer(self.scr, [("any key", "next hand"), ("q", "menu")], self.theme)
            else:
                self.message(row + 1, self._action_prompt(legal), self.theme.title)
                ui.footer(self.scr, [("h/s/d/p/r", "play"), ("?", "chart"),
                                     ("q", "menu")], self.theme)
            self.scr.refresh()

            key = self.wait_key()
            if key in (ord("q"), 27):
                break
            if feedback:
                scenario = None
                continue
            if key == ord("?"):
                self.chart_screen()
                continue
            if key == curses.KEY_RESIZE:
                continue
            ch = chr(key).lower() if 0 < key < 256 else ""
            if ch not in ACTION_KEYS:
                continue

            given = ACTION_KEYS[ch]
            tc = scenario.true_count if deviations else 0.0
            correct, dev = counting_action(
                scenario.player, scenario.upcard, rules, tc,
                use_deviations=deviations, include_fab4=rules.surrender,
            )
            ok = given == correct
            total += 1
            right += int(ok)
            streak = streak + 1 if ok else 0
            best_streak = max(best_streak, streak)
            self.stats.record(scenario.cell_key, ok, section=section)

            detail = self._cell_detail(scenario, rules)
            if dev is not None:
                cmp = ">=" if dev.direction == "ge" else "<="
                detail = (f"Index play: {dev.label}, {dev.action_name.lower()} at "
                          f"TC {cmp} {dev.index:+g} — you were at {tc:+.0f}."
                          if self.theme.unicode else
                          f"Index play: {dev.label}, {dev.action_name.lower()} at "
                          f"TC {cmp} {dev.index:+g} (you were at {tc:+.0f}).")
            elif deviations and scenario.deviation is not None:
                d = scenario.deviation
                cmp = ">=" if d.direction == "ge" else "<="
                detail = (f"{d.label}: index is TC {cmp} {d.index:+g}, you were at "
                          f"{tc:+.0f} — so play basic."
                          if self.theme.unicode else
                          f"{d.label}: index is TC {cmp} {d.index:+g}, you were at "
                          f"{tc:+.0f}, so play basic.")
            feedback = (correct, given, detail)

        self.stats.save()

    # ------------------------------------------------------------------
    def count_drill(self) -> None:
        """Cards flash past; call the running count when asked."""
        t = self.theme
        rules = self.settings.rules
        system = self.settings.count_system
        shoe = Shoe(rules.decks, rules.penetration, self.rng)
        counter = Counter(system, rules.decks)
        speed = self.settings.count_speed_ms
        manual = False
        paused = False
        next_quiz = self.rng.randint(12, 26)
        since_quiz = 0
        current: Card | None = None
        recent: list[Card] = []
        asked = 0
        correct_answers = 0

        while True:
            if ui.too_small(self.scr, self.theme):
                if self.wait_key() == ord("q"):
                    return
                continue
            self.scr.erase()
            acc = f"{correct_answers}/{asked}" if asked else "-"
            self.header("Count drill",
                        f"{system.name}   calls {acc}   {shoe.decks_left:.1f} decks left")

            h, w = self.scr.getmaxyx()
            if current is not None:
                ui.draw_big_card(self.scr, 3, max(2, (w - ui.BIG_W) // 2), current, t)
            tail = " ".join(c.label(t.unicode) for c in recent[-14:])
            ui.center(self.scr, 11, tail, t.dim)
            ui.center(self.scr, 13, f"{counter.seen} cards seen", t.dim)
            mode = "manual" if manual else f"{speed} ms"
            state = "PAUSED" if paused and not manual else mode
            ui.center(self.scr, 14, state, t.warn if paused else t.dim)

            ui.footer(self.scr, [("space", "next/pause"), ("+/-", "speed"),
                                 ("m", "manual"), ("c", "call count"),
                                 ("q", "menu")], t)
            self.scr.refresh()

            key = self.wait_key(None if (manual or paused) else speed)
            if key in (ord("q"), 27):
                break
            if key == ord("m"):
                manual = not manual
                continue
            if key == ord(" "):
                if manual:
                    pass  # falls through to deal a card
                else:
                    paused = not paused
                    continue
            elif key in (ord("+"), ord("=")):
                speed = max(150, speed - 100)
                self.settings.count_speed_ms = speed
                continue
            elif key in (ord("-"), ord("_")):
                speed = min(3000, speed + 100)
                self.settings.count_speed_ms = speed
                continue
            elif key == ord("c"):
                ok = self._ask_count(counter, shoe)
                asked += 1
                correct_answers += int(ok)
                self.stats.record_count_drill(ok)
                since_quiz = 0
                next_quiz = self.rng.randint(12, 26)
                continue
            elif key == curses.KEY_RESIZE:
                continue
            elif key != -1 and not (manual and key == ord(" ")):
                continue

            if shoe.needs_shuffle:
                shoe.shuffle()
                counter.reset()
                recent = []
                self._banner("Shuffle. Count resets.", t.warn)
                continue

            current = shoe.deal()
            counter.see(current)
            recent.append(current)
            since_quiz += 1
            if since_quiz >= next_quiz:
                ok = self._ask_count(counter, shoe)
                asked += 1
                correct_answers += int(ok)
                self.stats.record_count_drill(ok)
                since_quiz = 0
                next_quiz = self.rng.randint(12, 26)

        self.settings.save()
        self.stats.save()

    def _banner(self, text: str, attr: int) -> None:
        h, _ = self.scr.getmaxyx()
        ui.center(self.scr, h - 3, text, attr)
        self.scr.refresh()
        curses.napms(700)

    def _ask_count(self, counter: Counter, shoe: Shoe) -> bool:
        """Quiz the running (and true) count. Returns True if all answers match."""
        t = self.theme
        self.scr.erase()
        self.header("Call it")
        ui.safe_addstr(self.scr, 3, 6, f"{counter.seen} cards have gone by.", t.dim)

        rc = ui.read_line(self.scr, 5, 6, t, "Running count: ", 5, allowed="+-0123456789")
        if rc is None:
            return False
        ok = _int_or_none(rc) == counter.running

        tc_ok = True
        ask_tc = self.settings.ask_true_count and counter.system.balanced
        if ask_tc:
            hint = f"({shoe.decks_left:.2f} decks left)"
            ui.safe_addstr(self.scr, 7, 6, hint, t.dim)
            tc = ui.read_line(self.scr, 8, 6, t, "True count:    ", 5,
                              allowed="+-0123456789")
            if tc is None:
                tc_ok = False
            else:
                want = counter.true_count_floor
                tc_ok = _int_or_none(tc) == want

        row = 10
        ui.safe_addstr(self.scr, row, 6,
                       f"Running count was {counter.running:+d}",
                       t.good if ok else t.bad)
        if ask_tc:
            ui.safe_addstr(self.scr, row + 1, 6,
                           f"True count was {counter.true_count:+.2f} "
                           f"(play it as {counter.true_count_floor:+d}) "
                           f"with {counter.decks_remaining:.2f} decks left",
                           t.good if tc_ok else t.bad)
            ui.safe_addstr(self.scr, row + 3, 6,
                           f"{counter.running:+d} / {counter.decks_remaining:.2f} decks"
                           f" = {counter.true_count:+.2f}", t.dim)
        ui.footer(self.scr, [("any key", "keep dealing")], t)
        self.scr.refresh()
        self.wait_key()
        return ok and tc_ok

    # ------------------------------------------------------------------
    def play_shoe(self) -> None:
        """Full hands: bet, play, count, settle."""
        t = self.theme
        rules = self.settings.rules
        shoe = Shoe(rules.decks, rules.penetration, self.rng)
        counter = Counter(self.settings.count_system, rules.decks)
        bankroll = self.settings.bankroll
        unit = self.settings.unit
        show_count = self.settings.show_count
        hands_played = 0
        misplays = 0
        decisions = 0
        rnd: Round | None = None
        note = ""
        result_lines: list[str] = []

        while True:
            if ui.too_small(self.scr, self.theme):
                if self.wait_key() == ord("q"):
                    return
                continue

            if rnd is None:
                if shoe.needs_shuffle:
                    shoe.shuffle()
                    counter.reset()
                    note = "New shoe. Count reset."
                suggested = bet_units(counter.true_count)
                bet = suggested * unit
                rnd = Round(shoe, rules, counter, bet)
                rnd.start()
                result_lines = []
                if rnd.state == DONE:  # a natural settles before anyone acts
                    bankroll, result_lines = self._finish_round(rnd, bankroll)
                    hands_played += 1

            self.scr.erase()
            count_txt = (f"RC {counter.running:+d}  TC {counter.true_count:+.1f}"
                         if show_count else "count hidden")
            self.header("Play a shoe",
                        f"{bankroll:+.0f}u   {shoe.decks_left:.1f}d left   {count_txt}")

            hide = None if rnd.hole_shown or rnd.state == DONE else 1
            ui.safe_addstr(self.scr, 3, 6, "Dealer", t.dim)
            if rnd.hole_shown or rnd.state == DONE:
                ui.safe_addstr(self.scr, 3, 16, rnd.dealer.describe(), t.accent)
            ui.draw_hand(self.scr, 4, 6, rnd.dealer.cards, t, hide_index=hide)

            row = 8
            for i, hand in enumerate(rnd.hands):
                marker = ">" if i == rnd.active and rnd.state == PLAYER else " "
                tag = f"{marker} Hand {i + 1}" if len(rnd.hands) > 1 else f"{marker} You"
                attr = t.accent if i == rnd.active and rnd.state == PLAYER else t.dim
                ui.safe_addstr(self.scr, row, 4, f"{tag}  {hand.bet:.0f}u", attr)
                ui.safe_addstr(self.scr, row, 24, hand.describe(), t.dim)
                ui.draw_hand(self.scr, row + 1, 6, hand.cards, t)
                row += 4
                if row > self.scr.getmaxyx()[0] - 7:
                    break

            if note:
                self.message(row, note, t.warn)
                row += 1
            for line, attr in result_lines:
                self.message(row, line, attr)
                row += 1

            if rnd.state == INSURANCE:
                self.message(row + 1, "Dealer shows an ace. Insurance? [y/n]", t.title)
                ui.footer(self.scr, [("y/n", "insurance"), ("k", "toggle count"),
                                     ("q", "menu")], t)
            elif rnd.state == PLAYER:
                self.message(row + 1, self._action_prompt(rnd.legal()), t.title)
                ui.footer(self.scr, [("h/s/d/p/r", "play"), ("k", "toggle count"),
                                     ("c", "call count"), ("?", "chart"),
                                     ("q", "menu")], t)
            elif rnd.state == DEALER:
                self.message(row + 1, "Dealer plays...", t.dim)
                ui.footer(self.scr, [("any key", "deal")], t)
            else:
                self.message(row + 1, "Press any key for the next hand.", t.dim)
                ui.footer(self.scr, [("any key", "next"), ("k", "toggle count"),
                                     ("q", "menu")], t)
            self.scr.refresh()

            key = self.wait_key()
            if key in (ord("q"), 27):
                break
            if key == curses.KEY_RESIZE:
                continue
            if key == ord("k"):
                show_count = not show_count
                continue
            if key == ord("c") and rnd.state in (PLAYER, INSURANCE):
                self._ask_count(counter, shoe)
                continue
            if key == ord("?"):
                self.chart_screen()
                continue

            note = ""
            if rnd.state == INSURANCE:
                ch = chr(key).lower() if 0 < key < 256 else ""
                if ch not in ("y", "n"):
                    continue
                took = ch == "y"
                want = should_insure(counter.true_count)
                if self.settings.strict_shoe and took != want:
                    note = (f"Insurance is a count bet: take it at TC +3 or better "
                            f"(you were at {counter.true_count:+.1f}).")
                rnd.take_insurance(took)
                if rnd.state == DONE:
                    bankroll, result_lines = self._finish_round(rnd, bankroll)
                    hands_played += 1
                continue

            if rnd.state == PLAYER:
                ch = chr(key).lower() if 0 < key < 256 else ""
                if ch not in ACTION_KEYS:
                    continue
                given = ACTION_KEYS[ch]
                correct, dev = counting_action(
                    rnd.hand, rnd.upcard, rules, counter.true_count, len(rnd.hands),
                    use_deviations=self.settings.use_deviations,
                    include_fab4=rules.surrender,
                )
                key_name = _cell_key(rnd.hand, rnd.upcard)
                decisions += 1
                ok = given == correct
                if not ok:
                    misplays += 1
                self.stats.record(key_name, ok, section="shoe")
                if self.settings.strict_shoe and not ok:
                    extra = ""
                    if dev is not None:
                        cmp = ">=" if dev.direction == "ge" else "<="
                        extra = f"  (index: {dev.label} at TC {cmp} {dev.index:+g})"
                    note = f"Correct was {ACTION_NAMES[correct]}.{extra}"
                msg = rnd.act(given)
                if msg:
                    note = (note + "  " + msg).strip()
                if rnd.state == DEALER and not self._players_remain(rnd):
                    rnd.finish_dealer()
                    bankroll, result_lines = self._finish_round(rnd, bankroll)
                    hands_played += 1
                continue

            if rnd.state == DEALER:
                rnd.finish_dealer()
                bankroll, result_lines = self._finish_round(rnd, bankroll)
                hands_played += 1
                continue

            rnd = None  # DONE: next hand

        self.settings.bankroll = bankroll
        self.settings.show_count = show_count
        self.settings.save()
        self.stats.save()
        if decisions:
            self._summary_screen(hands_played, decisions, misplays, bankroll)

    @staticmethod
    def _players_remain(rnd: Round) -> bool:
        return any(not (h.is_bust or h.surrendered) for h in rnd.hands)

    def _finish_round(self, rnd: Round, bankroll: float) -> tuple[float, list]:
        t = self.theme
        lines = []
        for s in rnd.settlements:
            attr = t.good if s.payout > 0 else (t.bad if s.payout < 0 else t.dim)
            word = {"blackjack": "Blackjack!", "win": "Win", "lose": "Lose",
                    "push": "Push", "surrender": "Surrender",
                    "insurance": "Insurance"}.get(s.result, s.result)
            lines.append((f"{word}  {s.payout:+.1f}u", attr))
        return bankroll + rnd.net, lines

    def _summary_screen(self, hands: int, decisions: int, misplays: int,
                        bankroll: float) -> None:
        t = self.theme
        self.scr.erase()
        self.header("Session over")
        acc = (decisions - misplays) * 100 // max(decisions, 1)
        rows = [
            f"Hands played      {hands}",
            f"Decisions         {decisions}",
            f"Misplays          {misplays}   ({acc}% correct)",
            f"Bankroll          {bankroll:.1f}u",
        ]
        for i, line in enumerate(rows):
            ui.safe_addstr(self.scr, 4 + i, 6, line, t.plain)
        ui.footer(self.scr, [("any key", "menu")], t)
        self.scr.refresh()
        self.wait_key()

    # ------------------------------------------------------------------
    def chart_screen(self) -> None:
        t = self.theme
        rules = self.settings.rules
        rows = chart_rows(rules)
        sections = ["Hard totals", "Soft totals", "Pairs"]
        idx = 0
        while True:
            if ui.too_small(self.scr, self.theme):
                if self.wait_key() == ord("q"):
                    return
                continue
            self.scr.erase()
            section = sections[idx]
            self.header(f"Chart — {section}" if t.unicode else f"Chart - {section}",
                        rules.label)
            ui.safe_addstr(self.scr, 3, 10,
                           "  ".join(f"{u:>2}" for u in UP_LABELS), t.title)
            ui.safe_addstr(self.scr, 3, 2, "dealer", t.dim)
            r = 4
            for sec, label, codes in rows:
                if sec != section:
                    continue
                ui.safe_addstr(self.scr, r, 3, f"{label:>5}", t.dim)
                for i, code in enumerate(codes):
                    ui.safe_addstr(self.scr, r, 10 + i * 4, f"{code:>2}",
                                   t.code_attr(code))
                r += 1

            legend = [("H", "hit"), ("S", "stand"), ("D", "double"),
                      ("P", "split"), ("R", "surrender")]
            x = 3
            ui.safe_addstr(self.scr, r + 1, x, "key:", t.dim)
            x += 5
            for code, word in legend:
                ui.safe_addstr(self.scr, r + 1, x, code, t.code_attr(code))
                ui.safe_addstr(self.scr, r + 1, x + 2, word, t.dim)
                x += 3 + len(word) + 2
            ui.safe_addstr(self.scr, r + 2, 3,
                           "lower case suffix = what to do when the first choice "
                           "is not allowed", t.dim)
            ui.footer(self.scr, [("tab/arrows", "section"), ("q", "back")], t)
            self.scr.refresh()

            key = self.wait_key()
            if key in (ord("q"), 27):
                return
            if key in (9, curses.KEY_RIGHT, curses.KEY_DOWN, ord("l")):
                idx = (idx + 1) % len(sections)
            elif key in (curses.KEY_LEFT, curses.KEY_UP, ord("h")):
                idx = (idx - 1) % len(sections)

    # ------------------------------------------------------------------
    def stats_screen(self) -> None:
        t = self.theme
        while True:
            if ui.too_small(self.scr, self.theme):
                if self.wait_key() == ord("q"):
                    return
                continue
            self.scr.erase()
            self.header("Stats", "all sessions")
            r = 3
            for section, label in (("basic", "Basic strategy"),
                                   ("deviation", "Index plays"),
                                   ("shoe", "Shoe play")):
                a, e = self.stats.section_accuracy(section)
                pct = f"{(a - e) * 100 // a}%" if a else "-"
                ui.safe_addstr(self.scr, r, 6,
                               f"{label:<16} {a:>6} hands   {pct:>5} correct", t.plain)
                r += 1
            ca = self.stats.count_drills.get("attempts", 0)
            ce = self.stats.count_drills.get("errors", 0)
            pct = f"{(ca - ce) * 100 // ca}%" if ca else "-"
            ui.safe_addstr(self.scr, r, 6,
                           f"{'Count calls':<16} {ca:>6} calls   {pct:>5} correct",
                           t.plain)
            r += 2

            worst = self.stats.worst_cells(limit=10)
            ui.safe_addstr(self.scr, r, 6, "Cells you keep missing", t.title)
            r += 1
            if not worst:
                ui.safe_addstr(self.scr, r, 6, "Nothing yet — go drill."
                               if t.unicode else "Nothing yet - go drill.", t.dim)
            for key, cell in worst:
                ui.safe_addstr(self.scr, r, 6,
                               f"{key:<22} {cell.errors}/{cell.attempts} wrong", t.bad)
                r += 1
                if r > self.scr.getmaxyx()[0] - 4:
                    break

            ui.footer(self.scr, [("R", "reset stats"), ("q", "back")], t)
            self.scr.refresh()
            key = self.wait_key()
            if key in (ord("q"), 27):
                return
            if key == ord("R"):
                self.stats.reset()

    # ------------------------------------------------------------------
    def settings_screen(self) -> None:
        t = self.theme
        s = self.settings
        deck_choices = [1, 2, 4, 6, 8]
        pen_choices = [0.5, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9]
        systems = [x.name for x in SYSTEMS]

        def cycle(values, current, step):
            i = values.index(current) if current in values else 0
            return values[(i + step) % len(values)]

        fields = [
            ("Decks", lambda: str(s.decks),
             lambda d: setattr(s, "decks", cycle(deck_choices, s.decks, d))),
            ("Dealer soft 17", lambda: "hits" if s.h17 else "stands",
             lambda d: setattr(s, "h17", not s.h17)),
            ("Double after split", lambda: "yes" if s.das else "no",
             lambda d: setattr(s, "das", not s.das)),
            ("Late surrender", lambda: "yes" if s.surrender else "no",
             lambda d: setattr(s, "surrender", not s.surrender)),
            ("Blackjack pays", lambda: "3:2" if s.blackjack_pays > 1.3 else "6:5",
             lambda d: setattr(s, "blackjack_pays",
                               1.2 if s.blackjack_pays > 1.3 else 1.5)),
            ("Penetration", lambda: f"{s.penetration:.0%}",
             lambda d: setattr(s, "penetration",
                               cycle(pen_choices, s.penetration, d))),
            ("Count system", lambda: s.system,
             lambda d: setattr(s, "system", cycle(systems, s.system, d))),
            ("Drill hands", lambda: ("weighted to your misses"
                                     if s.drill_source == "weighted" else "dealt off a shoe"),
             lambda d: setattr(s, "drill_source",
                               "dealt" if s.drill_source == "weighted" else "weighted")),
            ("Index plays in drills", lambda: "on" if s.use_deviations else "off",
             lambda d: setattr(s, "use_deviations", not s.use_deviations)),
            ("Flag misplays in shoe", lambda: "on" if s.strict_shoe else "off",
             lambda d: setattr(s, "strict_shoe", not s.strict_shoe)),
            ("Show count in shoe", lambda: "on" if s.show_count else "off",
             lambda d: setattr(s, "show_count", not s.show_count)),
            ("Ask true count", lambda: "yes" if s.ask_true_count else "no",
             lambda d: setattr(s, "ask_true_count", not s.ask_true_count)),
            ("Count drill speed", lambda: f"{s.count_speed_ms} ms",
             lambda d: setattr(s, "count_speed_ms",
                               max(150, min(3000, s.count_speed_ms + 100 * d)))),
            ("Bet unit", lambda: f"{s.unit:.0f}",
             lambda d: setattr(s, "unit", max(1.0, s.unit + d))),
            ("Bankroll", lambda: f"{s.bankroll:.0f}u",
             lambda d: setattr(s, "bankroll", s.bankroll + 50 * d)),
        ]
        sel = 0
        while True:
            if ui.too_small(self.scr, self.theme):
                if self.wait_key() == ord("q"):
                    return
                continue
            self.scr.erase()
            self.header("Settings", s.rules.label)
            h, _ = self.scr.getmaxyx()
            # Scroll the list when the terminal cannot show every field at once.
            visible = max(3, h - 6)
            first = 0
            if len(fields) > visible:
                first = min(max(0, sel - visible // 2), len(fields) - visible)
            for row, i in enumerate(range(first, min(first + visible, len(fields)))):
                label, show, _ = fields[i]
                attr = t.accent if i == sel else t.plain
                marker = ">" if i == sel else " "
                ui.safe_addstr(self.scr, 3 + row, 4, f"{marker} {label:<24}", attr)
                ui.safe_addstr(self.scr, 3 + row, 32, show(),
                               t.warn if i == sel else t.dim)
            if len(fields) > visible:
                ui.safe_addstr(self.scr, 3 + visible, 4,
                               f"({sel + 1}/{len(fields)})", t.dim)
            ui.safe_addstr(self.scr, h - 2, 4,
                           self.settings.count_system.blurb, t.dim)
            ui.footer(self.scr, [("up/down", "field"), ("left/right", "change"),
                                 ("q", "save and back")], t)
            self.scr.refresh()

            key = self.wait_key()
            if key in (ord("q"), 27):
                break
            if key in (curses.KEY_DOWN, ord("j")):
                sel = (sel + 1) % len(fields)
            elif key in (curses.KEY_UP, ord("k")):
                sel = (sel - 1) % len(fields)
            elif key in (curses.KEY_RIGHT, ord("l"), 10, 13, curses.KEY_ENTER):
                fields[sel][2](1)
            elif key in (curses.KEY_LEFT, ord("h")):
                fields[sel][2](-1)
        s.save()


def _cell_key(hand: Hand, upcard: Card) -> str:
    from .drills import cell_key

    return cell_key(hand, upcard)


def _int_or_none(text: str) -> int | None:
    text = text.strip().replace("+", "")
    try:
        return int(text)
    except ValueError:
        return None


def main() -> None:
    curses.wrapper(lambda scr: App(scr).run())
