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
import random
import re
import zlib

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'

# Portrait grid geometry, shared with scripts/portrait.py. Size is in px at natural width.
PORTRAIT = {'cols': 56, 'size': 14, 'pitch': 1.0, 'weight': 700}
ADVANCE = .6  # JetBrains Mono advance width, in em
FAMILY = "JBM,'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
# Intro, played once: cursor idles, `neofetch` is typed, Enter, then the output prints top
# down at `rate` seconds per pixel. Then the closing prompt loops: idle, type, hold, erase.
INTRO = {'idle': .5, 'enter': .35, 'rate': .0011}
TYPING = {'start': .9, 'hold': 6.5, 'rest': .6, 'erase': .035, 'seed': 7}


def keyframes(name, events, prop, length, end=None):
    """Step keyframes from (seconds, value) events; `end` is the 100% value (default: loop back)."""
    frames = ''.join(f'{100 * at / length:.3f}%{{{prop}:{value}}}' for at, value in events)
    return f'@keyframes {name}{{{frames}100%{{{prop}:{events[0][1] if end is None else end}}}}}'


def blinking(spans, length):
    """Cursor opacity events: blink inside the idle spans, solid elsewhere."""
    events = []
    for start, end in spans:
        at, on = start, 1
        while at < end - 1e-6:
            events.append((at, on))
            at, on = at + .53, 1 - on
        if end < length:
            events.append((end, 1))
    return events


def shown_at(at):
    """Attributes that keep an element hidden until `at` seconds, then show it."""
    return f' class="r" style="animation-delay:{at:.2f}s"'

