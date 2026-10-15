# Independent Impeccable UI review

Reviewed the settled Paper and crimson identity against DESIGN.md and Impeccable polish, layout and craft-floor guidance. No source edits made by reviewer.

## Findings and resolution

1. **Confirmed record reading-surface padding defect.** Actor's `.record-body .normative` had zero inset and its paragraph began 2px from the crimson rule; record `pre` blocks also had zero inset. `actor-normative-1440.png` captures the original defect. Parent repaired shared record reading surfaces to 24px desktop and 20px mobile, with first/last paragraph margins trimmed. Final screenshots confirm the inset is consistent and text is readable in both themes.
2. **Confirmed navigation ambiguity.** Shared tree labelled both company-brain.html and index.html “The company brain”. Parent resolved the landing link label; final record navigation exposes one conceptual article link.

## Coverage

- Initial UI matrix: 84 rendered states across 14 representative surfaces,390/1024/1440 widths and light/dark. Homepage, Start here, path page, company brain, system map/evidence, reference catalog and exact Actor record, event, research, runtime overview/CLI, Craft and Robot learning. No document overflow or runtime errors.
- Media/non-card follow-up: 48 states across 8 surfaces,320/768/1440 widths and light/dark. Explicit eager image loading/decode avoids mistaking native lazy loading for broken assets.0 broken rendered images;0 document overflow. Inspected home continuity graphic, system-map/evidence surfaces, company-role/cycle layouts, event imagery and cards, library, runtime architecture and Craft.
- Final Actor confirmation:8states =320/390/1024/1440 widths ×light/dark,24record highlighted/code surfaces. Every inset matches 20px mobile/24px desktop; no inner or document clipping; no runtime errors; one “The company brain” sidebar link. `confirm.json` records values and `actor-fixed-*` captures final rendered result.

## Intentional surfaces

Path cards and reference destination cards already have 20px mobile/24px desktop padding. Reading-step containers delegate inset to padded summary/body. Event slides delegate inset to `.hack-idea-copy`; their outer 0 padding is intentional, avoiding padding around full-bleed imagery. Company knowledge-cycle is a linear diagram bounded only by horizontal rules, with 24px vertical space; no side card border needs inset. Reference reading aids are table-like definition lists with separators, not cards.

Remaining rendered surfaces are coherent with the approved warm palette, monospace identity, thin rules and restrained corners. No further actionable UI defect found in this bounded pass.

## Final contrast verification

Actor was additionally checked with axe-core's actual `color-contrast` rule at 390 and 1440 widths in light and dark themes: 4 states, 0 violations, 0 incomplete checks. `contrast.json` records computed colors. The static detector's crimson-on-ink combination does not occur in the rendered record: light links are crimson on warm paper; dark links use the theme's pale crimson, and highlighted prose/code use the theme's ink on subtle surface.
