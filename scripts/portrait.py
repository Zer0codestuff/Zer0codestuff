#!/usr/bin/env python3
"""Convert the portrait photo into the ASCII grids assets/portrait-{dark,light}.txt.

Optional step. The default build only needs the committed grids.
Needs macOS (Vision, through scripts/segment_photo.swift), Pillow and NumPy:
    python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
    .venv/bin/python scripts/portrait.py --photo /absolute/path/to/photo.jpg

Keep the photo outside the repository. Masks and landmarks are cached in
.local/portrait-cache, which is ignored by git.
"""
from pathlib import Path
import argparse
import json
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

from build_profile import PORTRAIT

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.local' / 'portrait-cache'
WORK_WIDTH = 1224
# Crop in working pixels (photo resized to 1224 px wide): hair, face and collar.
# The top edge puts both eyes in the middle of one glyph row, not across two.
CROP = (230, 334, 1090, 1394)
# Classic ramp, light to dense. Coarse on purpose: it should read as ASCII art.
RAMP = ' .:-=+*#%@'
CELL_W = 8
SMOOTH = .35  # pre-blur, in cells, so single pixels do not become noisy glyphs
TONE = {
    # Tone = mix of the photo and its smooth illumination, plus local contrast.
    # Dark: glyph density follows skin brightness; hair keeps a faint floor.
    'dark': dict(lo=.12, hi=.80, floor=.18, gamma=1.2, detail=2.0, mix=.5, dots=0),
    # Light: ink follows darkness, so hair is dense and the face stays open.
    # Dots mark the pale sweater so the shoulders keep their outline.
    'light': dict(lo=.20, hi=.75, floor=0, gamma=1.1, detail=1.7, mix=.4, dots=.12),
}
# Both eye openings end at this share of the darker eye's brightness. Relighting
# lifts the shadowed eye too, which made it read as closed.
EYE_DEPTH = .7
FADE_START, FADE_POWER = .62, 2.0
# Soft elliptical falloff that rounds off the shoulders: center and radii in crop units.
# The horizontal center follows the chin.
VIGNETTE = (.5, .36, .78, .74, .3)
# Bust symmetry starts half a row above the chin and is complete three rows later.
BUST_BLEND = (.5, 3)


def blur(a, sigma):
    if sigma <= 0:
        return a
    r = int(sigma * 3)
    k = np.exp(-np.arange(-r, r + 1) ** 2 / (2 * sigma ** 2))
    k /= k.sum()
    a = np.pad(a, r, mode='edge')
    a = np.apply_along_axis(np.convolve, 1, a, k, 'valid')
    return np.apply_along_axis(np.convolve, 0, a, k, 'valid')


def masked_blur(a, m, sigma):
    return blur(a * m, sigma) / np.clip(blur(m, sigma), 1e-4, None)


def resize(a, size):
    img = Image.fromarray(np.clip(a * 65535, 0, 65535).astype(np.uint16))
    return np.asarray(img.resize(size, Image.Resampling.LANCZOS), dtype=np.float64) / 65535


def segment(photo):
    key = CACHE / f'{photo.stem}-{int(photo.stat().st_mtime)}'
    face = key / 'face.json'
    if not face.exists() or 'leftEye' not in json.loads(face.read_text()):
        subprocess.run(['swift', str(ROOT / 'scripts' / 'segment_photo.swift'), str(photo), str(key)], check=True)
    return key


def load(photo):
    cache = segment(photo)
    image = ImageOps.exif_transpose(Image.open(photo)).convert('RGB')
    scale = WORK_WIDTH / image.width
    size = (WORK_WIDTH, round(image.height * scale))
    rgb = np.asarray(image.resize(size, Image.Resampling.LANCZOS), dtype=np.float64) / 255
    lum = rgb @ np.array([.2126, .7152, .0722])
    subject = np.asarray(Image.open(cache / 'subject.png').convert('L').resize(size, Image.Resampling.LANCZOS)) / 255
    person = np.asarray(Image.open(cache / 'person.png').convert('L').resize(size, Image.Resampling.LANCZOS)) / 255
    # The subject mask has the cleaner outline; person adds loose strands.
    mask = np.maximum(subject, np.clip((person - .35) / .5, 0, 1) * .8)
    face = json.loads((cache / 'face.json').read_text())
    points = {k: np.array(face[k]) * scale for k in ('leftPupil', 'rightPupil', 'leftEye', 'rightEye')}
    # The median line ends at the chin.
    points['chin'] = np.array(face['medianLine'][-1]) * scale
    return lum, mask, points