THEMES = {
    # Azzurri: Italian green, white and red with an azzurro radar. The portrait stays neutral.
    'dark': {
        'page': '#0d1117', 'ink': '#ffffff',
        'accent': '#4cd17f', 'label': '#ff6b6b', 'value': '#f2f2f2',
        'muted': '#9aa0a6', 'faint': '#4a4e54', 'grid': '#3a404a', 'trace': '#4fa8ff',
        'blocks': ['#3fbf6a', '#3fbf6a', '#f2f2f2', '#f2f2f2', '#ff5a5a', '#ff5a5a', '#4fa8ff', '#4fa8ff'],
    },
    'light': {
        'page': '#ffffff', 'ink': '#111111',
        'accent': '#0f7a3a', 'label': '#c62828', 'value': '#151515',
        'muted': '#595959', 'faint': '#a0a0a0', 'grid': '#cccccc', 'trace': '#0b63c4',
        'blocks': ['#0f9a48', '#0f9a48', '#e8e8e8', '#e8e8e8', '#d32f2f', '#d32f2f', '#0b63c4', '#0b63c4'],
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
        self.parts, self.css = [], []
        self.printing = None  # (start seconds, top y) while drawing neofetch output

    def when(self, y):
        return self.printing[0] + max(0, y - self.printing[1]) * INTRO['rate']

    def at(self, y):
        return shown_at(self.when(y)) if self.printing else ''

    def text(self, x, y, content, role='value', size=14, weight=400, anchor='start'):
        attrs = f' font-weight="{weight}"' if weight != 400 else ''
        attrs += f' text-anchor="{anchor}"' if anchor != 'start' else ''
        self.parts.append(f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="{self.c[role]}"{attrs}{self.at(y)}>{enc(content)}</text>')

    def spans(self, x, y, runs, size=14):
        """One line made of (text, role, weight) runs."""
        body = ''.join(
            f'<tspan fill="{self.c[role]}"' + (f' font-weight="{w}"' if w != 400 else '') + f'>{enc(t)}</tspan>'
            for t, role, w in runs)
        self.parts.append(f'<text x="{x:g}" y="{y:g}" font-size="{size}"{self.at(y)}>{body}</text>')

    def prompt_runs(self, command=''):
        p = self.profile
        return [(p['user'], 'accent', 700), ('@', 'muted', 400), (p['handle'], 'accent', 700),
                (' ~ ', 'trace', 400), ('% ', 'muted', 400), (command, 'value', 400)]

    def prompt(self, x, y, command, size=13):
        self.spans(x, y, self.prompt_runs(command), size)

    def typed_command(self, x, y, command, size=13):
        """Type `command` once after the prompt and press Enter. Returns the Enter time in seconds."""
        self.prompt(x, y, '', size)
        cw = size * ADVANCE
        x0 = x + sum(len(t) for t, _, _ in self.prompt_runs()) * cw
        rng = random.Random(TYPING['seed'] + 1)
        t, shown = INTRO['idle'], []
        for ch in command:
            shown.append(t)
            t += .06 + rng.random() * .07
        enter = shown[-1] + INTRO['enter']
        for i, ch in enumerate(command):
            self.parts.append(f'<text x="{x0 + i * cw:.1f}" y="{y:g}" font-size="{size}" fill="{self.c["value"]}"'
                              f'{shown_at(shown[i])}>{enc(ch)}</text>')
        n = len(command)
        moves = [(0, 0)] + [(at, i + 1) for i, at in enumerate(shown)]
        # Hidden by default, so static renderers show a single cursor, on the closing prompt.
        self.parts.append(f'<rect class="ncur" opacity="0" x="{x0 + n * cw:.1f}" y="{y - size * .78:.1f}" '
                          f'width="{cw:.1f}" height="{size * .98:.1f}" fill="{self.c["value"]}"/>')
        self.css.append(keyframes('nm', [(at, f'translateX({(col - n) * cw:.1f}px)') for at, col in moves], 'transform', enter,
                                  'translateX(0px)')
                        + keyframes('nb', blinking([(0, INTRO['idle'])], enter), 'opacity', enter, 0)
                        + f'.ncur{{animation:nm {enter:.2f}s step-end both,nb {enter:.2f}s step-end both}}')
        return enter

    def typed_prompt(self, x, y, runs, size=13, delay=0):
        """A prompt that appears at `delay`, where someone types `runs` ((text, role) pairs),
        waits, erases it and starts over.

        Static renderers and reduced motion show the whole command with the cursor after it.
        """
        self.parts.append(f'<g{shown_at(delay)}>')
        self.prompt(x, y, '', size)
        cw = size * ADVANCE
        x0 = x + sum(len(t) for t, _, _ in self.prompt_runs()) * cw
        chars = [(ch, role) for text, role in runs for ch in text]
        n = len(chars)
        # Human rhythm: uneven keystrokes, a beat after spaces, a pause before a comment.
        rng = random.Random(TYPING['seed'])
        t, shown = TYPING['start'], []
        for ch, _ in chars:
            t += .45 if ch == '#' else 0
            shown.append(t)
            t += .05 + rng.random() * .08 + (.07 if ch == ' ' else 0)
        typed = shown[-1]
        erase = typed + TYPING['hold']
        gone = [erase + (n - 1 - i) * TYPING['erase'] for i in range(n)]
        cleared = erase + n * TYPING['erase']
        cycle = cleared + TYPING['rest']
        loop = f'{cycle:.2f}s step-end {delay:.2f}s infinite backwards'

        css = []
        for i, (ch, role) in enumerate(chars):
            if ch == ' ':
                continue
            self.parts.append(f'<text class="tk k{i}" x="{x0 + i * cw:.1f}" y="{y:g}" font-size="{size}" '
                              f'fill="{self.c[role]}">{enc(ch)}</text>')
            css.append(f'.k{i}{{animation:k{i} {loop}}}'
                       + keyframes(f'k{i}', [(0, 0), (shown[i], 1), (gone[i], 0)], 'opacity', cycle))
        # The cursor sits after the full command; the animation moves it back to where typing is.
        moves = sorted([(0, 0)] + [(at, i + 1) for i, at in enumerate(shown)] + [(at, i) for i, at in enumerate(gone)])
        css.append(keyframes('cm', [(at, f'translateX({(col - n) * cw:.1f}px)') for at, col in moves], 'transform', cycle))
        # Solid while keys are pressed, blinking while idle.
        idle = ((0, TYPING['start']), (typed + .05, erase), (cleared, cycle))
        css.append(keyframes('cb', blinking(idle, cycle), 'opacity', cycle))
        self.parts.append(f'<rect class="tcur" x="{x0 + n * cw:.1f}" y="{y - size * .78:.1f}" width="{cw:.1f}" '
                          f'height="{size * .98:.1f}" fill="{self.c["value"]}"/>')
        self.parts.append('</g>')
        self.css.append(''.join(css) + f'.tcur{{animation:cm {loop},cb {loop}}}')

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
                 f'lengthAdjust="spacingAndGlyphs"{self.at(y + (r + .8) * size * pitch * scale)}>{enc(row)}</text>'
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
        self.parts.append(f'<g{self.at(y)}>{rects}</g>')

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
                out.append(f'<text x="{coords}" y="{py * step + gsize * .32:.1f}"{self.at(py * step)}>{glyph * len(xs)}</text>')
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
                 + ''.join(self.css)
                 + '.r{animation:on .01s step-end both}@keyframes on{from{opacity:0}to{opacity:1}}'
                 + '@media (prefers-reduced-motion:reduce){.r,.tk,.tcur,.ncur{animation:none}}</style>')
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" '
                f'viewBox="0 0 {self.width} {self.height}" role="img" aria-labelledby="title desc">'
                f'<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>{style}')
        return head + '\n' + '\n'.join(self.parts) + '\n</svg>\n'


def description(p):
    focus = '; '.join(f'{a["label"]} {a["value"]}' for a in p['focus'])
    projects = '; '.join(f'{name}: {desc}' for name, desc in p['building'] + p['work'])
    info = ' '.join(f'{k}: {v}.' for k, v in p['info'])
    return (f'Neofetch-style card with an ASCII portrait of {p["name"]}. {info} {" ".join(p["tagline"])} '
            f'Projects. {projects}. Focus radar with values {p["name"].split()[0]} chose, out of 100: {focus}. '
            f'The last prompt types: {"".join(t for t, _ in p["typing"]["desktop"])}. The card links to {p["website"]}.')


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
    c.printing = (c.typed_command(8, 20, 'neofetch') + .1, 30)
    h = c.portrait(204, 48, 280)
    x = 420
    sections = identity(c, x, 80, p) + 56
    y = project_list(c, x, sections, 'Building now', p['building'], gap=48)
    y = project_list(c, x, y + 12, 'Selected work', p['work'], gap=48)
    # Focus lines up with Building now unless the portrait reaches lower.
    # The closing prompt sits below whichever column ends lower.
    end = max(focus(c, 8, 204, max(48 + h + 34, sections), p), y + 12)
    ready, c.printing = c.when(end), None
    c.typed_prompt(8, end, p['typing']['desktop'], delay=ready)
    c.height = round(end + 16)
    return c.svg(f'{p["name"]} | {p["info"][0][1]}', description(p))


def mobile(theme, p):
    c = Card(theme, 400, 0, p)
    c.printing = (c.typed_command(20, 24, 'neofetch', 12) + .1, 34)
    h = c.portrait(200, 48, 252)
    x = 20
    y = identity(c, x, 48 + h + 44, p)
    y = project_list(c, x, y + 56, 'Building now', p['building'])
    y = project_list(c, x, y + 12, 'Selected work', p['work'])
    end = focus(c, x, 200, y + 26, p)
    ready, c.printing = c.when(end), None
    c.typed_prompt(x, end, p['typing']['mobile'], 12, delay=ready)
    c.height = round(end + 18)
    return c.svg(f'{p["name"]} | {p["info"][0][1]}', description(p))


def stamp_readme():
    """Add a content hash to each card URL in README.md, so browsers and GitHub's
    five minute image cache cannot keep showing an old card after an update."""
    readme = ROOT / 'README.md'
    def versioned(match):
        return f'assets/{match[1]}?v={zlib.crc32((ASSETS / match[1]).read_bytes()):08x}'
    readme.write_text(re.sub(r'assets/(profile-[a-z-]+\.svg)(?:\?v=[0-9a-f]+)?', versioned, readme.read_text()))


def main():
    profile = json.loads((ROOT / 'profile.json').read_text())
    for theme in THEMES:
        for name, render in (('', desktop), ('-mobile', mobile)):
            path = ASSETS / f'profile-{theme}{name}.svg'
            path.write_text(render(theme, profile))
            print(path.relative_to(ROOT))
    stamp_readme()


if __name__ == '__main__':
    main()
