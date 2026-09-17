#!/usr/bin/env python3
"""Build four text-only radar explorations without changing the live profile.

All geometry is rasterized into characters, including the Braille and block
variants. SVG is only the portable text container. No chart paths or images.
"""

from html import escape
from math import ceil, cos, hypot, pi, sin
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "explorations/radar"
STYLES = {
    "wireframe": ("Wireframe", "ASCII / open contour"),
    "braille": ("Braille", "Unicode Braille / fine dots"),
    "phosphor": ("Phosphor", "ASCII / circular grid"),
    "pixel": ("Pixel", "Unicode blocks / stepped fill"),
}
PALETTES = {
    "dark": dict(text="#f0f6fc", label="#ffa657", trace="#a5d6ff",
                 green="#3fb950", muted="#8b949e", grid="#465361",
                 fill="#294862", phosphor="#1c6130", block="#3b6380"),
    "light": dict(text="#1f2328", label="#953800", trace="#0550ae",
                  green="#1a7f37", muted="#59636e", grid="#a2adb8",
                  fill="#b5cee6", phosphor="#b8d9bf", block="#9dbcd9"),
}
CX, CY, RADIUS = 300, 238, 164


def vertices(values):
    return [(CX + sin(i * pi / 3) * RADIUS * v / 100,
             CY - cos(i * pi / 3) * RADIUS * v / 100)
            for i, v in enumerate(values)]


def inside(x, y, points):
    # Ray casting also handles concave score profiles and zero-valued axes.
    hit = False
    for a, b in zip(points, points[1:] + points[:1]):
        if (a[1] > y) != (b[1] > y):
            if x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]:
                hit = not hit
    return hit


class Grid:
    def __init__(self, cw=7.2, ch=12):
        self.cw, self.ch = cw, ch
        self.cols, self.rows = ceil(600 / cw), ceil(464 / ch)
        self.cells = {}

    def put(self, x, y, char, role, priority=0):
        col, row = round(x / self.cw), round(y / self.ch)
        if not (0 <= col < self.cols and 0 <= row < self.rows):
            return
        old = self.cells.get((col, row))
        if old is None or priority >= old[2]:
            self.cells[col, row] = (char, role, priority)

    def line(self, a, b, role="grid", char=None, priority=1, dashed=False):
        dx, dy = b[0] - a[0], b[1] - a[1]
        if char is None:
            char = "-" if abs(dy) < abs(dx) * .35 else "|" if abs(dx) < abs(dy) * .3 else "\\" if dx * dy > 0 else "/"
        steps = ceil(hypot(dx, dy) / 2)
        for i in range(steps + 1):
            if dashed and i % 7 > 2:
                continue
            t = i / max(1, steps)
            self.put(a[0] + dx * t, a[1] + dy * t, char, role, priority)

    def polygon(self, points, **kwargs):
        for a, b in zip(points, points[1:] + points[:1]):
            self.line(a, b, **kwargs)

    def svg(self, palette):
        parts = []
        # Consecutive same-color cells share a text node to keep SVGs small.
        for row in range(self.rows):
            col = 0
            while col < self.cols:
                current = self.cells.get((col, row))
                if current is None:
                    col += 1
                    continue
                start, role, chars = col, current[1], []
                while col < self.cols:
                    cell = self.cells.get((col, row))
                    if cell is None or cell[1] != role:
                        break
                    chars.append(cell[0])
                    col += 1
                value = escape("".join(chars))
                parts.append(f'<text x="{start*self.cw:.2f}" y="{row*self.ch:.2f}" fill="{palette[role]}" font-size="{self.ch:.2f}" textLength="{len(chars)*self.cw:.2f}" lengthAdjust="spacingAndGlyphs">{value}</text>')
        return "\n".join(parts)

    def plain(self):
        return "\n".join("".join(self.cells.get((c, r), (" ",))[0]
                                 for c in range(self.cols)).rstrip()
                         for r in range(self.rows))


class Braille:
    BITS = ((1, 8), (2, 16), (4, 32), (64, 128))



