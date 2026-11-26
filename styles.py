from __future__ import annotations

from . import config
from .button_logic import css_escape_color, configured_eases


def _sizes(c: dict):
    answer_width = {"full": 530, "normal": 120}.get(str(c.get("answer_button_width", "full")).lower(), 120)
    width = {"s": 42, "m": 82, "l": 122}.get(str(c.get("button_width", "s")).lower(), 42)
    height = {"s": 25, "m": 40, "l": 60}.get(str(c.get("button_height", "s")).lower(), 25)
    font = {"s": 14, "m": 16, "l": 20}.get(str(c.get("button_font_size", "s")).lower(), 14)
    radius = max(0, int(c.get("border_radius", 15)))
    return answer_width, width, height, font, radius


def _colors(c: dict, dark: bool):
    p = "dark" if dark else "light"
    return {
        1: (
            css_escape_color(c.get(f"{p}_background_again"), "transparent"),
            css_escape_color(c.get(f"{p}_text_again"), "inherit"),
        ),
        2: (
            css_escape_color(c.get(f"{p}_background_hard"), "transparent"),
            css_escape_color(c.get(f"{p}_text_hard"), "inherit"),
        ),
        3: (
            css_escape_color(c.get(f"{p}_background_good"), "transparent"),
            css_escape_color(c.get(f"{p}_text_good"), "inherit"),
        ),
        4: (
            css_escape_color(c.get(f"{p}_background_easy"), "transparent"),
            css_escape_color(c.get(f"{p}_text_easy"), "inherit"),
        ),
    }


def _button_color_css(c: dict, dark: bool) -> str:
    mode = str(c.get("color_mode", "colors")).lower()
    colors = _colors(c, dark)
    selectors = {ease: f'#middle button[data-ease="{ease}"]' for ease in (1, 2, 3, 4)}
    parts: list[str] = []
    for ease in configured_eases(int(c.get("button_count", 2))):
        bg, text = colors[ease]
        selector = selectors[ease]
        parts.append(f"{selector} {{ color: {text} !important; }}")
        if mode == "colors":
            parts.append(f"{selector} {{ background: {bg} !important; }}")
        elif mode == "hover":
            parts.append(f"{selector}:hover {{ background: {bg} !important; color: {text} !important; }}")
    return "\n".join(parts)


def build_css(c: dict | None = None) -> str:
    c = c or config.load()
    answer_width, width, height, font, radius = _sizes(c)
    light_colors = _button_color_css(c, False)
    # Current Anki uses the ``night-mode`` class, while older Anki releases
    # used ``nightMode``. Emit both forms so dark-mode colors remain reliable.
    dark_colors = _button_color_css(c, True)
    dark_colors = dark_colors.replace("#middle", ".nightMode #middle", 1) + "\n" + dark_colors.replace("#middle", ".night-mode #middle", 1)

    if c.get("outline", True):
        ow = max(1, int(c.get("outline_width", 2)))
        oo = max(0, int(c.get("outline_offset", 2)))
        outline = f"""
        #middle button:focus,
        #middle button:focus-visible,
        #middle button:active {{
            outline: {ow}px solid currentColor !important;
            outline-offset: {oo}px !important;
        }}
        .nightMode #middle button:focus,
        .nightMode #middle button:focus-visible,
        .nightMode #middle button:active,
        .night-mode #middle button:focus,
        .night-mode #middle button:focus-visible,
        .night-mode #middle button:active {{
            outline: {ow}px solid currentColor !important;
            outline-offset: {oo}px !important;
        }}
        """
    else:
        outline = "#middle button:focus, #middle button:focus-visible, #middle button:active { outline: none !important; }"

    return f"""
    /* Pass/Fail + KING merged styles */
    #middle button, #ansbut, #middle + button, button[onclick*='edit'], button[onclick*='more'] {{
        height: {height}px;
        font-size: {font}px;
        border: solid 1px rgba(100,100,100,.2) !important;
        border-top: solid .5px #878787 !important;
        border-radius: {radius}px !important;
        -webkit-appearance: none;
        appearance: none;
        cursor: pointer;
        margin: 2px 6px 6px !important;
        box-shadow: 0 0 1.5px .2px #000 !important;
        -webkit-box-shadow: 0 0 1.5px .2px #000 !important;
    }}
    #ansbut {{
        width: {answer_width}px !important;
        text-align: center;
    }}
    #middle button {{
        min-width: {width}px;
        text-align: center !important;
    }}
    button[onclick*='edit'], button[onclick*='more'] {{ text-align: center; }}

    {light_colors}

    .nightMode button,
    .night-mode button {{
        box-shadow: 0 0 2.5px .5px #000 !important;
        -webkit-box-shadow: 0 0 2.5px .5px #000 !important;
    }}
    {dark_colors}

    .nobold {{ color: var(--fg, var(--text-fg)); }}
    {outline}
    """

def build_style_tag(c: dict | None = None) -> str:
    css = build_css(c)
    return f"<style id='pfk-styles'>#middle {{}}\n{css}</style>"
