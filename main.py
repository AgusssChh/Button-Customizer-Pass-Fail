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


def _current_css() -> str:
    return build_css(config.load())


def on_webview_will_set_content(web_content, context) -> None:
    if not isinstance(context, ReviewerBottomBar):
        return
    if not config.get("style_main_screen_buttons", True):
        return
    web_content.head += f"<style id='{_STYLE_ID}'>{_current_css()}</style>"


def _refresh_style() -> None:
    if not getattr(mw, "bottomWeb", None):
        return
    if not config.get("style_main_screen_buttons", True):
        js = f"document.getElementById({_STYLE_ID!r})?.remove();"
    else:
        css = json.dumps(_current_css())
        js = f"""
        (() => {{
          const s = document.getElementById({_STYLE_ID!r});
          if (s) s.textContent = {css};
          else {{
            const n = document.createElement('style');
            n.id = {_STYLE_ID!r};
            n.textContent = {css};
            document.head.appendChild(n);
          }}
        }})();
        """
    try:
        mw.bottomWeb.eval(js)
    except Exception:
        pass


def _refresh_reviewer() -> None:
    reviewer = getattr(mw, "reviewer", None)
    if reviewer is None:
        return
    try:
        if getattr(reviewer, "state", None) == "answer":
            reviewer._showEaseButtons()
    except Exception:
        pass


def _open_settings() -> None:
    from .settings import SettingsDialog
    dialog = SettingsDialog(mw)
    dialog.exec()


def _add_tools_menu() -> None:
    global _MENU_ACTION
    menu = getattr(getattr(mw, "form", None), "menuTools", None)
    if menu is None:
        return
    if _MENU_ACTION is not None:
        return
    _MENU_ACTION = QAction("Pass/Fail + KING Button Customizer…", mw)
    _MENU_ACTION.triggered.connect(_open_settings)
    menu.addAction(_MENU_ACTION)


def apply_settings_now() -> None:
    _refresh_style()
    _refresh_reviewer()


def init() -> None:
    config.load()
    gui_hooks.reviewer_will_init_answer_buttons.append(replace_buttons)
    gui_hooks.reviewer_will_answer_card.append(remap_answer)
    gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
    if hasattr(gui_hooks, "theme_did_change"):
        gui_hooks.theme_did_change.append(_refresh_style)
    if hasattr(gui_hooks, "main_window_did_init"):
        gui_hooks.main_window_did_init.append(_add_tools_menu)
    else:
        _add_tools_menu()
    init_confirmation()
