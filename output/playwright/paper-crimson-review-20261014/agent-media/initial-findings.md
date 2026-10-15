# Independent current media review

Session: review-media-agent. Read-only source/build review, with browser artifacts only.

## Confirmed defect

P1: Embedded reference SVG subtle-fill custom-property cycle produces black-filled caution/ontology/decision surfaces and illegible dark text in light theme. Generated SVG compatibility block defines `--paper-soft:var(--ds-subtle)`; Paper appearance redefines `--ds-subtle:var(--paper-soft)!important` on SVG. Screenshot evidence: `desktop-light-2-1.png` (evidence note), `desktop-light-3-1.png` (decision bundle/admission), `desktop-light-4-1.png` (ontology region/nodes). Dark example: `desktop-dark-extra-2-1.png`.

Parent applied shared CSS correction during review. Exact final-build confirmation pending.

## Coverage and evidence

- Static media inventory: static-media-inventory.json.
- All 30 unique delivered img URLs returned HTTP 200: image-network-check.json.
- Main reference contains five unique explanatory SVGs and ten system-map views, with title/desc semantics and visible scroll controls. Desktop views captured in map-desktop-light-*.png.
- All nine Craft SVG figures preserve original artwork and explicit descriptive alt text. Each is in a keyboard-focusable diagram-scroll region with visible scroll instruction and Open diagram affordance. Mobile screenshots: mobile-light-extra-3-0.png through mobile-light-extra-11-0.png.
- Homepage knot/role artwork, event six-image set, original orb, research imagery and supplied reference PNG/WebP are included in initial desktop screenshots. Original geometry and semantic hues were not modified.
- Robot and runtime article inspected for displayed-media presence; these routes have documentation logo and text/code content rather than distinct graph/image types.
- Mobile system map defaults to the Relationship list view. Explicitly select Diagram for SVG inspection.

## Deterministic scan

`impeccable detect website/source --json` scanned the narrow website source markup (79 HTML/CSS/JS files). Raw: impeccable-source.json. It emitted 1,237 entries: 1,048 warnings and 189 advisories. The dominant rule was cramped-padding (926), much of it repeated original catalog/SVG markup. Other counts: design-system-color 123; design-system-radius 55; tiny-text 52; undersized-ui-text 36; wide-tracking 14; border-accent-on-rounded 8; numbered-section-labels 8; side-tab 6; italic-serif-display 3; hero-eyebrow-chip 2; kicker-above-heading 2; overused-font 1; oversized-h1 1. These are leads, not independently confirmed defects. Approved mono identity, preserved semantic hues/artwork, and retained content take precedence over generic detector aesthetics.
