#!/usr/bin/env python3
"""Build cross-browser NeoFetch SVGs using one tspan per rendered line."""

from __future__ import annotations

from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASCII_SOURCE = ROOT / "assets" / "ascii-detail.txt"
OUTPUTS = {
    "dark": ROOT / "assets" / "neofetch-dark.svg",
    "light": ROOT / "assets" / "neofetch-light.svg",
}

ASCII_START_Y = 0.0
ASCII_LINE_HEIGHT = 10.7
PROFILE_ROWS = (
    (112, "Role", "AI / data / product engineer", "value"),
    (142, "Focus", "local-first & multimodal AI", "value"),
    (172, "Stack", "Python, TypeScript, Swift, JavaScript", "value"),
    (202, "Building", "gh-issue-scout and local AI tools", "value"),
    (232, "Location", "Italy", "value"),
    (262, "Contact", "LinkedIn | Email", "contact"),
)

STATS_ROWS = (
    (362, "GitHub", "374 contributions in the last year", "positive"),
    (392, "Repos", "15 original public projects", "value"),
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
        "ascii": "#f0f6fc",
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
        "ascii": "#24292f",
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


def ascii_layer(ascii_lines: list[str]) -> str:
    rows = []
    for index, characters in enumerate(ascii_lines):
        y = ASCII_START_Y + index * ASCII_LINE_HEIGHT
        rows.append(f'<tspan x="18" y="{y:.1f}">{escape(characters)}</tspan>')
    return '<text x="18" class="ascii">\n' + "\n".join(rows) + "\n  </text>"


def build_svg(theme_name: str, ascii_lines: list[str]) -> str:
    theme = THEMES[theme_name]
    ascii_art = ascii_layer(ascii_lines)
    profile_rows = "\n".join(info_row(*row) for row in PROFILE_ROWS)
    stats_rows = "\n".join(info_row(*row) for row in STATS_ROWS)
    header_rule = "-" * (72 - len("gabriele@zer0codestuff") - 1)
    stats_rule = "-" * (72 - len("- GitHub Stats -") - 1)

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="1200px" height="560px" viewBox="0 0 1200 560" font-size="15px" role="img" aria-labelledby="title desc">
  <title id="title">Gabriele Monni's NeoFetch profile</title>
  <desc id="desc">ASCII portrait with skills and GitHub statistics.</desc>
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
    .ascii {{ fill: {theme['ascii']}; font-size: 8.7px; }}
    text, tspan {{ white-space: pre; font-variant-ligatures: none; }}
  </style>
  <rect x="1" y="1" width="1198" height="558" rx="15" fill="{theme['background']}" stroke="{theme['border']}" stroke-width="2"/>
  {ascii_art}
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
    if len(ascii_lines) != 44 or max(map(len, ascii_lines)) > 72:
        raise ValueError("ASCII source must contain 44 lines of at most 72 columns")

    for theme_name, output_path in OUTPUTS.items():
        output_path.write_text(
            build_svg(theme_name, ascii_lines), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
