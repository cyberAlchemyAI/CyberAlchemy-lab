# UI and UX improvement plan

Authorized by: “plan and fix”, 9 October 2026.
Scope: local article, its system map and the complete reference library. Source model identities, admissions, snapshot data and essay text are preserved.
Baseline: `output/playwright/ux-validator/20261009-ui-ux-review/review.html`.
Rollback: `versions/2026-10-09-ui-ux-before/manifest.json`.

## 1. Readability and feedback

- F01/F02: readable catalog selection and all clickable graph labels; hide irrelevant edges rather than fading text.
- F03: inspector beside the diagram on desktop; compact explanation before a relationship list on mobile; reveal feedback when it falls outside the viewport.
- F08/F11/F14: names containing the visible title and subtitle, with separate family descriptions, explicit named keyboard scroll regions, wrapped labels inside cards.

## 2. Entry paths and delivery

- F04: three starts in the compact header: governance, agent work, exact reference. Make the large map an explicitly opened explorer.
- F05: separate the full catalog/essays into `lab-reference-library.html`; preserve old deep links through forwarding. Supply smaller WebP image variants and lazy loading.
- F07/F13: readable relationship lists on mobile; named article diagrams with responsive text alternatives; larger headings and standalone navigation targets.

## 3. Finding and returning

- F06/F12: exact-title ranking, title/full-record scope, match explanations and a helpful zero-result state.
- F09: encode map view, governance focus, node and walkthrough position in the URL; restore on reload and Back/Forward.
- F10: label effective standing and version separately; keep exact identities and evidence intact.

## Completion evidence

Inspect the revised article and library with the already-authorized Playwright workflow: desktop/mobile rendering, graph selection, deep links, search and keyboard operation. Preserve before/after measurements and screenshots. No participant-study, assistive-technology or field-performance result is claimed from browser inspection.

Engineering targets from the review: initial HTML under 500 KB, initial resources under 1 MB, initial DOM under 3,000 elements; selected explanation in view; Ledger first for an exact search; zero observed card-label overflow; ordinary content contained at 320 CSS pixels. These are project targets, not universal standards.

Status: implemented and inspected, 9 October 2026.

## Delivered evidence

- Result: `research/ui-ux-fix-result.md` and `research/ui-ux-fix-result.json`.
- Visual report: `output/playwright/ux-fixes/20261009/result.html`.
- All three implementation groups above are complete. Initial HTML, initial DOM and cold payload meet the project budgets.
- Ten map layouts have zero observed card overflow and zero final accessible-name/ARIA violations. Named regions support observed keyboard panning.
- Source catalog/context bytes, all 484 captured digests and 95 essay paragraphs remain intact.

Further validation remains for assistive technology, other browser engines, participant comprehension and field performance. The full reference page retains its complete offline catalog. These boundaries are recorded in the result.
