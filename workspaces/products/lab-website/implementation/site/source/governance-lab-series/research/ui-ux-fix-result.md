# UI and UX fix result

Implemented and inspected on 9 October 2026. Scope: attachment article and reference library.

- Initial HTML: 2,671,041 → 393,483 bytes (85.27% smaller).
- Initial DOM: 17,723 → 2,867 elements.
- Cold initial payload: 703,527 bytes; desktop WebP illustration included.
- Article begins at about 605 px on desktop / 944 px on mobile 390, previously 2016 / 2990 px.
- Ten map layouts: zero final card overflow or accessible-name/ARIA violations.
- Map and six article diagram regions: keyboard panning observed.
- Ledger ranks first; zero-result recovery, deep links, Back/reload and local-file loading inspected.
- All 484 source digests and 95 essay paragraphs preserved.

All F01–F14 findings were addressed within browser-inspection scope. Full reference content now lives in `lab-reference-library.html`; legacy anchors forward there. The 2.35 MB reference catalog loads on explicit navigation.

Detailed result: `output/playwright/ux-fixes/20261009/result.html`.
Machine-readable result: `research/ui-ux-fix-result.json`.

Remaining validation: assistive technology and other browsers, participant comprehension, field performance, and SVG contrast flags that require manual inspection. No blanket accessibility conformance, calibrated UX score or field-performance claim.
