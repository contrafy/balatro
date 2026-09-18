"""Curses primitives: colours, card art, boxes, and input helpers.

Everything degrades: no colour, no unicode, and an 80x24 terminal all work.
"""

from __future__ import annotations

import curses
import os
from dataclasses import dataclass

from .cards import Card

MIN_COLS = 72
MIN_LINES = 20


@dataclass
class Theme:
    plain: int = 0
    title: int = 0
    dim: int = 0
    good: int = 0
    bad: int = 0
    warn: int = 0
    accent: int = 0
    red: int = 0
    black: int = 0
    highlight: int = 0
    unicode: bool = True

    # Chart cell colours, one per action code family.
    def code_attr(self, code: str) -> int:
        return {
            "H": self.bad,
            "S": self.good,
            "D": self.warn,
            "P": self.accent,
            "R": self.highlight,
        }.get(code[0], self.plain)


def supports_unicode() -> bool:
    if os.environ.get("BJTRAINER_ASCII"):
        return False
    encoding = (os.environ.get("LC_ALL") or os.environ.get("LC_CTYPE")
                or os.environ.get("LANG") or "")
    return "utf" in encoding.lower() or "UTF" in encoding


def make_theme() -> Theme:
    uni = supports_unicode()
    if not curses.has_colors():
        return Theme(
            title=curses.A_BOLD,
            dim=curses.A_DIM,
            good=curses.A_BOLD,
            bad=curses.A_REVERSE,
            warn=curses.A_BOLD,
            accent=curses.A_UNDERLINE,
            highlight=curses.A_REVERSE,
            unicode=uni,
        )
    curses.start_color()
    try:
        curses.use_default_colors()
        bg = -1
    except curses.error:  # pragma: no cover - ancient terminals
        bg = curses.COLOR_BLACK
    pairs = [
        (1, curses.COLOR_CYAN),
        (2, curses.COLOR_GREEN),
        (3, curses.COLOR_RED),
        (4, curses.COLOR_YELLOW),
        (5, curses.COLOR_MAGENTA),
        (6, curses.COLOR_WHITE),
        (7, curses.COLOR_BLUE),
    ]
    for idx, colour in pairs:
        curses.init_pair(idx, colour, bg)
    return Theme(
        title=curses.color_pair(1) | curses.A_BOLD,
        dim=curses.A_DIM,
        good=curses.color_pair(2) | curses.A_BOLD,
        bad=curses.color_pair(3) | curses.A_BOLD,
        warn=curses.color_pair(4) | curses.A_BOLD,
        accent=curses.color_pair(5) | curses.A_BOLD,
        red=curses.color_pair(3),
        black=curses.color_pair(6),
        highlight=curses.color_pair(7) | curses.A_BOLD,
        unicode=uni,
    )


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def safe_addstr(win, y: int, x: int, text: str, attr: int = 0) -> None:
    """addstr that silently clips instead of raising at the screen edge."""
    if y < 0 or x < 0:
        return
    h, w = win.getmaxyx()
    if y >= h or x >= w:
        return
    text = text[: max(0, w - x - 1)]
    try:
        win.addstr(y, x, text, attr)
    except curses.error:  # pragma: no cover - bottom-right cell
        pass


