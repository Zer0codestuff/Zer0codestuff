#!/usr/bin/env python3
"""Build cross-browser NeoFetch SVGs using one tspan per rendered line."""

from __future__ import annotations

from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASCII_SOURCE = ROOT / "assets" / "ascii-detail.txt"
TONE_SOURCE = ROOT / "assets" / "ascii-tones.txt"
OUTPUTS = {
    "dark": ROOT / "assets" / "neofetch-dark.svg",
    "light": ROOT / "assets" / "neofetch-light.svg",
}

ASCII_START_Y = 0.0
ASCII_LINE_HEIGHT = 10.7
TONE_LAYERS = tuple(
    (f"tone-{tone}", frozenset(str(tone))) for tone in range(10)
)

PROFILE_ROWS = (
    (112, "Role", "AI / data / product engineer", "value"),
    (142, "Focus", "local-first & multimodal AI", "value"),
    (172, "Stack", "Python, TypeScript, Swift, JavaScript", "value"),
    (202, "Building", "tools people can actually use", "value"),
    (232, "Location", "Italy", "value"),
    (262, "Contact", "LinkedIn | Email", "contact"),
)

STATS_ROWS = (
    (362, "GitHub", "322 contributions in the last year", "positive"),
    (392, "Repos", "13 original public projects", "value"),
    (422, "Shipping", "web, macOS, local AI", "value"),
)

THEMES = {
    "dark": {
        "background": "#161b22",
        "border": "#30363d",
        "text": "#c9d1d9",
        "key": "#ffa657",
        "value": "#a5d6ff",
        "positive": "#3fb950",
        "contact": "#ff7b72",
        "muted": "#616e7f",
        "tone-0": "#000000",
        "tone-1": "#181818",
        "tone-2": "#2a2a2a",
        "tone-3": "#424242",
        "tone-4": "#595959",
        "tone-5": "#727272",
        "tone-6": "#909090",
        "tone-7": "#aeaeae",
        "tone-8": "#cdcdcd",
        "tone-9": "#eeeeee",
        "host": "#3fb950",
    },
    "light": {
        "background": "#f6f8fa",
        "border": "#d0d7de",
        "text": "#24292f",
        "key": "#953800",
        "value": "#0550ae",
        "positive": "#1a7f37",
        "contact": "#cf222e",
        "muted": "#8c959f",
        "tone-0": "#000000",
        "tone-1": "#181818",
        "tone-2": "#2a2a2a",
        "tone-3": "#424242",
        "tone-4": "#595959",
        "tone-5": "#727272",
        "tone-6": "#909090",
        "tone-7": "#aeaeae",
        "tone-8": "#cdcdcd",
        "tone-9": "#eeeeee",
        "host": "#1a7f37",
    },
}


def info_row(y: int, label: str, value: str, value_class: str) -> str:
    prefix = f". {label}:"
    dot_count = max(2, 72 - len(prefix) - len(value) - 2)
    dots = " " + "." * dot_count + " "
    return (
        f'<tspan x="470" y="{y}" class="muted">. </tspan>'
        f'<tspan class="key">{escape(label)}</tspan>:'
        f'<tspan class="muted">{dots}</tspan>'
        f'<tspan class="{value_class}">{escape(value)}</tspan>'
    )


def ascii_layer(
    ascii_lines: list[str], tone_lines: list[str], css_class: str, tones: frozenset[str]
) -> str:
    rows = []
    for index, (characters, tone_map) in enumerate(zip(ascii_lines, tone_lines)):
        masked = "".join(
            character if tone in tones else " "
            for character, tone in zip(characters, tone_map)
        )
        y = ASCII_START_Y + index * ASCII_LINE_HEIGHT
        rows.append(f'<tspan x="18" y="{y:.1f}">{escape(masked)}</tspan>')
    return '<text x="18" class="ascii ' + css_class + '">\n' + "\n".join(rows) + "\n  </text>"


def build_svg(theme_name: str, ascii_lines: list[str], tone_lines: list[str]) -> str:
    theme = THEMES[theme_name]
    ascii_layers = "\n  ".join(
        ascii_layer(ascii_lines, tone_lines, css_class, tones)
        for css_class, tones in TONE_LAYERS
    )
    profile_rows = "\n".join(info_row(*row) for row in PROFILE_ROWS)
    stats_rows = "\n".join(info_row(*row) for row in STATS_ROWS)
    header_rule = "-" * (72 - len("gabriele@zer0codestuff") - 1)
    stats_rule = "-" * (72 - len("- GitHub Stats -") - 1)

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="1200px" height="560px" viewBox="0 0 1200 560" font-size="15px" role="img" aria-labelledby="title desc">
  <title id="title">Profilo NeoFetch di Gabriele Monni</title>
  <desc id="desc">Ritratto ASCII con competenze e statistiche GitHub.</desc>
  <style>
    @font-face {{
      src: local('Consolas'), local('Consolas Bold');
      font-family: 'ConsolasFallback';
      font-display: swap;
      -webkit-size-adjust: 109%;
      size-adjust: 109%;
    }}
    .key {{ fill: {theme['key']}; }}
    .value {{ fill: {theme['value']}; }}
    .positive {{ fill: {theme['positive']}; }}
    .contact {{ fill: {theme['contact']}; }}
    .muted {{ fill: {theme['muted']}; }}
    .host {{ fill: {theme['host']}; font-weight: 700; }}
    .ascii {{ font-size: 8.7px; }}
    .tone-0 {{ fill: {theme['tone-0']}; }}
    .tone-1 {{ fill: {theme['tone-1']}; }}
    .tone-2 {{ fill: {theme['tone-2']}; }}
    .tone-3 {{ fill: {theme['tone-3']}; }}
    .tone-4 {{ fill: {theme['tone-4']}; }}
    text, tspan {{ white-space: pre; font-variant-ligatures: none; }}
  </style>
  <rect x="1" y="1" width="1198" height="558" rx="15" fill="{theme['background']}" stroke="{theme['border']}" stroke-width="2"/>
  {ascii_layers}
  <text x="470" y="52" fill="{theme['text']}">
    <tspan x="470" y="52" class="host">gabriele@zer0codestuff</tspan><tspan class="muted"> {header_rule}</tspan>
{profile_rows}
    <tspan x="470" y="322">- GitHub Stats -</tspan><tspan class="muted"> {stats_rule}</tspan>
{stats_rows}
  </text>
</svg>
'''


def main() -> None:
    ascii_lines = ASCII_SOURCE.read_text(encoding="utf-8").splitlines()
    tone_lines = TONE_SOURCE.read_text(encoding="utf-8").splitlines()
    if len(ascii_lines) != 44 or max(map(len, ascii_lines)) > 72:
        raise ValueError("ASCII source must contain 44 lines of at most 72 columns")
    if len(tone_lines) != len(ascii_lines):
        raise ValueError("Tone map must contain one row for every ASCII row")
    if any(len(tones) != len(characters) for characters, tones in zip(ascii_lines, tone_lines)):
        raise ValueError("Tone-map rows must match the width of their ASCII rows")
    if any(set(tones) - set(" 0123456789") for tones in tone_lines):
        raise ValueError("Tone map may contain only spaces and digits 0-9")

    for theme_name, output_path in OUTPUTS.items():
        output_path.write_text(
            build_svg(theme_name, ascii_lines, tone_lines), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