class BrailleGrid(Grid):
    """One square dot lattice, independent of font cell bearings and run width."""

    STEP = 2.8

    def __init__(self):
        super().__init__(self.STEP * 2, self.STEP * 4)
        self.points = {}

    def line(self, a, b, role="grid"):
        x0, y0 = (round(v / self.STEP) for v in a)
        x1, y1 = (round(v / self.STEP) for v in b)
        dx, dy = abs(x1-x0), -abs(y1-y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        error = dx + dy
        while True:
            if role == "trace" or (x0, y0) not in self.points:
                self.points[x0, y0] = role
            if (x0, y0) == (x1, y1):
                break
            twice = 2 * error
            if twice >= dy:
                error += dy
                x0 += sx
            if twice <= dx:
                error += dx
                y0 += sy

    def svg(self, palette, dot_size=12):
        parts = []
        for role in ("grid", "trace"):
            for row in sorted({y for x, y in self.points}):
                xs = sorted(x for (x, y), kind in self.points.items()
                            if y == row and kind == role)
                if xs:
                    # A single-dot Braille glyph at each explicit coordinate
                    # avoids unequal dot gaps inside and between font cells.
                    coords = " ".join(f"{x*self.STEP:.1f}" for x in xs)
                    parts.append(f'<text x="{coords}" y="{row*self.STEP:.1f}" fill="{palette[role]}" font-size="{dot_size}">{"⠁"*len(xs)}</text>')
        return "\n".join(parts)

    def plain(self):
        cells = {}
        for x, y in self.points:
            key = x // 2, y // 4
            cells[key] = cells.get(key, 0) | Braille.BITS[y % 4][x % 2]
        return "\n".join("".join(chr(0x2800+cells.get((x,y),0))
                                 for x in range(self.cols)).rstrip("⠀")
                         for y in range(self.rows))


def make_chart(style, values):
    grid = Grid(7.2, 12) if style != "braille" else Grid(7.2, 14)
    shape = vertices(values)
    if style == "braille":
        grid = BrailleGrid()
        for level in (25, 50, 75, 100):
            ring = vertices([level] * 6)
            for a, b in zip(ring, ring[1:] + ring[:1]):
                grid.line(a, b)
        for v in vertices([100] * 6):
            grid.line((CX, CY), v)
        for a, b in zip(shape, shape[1:] + shape[:1]):
            grid.line(a, b, "trace")
        return grid
    elif style == "pixel":
        grid = Grid(7.2, 12)
        for row in range(grid.rows):
            for col in range(grid.cols):
                x, y = col * grid.cw, row * grid.ch
                upper = inside(x, y - 3, shape)
                lower = inside(x, y + 3, shape)
                if upper or lower:
                    edge = any(not inside(x+dx, y+dy, shape)
                               for dx, dy in ((-7, 0), (7, 0), (0, -8), (0, 8)))
                    char = "█" if upper and lower else "▀" if upper else "▄"
                    if not edge:
                        char = "░" if (col + row) % 3 else "▒"
                    grid.put(x, y, char, "trace" if edge else "block", 3 if edge else 0)
        for level in (25, 50, 75, 100):
            grid.polygon(vertices([level]*6), char="·", dashed=True, priority=1)
        for v in vertices([100]*6):
            grid.line((CX, CY), v, char="·", dashed=True)
        for x, y in shape:
            grid.put(x, y, "■", "label", 5)
    else:
        if style == "phosphor":
            for row in range(grid.rows):
                for col in range(grid.cols):
                    x, y = col*grid.cw, row*grid.ch
                    if inside(x, y, shape):
                        char = ":" if (col + row) % 3 else "+"
                        grid.put(x, y, char, "phosphor")
            for level in (25, 50, 75, 100):
                points = [(CX + sin(i*pi/90)*RADIUS*level/100,
                           CY - cos(i*pi/90)*RADIUS*level/100) for i in range(180)]
                grid.polygon(points, char=".", priority=1)
        else:
            for level in (25, 50, 75, 100):
                grid.polygon(vertices([level]*6), char=".", priority=1)
        for v in vertices([100]*6):
            grid.line((CX, CY), v, char=":" if style == "wireframe" else ".", priority=2)
        grid.polygon(shape, role="green" if style == "phosphor" else "trace",
                     char="#" if style == "phosphor" else None, priority=3)
        for x, y in shape:
            grid.put(x, y, "@" if style == "phosphor" else "o", "label", 5)
    grid.put(CX, CY, "+", "muted", 5)
    return grid


def text(x, y, content, color, size=16, anchor="start"):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" text-anchor="{anchor}">{escape(str(content))}</text>'


def build_braille(theme, axes, grid, mobile):
    p = dict(PALETTES[theme])
    p.update(grid="#36404d" if theme == "dark" else "#c2c8d0",
             trace="#79b8d4" if theme == "dark" else "#12698d")
    w, h = (440, 410) if mobile else (600, 490)
    desc = "; ".join(f'{a["label"]}: {a["value"]}/100' for a in axes)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
             '<title id="title">Braille focus radar</title>',
             f'<desc id="desc">Profile focus. {escape(desc)}. Rings at 25, 50, 75 and 100.</desc>',
             '<g font-family="Menlo,Consolas,monospace" style="font-variant-ligatures:none">']
    if mobile:
        parts += ['<g transform="translate(16 4) scale(.68)">', grid.svg(p, dot_size=16), '</g>']
        positions = [(220, 26, "middle"), (340, 100, "start"),
                     (340, 227, "start"), (220, 322, "middle"),
                     (100, 227, "end"), (100, 100, "end")]
        labels = [["Local AI"], ["Data", "analysis"], ["Native", "apps"],
                  ["Automation"], ["AI", "research"], ["Multimodal", "AI"]]
    else:
        parts.append(grid.svg(p))
        positions = [(300, 42, "middle"), (464, 151, "start"),
                     (464, 326, "start"), (300, 443, "middle"),
                     (136, 326, "end"), (136, 151, "end")]
        labels = [[a["label"]] for a in axes]
    for axis, lines, (x, y, anchor) in zip(axes, labels, positions):
        for line in lines:
            parts.append(text(x, y, line, p["text"], 15 if mobile else 16, anchor))
            y += 18
        parts.append(text(x, y, f'{axis["value"]}/100', p["muted"], 14, anchor))
    parts += ['</g></svg>']
    return "\n".join(parts) + "\n"


