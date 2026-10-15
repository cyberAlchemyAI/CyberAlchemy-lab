# Independent current-site design review

Reviewed the served current edition at `http://127.0.0.1:8767/` against `website/DESIGN.md`. This review made no source changes or builds. Browser session: `review-current-agent`.

## Actionable findings

1. **P1 — Compact documentation search clips result text off the left side.** At 390×844, open Start here and enter `runtime`. The results rectangle is x=-34, width=358, right=324; result headings, count, and snippets lose their first characters. Reproduces on a fresh mobile load in both themes. At 900px, the panel begins at y=64 while the compact header ends at y=123, covering the navigation row. At 1024/1100/1280, right anchoring fits. Likely owner: `website/source/governance-lab-series/assets/site-search.css:6` and `:13`, with the compact header rules in `assets/paper-crimson/appearance.css:95`. Evidence: `docs-search-mobile-fresh-dark.png`, `docs-search-mobile-light.png`, `docs-search-900-dark.png`.

2. **P2 — Dark search keeps light toolbar and highlight fills.** In an actual user-selected dark theme, `.site-search-toolbar` has white background while the count uses rgb(198,177,171); highlighted words inherit rgb(250,240,232) or rgb(198,177,171) on #fff1b8. Matching terms become harder to read than the surrounding text. Likely owner: `website/source/governance-lab-series/assets/site-search.css:14`, `:17`, `:23`, `:24` and the incomplete search-role mapping in `assets/paper-crimson/appearance.css:39`. Evidence: `docs-search-tablet-dark.png`, `docs-search-mobile-fresh-dark.png`.

3. **P2 — Expanded original-home company-brain map loses its layout scope.** Expand “More about the company brain” at 1440px. The core SVG grows into a large cylinder; “Shared project state / Durable knowledge” overlaps the instruction and following heading. `.brain-map-core` computes to position:static,width:auto,height:auto because `.research-site .brain-map-core` no longer matches after the original content is placed inside `.legacy-home-content`. Its caption remains absolutely positioned. The core label spans y=3003..3057 while `.brain-map-hint` spans y=2999..3027 in the reproduction. Likely owner: `website/source/governance-lab-series/assets/company-brain-map.css:30` and `:32`, with wrapper ownership in `website/paper_crimson.py:39`. Preserve the original map content and interaction while restoring a matching scoped layout. Evidence: `expanded-home-map-overlap-desktop-dark.png`, `expanded-dark-section-0.png`, `home-expanded-desktop-light.png`.

## Coverage and passing observations

- Captured homepage normal/expanded in desktop/mobile and both themes. Inspected the retained original content, not just the opening screen.
- Captured Start here, all six reading paths, guide overview/system map, incident walkthrough, record examples, practical guides, library, research, company-brain essay, hackathon, source/status, all fourteen runtime pages, Craft, robot essay index, and representative exact Definition/Work records.
- Default comparison: 1440×1000 light and 390×844 dark; additional family representatives in desktop dark/mobile light. Compact navigation examined at 768px, search additionally at 900/1024/1100/1280px.
- All three reading steps were marked read on every path. The completed progress message and “Mark as unread” controls wrap cleanly at 360px. Evidence: `completed-path-360.png` and each `path-*-mobile-dark.png`.
- Documentation/site menus open and remain usable at mobile/tablet sizes. Homepage More menu stays within the viewport. Search ArrowDown + Enter opens `runtime-status.html`.
- Main prose columns, headings, cards, representative exact record bodies, and runtime first screens remain readable. No additional substantive design defects were found within this bounded round.

## Evidence notes

Screenshots are in this directory. `contact-*.jpg` are overview sheets; individual PNGs retain detail. The initial capture script briefly changed only the theme data attribute; all route-level mobile dark screenshots were subsequently regenerated using the actual theme control. An apparent dark-logo problem from that synthetic state was retracted: the real theme control correctly selects `logo-dark.svg`.

This is a visual and interaction review of representative surfaces, not a proof of every formal record or every outbound link. Parent review owns the automated integrity/accessibility matrix and subsequent build validation.
