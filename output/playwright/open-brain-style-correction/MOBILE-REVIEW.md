# Mobile style correction review

Reviewed 16 October 2026 using isolated Playwright CLI Chromium session `ob-mobile`. Read-only review of live `https://cyberalchemize.com/` and local preview `http://127.0.0.1:8780/`; no website source edits or deployment.

## Comparison

18 bounded comparison renders: live/local homepage at 320, 390 and 768 CSS pixels in light/dark, and live/local Start here at those three widths in light. Measured observations are in `mobile-metrics.json`; paired screenshots use `mobile-{live|preview}-{width}-{theme}-{home|start}.png`.

The homepage visual identity is restored. Frame, centered knot size and location, headline typography, theme colors and control arrangement match the live composition. The intentionally retained new headline and explanatory content differ from live copy.

| Width | Live and local H1 size / line height | Live and local knot image width / x |
|---|---|---|
| 320 | 30px / 32.4px | 262px / 29px |
| 390 | 33.15px / 35.802px | 310px / 40px |
| 768 | 43px / 46.44px | 390px / 189px |

No document overflow in the comparison set. Both live and local use the same warm paper/ink/crimson and dark equivalents. The restored bordered frame, engraved knot and centered hero are visible in actual renders.

## Bounded regression checks

- Latest documentation header matches live height: 123px at 320, 125px at 768. The visible summary is Menu. Native keyboard opening/Escape/focus return pass.
- Search returns 12 campaign results. At 320 its result panel stays within x16–304, bottom 875 in a 900px viewport; Tab then Escape dismisses while preserving the populated input.
- Theme persists from local documentation to homepage and back, all dark.
- Directory cards at 768 are 335px wide, with 24px padding and the live card surface. No document overflow.
- Campaign phone table is stacked and labeled, width 258px inside the restored frame; currency values remain intact. Craft capacity also fits 320 with table width 258px.
- Campaign canvas opens, Zoom in reports 125%, Fit restores the original transform, and Escape restores the article opener. Screenshot `mobile-preview-320-canvas.png`.
- The final Start here render restores breadcrumb/title before the comparison chooser, as requested by the parent.

## Findings

The initial documentation summary wrapped Site navigation / Menu across three lines, increasing the header height to 165px. Parent fixed it during this review; final 123/125px heights and keyboard behavior were confirmed.

The directory card title difference was also fixed: final computed styles are 18px / 27px, weight 600, matching live documentation choice cards. The final actual render is `mobile-final-768-cards.png`; the document remains 768px wide.

All reported findings are resolved. No functional blocker or unresolved style-fidelity finding remains within the bounded review. Review browser closed.

This review establishes local Chromium responsive observations, not physical-device Safari, screen-reader or WCAG conformance. It does not re-audit preserved record bodies or all routes.
