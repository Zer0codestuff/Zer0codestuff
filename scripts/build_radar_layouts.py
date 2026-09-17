#!/usr/bin/env python3
"""Build local profile composition proposals around the approved Braille radar."""
from pathlib import Path
from html import escape
import json
import textwrap
from build_neofetch import portrait_row
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'explorations/radar/layouts'
PROFILE = json.loads((ROOT / 'profile.json').read_text())
PALETTES = json.loads((ROOT / 'explorations/radar/palettes.json').read_text())
COLORS = {
    'dark': dict(ink='#ffffff', text='#f0f6fc', label='#ffa657', value='#a5d6ff', heading='#3fb950', muted='#6e7681'),
    'light': dict(ink='#000000', text='#1f2328', label='#953800', value='#0550ae', heading='#1a7f37', muted='#8c959f'),
}
PROJECTS = [
    ('MUVAD', 'Explainable video anomaly detection'),
    ('AI Capability Signals', 'Frontier-model research'),
    ('Video Edit Checker', 'Local video & audio analysis'),
]
NAMES = {'projects':'A / Project ledger', 'toolkit':'B / Toolkit split', 'compact':'C / Compact terminal'}


class Card:
    def __init__(self, name, theme, width, height, palette=None):
        self.theme, self.c = theme, dict(COLORS[theme])
        self.palette = palette
        self.strong_light = theme == 'light' and palette == 'coral'
        if palette:
            self.c.update(PALETTES[palette][theme])
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(NAMES[name])} | Gabriele Monni</title>',
            '<desc id="desc">Local layout proposal with the existing ASCII portrait, confirmed profile information and the Braille radar. Profile focus values selected by Gabriele Monni.</desc>',
            f'<g font-family="Menlo,Consolas,monospace" font-weight="{600 if self.strong_light else 400}" style="font-variant-ligatures:none">']

    def text(self, x, y, value, role='text', size=14, anchor='start'):
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{self.c[role]}" text-anchor="{anchor}">{escape(value)}</text>')

    def heading(self, x, y, value, width):
        self.text(x, y, value, 'heading')
        count = max(0, int(width/8.43)-len(value)-2)
        self.text(x+(len(value)+2)*8.43, y, '-'*count, 'muted')

    def row(self, x, y, key, value, width):
        self.text(x, y, key+':', 'label')
        count = max(0, int(width/8.43)-len(key)-len(value)-4)
        self.text(x+(len(key)+2)*8.43, y, '.'*count, 'muted')
        self.text(x+width, y, value, 'value', anchor='end')

    def block(self, x, y, title, lines, size=14):
        self.text(x, y, title, 'label', size)
        for i, line in enumerate(lines):
            self.text(x, y+24+i*21, line, 'value', size)

    def portrait(self, x, y, width):
        scale = width/390
        self.parts.append(f'<g fill="{self.c["ink"]}" font-size="9.7" font-weight="400" transform="translate({x} {y}) scale({scale})" xml:space="preserve">')
        lines = (ROOT/f'assets/portrait-{self.theme}.txt').read_text().splitlines()
        for i, line in enumerate(lines):
            encoded = portrait_row(line, self.theme)
            self.parts.append(f'<text x="0" y="{i*9.1:.1f}" textLength="390" lengthAdjust="spacingAndGlyphs">{encoded}</text>')
        self.parts.append('</g>')

    def radar(self, x, y, width, mobile=False):
        suffix = '-mobile' if mobile else ''
        source = (ROOT/f'explorations/radar/assets/braille-{self.theme}{suffix}.svg').read_text()
        root = ET.fromstring(source)
        # Nest the existing SVG verbatim, preserving every dot and its geometry.
        body = source[source.index('>')+1:source.rfind('</svg>')]
        body = body.replace('id="title"', 'id="radar-title"').replace('id="desc"', 'id="radar-desc"')
        if self.palette:
            original = {'dark': {'#f0f6fc':'text', '#8b949e':'muted', '#36404d':'grid', '#79b8d4':'trace'},
                        'light': {'#1f2328':'text', '#59636e':'muted', '#c2c8d0':'grid', '#12698d':'trace'}}
            for color, role in original[self.theme].items():
                if role in self.c:
                    body = body.replace(f'fill="{color}"', f'fill="{self.c[role]}"')
        if self.strong_light:
            # Keep the regular Braille glyph shape; bold fonts can expose
            # unwanted dots. Thicken only the existing dot outlines.
            import re
            body = re.sub(
                r'(<text [^>]*fill="([^"]+)"[^>]*)(>⠁)',
                lambda m: m[1] + f' font-weight="400" stroke="{m[2]}" stroke-width="{0.35 if m[2] == self.c["trace"] else 0.08}"' + m[3],
                body,
            )
        ratio = float(root.attrib['height'])/float(root.attrib['width'])
        self.parts.append(f'<svg x="{x}" y="{y}" width="{width}" height="{width*ratio}" viewBox="{root.attrib["viewBox"]}" role="img" aria-labelledby="radar-title radar-desc">{body}</svg>')

    def finish(self):
        return '\n'.join(self.parts+['</g></svg>'])+'\n'


