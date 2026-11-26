from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from aqt import mw

ADDON_ID = "passfail_king_buttons"

DEFAULTS: dict[str, Any] = {
    "button_count": 2,
    "enable_names": True,
    "again_name": "Fail",
    "hard_name": "Hard",
    "good_name": "Pass",
    "easy_name": "Easy",
    "color_mode": "colors",
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
    "button_font_size_px": 14,
    "button_height_px": 25,
    "button_width_px": 42,
    "answer_button_width_px": 530,
    "bottom_bar_height_px": 0,
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

_OLD_SIZE_MAPS = {
    "button_font_size": {"s": 14, "m": 16, "l": 20},
    "button_height": {"s": 25, "m": 40, "l": 60},
    "button_width": {"s": 42, "m": 82, "l": 122},
    "answer_button_width": {"full": 530, "normal": 120},
}

_config: dict[str, Any] | None = None


def _addon_dir() -> Path:
    return Path(mw.addonManager.addonsFolder(ADDON_ID))


def _meta_path() -> Path:
    return _addon_dir() / "meta.json"


def _defaults_path() -> Path:
    return _addon_dir() / "config.json"


def _load_defaults() -> dict[str, Any]:
    try:
        with _defaults_path().open(encoding="utf-8") as f:
            value = json.load(f)
        if isinstance(value, dict):
            defaults = deepcopy(DEFAULTS)
            defaults.update(value)
            return defaults
    except Exception:
        pass
    return deepcopy(DEFAULTS)


def _load_user_config_from_meta() -> dict[str, Any]:
    """Read Anki's persisted add-on config directly from meta.json.

    This deliberately bypasses any intermediary in-memory state so the Tools
    window sees changes made through Anki's built-in Add-ons > Config editor.
    """
    try:
        with _meta_path().open(encoding="utf-8") as f:
            meta = json.load(f)
        value = meta.get("config", {})
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _write_user_config(conf: dict[str, Any]) -> None:
    """Persist through Anki's API and leave meta.json as the source of truth."""
    mw.addonManager.writeConfig(ADDON_ID, deepcopy(conf))


def _normalise_legacy_size_keys(data: dict[str, Any], raw: dict[str, Any]) -> bool:
    changed = False
    for old_key, value_map in _OLD_SIZE_MAPS.items():
        new_key = f"{old_key}_px"
        if new_key in raw or old_key not in raw:
            continue
        old_value = str(raw.get(old_key, "")).lower()
        if old_value in value_map:
            data[new_key] = value_map[old_value]
            changed = True
    return changed


def _repair_blank_values(data: dict[str, Any]) -> bool:
    changed = False
    for key in DEFAULTS:
        if key in data and isinstance(data[key], str) and not data[key].strip():
            data[key] = deepcopy(DEFAULTS[key])
            changed = True
    return changed


def _try_get_addon_config(name: str) -> dict[str, Any]:
    try:
        value = mw.addonManager.getConfig(name)
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _migrate_old_addons(data: dict[str, Any], raw: dict[str, Any]) -> bool:
    if not data.get("migrate_old_settings", True):
        return False

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
            if old_key in old_pf and new_key not in raw:
                data[new_key] = old_pf[old_key]
                changed = True
        if "toggle_names_textcolors" in old_pf and "enable_names" not in raw:
            data["enable_names"] = bool(int(old_pf["toggle_names_textcolors"]))
            changed = True
        if "button_count" not in raw:
            data["button_count"] = 2
            changed = True

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
            "confirmation": "confirmation",
            "confirmation time": "confirmation_time",
            "confirmation x-offset": "confirmation_x_offset",
            "confirmation y-offset": "confirmation_y_offset",
            "outline": "outline",
            "style main screen buttons": "style_main_screen_buttons",
        }
        for old_key, new_key in king_map.items():
            if old_key in old_king and new_key not in raw:
                data[new_key] = old_king[old_key]
                changed = True

        size_mappings = {
            "button font size": "button_font_size_px",
            "button height": "button_height_px",
            "button width": "button_width_px",
            "answer button width": "answer_button_width_px",
        }
        for old_key, new_key in size_mappings.items():
            if new_key in raw or old_key not in old_king:
                continue
            value = old_king[old_key]
            converted = _OLD_SIZE_MAPS.get(new_key.removesuffix("_px"), {}).get(str(value).lower())
            if converted is not None:
                data[new_key] = converted
                changed = True

        if "button color" in old_king and "color_mode" not in raw:
            old_mode = str(old_king["button color"]).lower()
            if old_mode in {"default", "text", "hover", "colors"}:
                data["color_mode"] = old_mode
                changed = True

    if changed:
        data["migrate_old_settings"] = False
    return changed


def load(*, force: bool = False) -> dict[str, Any]:
    global _config
    if _config is None or force:
        defaults = _load_defaults()
        raw = _load_user_config_from_meta()
        merged = deepcopy(defaults)
        merged.update(raw)
        changed = _normalise_legacy_size_keys(merged, raw)
        changed = _repair_blank_values(merged) or changed
        changed = _migrate_old_addons(merged, raw) or changed
        _config = merged
        if changed:
            _write_user_config(_config)
    return _config


def reload() -> dict[str, Any]:
    return load(force=True)


def get(key: str, default: Any = None) -> Any:
    return load().get(key, default)


def all() -> dict[str, Any]:
    return deepcopy(load())


def update(values: dict[str, Any]) -> None:
    global _config
    current = load(force=True)
    for key in DEFAULTS:
        if key in values:
            current[key] = values[key]
    _repair_blank_values(current)
    _config = current
    _write_user_config(current)


def replace_external(conf: dict[str, Any]) -> None:
    """Update the in-memory copy after Anki's built-in Config editor saves."""
    global _config
    defaults = _load_defaults()
    merged = deepcopy(defaults)
    if isinstance(conf, dict):
        merged.update(conf)
    _config = merged
