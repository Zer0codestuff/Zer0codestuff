# Radar studies

Four local design previews for the existing GitHub profile. The user requested alternatives to compare before choosing one and approved illustrative scores on 2026-09-12.

| Design | Rendering | Character |
| --- | --- | --- |
| A / Wireframe | ASCII contour and polygon rings | Open and close to Neofetch |
| B / Braille | Unicode Braille dots and an open contour | Closest to the supplied reference |
| C / Phosphor | ASCII fill and circular rings | Green terminal display |
| D / Pixel | Unicode blocks and shading | A heavier, stepped silhouette |

Run `python3 scripts/build_radar_previews.py` from the project root. It reads `explorations/radar/data.json` and creates 16 standalone SVGs for four styles, two themes and two layouts, plus four text grids. Python's standard library is sufficient. Each SVG contains only text, groups and accessible descriptions. Backgrounds are transparent. No scripts, external fonts, raster images or chart paths are embedded.

Run `python3 -m http.server 8765 --bind 127.0.0.1` from the project root, then open [the gallery](http://127.0.0.1:8765/explorations/radar/). Use Compare, In profile, Dark and Light to review the options. The profile view reuses the existing portrait and information assets. The live README is unchanged.

All six axes have the same 0 to 100 scale and 25-point rings. Categories and clockwise ordering are identical in all variants. Wireframe, Phosphor and Pixel mobile diagrams use numbered axes matched to labels below. The revised Braille variant keeps names and scores beside the axes, including on mobile. Scores are explicitly illustrative and do not measure ability, activity or GitHub statistics. The text exports list labels clockwise from the top.

The visual reference is the [Magnitude terminal radar shared by Akshay Pachaar](https://x.com/akshay_pachaar/status/2095906342154424750). Its video thumbnail was inspected. These renderers were written independently; no reference code or media was copied.

Verified on 2026-09-12: SVG parsing, text-only output, ASCII character sets for A and C, zero/maximum/alternating score inputs, desktop and mobile image loading, theme changes, variant selection, profile composition and viewport bounds. No browser page errors were reported. Screenshots are in ignored `.local/radar-qa/`. GitHub embedding of these new radar assets has not been tested publicly.

Next: choose a design and confirm the final categories and the meaning and values of the scores before adding it to the published profile.

## Braille revision, 2026-09-16

The user selected Braille and rejected its uneven lines. After inspecting a frame from the supplied video, the renderer was rebuilt on a single square dot lattice. Explicitly positioned single-dot Braille glyphs prevent font cell spacing and per-run compression from bending the lines. Integer line rasterization keeps segments connected. The SVG has no fill, vertex stars, side list or bars. Neutral labels and scores sit beside the axes; the six illustrative categories remain unchanged. The gallery adds a Radar only view. The previous Braille assets are preserved under ignored `.local/radar-qa/braille-before/`.

The final assets were parsed and inspected in dark desktop and light mobile views. Segment checks cover sample, zero, maximum and alternating scores. This is still a local preview, with no change to the published README.

## Profile layout proposals

Run `python3 scripts/build_radar_layouts.py` after rebuilding the radar, then open `/explorations/radar/layouts.html`. This creates three independent profile compositions with the approved radar on the right. A / Project ledger pairs projects with a larger radar. B / Toolkit split pairs languages and focus areas with a medium radar. C / Compact terminal places current work and a smaller radar beside the portrait. Each has transparent dark/light and desktop/mobile SVGs. The generator reuses the original portrait grids and embeds the approved Braille asset without changing its geometry. All copy comes from existing profile content. These are local proposals pending selection; no live README changes or publication.

## Toolkit color studies

The user selected layout B and requested palettes without yellow or green. `/explorations/radar/colors.html` compares Glacier, Iris, Rose and Silver. Definitions are in `palettes.json`; run `python3 scripts/build_radar_layouts.py` to regenerate all 16 palette SVGs alongside the 12 layout SVGs. Colors change across headings, labels, values and the radar; geometry and the monochrome portrait stay identical. The Building text is now Local AI tools, following the requested removal of the issue-scout project from local sources and generated assets. No publication has occurred.

The multicolor follow-up is at `/explorations/radar/multicolor.html`: Prism, Coral and Polar use distinct colors for headings, labels, values and the radar. They use the same JSON and build command. There are now seven palettes and 28 palette SVGs. The original four options remain at `colors.html`. Yellow and green remain excluded, and no geometry changes or publication were made.

## Ten additional palettes

The next review is `/explorations/radar/round-3.html`. `round-3.json` selects ten new palettes from the shared palette definitions. Compare all ten in a grid or use Inspect to see one at full width. The existing generator produces their 40 SVG variants along with earlier proposals, 68 palette assets total. Only colors differ from the approved Toolkit composition. The new text/trace colors have a computed contrast ratio of at least 5.52:1 on the intended page backgrounds; this does not measure the perceived visibility of antialiased Braille dots. No option is selected or published.

## Coral refinement

Coral is the selected direction, with darker red headings and a blue radar. The light portrait uses lighter skin midtones and reduced sharpening; the dark portrait is unchanged. Building now includes Local AI tools and Native macOS apps from profile.json. The updated preview is multicolor.html?theme=light&layout=coral. Desktop dark/light and mobile light were visually checked. These remain local previews with illustrative radar values.

## Light contrast correction

The separate light portrait conversion was rejected. Both themes now share the approved dark character grid, with theme-specific ink. Coral light has darker colors, stronger information text and darker radar rings. Regular Braille glyphs with a small matching stroke preserve dot positions without bold-font artifacts. Desktop and mobile light were inspected; portrait-grid equality and SVG parsing were checked. Nothing was published.

## Light portrait tonal correction

The identical-grid light experiment was rejected. The current light portrait restores dense dark characters in shadows and uses neutral grayscale ink and stronger deep-shadow glyphs. Both generators share portrait_row. The dark portrait, information text and radar remain unchanged. Desktop/mobile rendering and all 84 SVGs were checked. No publication.

## Approved profile integration

The user accepted Coral and authorized publication on 2026-09-16. AI research is now 72, Automation 82 and Data analysis 80. The main build generates the four approved profile assets. Historical alternatives remain local studies; their generated files are ignored and can be rebuilt with the exploration scripts.
