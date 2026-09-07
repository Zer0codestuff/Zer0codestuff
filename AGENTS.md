# GitHub profile Neofetch

## Purpose and architecture
Profile README for `Zer0codestuff/Zer0codestuff`. A Python generator combines a real ASCII portrait with English profile information into four standalone SVG cards for desktop/mobile and light/dark themes. No website framework or hosted backend is needed. `preview.html` is a local preview, not a separate website.

## Build and preview
- Create a virtual environment and install `requirements.txt` when converting a photo.
- Run `python3 scripts/build_neofetch.py` to rebuild all SVGs from `assets/portrait-dark.txt`, `assets/portrait-light.txt` and `profile.json`. The default build uses only the standard library.
- Run `.venv/bin/python scripts/build_neofetch.py --photo /absolute/path/to/photo` to regenerate the portrait. Crop and silhouette coordinates target the user-supplied upright portrait.
- Run `python3 -m http.server 8765 --bind 127.0.0.1`, then open `/preview.html`.
- Inspect at desktop and mobile widths. Check SVG parsing, character grid dimensions and viewport bounds after changes.

## Current status and recent changes
Rebuilt from scratch in September 2026. Replaced old colored cards, old ASCII sources and stale statistics. The portrait now has 68 columns and 46 rows. Dark mode preserves the supplied photo's light/shadow polarity; light mode uses dark ink for shadows. The rejected 52-column negative portrait lost facial detail. Local sharpening and a moderate grid preserve eyes, eyebrows and mouth without returning to the original 104-column version. Profile content comes from https://gabrielemonni.me, checked on 2026-09-05. Compact sections use dotted leaders and right-aligned values, inspired by https://github.com/Andrew6rant/Andrew6rant. No source code or portrait from that repository is copied.

## Constraints
- Portrait characters remain monochrome. The information column uses orange labels, blue values, green headings and muted separators, following the latest user request. English artifact text. No em dashes.
- SVG backgrounds are transparent so they inherit GitHub's actual background. The preview uses Primer page backgrounds, dark `#0d1117` and light `#ffffff`. The README chooses theme and viewport variants with picture sources. GitHub theme settings need a final check after publication.
- Keep the supplied person's face recognizable while retaining visibly coarse ASCII characters.
- The original photo remains outside the repository. The generated text grids are the reproducible sources.
- Use real, relevant information from the user's site. The selected projects replace volatile GitHub statistics.
- A pre-existing untracked preview was preserved in ignored `.local/previous/preview.html` before replacement.

## Known issues and next steps
Desktop light/dark and dark mobile previews were visually inspected, with mobile image loading and viewport bounds checked. The local preview server was restarted on 2026-09-07 after it stopped responding. The user approved publishing this redesign on 2026-09-07. The newer remote profile change featuring gh-issue-scout is preserved in the Building row. Contact text inside the SVG is not independently clickable when embedded as an image; real contact links are below it in the README. GitHub rendering after publication still needs checking. The mobile card stacks portrait and information through a picture media source.

## Do not
- Reuse the rejected old design or ASCII portraits.
- Reintroduce an inverted dark-mode face, an overly dense photorealistic grid, fake statistics, invented interests, or decorative UI.
- Use a solid black card background that creates a visible rectangle against GitHub.
- Publish the original photo or ignored local files.
- Add generic profile widgets, decorative badges, counters, or unrelated sections.
- Remove the gh-issue-scout reference without a user request.
