from __future__ import annotations

from . import config
from .button_logic import css_escape_color, configured_eases


def _sizes(c: dict):
    width = max(1, int(c.get("button_width_px", 42)))
    height = max(1, int(c.get("button_height_px", 25)))
    font = max(1, int(c.get("button_font_size_px", 14)))
    answer_width = max(1, int(c.get("answer_button_width_px", 530)))
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


def _button_color_css(c: dict, dark: bool, scope: str = "") -> str:
    mode = str(c.get("color_mode", "colors")).lower()
    if mode == "default":
        return ""

    colors = _colors(c, dark)
    parts: list[str] = []
    for ease in configured_eases(int(c.get("button_count", 2))):
        bg, text = colors[ease]
        selector = f'{scope} #middle button[data-ease="{ease}"]'.strip()
        parts.append(f"{selector} {{ color: {text} !important; }}")
        if mode == "colors":
            parts.append(f"{selector} {{ background: {bg} !important; }}")
        elif mode == "hover":
            parts.append(
                f"{selector}:hover {{ background: {bg} !important; color: {text} !important; }}"
            )
    return "\n".join(parts)


def _bottom_bar_css(c: dict) -> str:
    height = max(0, int(c.get("bottom_bar_height_px", 0)))
    if height <= 0:
        return ""
    return f"""
    html, body {{
        min-height: {height}px !important;
    }}
    #outer {{
        min-height: {height}px !important;
    }}
    #innertable, #innertable > tbody, #innertable > tbody > tr {{
        min-height: {height}px !important;
        height: {height}px !important;
    }}
    #innertable > tbody > tr > td {{
        min-height: {height}px !important;
        vertical-align: middle !important;
    }}
    """


def build_css(c: dict | None = None) -> str:
    c = c or config.load()
    answer_width, width, height, font, radius = _sizes(c)
    style_main = bool(c.get("style_main_screen_buttons", True))

    if style_main:
        light_colors = _button_color_css(c, False)
        dark_colors = _button_color_css(c, True, ".nightMode")
        dark_colors += "\n" + _button_color_css(c, True, ".night-mode")

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
            """
        else:
            outline = "#middle button:focus, #middle button:focus-visible, #middle button:active { outline: none !important; }"

        button_css = f"""
        #middle button, #ansbut, #middle + button, button[onclick*='edit'], button[onclick*='more'] {{
            min-height: {height}px;
            height: auto !important;
            font-size: {font}px;
            line-height: 1.15;
            border: solid 1px rgba(100,100,100,.2) !important;
            border-top: solid .5px #878787 !important;
            border-radius: {radius}px !important;
            -webkit-appearance: none;
            appearance: none;
            cursor: pointer;
            margin: 2px 6px 6px !important;
            box-shadow: 0 0 1.5px .2px #000 !important;
            -webkit-box-shadow: 0 0 1.5px .2px #000 !important;
            padding: 4px 6px !important;
            box-sizing: border-box;
        }}
        #ansbut {{
            width: {answer_width}px !important;
            text-align: center;
        }}
        #middle button {{
            min-width: {width}px;
            text-align: center !important;
            vertical-align: middle;
        }}
        #middle button .nobold {{
            display: block !important;
            line-height: 1.05 !important;
            margin-top: 2px !important;
            white-space: nowrap !important;
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
    else:
        button_css = ""

    return f"""
    /* Button Customizer + Pass/Fail */
    {button_css}
    {_bottom_bar_css(c)}
    """


def build_style_tag(c: dict | None = None) -> str:
    css = build_css(c)
    return f"<style id='pfk-styles'>{css}</style>"
