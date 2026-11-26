from __future__ import annotations

from html import escape

from aqt import gui_hooks, mw
from aqt.qt import *
from aqt.theme import theme_manager

from . import config
from .button_logic import configured_eases

_REGISTERED = False
_popup: QLabel | None = None
_popup_timer: QTimer | None = None


def _safe_color(value: str, fallback: str) -> str:
    text = str(value or "").strip()
    qcolor = QColor(text)
    return text if qcolor.isValid() else fallback


def _show(reviewer, card, ease: int) -> None:
    global _popup, _popup_timer

    c = config.load()
    if not c.get("confirmation", True) or ease not in (1, 2, 3, 4):
        return

    eases = configured_eases(int(c.get("button_count", 2)))
    if ease not in eases:
        return
    idx = eases.index(ease)
    count = len(eases)

    aw = mw.app.activeWindow() or mw
    width = max(1, int(c.get("button_width_px", 42)))
    height = max(1, int(c.get("button_height_px", 25)))
    gap = width + 12
    total = (count - 1) * gap

    center = aw.mapToGlobal(QPoint(aw.width() // 2, 0))
    x = int(center.x() - total / 2 + idx * gap - width / 2 + int(c.get("confirmation_x_offset", 0)))
    y = int(aw.mapToGlobal(QPoint(0, aw.height())).y() - height - 30 - int(c.get("confirmation_y_offset", 0)))

    palette = "dark" if theme_manager.night_mode else "light"
    name_key = {1: "again", 2: "hard", 3: "good", 4: "easy"}[ease]
    bg = _safe_color(c.get(f"{palette}_background_{name_key}"), "#444444" if theme_manager.night_mode else "#dddddd")
    fg = _safe_color(c.get(f"{palette}_text_{name_key}"), "#ffffff" if theme_manager.night_mode else "#000000")
    label = {
        1: c.get("again_name", "Fail"),
        2: c.get("hard_name", "Hard"),
        3: c.get("good_name", "Pass"),
        4: c.get("easy_name", "Easy"),
    }[ease]

    if _popup is None:
        _popup = QLabel(mw, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        _popup.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        _popup.setAlignment(Qt.AlignmentFlag.AlignCenter)
        _popup.setMargin(0)
        _popup.setContentsMargins(8, 3, 8, 3)

    _popup.setText(escape(str(label)))
    _popup.setStyleSheet(
        f"QLabel {{ background: {bg}; color: {fg}; border: 1px solid rgba(0,0,0,0.35); "
        f"border-radius: 4px; padding: 3px 8px; font-size: 12px; }}"
    )
    _popup.adjustSize()
    _popup.move(x, y)
    _popup.show()
    _popup.raise_()

    if _popup_timer is None:
        _popup_timer = QTimer(_popup)
        _popup_timer.setSingleShot(True)
        _popup_timer.timeout.connect(_popup.hide)
    _popup_timer.stop()
    _popup_timer.start(max(50, int(c.get("confirmation_time", 450))))


def init() -> None:
    global _REGISTERED
    if _REGISTERED:
        return
    gui_hooks.reviewer_did_answer_card.append(_show)
    _REGISTERED = True
