#!/usr/bin/env python3
"""Build the selected Coral profile for GitHub in all four theme/size variants."""
from pathlib import Path
import build_radar_previews as radar
import build_radar_layouts as layouts

ROOT = Path(__file__).resolve().parents[1]


def main():
    radar.main()
    for theme in ('dark', 'light'):
        for mobile in (False, True):
            render = layouts.mobile if mobile else layouts.desktop
            source = render('toolkit', theme, 'coral')
            source = source.replace('B / Toolkit split | Gabriele Monni',
                                    'Gabriele Monni | Software engineer')
            source = source.replace('Local layout proposal with the existing ASCII portrait, confirmed profile information and the Braille radar.',
                                    'ASCII portrait, profile information and a Braille focus radar.')
            suffix = '-mobile' if mobile else ''
            path = ROOT / 'assets' / f'profile-{theme}{suffix}.svg'
            path.write_text(source)
            print(path.relative_to(ROOT))


if __name__ == '__main__':
    main()
