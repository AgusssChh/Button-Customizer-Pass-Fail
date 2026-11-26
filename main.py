from __future__ import annotations

import json

from aqt import gui_hooks, mw
from aqt.qt import *
from aqt.reviewer import ReviewerBottomBar

from . import config
from .button_logic import replace_buttons, remap_answer
from .confirmation import init as init_confirmation
from .styles import build_css

_STYLE_ID = "pfk-styles"
_MENU_ACTION = None
_REGISTERED = False


def _current_css() -> str:
    return build_css(config.load())


def on_webview_will_set_content(web_content, context) -> None:
    if not isinstance(context, ReviewerBottomBar):
        return
    c = config.load()
    if not c.get("style_main_screen_buttons", True) and int(c.get("bottom_bar_height_px", 0)) <= 0:
        return
    web_content.head += f"<style id='{_STYLE_ID}'>{_current_css()}</style>"


def _refresh_style() -> None:
    bottom = getattr(mw, "bottomWeb", None)
    if not bottom:
        return
    c = config.load()
    css = _current_css()
    if not c.get("style_main_screen_buttons", True) and int(c.get("bottom_bar_height_px", 0)) <= 0:
        css = ""
    payload = json.dumps(css)
    remove_style = css == ""
    js = f"""
    (() => {{
      const old = document.getElementById({_STYLE_ID!r});
      if ({str(remove_style).lower()}) {{
        if (old) old.remove();
        return;
      }}
      const css = {payload};
      if (old) old.textContent = css;
      else {{
        const n = document.createElement('style');
        n.id = {_STYLE_ID!r};
        n.textContent = css;
        document.head.appendChild(n);
      }}
    }})();
    """
    try:
        bottom.eval(js)
        if hasattr(bottom, "adjustHeightToFit"):
            bottom.adjustHeightToFit()
    except Exception:
        pass


def _refresh_reviewer() -> None:
    reviewer = getattr(mw, "reviewer", None)
    if reviewer is None:
        return
    try:
        if getattr(reviewer, "state", None) == "answer":
            reviewer._showEaseButtons()
        elif getattr(reviewer, "state", None) == "question":
            reviewer._showAnswerButton()
    except Exception:
        pass


def _open_settings() -> None:
    # Always discard the add-on's cached copy and read the persisted meta.json
    # value. This makes Tools -> Button Customizer reflect changes made in
    # Anki's built-in Add-ons -> Config editor immediately.
    config.reload()
    from .settings import SettingsDialog

    dialog = SettingsDialog(mw)
    dialog.exec()


def _config_updated_by_anki(new_conf) -> None:
    config.replace_external(new_conf)
    _refresh_style()
    _refresh_reviewer()


def _add_tools_menu() -> None:
    global _MENU_ACTION
    menu = getattr(getattr(mw, "form", None), "menuTools", None)
    if menu is None or _MENU_ACTION is not None:
        return
    _MENU_ACTION = QAction("Button Customizer + Pass/Fail…", mw)
    _MENU_ACTION.triggered.connect(_open_settings)
    menu.addAction(_MENU_ACTION)


def apply_settings_now() -> None:
    _refresh_style()
    _refresh_reviewer()


def init() -> None:
    global _REGISTERED
    config.load()
    if _REGISTERED:
        return
    gui_hooks.reviewer_will_init_answer_buttons.append(replace_buttons)
    gui_hooks.reviewer_will_answer_card.append(remap_answer)
    gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
    if hasattr(gui_hooks, "theme_did_change"):
        gui_hooks.theme_did_change.append(_refresh_style)
    if hasattr(mw.addonManager, "setConfigUpdatedAction"):
        mw.addonManager.setConfigUpdatedAction(__name__, _config_updated_by_anki)
    if hasattr(gui_hooks, "main_window_did_init"):
        gui_hooks.main_window_did_init.append(_add_tools_menu)
    else:
        _add_tools_menu()
    init_confirmation()
    _REGISTERED = True
