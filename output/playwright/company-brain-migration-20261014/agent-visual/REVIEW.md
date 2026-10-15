# Company-brain migration visual review

Reviewed the live local build at 127.0.0.1:8767 on 2026-10-14 (America/Sao_Paulo). No source edits, builds, publication, or deployment performed.

## Finding

No persistent visual or navigation defect confirmed in the reviewed migration. An initial #craft screenshot taken 200ms after navigation showed the hero metrics instead of Craft. A fresh settled navigation correctly placed both the alias and actual Craft section at y112.34 (390px viewport), with scrollY3512. Treat the initial capture as a transient layout/anchor settling observation, not proof of a permanent wrong destination. A direct mapping to the real target would avoid dependence on a zero-height alias.

## Coverage

- Home, Start here and company-brain: 1440, 1024, 768, 390 and 320px; real mode=light/dark with verify=migration-visual on each route. Thirty full-page screenshots captured. No document horizontal overflow in any case.
- Paper and crimson appearance remains coherent. Article uses the documentation tree, reading column, compact navigation and local outline. Card grids collapse into one column when necessary; prose remains readable at 320px.
- Start here contains one primary set of six task paths and compact lookup utilities. Understand the Lab links to company-brain, incident walkthrough and system map in that order.
- Role map, knowledge cycle, purpose/work sequence, incident comparison and agent handoff remain contained. Role-map caption stays within the figure; all five controls update the explanation and exclusive aria-pressed state. Selected Knowledge dark screenshot confirms readable selected label and outline.
- index#lab redirects to company-brain#company-knowledge; start-here#definitions-first redirects to company-brain#definitions-first, preserving mode and verification query parameters.
- JavaScript-disabled index#lab-home exposes its visible fallback. Focusing its link and pressing Enter opens company-brain#company-brain and the correct article heading. The static fallback uses an ordinary relative href and does not propagate query parameters.

## Evidence

- details.json: measured layout, overflow, role control states, caption bounds and fragment destinations.
- finish.log: initial #craft capture and Understand the Lab route order.
- no-script.log: JavaScript-disabled fallback and keyboard activation.
- figure-*.png: desktop and 320px figures in both themes; captured below the sticky header to avoid screenshot overlay artifacts.
- role-*.png: all five selected role states at 390px dark.
- index/start-here/company-brain-<width>-<mode>.png: full-page viewport matrix.
- legacy-craft-390-light.png: initial transient anchor position; should not be used as settled-state evidence.

The first layout-metrics.log contains the executed capture script only; details.json is the actual measurement record. Other five paths were outside this visual review's changed route; parent content review covered their preservation.
