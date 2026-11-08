# Open company brain — local design preview

This is the isolated implementation of the October 16 UX/UI specification and copy deck in `docs/proposals/0010-lab-craft-content/`. It does not build or deploy the maintained website.

## Visual identity correction

The user rejected the initial preview's visual drift. The current preview keeps the new content and uses the actual live site's centered opening, bordered frame, compact header, typography, footer and component styles. `live-assets/` contains read-only CSS snapshots captured from the live home, guide and Craft pages; `live-assets.json` records their exact URLs and hashes. They overlay only this preview's copied assets during its build. The homepage and documentation header templates are adapted from the rendered live headers. Shared `assets/preview.css` now contains only the new-content adapters and interaction surfaces, rather than an independent site design.

The initial review in `output/playwright/open-brain-20261016/` established functional checks, not visual fidelity. The subsequent actual-live comparison and correction evidence is in `output/playwright/open-brain-style-correction/`.

## View

- Home: http://127.0.0.1:8780/governance-lab-series/index.html
- Compare documentation entrances: http://127.0.0.1:8780/governance-lab-series/preview-options.html
- Practical guide directory: http://127.0.0.1:8780/governance-lab-series/team-examples.html
- Craft: http://127.0.0.1:8780/craft-documentation-proposal/craft-model.html

The default preview entrance is team/task first. The three alternatives are still available for comparison; this implementation does not settle that editorial choice.

## Restart

From the repository root:

```bash
python3 -m http.server 8780 --bind 127.0.0.1 --directory website/previews/open-brain-20261016/site
```

To rebuild **only this preview**, using the existing website Python environment:

```bash
website/.venv/bin/python website/previews/open-brain-20261016/build_preview.py
website/.venv/bin/python website/previews/open-brain-20261016/verify_preview.py
```

The builder reads `website/dist`, clones it into this directory's ignored `site/`, and overlays the new pages and assets. It deletes and recreates only its own generated `site/` directory. Keep maintained production build/deployment commands out of this workflow. `prepare_content.py` was used to extract the approved public copy and record the original hashes; do not rerun it to reset the preservation baseline during verification.

## Included

27 new or recomposed pages: homepage, A/B/C documentation entrances and chooser, ten task guides, company brain, governance lenses, continuity, incident and learning entrances, Craft, research and contribution/source status. Includes local search, department/industry filtering, theme continuity, deep links into retained details, keyboard-accessible diagram expansion, selection and zoom.

The existing reference, runtime, research, event, reading paths, downloads and assets remain available at their original paths. Rewritten narrative pages disclose their maintained detailed article below the new entrance. Original fragments remain resolvable; some introduction fragments lead to the corresponding new explanation. The learning introduction owns `#learning`; the captured formal chapter is directly available at `#learning-maintained`.

The search index contains 509 document entries. Theme and existing reading preferences are local to the browser origin. No backend integrations, new runtime capabilities, or publication are implied by these interface examples.

## Evidence

- `verification.json`: route, fragment, asset, duplicate-ID and source-integrity checks.
- `baseline.json`: 2,271 maintained source/build input and output hashes captured before implementation.
- `build.json`: exact overlaid routes and retained article inventory.
- `impeccable-detect.json`: mechanical design detector output.
- `../../../output/playwright/open-brain-20261016/REVIEW.md`: browser review and limits.

Canonical source and `website/dist` are unchanged relative to the recorded baseline. No deployment, commit or push was performed.

## Homepage card artwork

Three generated engraving illustrations now accompany the campaign, customer reply and sales handoff cards. Optimized responsive WebP assets and provenance are in `assets/card-images/`. The images are confined to this local preview. Browser evidence is recorded in `output/playwright/open-brain-card-images/` at the repository root.

## Full preview polish

The all-page pass harmonizes retained-page headers and reading sizes, moves preview metadata into themed footers, fixes navigation context and empty/tablet outlines, and renders five runtime diagrams while preserving their exact source. The normal preview build adds content fingerprints to CSS/JS references so existing tabs load the current assets.

`prepare_runtime_diagrams.js` is a one-time regeneration helper using pinned Mermaid11.17.2 in the local Playwright browser. The saved preview inputs are its generated SVGs and source/hash manifest in `assets/runtime-diagrams/`; viewing or rebuilding the preview requires no CDN dependency.

Final evidence: `output/playwright/open-brain-polish-20261016/REVIEW.md` at the repository root. All510 non-redirect routes passed2,040 final layout states; all513 HTML files pass internal link/asset checks. The maintained source/build baseline remains unchanged.

## Independent final review

The final mobile/desktop review restored scoped legacy figure styles and the existing role-map/guided-reading scripts inside retained articles. It also corrected search action alignment, captions and compact research layouts. `assets/retained-figures.css` contains scoped original component rules; `assets/final-polish.css` contains the final responsive adapters. `prepare_retained_styles.py` regenerates only the former from existing captured assets; ordinary preview builds use the saved CSS.

Evidence: `output/playwright/final-preview-20261016/REVIEW.md` at the repository root, with separate independent mobile and desktop reports. All maintained website files and live deployment remain unchanged.
