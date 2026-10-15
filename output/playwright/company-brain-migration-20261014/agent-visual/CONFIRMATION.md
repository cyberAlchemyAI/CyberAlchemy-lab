# Narrow final-build confirmation

Checked fresh `verify=migration-confirm` URLs at 390px in light mode.

PASS: direct entry from about:blank to index#craft rewrites to #paper-craft and reaches Craft (section top36.34 after settling). Direct entry to index#hero-title rewrites to #paper-hero-title and reaches the H1 (top20.125). Both preserve mode/verify query parameters.

PASS: JavaScript-disabled index#craft keeps the native legacy hash and reaches Craft. The alias is 1px high, top112.34, matching the real section top112.34. Computed root scroll-behavior is auto.

PASS: JavaScript-disabled index#lab-home displays the cross-page fallback. Both ordinary click and focus+Enter reach company-brain.html#company-brain and its correct H1.

REMAINING CASE: same-document navigation from index#craft to index#hero-title changes the URL to #paper-hero-title but leaves the viewport at Craft. Measured scrollY3588 and H1 top−3075.875, unchanged on another measurement over six seconds later. Computed root scroll-behavior was smooth after redirect. This is distinct from the passing fresh-entry tests. Parent informed; no source edits performed.

Evidence: confirmation.log, confirmation-fresh-entry.log, confirm-*.png. Browser session closed after capture.
