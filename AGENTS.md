# GitHub profile Neofetch

## Purpose and architecture
Profile README for `Zer0codestuff/Zer0codestuff`. Standard-library Python generates four transparent SVG cards: desktop/mobile in dark/light. The card reads as `neofetch` output: an ASCII portrait and a dotted focus radar on the left, the name, info rows, tagline, color blocks and projects on the right. Azzurri palette. No hosted backend or website framework.

- `profile.json`: all card text, projects and the six focus values (0 to 100).
- `assets/portrait-{dark,light}.txt`: 56 x 41 glyph grids on the classic ramp ` .:-=+*#%@`.
- `assets/fonts/`: JetBrains Mono NL subsets (Regular, Bold) embedded in every SVG as base64 WOFF2, with the OFL license.
- `scripts/build_profile.py`: builds the four cards. Standard library only.
- `scripts/check_cards.py`: parses the cards, checks IDs, fonts, radar labels and text bounds.
- `scripts/portrait.py`: optional photo to grid conversion (macOS, Pillow, NumPy).
- `scripts/segment_photo.swift`: Vision subject mask, person mask and pupils for the conversion.
- `scripts/subset_fonts.py`: optional. Rebuilds the font subsets with fonttools.
- `README.md`: picture sources pick theme and viewport (mobile at 600px and below). The whole card links to gabrielemonni.me. Nothing else sits below it: the user wants only the terminal card (contact links removed on 2026-10-02).
- `preview.html`: the README picture plus all four assets side by side.

## Build and validation
- `python3 scripts/build_profile.py`, then `python3 scripts/check_cards.py`.
- Portrait from the photo: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`, then `.venv/bin/python scripts/portrait.py --photo /absolute/path/to/photo.jpg`, then rebuild. The crop targets the supplied upright photo. Keep the photo outside the repository; masks are cached in ignored `.local/portrait-cache`.
- The conversion relights the shadowed half of the face from its mirror image, then gives both eye openings (Vision eye outlines) the same darkness, because relighting had lifted the shadowed eye until it read as closed. The crop's top edge keeps both eyes inside one glyph row. It then softens the photo, maps tone per theme with moderate local contrast, then quantizes each cell to one of ten glyphs, all fully opaque. Dark: glyph density follows skin brightness, hair keeps a faint floor. Light: ink follows darkness, and a faint dot marks the pale sweater so the shoulders keep their outline.
- Keep the portrait at 56 columns with the classic ramp. On 2026-10-02 the user rejected a 70-column, opacity-calibrated version as too detailed and unsettling. Lower-resolution options (Andrew6rant-style 40 and 34 columns, classic 36 and 30) were declined. Between 44 columns and the original 68, the user chose 56 over letter-ramp (56) and mixed-ramp (52) alternatives.
- Preview: `python3 -m http.server 8765 --bind 127.0.0.1`, open `/preview.html`. Check dark/light at desktop width, at about 700px and at 390px.
- GitHub serves SVGs with `default-src 'none'`. The embedded data URI fonts still load in Chrome, Firefox and WebKit under that policy (tested locally on 2026-10-02). Fallback fonts keep the layout because portrait rows use `textLength`.

## Current status
Full redesign on 2026-10-02, at the user's request, replacing the previous Coral Toolkit card. The user approved a 44-column classic portrait and asked to publish it the same day. Later on 2026-10-02 the user compared it with the original 68-column portrait, picked the 56-column middle ground (M1, same classic ramp) and raised Native apps from 58 to 72. The user then reported one eye looking closed; fixed with eye balancing and a 6 px crop shift. The user then shrank the portrait to 280 px wide (252 on mobile) and picked the Azzurri palette over Coral and six other red, green and blue palettes (GitHub, One Dark, ANSI, Pastel, Neon, Terra), keeping the portrait neutral. Contact links below the card were removed, and the closing prompt now types an invitation to open the site (option A of three). Published in commit 48ca328 and checked on the live profile (dark desktop). Right after a push, github.com/.../raw/ URLs can return 504 for a few minutes and browsers may cache the broken image: reload before debugging.

- New portrait conversion from the original photo: 56 columns, ten tones, fully opaque glyphs. A first 70-column photographic version was rejected as too detailed; the coarse one keeps brows, eyes, nose, beard and the hair silhouette readable while looking like ASCII art.
- New layout: portrait and radar in the left column, all text in the right column. The portrait is 280 px wide on desktop. Focus lines up with Building now unless the portrait reaches lower, and the closing prompt sits below whichever column ends lower; desktop is 880 x 828, mobile 400 x 1448.
- New content from gabrielemonni.me and public repos, checked on 2026-10-02: info rows (role, work, study, base, code, stack, languages, web), the site tagline, Building now (WhisperDrop, AgentFiles, DwarfStar) and Selected work (MUVAD, AI Capability Signals, Video Edit Checker).
- Radar values: Local AI 92, Data analysis 80, Native apps 72, Automation 82, AI research 77, Multimodal AI 88. Same principle as the approved Braille radar: one square dot lattice, explicitly positioned glyphs, open contour, no fill. Dots are now the font's `·` and `•` because JetBrains Mono has no Braille block.
- The closing prompt is the only animation: it types `profile.json` `typing` (desktop: `open gabrielemonni.me  # click for an adventure`, mobile: `open gabrielemonni.me`) with uneven keystrokes, blinks while idle, erases and loops about every 15 s. Timings live in `TYPING` in build_profile.py. Without animation (static renderers, reduced motion) the full command shows with the cursor after it. Keyframe names are global inside one document, so preview pages must not inline several cards together. A line-by-line reveal of the whole card was tried and dropped: renderers that capture the first frame showed an empty card.
- Azzurri palette: green headings and prompt, red labels and radar scores, white values, an azzurro radar contour and prompt path. The color blocks read as the Italian flag plus azzurro. Earlier bolder studies (amber, phosphor, lolcat and gradient portraits) were declined.
- Removed the old generators (`build_neofetch.py`, `build_radar_*.py`) and `explorations/`. They remain in git history.

## Preferences and constraints
- English artifacts. No em dashes. Apply the unslop skill to prose.
- Monochrome portrait, coarse and simple: visible ASCII glyphs and a recognizable face, never photographic.
- Transparent SVG backgrounds. Preview backgrounds are GitHub dark #0d1117 and white.
- Azzurri: green headings, red labels, neutral values, azzurro radar. Light mode needs strong text and visible radar rings.
- The portrait stays neutral: white on dark, near-black on light. No tinted or gradient portrait.
- Radar values are focus values the user chose. Never present them as measured skills or live GitHub statistics.
- Local QA, the original photo, masks and backups stay outside version control.
- Trailing spaces in portrait grids are intentional fixed-width padding.
- Commit or publish only when the user asks.

## Do not
- Reintroduce an inverted dark face or the dark grid printed as black on white.
- Return to pale light portraits or faint light-theme text and radar.
- Add yellow or orange accents to the Azzurri card.
- Reintroduce gh-issue-scout references.
- Add fake statistics, invented interests, badges, counters or unrelated widgets.
- Add a solid card background, filled radar texture, vertex stars, sidebar bars or uneven dot spacing.
- Return to a centered radar alone below the desktop profile.
- Add load-in animations that hide card content. Only the closing prompt may start empty.
- Drop the eye balancing or move the crop so the eyes straddle two rows: one eye then looks closed.
- Publish the original photo or ignored local files.
