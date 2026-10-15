# Independent preview design review

Scope: Paper & crimson preview only, `http://127.0.0.1:8768/`. No files under `website/` edited. Baseline screenshots cover 15 page families at 390px and 1440px in light/dark (60 states), plus lower marketing sections, long title exact record and robot essay anchors (32 states). No page-level horizontal overflow or runtime errors in the baseline. Parent review separately covers every guide/library/Craft chapter and open interaction states.

## Confirmed issues

1. **P1 — Inverted research culture section loses heading and lead in both themes.** Route `/governance-lab-series/research.html#culture`, 390/1440, light/dark. `.culture-section .culture-questions` inherits the preview global heading foreground matching the panel background, so the prominent “What if? How to?” disappears; `.section-marker`, `.eyebrow` and `.section-lead` also receive inappropriate global palette overrides. Scope inverse surface/ink/muted/line tokens to the component, with explicit foregrounds for its heading and lead. Evidence `culture-390-light.png`, `culture-390-dark.png`, `culture-1440-light.png`.

2. **P1 — Overview entry paths retain white/blue surfaces in dark mode.** Route `/governance-lab-series/governance-lab-reference.html`, 390/1440. `.entry-paths`, `.entry-paths>a` use legacy pale blue/white backgrounds; inherited ink becomes nearly white, making all three links difficult to read. Replace backgrounds, borders and hover with preview soft/surface/line tokens. Evidence `guide-390-dark.png`, light comparison `guide-390-light.png`.

3. **P2 — Semantic diagram labels are too dark in dark mode.** Route `/governance-lab-series/governance-lab-reference.html#system-map`, 1440 (same owners on phone). `.smap-legend-item` and `.smap-edge-label` use saturated dark family/concept colors. Retain semantic categories but provide lighter dark-theme variants for the relevant `--smap-*` and model-concept tokens, including child SVG scopes. Check label stroke/halo uses actual dark surface. Evidence `map-1440-dark.png`.

4. **P2 — Marketing wordmark remains dark in dark mode.** Routes `/governance-lab-series/research.html`, `/governance-lab-series/hackathon.html`, 390/1440. Marketing link class is `.research-brand`, while `preview-theme.js` only updates `.brand img`. Include the marketing class in asset switching and shared sizing. Evidence `research-1440-dark.png`, `hackathon-1440-dark.png`. This is a selector omission, not a picture/source issue.

5. **P2 — Homepage compresses meaningful mobile text to 7–10px.** Route `/`, 390. `.art-caption`7px, `.facts dd`8px, `.workbench-header`8px and its `.tag`7px, `.record-state`8px, `.connection-list small`9px, action `.button`10px. Raise metadata to about11px and explanatory/control copy to12–13px, preserving ruled mono direction and checking wrapping. This is a readability judgment supported by computed font sizes, not a measured user-study outcome. Evidence `home-390-light.png`, `review.json`.

## Stable observations

The base mono/ruled Paper & crimson direction is coherent. The exact-record sample and longest title wrap naturally; catalog, Start here, incident walkthrough, Craft hero, reader form, company incident and hackathon carousel have no additional visible design failure in the sampled states. Preserve their content and interactions. Optional taste changes (larger whitespace, alternate font, removing semantic diagram colors, changing illustration style) are not recommended as defects.

## Evidence limits

`deep-confirmation.json` contains32states. Hash-only navigations can capture intermediate smooth scrolling, so robot essay anchor screenshots alone do not establish each essay's final scroll alignment; use parent chapter route checks or reduced-motion/stable scrolling confirmation for that claim. Initial `deep.raw.json` is a retained collector failure from treating hash navigation's null response as a network failure, not a website fault. No physical-device, participant or assistive-technology sessions claimed.

## Final correction confirmation

All five findings are resolved in the current preview. Twenty correction states confirmed culture, entry paths, logo and homepage typography. Four final focused states (map and embedded incident diagram at390/1440 dark) confirmed actual SVG-local surface, foreground and semantic tints. Node titles, subtitles and edge labels now read against dark nodes/canvas, and the label halo follows the real surface. Current evidence: `final-current.json` and `final-current-*.png`. Earlier `final-map.*` captured cached pre-correction HTML referencing the old CSS bundle; it is diagnostic evidence, not the final state. No additional concrete defect remains from this independent review.
