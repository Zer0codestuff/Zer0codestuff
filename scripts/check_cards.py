#!/usr/bin/env python3
"""Sanity checks for the generated cards. Standard library only.

Parses each SVG, checks unique IDs, the focus scores, the embedded fonts and
that every text line stays inside the canvas (the font is monospaced, so a
line is len(text) * size * 0.6 wide).
"""
from pathlib import Path
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = '{http://www.w3.org/2000/svg}'


def text_of(node):
    return ''.join(node.itertext()).replace('\xa0', ' ')


def check(path, profile):
    problems = []
    source = path.read_text()
    root = ET.fromstring(source)
    width, height = float(root.get('width')), float(root.get('height'))
    ids = [el.get('id') for el in root.iter() if el.get('id')]
    if len(ids) != len(set(ids)):
        problems.append('duplicate ids')
    if source.count('@font-face') != 2 or 'data:font/woff2;base64,' not in source:
        problems.append('embedded fonts missing')
    texts = [text_of(t) for t in root.iter(NS + 'text')]
    for axis in profile['focus']:
        if axis['label'] not in texts or str(axis['value']) not in texts:
            problems.append(f'radar label missing: {axis["label"]} {axis["value"]}')
    for node in root.iter(NS + 'text'):
        if node.get('textLength') or ' ' in (node.get('x') or ''):
            continue  # portrait rows and radar dots are positioned explicitly
        x = float(node.get('x', 0))
        size = float(node.get('font-size', 14))
        span = len(text_of(node)) * size * .6
        anchor = node.get('text-anchor', 'start')
        left = x - (span if anchor == 'end' else span / 2 if anchor == 'middle' else 0)
        y = float(node.get('y', 0))
        if left < 0 or left + span > width or y > height or y < size * .7:
            problems.append(f'out of bounds: {text_of(node)!r} at x={left:.0f}..{left + span:.0f}, y={y:.0f}')
    return problems, len(source)


def main():
    profile = json.loads((ROOT / 'profile.json').read_text())
    failed = False
    for path in sorted((ROOT / 'assets').glob('profile-*.svg')):
        problems, size = check(path, profile)
        status = 'ok' if not problems else 'FAIL'
        print(f'{status:4} {path.relative_to(ROOT)} ({size / 1024:.0f} KB)')
        for p in problems:
            print('     ', p)
        failed |= bool(problems)
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
