CyberAlchemy Lab Paper & crimson website preview

Preview: http://127.0.0.1:8768/
Guide: http://127.0.0.1:8768/governance-lab-series/start-here.html
Reference: http://127.0.0.1:8768/governance-lab-series/lab-reference-library.html#catalog-definitions
Craft: http://127.0.0.1:8768/craft-documentation-proposal/craft-model.html

All 484 HTML routes are isolated in this preview, including the approved custom homepage and 454 exact reference pages. Internal links stay within the preview. Paper & crimson is fixed; light/dark preference is shared across pages.

The current website under website/ is a read-only source. None of its 6,217 inspected files changed.

Rebuild the preview from repository root:
python3 output/website-experiments/telegraph-direction-20261014/build_preview.py --reuse-preview

Serve it:
python3 -m http.server 8768 --bind 127.0.0.1 --directory output/website-experiments/telegraph-direction-20261014/dist

Maintained preview files are in source/. The build overlays its shared theme on copies of website/dist. Edit the preview source, then rebuild; do not edit the current website to change this experiment.

The preview has its own release-manifest.json identifying it as unpublished. Copied research and capture receipts describe the retained source edition. No publication, form activation or authority promotion is performed.

Verification evidence: output/playwright/paper-site-20261014/VERIFICATION.json
Static and exact-content checks: python3 output/playwright/paper-site-20261014/verify_static.py
Search parity checks: node output/playwright/paper-site-20261014/verify-search.cjs

The old color studies and initial prototype evidence remain in their dated output/playwright folders.

Independent preview design review (2026-10-14)
The subagent confirmed all five design findings resolved: inverse culture contrast, warm entry-card surfaces, dark diagrams and legends, research logos, and mobile text sizing. Homepage labeled groups also have valid semantics. Shared preview assets use content-hash URLs.

Current review evidence: output/playwright/preview-design-review-20261014/VERIFICATION.json
105 responsive states, 10 map layouts, 12 interaction checks, 54 dark routes and 26 axe states passed. All 478 pages and 22,191 local references passed static checks. The 454 formal reading bodies and all 6,217 inspected current-site files are unchanged.

Guided documentation cards (2026-10-14)
Documentation entrance: http://127.0.0.1:8768/governance-lab-series/start-here.html?review=docs-cards
Six task-based reading paths contain 18 verified documentation destinations. Reading progress is optional and browser-local; underlying guides and contracts retain their existing content. Navigation cards also cover overview choices, next-reading links, essay indexes and reference categories.

Maintained editorial path copy and static HTML generation: docs_preview.py. Reading behavior: source/docs-reading-path.js. Shared card styling: source/preview-theme.css. The build reuses pure source search compilers read-only to preserve the 708 existing entries and add six paths to quick/complete search; preview search assets are versioned.

Current evidence: output/playwright/docs-cards-20261014/VERIFICATION.json
Application analysis: output/playwright/docs-cards-20261014/CARD-APPLICATION.txt
Verification: 150 responsive states, 18 destinations, eight axe states with zero automatic violations, six fallback/storage/keyboard checks, five final integration checks and 39 search relevance checks. All 484 pages, 22,530 local references and 454 exact record reading bodies pass static verification.

Repeat checks from repository root:
python3 output/playwright/docs-cards-20261014/verify-static.py
node output/playwright/docs-cards-20261014/verify-search.cjs

Docs, graph and image review (2026-10-14)
Two independent reviewers covered all six reading paths, documentation cards, every graph family, all ten map layouts, 27 standalone SVG assets, and linked imagery. Five confirmed refinements were implemented within the preview. Original website/source and website/dist remain byte-identical across 2,123 files; unrelated promotion artifacts changed outside this task and are listed in the evidence.

Use --reuse-preview to preserve the reviewed edition; omit it only when intentionally refreshing from the latest current-site source. The build can update overlays without duplicating headers, notes or scripts. visual_review.py maintains figure instructions, full-size links and the map label correction. The homepage search total is derived from the preview index.

Final verification: output/playwright/docs-visual-review-20261014/VERIFICATION.json
Current static check: python3 output/playwright/docs-visual-review-20261014/primary/verify-static.py
Search regression: node output/playwright/docs-visual-review-20261014/primary/verify-search.cjs