def identity(card, x, y, width, rows):
    card.heading(x, y, 'gabriele@zer0codestuff', width)
    for i, (key, value) in enumerate(rows):
        card.row(x, y+42+i*25, key, value, width)


def contact(card, x, y, width):
    card.heading(x, y, 'Contact', width)
    for i, (key, value) in enumerate([('Website', PROFILE['website']), ('Email', PROFILE['email']), ('LinkedIn', 'in/hire-gabriele-monni')]):
        card.row(x, y+30+i*25, key, value, width)


def desktop(name, theme, palette=None):
    basic = [('Name', PROFILE['name']), ('Role', PROFILE['role']), ('Location', PROFILE['location']), ('Work', 'IT Technical Officer')]
    if name == 'projects':
        c = Card(name, theme, 1080, 930, palette)
        c.portrait(38, 60, 330)
        identity(c, 430, 38, 610, basic+[
            ('Languages.Code', 'Python, TypeScript, Swift, SQL'),
            ('Languages.Spoken', 'Italian, English'),
            ('Focus.AI', 'Multimodal systems, local inference'),
            ('Focus.Product', 'Native macOS apps, data products')])
        contact(c, 430, 307, 610)
        c.heading(38, 463, 'Selected work', 370)
        for i, (title, desc) in enumerate(PROJECTS):
            c.block(38, 510+i*85, title, textwrap.wrap(desc, 35))
        c.heading(38, 780, 'Building now', 370)
        c.text(38, 817, PROFILE['building'][0], 'value')
        c.text(38, 842, PROFILE['building'][1], 'value')
        c.radar(460, 424, 600)
    elif name == 'toolkit':
        c = Card(name, theme, 1080, 860, palette)
        c.portrait(58, 49, 285)
        identity(c, 410, 38, 630, basic+[
            ('Building', ' / '.join(PROFILE['building'])),
            ('Languages.Spoken', 'Italian, English')])
        c.heading(410, 265, 'Selected work', 630)
        for i, (title, desc) in enumerate(PROJECTS):
            c.row(410, 297+i*25, title, desc, 630)
        c.heading(38, 402, 'Toolkit', 445)
        c.block(38, 450, 'Languages', ['Python / TypeScript', 'Swift / SQL'])
        c.block(38, 542, 'Applied AI', ['Local inference', 'Multimodal systems'])
        c.block(264, 542, 'Products', ['Native macOS apps', 'Data products'])
        contact(c, 38, 683, 445)
        c.radar(530, 398, 520)
    else:
        c = Card(name, theme, 1080, 720, palette)
        c.portrait(28, 62, 270)
        identity(c, 350, 38, 690, basic+[
            ('Code', 'Python, TypeScript, Swift, SQL'),
            ('Spoken', 'Italian, English')])
        c.heading(350, 274, 'Building now', 245)
        c.text(350, 312, PROFILE['building'][0], 'value')
        c.text(350, 337, PROFILE['building'][1], 'value')
        c.heading(350, 390, 'Focus', 245)
        for i, value in enumerate(['Local inference', 'Multimodal systems', 'Native macOS apps', 'Data products']):
            c.text(350, 426+i*24, value, 'value')
        c.heading(28, 400, 'Selected work', 270)
        for i, (title, _) in enumerate(PROJECTS):
            c.text(28, 438+i*31, title, 'label')
        c.radar(615, 225, 440)
        contact(c, 350, 607, 690)
    return c.finish()


