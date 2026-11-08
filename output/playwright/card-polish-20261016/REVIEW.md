# Preview card review · 16 October 2026

Scope: the isolated open-brain preview on port 8780. No publishing, commits, or maintained website edits.

## Coverage

Inventoried card and grid classes across all 513 generated HTML files. Browser inspection covered 20 pages containing card families, plus the reference library's expanded essays view: 21 views at 320, 390, 768, 1024 and 1440 pixels in light and dark themes (210 rendered states). This includes homepage examples and comparison panels, guide choices, reading-path entry cards and six reading-path pages, reference destinations and chapters, robot chapters, governance lenses and learning stages, and the two hackathon categories.

## Changes

- Added shared preview-only card CSS after the incumbent styles; asset fingerprinting prevents stale CSS.
- Shared content tracks align headings, descriptions, imagery and actions within desktop rows, without fixed card heights.
- Kept content-driven mobile stacking with consistent 20/24px insets.
- Corrected the divider when homepage examples wrap to a second row.
- Aligned the Q1/Q2 note panels and the hackathon judging paragraphs.
- Reset legacy multi-column chapter interiors to a single readable card column.
- Bounded governance/learning icons at 24px and restored card padding.
- Kept embedded legacy article navigation in normal flow so it cannot cover cards.
- Preserved hidden guide cards when filters change.

## Verification

`final.json` and `alignment-findings.json`: 210 states; no document overflow or mismatched widths/heights/content starts within populated card rows. Stacked cards intentionally follow their content length.

Representative desktop/mobile screenshots cover ten component families. Final viewport captures confirm the governance and learning cards are unobscured. Earlier long element screenshots include fixed browser-page navigation in the crop; the final viewport captures are the visual authority for those components.

`filter-confirmation.txt`: selecting Marketing shows exactly one guide; clearing restores all ten at both 390px and 1440px. Reading-step disclosure toggles work. No script errors occurred during the interaction checks.

The preview verifier reports 513 pages, zero link or asset issues, no missing original routes/anchors, no duplicate IDs in recomposed pages, and byte-preserved original content for 468 exact reference/runtime pages after removing additive preview wrappers. All 2,271 maintained website hashes remain unchanged.

Source changes are limited to the preview's card stylesheet, builder and verifier normalization for the additive stylesheet tag. No copy or link destinations changed.
