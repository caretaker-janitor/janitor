"""Render the terminal colour codes in logs as HTML."""

import re
from dataclasses import dataclass, replace
from typing import Optional

from markupsafe import Markup, escape

__all__ = ["ansi_to_html"]

# Escape sequences: CSI (ESC [ params intermediates final), OSC (ESC ] text,
# ended by BEL or ESC \) or another one, such as ESC ( B.
_ESCAPE_RE = re.compile(
    r"\x1b(?:\[([0-?]*)([ -/]*)([@-~])|\][^\x07\x1b]*(?:\x07|\x1b\\)?|[ -/]*[0-~])"
)
# Parameters of a colour code; others, such as "38:2::255:0:0", are left out.
_SGR_PARAMS_RE = re.compile(r"[0-9;]*\Z")

_BASIC_COLOURS = [
    "#000000",
    "#cd0000",
    "#00cd00",
    "#cdcd00",
    "#0000ee",
    "#cd00cd",
    "#00cdcd",
    "#e5e5e5",
]
_BRIGHT_COLOURS = [
    "#7f7f7f",
    "#ff0000",
    "#00ff00",
    "#ffff00",
    "#5c5cff",
    "#ff00ff",
    "#00ffff",
    "#ffffff",
]


def _xterm_colour(index: int) -> Optional[str]:
    if index < 8:
        return _BASIC_COLOURS[index]
    if index < 16:
        return _BRIGHT_COLOURS[index - 8]
    if index < 232:
        levels = [0, 95, 135, 175, 215, 255]
        index -= 16
        r, g, b = levels[index // 36], levels[index // 6 % 6], levels[index % 6]
        return f"#{r:02x}{g:02x}{b:02x}"
    if index < 256:
        grey = 8 + (index - 232) * 10
        return f"#{grey:02x}{grey:02x}{grey:02x}"
    return None


@dataclass(frozen=True)
class _Style:
    bold: bool = False
    italic: bool = False
    underline: bool = False
    fg: Optional[str] = None
    bg: Optional[str] = None

    def css(self) -> str:
        parts = []
        if self.bold:
            parts.append("font-weight: bold")
        if self.italic:
            parts.append("font-style: italic")
        if self.underline:
            parts.append("text-decoration: underline")
        if self.fg:
            parts.append(f"color: {self.fg}")
        if self.bg:
            parts.append(f"background-color: {self.bg}")
        return "; ".join(parts)


def _extended_colour(params: list[int]) -> tuple[Optional[str], int]:
    """Read a 38/48 colour; return it and the number of parameters used."""
    if params[:1] == [5] and len(params) >= 2:
        return _xterm_colour(params[1]), 2
    if params[:1] == [2] and len(params) >= 4:
        r, g, b = params[1:4]
        if max(r, g, b) > 255:
            return None, 4
        return f"#{r:02x}{g:02x}{b:02x}", 4
    return None, len(params)


def _apply_sgr(style: _Style, text: str) -> _Style:
    params = [int(p) if p else 0 for p in text.split(";")]
    i = 0
    while i < len(params):
        code = params[i]
        i += 1
        if code == 0:
            style = _Style()
        elif code == 1:
            style = replace(style, bold=True)
        elif code == 3:
            style = replace(style, italic=True)
        elif code == 4:
            style = replace(style, underline=True)
        elif code == 22:
            style = replace(style, bold=False)
        elif code == 23:
            style = replace(style, italic=False)
        elif code == 24:
            style = replace(style, underline=False)
        elif 30 <= code <= 37:
            style = replace(style, fg=_BASIC_COLOURS[code - 30])
        elif code == 39:
            style = replace(style, fg=None)
        elif 40 <= code <= 47:
            style = replace(style, bg=_BASIC_COLOURS[code - 40])
        elif code == 49:
            style = replace(style, bg=None)
        elif 90 <= code <= 97:
            style = replace(style, fg=_BRIGHT_COLOURS[code - 90])
        elif 100 <= code <= 107:
            style = replace(style, bg=_BRIGHT_COLOURS[code - 100])
        elif code in (38, 48):
            colour, used = _extended_colour(params[i:])
            i += used
            if colour is not None:
                if code == 38:
                    style = replace(style, fg=colour)
                else:
                    style = replace(style, bg=colour)
    return style


def ansi_to_html(lines: list[str]) -> list[Markup]:
    """Convert log lines with terminal colour codes to HTML.

    Colours and bold, italic and underlined text become styled spans; a style
    carries over to the next line until it is reset. Other escape sequences,
    such as cursor movement, are left out. Each line loses its line ending.
    """
    style = _Style()
    ret = []
    for line in lines:
        line = line.rstrip("\n")
        out = []
        pos = 0
        for m in [*_ESCAPE_RE.finditer(line), None]:
            end = m.start() if m else len(line)
            if end > pos:
                css = style.css()
                text = escape(line[pos:end])
                if css:
                    out.append(Markup('<span style="{}">{}</span>').format(css, text))
                else:
                    out.append(text)
            if m is None:
                break
            pos = m.end()
            if (
                m.group(3) == "m"
                and not m.group(2)
                and _SGR_PARAMS_RE.match(m.group(1))
            ):
                style = _apply_sgr(style, m.group(1))
        ret.append(Markup("").join(out))
    return ret
