# GitHub profile Neofetch

## Purpose and architecture
Profile README for `Zer0codestuff/Zer0codestuff`. Standard-library Python generates four transparent SVG cards for desktop/mobile and dark/light themes. The selected composition is B / Toolkit split in Coral, with an ASCII portrait and a Braille focus radar. No hosted backend or website framework.

- `profile.json`: confirmed profile information and Building activities.
- `assets/portrait-{dark,light}.txt`: reproducible 68-column, 46-row ASCII grids.
- `explorations/radar/data.json`: six radar axes on a 0 to 100 scale.
- `explorations/radar/palettes.json`: palette definitions, including selected Coral.
- `scripts/build_neofetch.py`: entry point, photo conversion and shared portrait rendering.
- `scripts/build_profile.py`: builds the selected profile using the radar and layout modules.
- `README.md`: theme/viewport selection through picture sources, with contact links below.
- `preview.html`: local preview of the actual published assets.

## Build and validation
- `python3 scripts/build_neofetch.py` builds the selected four profile cards. No dependencies needed.
- `python3 scripts/build_profile.py` is an equivalent entry point.
- Optional photo conversion: create a virtual environment, install requirements.txt, then run `.venv/bin/python scripts/build_neofetch.py --photo /absolute/path/to/photo`. Crop and mask coordinates target the supplied upright photo. Keep the photo outside the repository.
- `--classic` explicitly builds the older profile without the radar. Do not use it for publication.
- `python3 -m http.server 8765 --bind 127.0.0.1`, then open `/preview.html`.
- Inspect light/dark desktop and mobile. Check SVG parsing, unique IDs, score labels, image loading and viewport bounds.
- To rebuild the historical local galleries, run `python3 scripts/build_radar_previews.py` and `python3 scripts/build_radar_layouts.py`. Generated exploration assets are ignored; gallery sources remain reproducible.

## Current status and recent changes
The user accepted Coral and the grayscale light portrait, and authorized publication on 2026-09-16 after adjusting the radar. Scores are Local AI 92, Data analysis 80, Native apps 58, Automation 82, AI research 77 and Multimodal AI 88. The user selected these profile focus values and requested removing the illustrative caption on 2026-09-17. The main assets now contain the approved layout and radar. Building includes Local AI tools and Native macOS apps; the former issue-scout reference is removed.

The user-supplied dark portrait remains unchanged. The light portrait uses shadow-dense ASCII characters with neutral grayscale ink and stronger glyphs in deep shadows. Copying the dark character grid into black ink on white was rejected because it looked like a negative. A pale light conversion was also rejected. Both generators share portrait_row to keep the accepted rendering consistent.

Coral uses red headings, blue labels/radar and neutral values. Light mode has stronger text, darker separators and radar rings. Braille uses explicitly positioned dots on a uniform lattice. Regular dot glyphs with a small matching stroke prevent bold-font artifacts in light mode. Profile content was sourced from gabrielemonni.me on 2026-09-05. Contact text in embedded SVGs is not independently clickable; real contact links are below the card.

Validation before publication: all four final SVGs parse, have unique IDs and the requested scores. Desktop and mobile in both themes were visually checked. At 390px, both mobile sources load without horizontal overflow. The selected build is reproducible from tracked sources without the original photo. Public rendering may vary with custom GitHub themes.

## Preferences and constraints
- English artifacts. No em dashes. Apply the unslop skill to prose.
- Monochrome portrait, visibly coarse ASCII and recognizable face. Keep the accepted crop and silhouette.
- Transparent SVG backgrounds. Preview backgrounds are GitHub dark #0d1117 and white.
- Keep approved toolkit-left/radar-right desktop geometry. Mobile stacks sections.
- Local QA, earlier backups and the original photo stay outside version control.
- Trailing spaces in portrait grids are intentional fixed-width padding.

## Do not
- Reintroduce the rejected old portrait, inverted dark face, or dark-grid-on-white negative.
- Restore the pale light portrait or faint Coral light text/radar.
- Add yellow, orange or green accents to the selected Coral card.
- Reintroduce gh-issue-scout references.
- Add fake statistics, invented interests, badges, counters or unrelated widgets.
- Describe the user-selected radar values as measured skills or live GitHub statistics.
- Add a solid card background, filled radar texture, vertex stars, sidebar bars or uneven Braille spacing.
- Return to a centered radar alone below the desktop profile.
- Publish the original photo, ignored local files or generated rejected design galleries.

## Score update, 2026-09-17
AI research is now 77. The user requested publication and removal of the visible illustrative caption. Braille SVG titles, descriptions and README alt text now describe profile focus values. The layout and remaining scores are unchanged.
