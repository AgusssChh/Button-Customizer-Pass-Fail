from __future__ import annotations

from copy import deepcopy
from typing import Any

from aqt import mw

DEFAULTS: dict[str, Any] = {
    "button_count": 2,
    "enable_names": True,
    "again_name": "Fail",
    "hard_name": "Hard",
    "good_name": "Pass",
    "easy_name": "Easy",
    "color_mode": "colors",  # default, text, hover, colors
    "light_background_again": "#ff6961",
    "light_background_hard": "#ffb861",
    "light_background_good": "#61ffb8",
    "light_background_easy": "#61a8ff",
    "dark_background_again": "#b84f49",
    "dark_background_hard": "#b98045",
    "dark_background_good": "#46b982",
    "dark_background_easy": "#467ebd",
    "light_text_again": "#000000",
    "light_text_hard": "#000000",
    "light_text_good": "#000000",
    "light_text_easy": "#000000",
    "dark_text_again": "#ffffff",
    "dark_text_hard": "#ffffff",
    "dark_text_good": "#ffffff",
    "dark_text_easy": "#ffffff",
    "border_radius": 15,
    "button_font_size": "S",
    "button_height": "S",
    "button_width": "S",
    "answer_button_width": "full",
    "confirmation": True,
    "confirmation_time": 450,
    "confirmation_x_offset": 0,
    "confirmation_y_offset": 0,
    "outline": True,
    "outline_width": 2,
    "outline_offset": 2,
    "style_main_screen_buttons": True,
    "migrate_old_settings": True,
}

_config: dict[str, Any] | None = None


def _addon_name() -> str:
    return mw.addonManager.addonFromModule(__name__)


def _load_raw() -> dict[str, Any]:
    raw = mw.addonManager.getConfig(__name__) or {}
    merged = deepcopy(DEFAULTS)
    merged.update(raw)
    return merged


def _try_get_addon_config(name: str) -> dict[str, Any]:
    try:
        data = mw.addonManager.getConfig(name)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _migrate_once(data: dict[str, Any]) -> None:
    if not data.get("migrate_old_settings", True):
        return
    # Preserve useful settings from the original add-ons when they are present.
    old_pf = _try_get_addon_config("PassFail2")
    old_king = _try_get_addon_config("374005964")

    changed = False

    if old_pf:
        mapping = {
            "again_button_name": "again_name",
            "good_button_name": "good_name",
            "again_button_textcolor": "light_text_again",
            "good_button_textcolor": "light_text_good",
        }
        for old_key, new_key in mapping.items():
            if old_key in old_pf:
                data[new_key] = old_pf[old_key]
                changed = True
        if "toggle_names_textcolors" in old_pf:
            data["enable_names"] = bool(int(old_pf["toggle_names_textcolors"]))
            changed = True
        data["button_count"] = 2

    if old_king:
        king_map = {
            "AgainColor": "light_background_again",
            "HardColor": "light_background_hard",
            "GoodColor": "light_background_good",
            "EasyColor": "light_background_easy",
            "Nightmode_AgainColor": "dark_background_again",
            "Nightmode_HardColor": "dark_background_hard",
            "Nightmode_GoodColor": "dark_background_good",
            "Nightmode_EasyColor": "dark_background_easy",
            "border radius": "border_radius",
            "button font size": "button_font_size",
            "button height": "button_height",
            "button width": "button_width",
            "answer button width": "answer_button_width",
            "confirmation": "confirmation",
            "confirmation time": "confirmation_time",
            "confirmation x-offset": "confirmation_x_offset",
            "confirmation y-offset": "confirmation_y_offset",
            "outline": "outline",
            "style main screen buttons": "style_main_screen_buttons",
        }
        for old_key, new_key in king_map.items():
            if old_key in old_king:
                data[new_key] = old_king[old_key]
                changed = True
        old_mode = str(old_king.get("button color", "colors")).lower()
        if old_mode in {"default", "text", "hover", "colors"}:
            data["color_mode"] = old_mode
            changed = True

    if changed:
        data["migrate_old_settings"] = False
        mw.addonManager.writeConfig(__name__, data)


def load() -> dict[str, Any]:
    global _config
    if _config is None:
        _config = _load_raw()
        _migrate_once(_config)
    return _config


def get(key: str, default: Any = None) -> Any:
    return load().get(key, default)


def all() -> dict[str, Any]:
    return deepcopy(load())


def update(values: dict[str, Any]) -> None:
    global _config
    current = load()
    for key in DEFAULTS:
        if key in values:
            current[key] = values[key]
    _config = current
    mw.addonManager.writeConfig(__name__, current)