def center(win, y: int, text: str, attr: int = 0) -> None:
    _, w = win.getmaxyx()
    safe_addstr(win, y, max(0, (w - len(text)) // 2), text, attr)


def hline(win, y: int, x: int, width: int, theme: Theme, attr: int = 0) -> None:
    ch = "─" if theme.unicode else "-"
    safe_addstr(win, y, x, ch * width, attr or theme.dim)


def draw_box(win, y: int, x: int, h: int, w: int, theme: Theme,
             title: str = "", attr: int = 0) -> None:
    if theme.unicode:
        tl, tr, bl, br, hz, vt = "┌", "┐", "└", "┘", "─", "│"
    else:
        tl = tr = bl = br = "+"
        hz, vt = "-", "|"
    safe_addstr(win, y, x, tl + hz * (w - 2) + tr, attr)
    for row in range(1, h - 1):
        safe_addstr(win, y + row, x, vt, attr)
        safe_addstr(win, y + row, x + w - 1, vt, attr)
    safe_addstr(win, y + h - 1, x, bl + hz * (w - 2) + br, attr)
    if title:
        safe_addstr(win, y, x + 2, f" {title} ", theme.title)


CARD_W, CARD_H = 5, 3


def card_lines(c: Card | None, theme: Theme, hidden: bool = False) -> list[str]:
    """Three rows of card art, 5 columns wide."""
    if theme.unicode:
        top, bot, side = "┌───┐", "└───┘", "│"
        back = "▒▒▒"
    else:
        top = bot = "+---+"
        side, back = "|", "###"
    if hidden or c is None:
        return [top, f"{side}{back}{side}", bot]
    face = c.label(theme.unicode)
    return [top, f"{side}{face:<3}{side}", bot]


def draw_card(win, y: int, x: int, c: Card | None, theme: Theme,
              hidden: bool = False) -> None:
    attr = theme.dim if hidden or c is None else (
        theme.red if c.is_red else theme.black
    )
    for i, line in enumerate(card_lines(c, theme, hidden)):
        safe_addstr(win, y + i, x, line, attr)


def draw_hand(win, y: int, x: int, cards, theme: Theme,
              hide_index: int | None = None, gap: int = 1) -> int:
    """Draw a row of cards; returns the width used."""
    step = CARD_W + gap
    for i, c in enumerate(cards):
        draw_card(win, y, x + i * step, c, theme, hidden=(i == hide_index))
    return max(0, len(cards) * step - gap)


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------

def read_line(win, y: int, x: int, theme: Theme, prompt: str = "",
              maxlen: int = 8, allowed: str | None = None) -> str | None:
    """Read a short line inline. Returns None if the user pressed Esc."""
    buf = ""
    safe_addstr(win, y, x, prompt, theme.title)
    field_x = x + len(prompt)
    while True:
        safe_addstr(win, y, field_x, " " * (maxlen + 2))
        safe_addstr(win, y, field_x, buf + "_", theme.accent)
        win.refresh()
        try:
            key = win.getch()
        except KeyboardInterrupt:  # pragma: no cover
            return None
        if key in (curses.KEY_ENTER, 10, 13):
            return buf
        if key == 27:
            return None
        if key in (curses.KEY_BACKSPACE, 127, 8):
            buf = buf[:-1]
            continue
        if key == curses.KEY_RESIZE:
            return read_line(win, y, x, theme, prompt, maxlen, allowed)
        if 32 <= key < 127 and len(buf) < maxlen:
            ch = chr(key)
            if allowed is None or ch in allowed:
                buf += ch


def too_small(win, theme: Theme) -> bool:
    h, w = win.getmaxyx()
    if h >= MIN_LINES and w >= MIN_COLS:
        return False
    win.erase()
    safe_addstr(win, 0, 0, "Terminal too small.", theme.bad)
    safe_addstr(win, 1, 0, f"Need {MIN_COLS}x{MIN_LINES}, have {w}x{h}.")
    safe_addstr(win, 2, 0, "Resize, or press q to quit.")
    win.refresh()
    return True


def footer(win, keys: list[tuple[str, str]], theme: Theme) -> None:
    h, w = win.getmaxyx()
    parts = []
    for key, label in keys:
        parts.append(f"{key} {label}")
    sep = "  ·  " if theme.unicode else "  |  "
    text = sep.join(parts)
    safe_addstr(win, h - 1, max(0, (w - len(text)) // 2), text[: w - 1], theme.dim)


BIG_W, BIG_H = 11, 7


def big_card_lines(c: Card, theme: Theme) -> list[str]:
    """Seven rows of card art, 11 columns wide, for the flash-card drill."""
    face = c.rank
    suit = SUIT_GLYPH_SAFE(c, theme)
    if theme.unicode:
        top = "┌" + "─" * 9 + "┐"
        bot = "└" + "─" * 9 + "┘"
        v = "│"
    else:
        top = bot = "+" + "-" * 9 + "+"
        v = "|"
    left = f"{face}{suit}".ljust(3)
    right = f"{face}{suit}".rjust(3)
    return [
        top,
        f"{v} {left}     {v}",
        f"{v}         {v}",
        f"{v}    {suit}    {v}",
        f"{v}         {v}",
        f"{v}     {right} {v}",
        bot,
    ]


def SUIT_GLYPH_SAFE(c: Card, theme: Theme) -> str:
    from .cards import SUIT_GLYPH

    return SUIT_GLYPH[c.suit] if theme.unicode else c.suit.upper()


def draw_big_card(win, y: int, x: int, c: Card, theme: Theme) -> None:
    attr = theme.red if c.is_red else theme.black
    for i, line in enumerate(big_card_lines(c, theme)):
        safe_addstr(win, y + i, x, line, attr | curses.A_BOLD)
