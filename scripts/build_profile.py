#!/usr/bin/env python3
"""Build the four GitHub profile cards: desktop/mobile x dark/light.

Standard library only. Reads profile.json, the portrait grids in assets/ and
the embedded JetBrains Mono subsets. Writes assets/profile-*.svg.
"""
from pathlib import Path
from html import escape
from math import cos, pi, sin
import base64
import json

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'

# Portrait grid geometry, shared with scripts/portrait.py. Size is in px at natural width.
PORTRAIT = {'cols': 56, 'size': 14, 'pitch': 1.0, 'weight': 700}
ADVANCE = .6  # JetBrains Mono advance width, in em
FAMILY = "JBM,'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

THEMES = {
    'dark': {
        'page': '#0d1117', 'ink': '#ffffff',
        'accent': '#e86d7d', 'label': '#8cbfff', 'value': '#e2e6ee',
        'muted': '#8b949e', 'faint': '#484f58', 'grid': '#454d58', 'trace': '#8cbfff',
        'blocks': ['#e86d7d', '#b8475a', '#8cbfff', '#4f86c6', '#e2e6ee', '#8b949e', '#484f58', '#21262d'],
    },
    'light': {
        'page': '#ffffff', 'ink': '#111111',
        'accent': '#a3243c', 'label': '#123f78', 'value': '#101820',
        'muted': '#46515e', 'faint': '#8c959f', 'grid': '#a3adb8', 'trace': '#0b4fa3',
        'blocks': ['#a3243c', '#d9566d', '#123f78', '#4f86c6', '#101820', '#46515e', '#8c959f', '#d0d7de'],
    },
}


def font_faces():
    faces = []
    for weight, name in ((400, 'Regular'), (700, 'Bold')):
        data = base64.b64encode((ASSETS / 'fonts' / f'JetBrainsMonoNL-{name}.subset.woff2').read_bytes()).decode()
        faces.append(f'@font-face{{font-family:JBM;font-weight:{weight};src:url(data:font/woff2;base64,{data}) format("woff2")}}')
    return ''.join(faces)


def font_style():
    return f'<style>{font_faces()}</style>'


def enc(s):
    return escape(s).replace(' ', '&#160;')


