#!/usr/bin/env python3
"""Subset JetBrains Mono NL into the small WOFF2 files embedded in the cards.

Optional maintenance step. Needs fonttools and brotli:
    .venv/bin/pip install fonttools brotli
    .venv/bin/python scripts/subset_fonts.py /path/to/JetBrainsMono-2.304/fonts/ttf
"""
from pathlib import Path
import sys

from fontTools import subset

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'fonts'
# Printable ASCII plus the few symbols used by the cards.
TEXT = ''.join(chr(c) for c in range(32, 127)) + '·•●─━│┃╭╮╰╯├┤┬┴┼█▌▏→←↑↓'


def main():
    source = Path(sys.argv[1])
    OUT.mkdir(parents=True, exist_ok=True)
    for weight in ('Regular', 'Bold'):
        options = subset.Options()
        options.flavor = 'woff2'
        options.layout_features = []
        options.hinting = False
        options.desubroutinize = True
        font = subset.load_font(source / f'JetBrainsMonoNL-{weight}.ttf', options)
        subsetter = subset.Subsetter(options)
        subsetter.populate(text=TEXT)
        subsetter.subset(font)
        path = OUT / f'JetBrainsMonoNL-{weight}.subset.woff2'
        subset.save_font(font, path, options)
        print(path.relative_to(ROOT), path.stat().st_size, 'bytes')


if __name__ == '__main__':
    main()
