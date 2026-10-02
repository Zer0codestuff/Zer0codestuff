# GitHub profile Neofetch

## Purpose and architecture
Profile README for `Zer0codestuff/Zer0codestuff`. Standard-library Python generates four transparent SVG cards: desktop/mobile in dark/light. The card reads as `neofetch` output: an ASCII portrait and a dotted focus radar on the left, the name, info rows, tagline, color blocks and projects on the right. Coral palette. No hosted backend or website framework.

- `profile.json`: all card text, projects and the six focus values (0 to 100).
- `assets/portrait-{dark,light}.txt`: 44 x 33 glyph grids on the classic ramp ` .:-=+*#%@`.
- `assets/fonts/`: JetBrains Mono NL subsets (Regular, Bold) embedded in every SVG as base64 WOFF2, with the OFL license.
- `scripts/build_profile.py`: builds the four cards. Standard library only.
- `scripts/check_cards.py`: parses the cards, checks IDs, fonts, radar labels and text bounds.
- `scripts/portrait.py`: optional photo to grid conversion (macOS, Pillow, NumPy).
- `scripts/segment_photo.swift`: Vision subject mask, person mask and pupils for the conversion.
- `scripts/subset_fonts.py`: optional. Rebuilds the font subsets with fonttools.
- `README.md`: picture sources pick theme and viewport (mobile at 600px and below). Real contact links sit below the card.
- `preview.html`: the README picture plus all four assets side by side.

## Build and validation
- `python3 scripts/build_profile.py`, then `python3 scripts/check_cards.py`.
- Portrait from the photo: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`, then `.venv/bin/python scripts/portrait.py --photo /absolute/path/to/photo.jpg`, then rebuild. The crop targets the supplied upright photo. Keep the photo outside the repository; masks are cached in ignored `.local/portrait-cache`.
- The conversion relights the shadowed half of the face from its mirror image, softens the photo, maps tone per theme with moderate local contrast, then quantizes each cell to one of ten glyphs, all fully opaque. Dark: glyph density follows skin brightness, hair keeps a faint floor. Light: ink follows darkness, and a faint dot marks the pale sweater so the shoulders keep their outline.
- Keep the portrait at 44 columns. On 2026-10-02 the user rejected a 70-column, opacity-calibrated version as too detailed and unsettling. Lower-resolution options (Andrew6rant-style 40 and 34 columns with a 70-glyph ramp, classic 36 and 30 columns) were compared and also declined in favor of the 44-column version.
- Preview: `python3 -m http.server 8765 --bind 127.0.0.1`, open `/preview.html`. Check dark/light at desktop width, at about 700px and at 390px.
- GitHub serves SVGs with `default-src 'none'`. The embedded data URI fonts still load in Chrome, Firefox and WebKit under that policy (tested locally on 2026-10-02). Fallback fonts keep the layout because portrait rows use `textLength`.

## Current status
Full redesign on 2026-10-02, at the user's request, replacing the previous Coral Toolkit card. The user approved the 44-column classic portrait and asked to publish it the same day.

- New portrait conversion from the original photo: 44 columns, large glyphs, ten tones. A first 70-column photographic version was rejected as too detailed; the coarse one keeps brows, eyes, nose, beard and the hair silhouette readable while looking like ASCII art.
- New layout: portrait and radar in the left column, all text in the right column. The portrait uses the text glyph size when it fits. The closing prompt sits below whichever column ends lower; desktop is 880 x 847, mobile 400 x 1552.
- New content from gabrielemonni.me and public repos, checked on 2026-10-02: info rows (role, work, study, base, code, stack, languages, web), the site tagline, Building now (WhisperDrop, AgentFiles, DwarfStar) and Selected work (MUVAD, AI Capability Signals, Video Edit Checker).
- Radar values unchanged: Local AI 92, Data analysis 80, Native apps 58, Automation 82, AI research 77, Multimodal AI 88. Same principle as the approved Braille radar: one square dot lattice, explicitly positioned glyphs, open contour, no fill. Dots are now the font's `·` and `•` because JetBrains Mono has no Braille block.
- A blinking cursor on the closing prompt is the only animation. A line-by-line reveal was tried and dropped: renderers that capture the first frame showed an empty card.
- Coral kept. The light accent moved from #781b30 to #a3243c so headings read as coral rather than wine.
- Removed the old generators (`build_neofetch.py`, `build_radar_*.py`) and `explorations/`. They remain in git history.

## Preferences and constraints
- English artifacts. No em dashes. Apply the unslop skill to prose.
- Monochrome portrait, coarse and simple: visible ASCII glyphs and a recognizable face, never photographic.
- Transparent SVG backgrounds. Preview backgrounds are GitHub dark #0d1117 and white.
- Coral: coral headings, blue labels and radar, neutral values. Light mode needs strong text and visible radar rings.
- Radar values are focus values the user chose. Never present them as measured skills or live GitHub statistics.
- Local QA, the original photo, masks and backups stay outside version control.
- Trailing spaces in portrait grids are intentional fixed-width padding.
- Commit or publish only when the user asks.

## Do not
- Reintroduce an inverted dark face or the dark grid printed as black on white.
- Return to pale light portraits or faint Coral light text and radar.
- Add yellow, orange or green accents to the Coral card.
- Reintroduce gh-issue-scout references.
- Add fake statistics, invented interests, badges, counters or unrelated widgets.
- Add a solid card background, filled radar texture, vertex stars, sidebar bars or uneven dot spacing.
- Return to a centered radar alone below the desktop profile.
- Add load-in animations that start hidden.
- Publish the original photo or ignored local files.