def build(style, theme, axes, grid, mobile=False):
    if style == "braille":
        return build_braille(theme, axes, grid, mobile)
    p = PALETTES[theme]
    name, technique = STYLES[style]
    width, height = (440, 760) if mobile else (900, 580)
    title = f"{name} radar | Illustrative profile values"
    description = "; ".join(f'{a["label"]}: {a["value"]}/100' for a in axes)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
             f'<title id="title">{escape(title)}</title>',
             f'<desc id="desc">Demonstration only, not measured skills. {escape(description)}. All axes use a 0 to 100 scale with 25-point rings.</desc>',
             '<g font-family="Menlo,Consolas,monospace" style="font-variant-ligatures:none" xml:space="preserve">',
             text(22, 30, "Focus.map", p["green"], 17),
             text(width-22, 30, "demo / 100", p["muted"], 13, "end")]
    scale, tx, ty = (.70, 10, 45) if mobile else (1, 0, 44)
    parts.append(f'<g transform="translate({tx} {ty}) scale({scale})">')
    parts.append(grid.svg(p))
    positions = [(300, 43, "middle"), (459, 155, "start"),
                 (459, 330, "start"), (300, 444, "middle"),
                 (141, 330, "end"), (141, 155, "end")]
    if not mobile:
        for axis, (x, y, anchor) in zip(axes, positions):
            parts.append(text(x, y, axis["label"], p["label"], 15, anchor))
    parts.append('</g>')
    if mobile:
        for i, (x, y, anchor) in enumerate(positions):
            parts.append(text(round(tx+x*scale, 1), round(ty+y*scale, 1),
                              f"{i+1:02}", p["label"], 19, anchor))
        start_x, start_y, span, spacing = 22, 414, 396, 44
    else:
        start_x, start_y, span, spacing = 636, 134, 238, 51
        parts.append(text(start_x, 95, "Focus areas", p["green"], 15))
    for i, axis in enumerate(axes):
        y = start_y + i * spacing
        if mobile:
            parts.append(text(start_x, y, f"{i+1:02}", p["label"], 18))
        parts.append(text(start_x+(36 if mobile else 0), y, axis["label"], p["text"], 18 if mobile else 14))
        parts.append(text(start_x+span, y, f'{axis["value"]:02}', p["trace"], 19 if mobile else 16, "end"))
        filled = round(axis["value"] / 5)
        glyph = "━" if style == "braille" else "■" if style == "pixel" else "#" if style == "phosphor" else "="
        parts.append(text(start_x, y+18, glyph*filled, p["green"] if style == "phosphor" else p["trace"], 11))
        parts.append(text(start_x+filled*6.62, y+18, "."*(20-filled), p["grid"], 11))
    footer_y = 717 if mobile else 520
    parts += [text(22, footer_y, "Scale 0 / 25 / 50 / 75 / 100", p["muted"], 12),
              text(22, footer_y+25, "Illustrative values. Design preview only.", p["muted"], 12),
              '</g></svg>']
    return "\n".join(parts) + "\n"


def main():
    data = json.loads((OUT / "data.json").read_text())
    axes = data["axes"]
    if len(axes) != 6 or data["scale"] != 100:
        raise ValueError("The exploration uses six axes on a 0 to 100 scale.")
    if any(type(a["value"]) not in (int, float) or not 0 <= a["value"] <= 100 for a in axes):
        raise ValueError("Each score must be a number from 0 to 100.")
    (OUT / "assets").mkdir(parents=True, exist_ok=True)
    for style in STYLES:
        grid = make_chart(style, [a["value"] for a in axes])
        source = "Illustrative values. Design preview only.\n" + "\n".join(
            f'{i+1}. {a["label"]}: {a["value"]}/100' for i, a in enumerate(axes))
        source += "\nAxes run clockwise, starting at the top. Rings: 25, 50, 75, 100.\n\n" + grid.plain() + "\n"
        (OUT / "assets" / f"{style}.txt").write_text(source)
        for theme in PALETTES:
            for mobile in (False, True):
                suffix = "-mobile" if mobile else ""
                path = OUT / "assets" / f"{style}-{theme}{suffix}.svg"
                path.write_text(build(style, theme, axes, grid, mobile))
    print("Built 16 SVG previews and 4 text grids in explorations/radar/assets")


if __name__ == "__main__":
    main()