class Card:
    def __init__(self, theme, width, height, profile):
        self.c = THEMES[theme]
        self.theme, self.width, self.height, self.profile = theme, width, height, profile
        self.parts = []

    def text(self, x, y, content, role='value', size=14, weight=400, anchor='start'):
        attrs = f' font-weight="{weight}"' if weight != 400 else ''
        attrs += f' text-anchor="{anchor}"' if anchor != 'start' else ''
        self.parts.append(f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="{self.c[role]}"{attrs}>{enc(content)}</text>')

    def spans(self, x, y, runs, size=14):
        """One line made of (text, role, weight) runs."""
        body = ''.join(
            f'<tspan fill="{self.c[role]}"' + (f' font-weight="{w}"' if w != 400 else '') + f'>{enc(t)}</tspan>'
            for t, role, w in runs)
        self.parts.append(f'<text x="{x:g}" y="{y:g}" font-size="{size}">{body}</text>')

    def prompt(self, x, y, command, size=13, cursor=False):
        p = self.profile
        runs = [(p['user'], 'accent', 700), ('@', 'muted', 400), (p['handle'], 'accent', 700),
                (' ~ ', 'label', 400), ('% ', 'muted', 400), (command, 'value', 400)]
        self.spans(x, y, runs, size)
        if cursor:
            cx = x + sum(len(t) for t, _, _ in runs) * size * ADVANCE
            self.parts.append(f'<rect class="cursor" x="{cx:.1f}" y="{y - size * .78:.1f}" '
                              f'width="{size * ADVANCE:.1f}" height="{size * .98:.1f}" fill="{self.c["value"]}"/>')

    def heading(self, x, y, title, size=14):
        self.text(x, y, title, 'accent', size, 700)

    def portrait(self, cx, y, max_width):
        """Draw the portrait grid with the drawn glyphs centered on cx. Returns its height."""
        cols, size, pitch = PORTRAIT['cols'], PORTRAIT['size'], PORTRAIT['pitch']
        natural = cols * size * ADVANCE
        # Same glyph size as the text column, like real terminal output, unless it would not fit.
        scale = min(1, max_width / natural)
        chars = (ASSETS / f'portrait-{self.theme}.txt').read_text().splitlines()
        assert all(len(r) == cols for r in chars)
        # Both themes share one horizontal anchor so the cards line up.
        grids = [(ASSETS / f'portrait-{t}.txt').read_text().splitlines() for t in THEMES]
        used = [i for g in grids for row in g for i, ch in enumerate(row) if ch != ' ']
        x = cx - (min(used) + max(used) + 1) / 2 * size * ADVANCE * scale
        lines = [f'<text y="{(r + .8) * size * pitch:.2f}" textLength="{natural:g}" '
                 f'lengthAdjust="spacingAndGlyphs">{enc(row)}</text>'
                 for r, row in enumerate(chars) if row.strip()]
        transform = f'translate({x:.2f} {y:g})' + (f' scale({scale:.4f})' if abs(scale - 1) > 1e-4 else '')
        self.parts.append(f'<g class="portrait" transform="{transform}" fill="{self.c["ink"]}" font-size="{size}" '
                          f'font-weight="{PORTRAIT["weight"]}" xml:space="preserve">' + '\n'.join(lines) + '</g>')
        # Height down to the last drawn row of either theme, so both cards share one layout.
        last = max(r for g in grids for r, row in enumerate(g) if row.strip())
        return (last + 1) * size * pitch * scale


    def blocks(self, x, y, size=14, width=3):
        cell = size * ADVANCE * width
        rects = ''.join(f'<rect x="{x + i * cell:.1f}" y="{y - size * .8:.1f}" width="{cell:.1f}" height="{size * 1.05:.1f}" '
                        f'fill="{color}"/>' for i, color in enumerate(self.c['blocks']))
        self.parts.append(f'<g>{rects}</g>')

    def radar(self, cx, cy, radius, axes, size=12, step=3.0):
        """Dotted radar on one square lattice: rings, spokes and the focus contour."""
        def vertex(i, v):
            a = i * pi / 3
            return cx + sin(a) * radius * v / 100, cy - cos(a) * radius * v / 100

        points = {}

        def line(a, b, role):
            # Integer line rasterization on the lattice keeps every segment connected.
            x0, y0 = (round(v / step) for v in a)
            x1, y1 = (round(v / step) for v in b)
            dx, dy = abs(x1 - x0), -abs(y1 - y0)
            sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
            err = dx + dy
            while True:
                if role == 'trace' or (x0, y0) not in points:
                    points[x0, y0] = role
                if (x0, y0) == (x1, y1):
                    break
                e2 = 2 * err
                if e2 >= dy:
                    err += dy
                    x0 += sx
                if e2 <= dx:
                    err += dx
                    y0 += sy

        for level in (25, 50, 75, 100):
            ring = [vertex(i, level) for i in range(6)]
            for a, b in zip(ring, ring[1:] + ring[:1]):
                line(a, b, 'grid')
        for i in range(6):
            line((cx, cy), vertex(i, 100), 'grid')
        shape = [vertex(i, ax['value']) for i, ax in enumerate(axes)]
        for a, b in zip(shape, shape[1:] + shape[:1]):
            line(a, b, 'trace')
        for role, glyph, gsize in (('grid', '·', 10), ('trace', '•', 9)):
            rows = {}
            for (px, py), kind in points.items():
                if kind == role:
                    rows.setdefault(py, []).append(px)
            out = []
            for py in sorted(rows):
                xs = sorted(rows[py])
                coords = ' '.join(f'{px * step:.1f}' for px in xs)
                # One glyph per lattice point: font spacing cannot bend the lines.
                out.append(f'<text x="{coords}" y="{py * step + gsize * .32:.1f}">{glyph * len(xs)}</text>')
            weight = ' font-weight="700"' if role == 'trace' else ''
            self.parts.append(f'<g fill="{self.c[role]}" font-size="{gsize}" text-anchor="middle"{weight}>'
                              + ''.join(out) + '</g>')
        sides = [(0, -1), (1, -1), (1, 1), (0, 1), (-1, 1), (-1, -1)]
        for i, ax in enumerate(axes):
            vx, vy = vertex(i, 100)
            ox, oy = sides[i]
            anchor = 'middle' if ox == 0 else ('start' if ox > 0 else 'end')
            lx = round(vx + ox * 14, 1)
            # Name baseline: above the top vertex, below the bottom one, level with the side ones.
            if ox == 0:
                ly = vy - 16 - size * 1.2 if oy < 0 else vy + 16 + size * .9
            else:
                ly = vy - size * .25
            self.text(lx, round(ly, 1), ax['label'], 'value', size, 700, anchor)
            self.text(lx, round(ly + size * 1.3, 1), str(ax['value']), 'label', size, 400, anchor)

    def svg(self, title, desc):
        style = ('<style>' + font_faces()
                 + f'text{{font-family:{FAMILY};font-variant-ligatures:none}}'
                 + '.cursor{animation:blink 1.2s steps(1) infinite}@keyframes blink{50%{opacity:0}}'
                 + '@media (prefers-reduced-motion:reduce){.cursor{animation:none}}</style>')
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" '
                f'viewBox="0 0 {self.width} {self.height}" role="img" aria-labelledby="title desc">'
                f'<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>{style}')
        return head + '\n' + '\n'.join(self.parts) + '\n</svg>\n'


