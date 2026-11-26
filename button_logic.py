from __future__ import annotations

from html import escape
from typing import Iterable

EASE_NAMES = {
    1: "Again",
    2: "Hard",
    3: "Good",
    4: "Easy",
}


def configured_eases(button_count: int) -> tuple[int, ...]:
    if button_count == 2:
        return (1, 3)
    if button_count == 3:
        return (1, 2, 3)
    return (1, 2, 3, 4)


def labels(config: dict) -> dict[int, str]:
    return {
        1: config.get("again_name", "Fail"),
        2: config.get("hard_name", "Hard"),
        3: config.get("good_name", "Pass"),
        4: config.get("easy_name", "Easy"),
    }


def replace_buttons(buttons_tuple, reviewer, card):
    from . import config as cfg
    c = cfg.load()
    count = int(c.get("button_count", 2))
    if count not in (2, 3, 4):
        count = 2
    ls = labels(c)
    result = tuple((ease, ls[ease]) for ease in configured_eases(count))
    if c.get("enable_names", True):
        return result

    # When custom names are disabled, retain Anki's labels from the original hook where possible.
    original = {ease: text for ease, text in buttons_tuple}
    return tuple((ease, original.get(ease, EASE_NAMES[ease])) for ease in configured_eases(count))


def remap_answer(ease_tuple, reviewer, card):
    from . import config as cfg
    count = int(cfg.get("button_count", 2))
    proceed, ease = ease_tuple
    if not proceed:
        return ease_tuple
    if count == 2:
        return True, 1 if ease == 1 else 3
    if count == 3:
        return True, min(ease, 3)
    return True, ease


def button_selector(ease: int) -> str:
    return f'#middle button[data-ease="{ease}"]'


def css_escape_color(value: str, fallback: str) -> str:
    value = str(value or "").strip()
    # Accept normal CSS color names/functions as the original add-on did, while rejecting braces.
    if any(ch in value for ch in "{};<>"):
        return fallback
    return value or fallback
