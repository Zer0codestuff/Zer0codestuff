# Project guidance

## Purpose and architecture

This repository renders the public GitHub profile for `Zer0codestuff`. `README.md` embeds the generated NeoFetch-style card. `scripts/build_neofetch.py` reads the ASCII source and writes the light and dark SVG assets.

## Run and verify

- Regenerate assets with `python3 scripts/build_neofetch.py`.
- Verify that both SVG files parse as XML and contain the expected accessible title and description.
- Review the rendered README on GitHub after pushing changes.

## Current status

The profile card is generated successfully for light and dark themes. Its displayed statistics are static and need manual updates.

## Recent changes

- Translated the README alt text and SVG accessibility metadata to English.
- Updated the profile card to the verified contribution and original-repository counts from 2026-08-29.
- Featured `gh-issue-scout` in the profile card and added a direct README link to the project.
- Documented the build and verification workflow.

## Project constraints

- Keep all repository text and accessibility metadata in English.
- Keep the existing minimal NeoFetch layout and monochrome ASCII portrait.
- Regenerate both SVG variants after changing the generator or ASCII source.

## Known issues and next steps

- Profile statistics are hard-coded in `scripts/build_neofetch.py` and can become stale.
- The README currently embeds only the dark SVG variant.

## Do not

- Do not replace the generated card with generic profile widgets.
- Do not add decorative badges, counters, or unrelated sections.
- Do not change the portrait or palette without a visual comparison.