def description(p):
    focus = '; '.join(f'{a["label"]} {a["value"]}' for a in p['focus'])
    projects = '; '.join(f'{name}: {desc}' for name, desc in p['building'] + p['work'])
    info = ' '.join(f'{k}: {v}.' for k, v in p['info'])
    return (f'Neofetch-style card with an ASCII portrait of {p["name"]}. {info} {" ".join(p["tagline"])} '
            f'Projects. {projects}. Focus radar with values {p["name"].split()[0]} chose, out of 100: {focus}.')


def info_block(card, x, y, p, size=14, step=24):
    card.text(x, y, p['name'], 'accent', size + 4, 700)
    card.text(x, y + 16, '─' * len(p['name']), 'faint', size + 4)
    y += 46
    for key, value in p['info']:
        card.spans(x, y, [(key, 'label', 700), (': ', 'muted', 400), (value, 'value', 400)], size)
        y += step
    return y


def project_list(card, x, y, title, items, size=14, desc_size=13, gap=46):
    card.heading(x, y, title, size)
    y += 30
    for name, desc in items:
        card.text(x, y, name, 'label', size, 700)
        card.text(x, y + 19, desc, 'muted', desc_size)
        y += gap
    return y


def identity(c, x, y, p):
    """Name, neofetch rows, tagline and color blocks; returns the next free y."""
    y = info_block(c, x, y, p)
    c.text(x, y + 8, p['tagline'][0], 'muted', 13)
    c.text(x, y + 28, p['tagline'][1], 'muted', 13)
    c.blocks(x, y + 66)
    return y + 66


def focus(c, x, cx, y, p):
    """Focus heading and radar below y; returns the baseline of the closing prompt."""
    c.heading(x, y, 'Focus')
    c.radar(cx, y + 154, 100, p['focus'])
    return y + 326


def desktop(theme, p):
    # Two columns: ASCII visuals on the left, the neofetch text on the right.
    c = Card(theme, 880, 0, p)
    c.prompt(8, 20, 'neofetch')
    h = c.portrait(204, 48, 372)
    x = 420
    y = identity(c, x, 80, p)
    y = project_list(c, x, y + 56, 'Building now', p['building'], gap=48)
    y = project_list(c, x, y + 12, 'Selected work', p['work'], gap=48)
    # The closing prompt sits below whichever column ends lower.
    end = max(focus(c, 8, 204, 48 + h + 34, p), y + 12)
    c.prompt(8, end, '', cursor=True)
    c.height = round(end + 16)
    return c.svg(f'{p["name"]} | {p["info"][0][1]}', description(p))


def mobile(theme, p):
    c = Card(theme, 400, 0, p)
    c.prompt(20, 24, 'neofetch', 12)
    h = c.portrait(200, 48, 336)
    x = 20
    y = identity(c, x, 48 + h + 44, p)
    y = project_list(c, x, y + 56, 'Building now', p['building'])
    y = project_list(c, x, y + 12, 'Selected work', p['work'])
    end = focus(c, x, 200, y + 26, p)
    c.prompt(x, end, '', 12, cursor=True)
    c.height = round(end + 18)
    return c.svg(f'{p["name"]} | {p["info"][0][1]}', description(p))


def main():
    profile = json.loads((ROOT / 'profile.json').read_text())
    for theme in THEMES:
        for name, render in (('', desktop), ('-mobile', mobile)):
            path = ASSETS / f'profile-{theme}{name}.svg'
            path.write_text(render(theme, profile))
            print(path.relative_to(ROOT))


if __name__ == '__main__':
    main()
