from __future__ import annotations

from aqt import gui_hooks, mw, utils
from aqt.qt import *

from . import config


class _State:
    label = None


_REGISTERED = False


def _position_for(index: int, count: int, width_mode: str, window_width: int, x_offset: int) -> int:
    width = {"s": 62, "m": 87, "l": 125}.get(width_mode, 62)
    gap = {"s": 75, "m": 97.33, "l": 135}.get(width_mode, 75)
    total = (count - 1) * gap
    return int(window_width / 2 - total / 2 + index * gap - width / 2 + x_offset)


def _show(reviewer, card, ease: int) -> None:
    c = config.load()
    if not c.get("confirmation", True):
        return
    if ease not in (1, 2, 3, 4):
        return
    count = len(__import__("passfail_king_buttons.button_logic", fromlist=["configured_eases"]).configured_eases(int(c.get("button_count", 2))))
    try:
        idx = __import__("passfail_king_buttons.button_logic", fromlist=["configured_eases"]).configured_eases(int(c.get("button_count", 2))).index(ease)
    except ValueError:
        return

    aw = mw.app.activeWindow() or mw
    width_mode = str(c.get("button_width", "s")).lower()
    height_mode = str(c.get("button_height", "s")).lower()
    label_height = {"s": 26, "m": 41, "l": 61}.get(height_mode, 26)
    y = {"s": -36, "m": -51, "l": -71}.get(height_mode, -36) - int(c.get("confirmation_y_offset", 0))
    y = max(0, aw.mapToGlobal(QPoint(0, int(y + aw.height()))).y())
    x = _position_for(idx, count, width_mode, aw.width(), int(c.get("confirmation_x_offset", 0)))
    color_key = "light" if not getattr(__import__("aqt.theme", fromlist=["theme_manager"]), "theme_manager").night_mode else "dark"
    bg = c.get(f"{color_key}_background_{'again' if ease == 1 else 'hard' if ease == 2 else 'good' if ease == 3 else 'easy'}", "#ddd")
    names = {1: c.get("again_name", "Fail"), 2: c.get("hard_name", "Hard"), 3: c.get("good_name", "Pass"), 4: c.get("easy_name", "Easy")}
    font_size = {"s": "", "m": "font-size:16px;", "l": "font-size:20px;"}.get(str(c.get("button_font_size", "s")).lower(), "")
    utils.tooltipWithColour(
        f"<div style='color:#3a3a3a;{font_size}'>{names[ease]}</div>",
        bg,
        x=x,
        y=y,
        xref=0,
        period=int(c.get("confirmation_time", 450)),
        width={"s": 62, "m": 87, "l": 125}.get(width_mode, 62),
        height=label_height,
    )


def init() -> None:
    global _REGISTERED
    if _REGISTERED:
        return
    # Anki 26.x exposes this as a typed hook object, not an iterable list.
    # Track our own registration state instead of using ``_show not in hook``.
    gui_hooks.reviewer_did_answer_card.append(_show)
    _REGISTERED = True
