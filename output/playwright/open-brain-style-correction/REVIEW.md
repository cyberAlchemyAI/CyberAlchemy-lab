# Live identity restoration — October 16, 2026

The user rejected the first local preview for changing the approved style. This correction compares the actual live site against the revised local preview; it supersedes any implication of style approval in the initial implementation review.

Live comparison: https://cyberalchemize.com/governance-lab-series/index.html and https://cyberalchemize.com/governance-lab-series/start-here.html. Local comparison: their paths at http://127.0.0.1:8780/.

## Implementation

The preview now reuses captured live CSS and rendered header markup, with a source URL/SHA256 manifest in `website/previews/open-brain-20261016/live-assets.json`. Maintained source and `website/dist` are read only. The centered knot/headline, full bordered frame, native header controls, section rules, workbench, destination grammar and footer return. New copy, practical tasks and A/B/C entrances remain. Start presents breadcrumb/title before comparison controls, and familiar choice cards rather than a task table.

The custom preview stylesheet was replaced with bounded content/interaction adapters. Captured live assets overlay only the ignored preview `site/` tree at build time. Header menu behavior follows the actual1200px compact threshold; article navigation follows its reading breakpoint independently. Theme buttons preserve their SVG icon.

## Review

- Root inspected actual live home and docs in Chromium and compared final desktop captures visually.
- Independent desktop reviewer compared live/local at1440px and compact navigation at1024px. Fixed a legacy `home-view` class collision that narrowed and vertically offset the frame, and an outside-click handler hiding desktop navigation. Final frame x20/y0/width1400 and homepage header72px match live at1440px. Desktop persistent navigation, compact Menu activation/dismissal, resize restoration and overflow checks passed.
- Independent mobile reviewer compared18 live/local renders across320/390/768px. Centered knot bounds, heading typography, colors and frame match the live reference. No page overflow. After replacing the captured desktop summary with the actual compact label Menu, header heights123px at320 and125px at768 match live. Keyboard menu/Escape/focus restoration, search/theme, directory/table/canvas interactions passed. A bounded card-heading override restores the live18px/27px title role rather than article H2 metrics.
- Static integrity/link/asset checks cover513 HTML files: no missing original routes/fragments, no broken internal links or referenced files, no duplicate IDs in recomposed pages. All2,271 maintained hashes remain unchanged. The454 reference and14 runtime HTML pages preserve their exact content apart from the declared local ribbon/noindex insertions.

Evidence includes actual-live, initial-correction, and final captures in this directory. Chromium responsive viewports provide this bounded review; physical devices, other engines, full accessibility certification, backend execution and publication are outside it. No deployment, push or live-site mutation occurred.