def relight(lum, mask, face):
    """Lift the shadowed side of the face towards its mirror image."""
    left, right = face['leftPupil'][0], face['rightPupil'][0]
    eyes = (left + right) / 2
    span = np.linalg.norm(right - left)
    cx, cy, rx, ry = eyes[0], eyes[1] + .6 * span, 1.5 * span, 1.8 * span
    base = masked_blur(lum, np.clip(mask, 1e-3, 1), .25 * span)
    h, w = lum.shape
    mirror = base[:, np.clip(np.round(2 * cx - np.arange(w)).astype(int), 0, w - 1)]
    gain = np.clip(np.maximum(base, mirror) / np.maximum(base, 1e-3), 1, 2.5)
    yy, xx = np.mgrid[0:h, 0:w]
    weight = np.clip((1.3 - ((xx - cx) / rx) ** 2 - ((yy - cy) / ry) ** 2) / .6, 0, 1)
    return np.clip(lum * (1 + (gain - 1) * weight), 0, 1)


def balance_eyes(lum, face):
    """Give both eye openings the same darkness, so neither looks closed."""
    h, w = lum.shape
    masks, means = [], []
    for key in ('leftEye', 'rightEye'):
        shape = Image.new('L', (w, h))
        ImageDraw.Draw(shape).polygon([tuple(p) for p in face[key]], fill=255)
        m = np.asarray(shape.filter(ImageFilter.GaussianBlur(4)), dtype=np.float64) / 255
        masks.append(m)
        means.append((lum * m).sum() / m.sum())
    target = min(means) * EYE_DEPTH
    for m, mean in zip(masks, means):
        lum = lum * (1 + (target / mean - 1) * m)
    return lum


def tone(lum, mask, face, theme, cols, rows, ch):
    """Ink amount per pixel, 0 to 1, for one theme."""
    W, H = cols * CELL_W, rows * ch
    x0, y0, x1, y1 = CROP
    axis = (face['chin'][0] - x0) / (x1 - x0)
    lum = resize(lum[y0:y1, x0:x1], (W, H))
    mask = np.clip(resize(mask[y0:y1, x0:x1], (W, H)), 0, 1)
    soft = np.clip(mask, 1e-3, 1)
    lum = masked_blur(lum, soft, SMOOTH * CELL_W)
    base = masked_blur(lum, soft, 3 * CELL_W)
    t = TONE[theme]
    mixed = lum * (1 - t['mix']) + base * t['mix']
    span = t['hi'] - t['lo']
    if theme == 'dark':
        b = np.clip((mixed - t['lo']) / span, 0, 1)
        out = t['floor'] + (1 - t['floor']) * b ** t['gamma'] + t['detail'] * (lum - base)
    else:
        b = np.clip((t['hi'] - mixed) / span, 0, 1)
        out = t['floor'] + (1 - t['floor']) * b ** t['gamma'] - t['detail'] * (lum - base)
    # The body is turned a little in the photo, so the bust leaned right of the chin.
    # Below the chin, mirror it around the chin's vertical axis: centered, level shoulders.
    chin = (face['chin'][1] - y0) / (y1 - y0) * H
    mirror = np.clip(np.round(2 * axis * W - np.arange(W)).astype(int), 0, W - 1)
    w = np.clip((np.arange(H)[:, None] - chin + BUST_BLEND[0] * ch) / (BUST_BLEND[1] * ch), 0, 1)
    out = out * (1 - w) + (out + out[:, mirror]) / 2 * w
    mask = mask * (1 - w) + np.minimum(mask, mask[:, mirror]) * w
    yy = np.linspace(0, 1, H)[:, None]
    xx = np.linspace(0, 1, W)[None, :]
    _, vy, rx, ry, falloff = VIGNETTE
    vx = axis
    oval = np.clip((1 - np.sqrt(((xx - vx) / rx) ** 2 + ((yy - vy) / ry) ** 2)) / falloff, 0, 1)
    drop = np.clip((1 - yy) / (1 - FADE_START), 0, 1)
    fade = drop ** FADE_POWER * oval
    hard = np.clip((mask - .25) / .5, 0, 1)
    tone = np.clip(out, 0, 1) * hard * fade
    # Pale areas inside the silhouette keep a faint dot, so the outline survives.
    return np.maximum(tone, t['dots'] * hard * oval * drop ** .5)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--photo', type=Path, required=True)
    args = parser.parse_args()
    lum, mask, face = load(args.photo.expanduser().resolve())
    lum = balance_eyes(relight(lum, mask, face), face)
    cols, pitch = PORTRAIT['cols'], PORTRAIT['pitch']
    ch = round(CELL_W * pitch / .6)
    rows = round(cols * (CROP[3] - CROP[1]) / (CROP[2] - CROP[0]) * .6 / pitch)
    for theme in ('dark', 'light'):
        cells = tone(lum, mask, face, theme, cols, rows, ch).reshape(rows, ch, cols, CELL_W).mean(axis=(1, 3))
        level = np.clip(np.round(cells * (len(RAMP) - 1)), 0, len(RAMP) - 1).astype(int)
        text = '\n'.join(''.join(RAMP[v] for v in row) for row in level) + '\n'
        (ROOT / 'assets' / f'portrait-{theme}.txt').write_text(text)
        print(f'assets/portrait-{theme}.txt', f'{cols}x{rows}')


if __name__ == '__main__':
    main()
