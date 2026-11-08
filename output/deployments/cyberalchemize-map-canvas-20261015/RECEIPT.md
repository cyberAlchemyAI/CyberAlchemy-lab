# System-map canvas — deployed and verified

[Open the map](https://cyberalchemize.com/governance-lab-series/governance-lab-reference.html?review=canvas#system-map)

Click **Expand map**, a diagram preview, or a concept to open the expanded
canvas. Drag to pan; use wheel/pinch or zoom buttons; Fit shows the whole map;
Focus enlarges the selected concept. Arrow keys pan, +/− zoom and 0 fits.
Keyboard navigation reveals focused concepts after zoom. Close or Escape
returns to the original reading presentation, focus and scroll position.

The original SVG and original inspector are moved together rather than cloned.
View/lens selection, semantic colors, model data and definition/article links
remain connected. Phones/tablets get a collapsible details drawer. All original
inline reading modes and the no-JavaScript map remain available. The approved
Paper & crimson identity is preserved.

Release: `lab-20261015T070744Z-1533ea94e251`.
ZIP SHA-256: `0e4dd46f9309ea09cf8b99bb46a79eb4539801e01bff51073522b093eb508242`.
Manifest SHA-256: `1533ea94e25130f2598d30dc343f9c6484bcd5652f3a2e95f057496270d46296`.

## Verification

- Local: 120 canvas layouts across six screen sizes (including tablet and
  landscape), both themes, six map views and five governance lenses. All 249
  checks pass, including mouse, wheel, synthesized touch drag and pinch,
  keyboard visibility, native modal behavior, selection, navigation and restore.
- Live: 60 canvas layouts and 129 checks pass at 320 × 700, 390 × 844 and
  1440 × 900 in both themes. Two axe audits per environment: zero violations.
  No runtime errors. No canvas scrollbars or clipped nodes when fitted.
- No-JavaScript map remains available and fits; unsupported expansion is hidden.
- Build: all 41,842 documentation checks pass. Release ZIP/manifest agree.
- All 1,241 public release files match the reviewed bytes over verified HTTPS.
  Ten existing public/protected routes retain content/status/security headers.
- All 498 routes, original content/links/fragment IDs, 454 formal record bodies,
  14 runtime bodies and 552 source captures remain. The model, original SVG
  geometry and all 66 visual/font/download/calendar assets are unchanged.
- All 23,923 local references resolve, with no duplicate IDs. Search retains
  806 entries and passes its existing 59 queries and payload/parity checks.
- Combined live tree: 1,252 files, preserving eight secondary files and earlier
  hashed asset URLs. Hosting configuration, credentials, static image and
  unrelated containers remain unchanged.

A complete private rollback is retained outside the served tree at
`/srv/co-op-engine/deployments/lab-20261015T070744Z-1533ea94e251/rollback`.
The earlier candidate recorded under `pre-keyboard-candidate/` was staged only
and never served. No Git commit/push was performed. The local server stays up.

Evidence uses Chromium viewport emulation and actual mouse/keyboard input,
plus Chrome DevTools synthesized touch events. Physical devices and Safari
were not tested. The Impeccable detector's two neutral modal veil/shadow color
advisories are intentional depth/occlusion treatments; no design-document
repair was performed. [Local review](../../playwright/map-canvas-20261015/REVIEW.md).