def mobile(name, theme, palette=None):
    c = Card(name, theme, 440, {'projects':1600, 'toolkit':1630, 'compact':1490}[name], palette)
    c.heading(24, 30, 'gabriele@zer0codestuff', 390)
    c.portrait(65, 70, 310)
    c.text(24, 421, PROFILE['name'], 'heading', 20)
    c.text(24, 451, PROFILE['role'], 'value', 17)
    c.text(24, 477, PROFILE['location'], 'value', 16)
    c.text(24, 512, 'IT Technical Officer', 'label', 16)
    if name == 'projects':
        c.heading(24, 566, 'Selected work', 390)
        for i, (title, desc) in enumerate(PROJECTS):
            c.block(24, 607+i*74, title, textwrap.wrap(desc, 35), 15)
        c.block(24, 839, 'Building now', PROFILE['building'], 15)
        c.text(24, 920, 'Python / TypeScript / Swift / SQL', 'value', 15)
        c.text(24, 950, 'Local inference / Multimodal systems', 'value', 15)
        c.text(24, 974, 'Native macOS apps / Data products', 'value', 15)
        c.radar(0, 1015, 440, True)
        end = 1480
    elif name == 'toolkit':
        c.heading(24, 566, 'Toolkit', 390)
        c.block(24, 607, 'Languages', ['Python / TypeScript / Swift / SQL'], 15)
        c.block(24, 680, 'Applied AI', ['Local inference / Multimodal systems'], 15)
        c.block(24, 753, 'Products', ['Native macOS apps / Data products'], 15)
        c.block(24, 826, 'Building now', PROFILE['building'], 15)
        c.heading(24, 915, 'Selected work', 390)
        for i, (title, _) in enumerate(PROJECTS):
            c.text(24, 950+i*25, title, 'label', 15)
        c.radar(0, 1055, 440, True)
        end = 1510
    else:
        c.block(24, 566, 'Building now', PROFILE['building'], 15)
        c.block(24, 640, 'Focus', ['Local inference / Multimodal systems', 'Native macOS apps / Data products'], 15)
        c.text(24, 740, 'Python / TypeScript / Swift / SQL', 'value', 15)
        c.heading(24, 787, 'Selected work', 390)
        for i, (title, _) in enumerate(PROJECTS):
            c.text(24, 819+i*25, title, 'label', 15)
        c.radar(0, 915, 440, True)
        end = 1370
    c.text(24, end, PROFILE['website'], 'value', 15)
    c.text(24, end+27, PROFILE['email'], 'value', 15)
    c.text(24, end+54, 'in/hire-gabriele-monni', 'value', 15)
    c.text(24, end+81, 'Italian / English', 'muted', 14)
    return c.finish()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name in NAMES:
        for theme in COLORS:
            (OUT/f'{name}-{theme}.svg').write_text(desktop(name, theme))
            (OUT/f'{name}-{theme}-mobile.svg').write_text(mobile(name, theme))
    palette_out = OUT.parent / 'palettes'
    palette_out.mkdir(exist_ok=True)
    for palette in PALETTES:
        for theme in COLORS:
            (palette_out/f'{palette}-{theme}.svg').write_text(desktop('toolkit', theme, palette))
            (palette_out/f'{palette}-{theme}-mobile.svg').write_text(mobile('toolkit', theme, palette))
    print(f'Built 12 layout SVGs and {len(PALETTES)*4} Toolkit palette SVGs')


if __name__ == '__main__':
    main()
