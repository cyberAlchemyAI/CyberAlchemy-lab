# GitHub header action — deployed and verified

[Open the live website](https://cyberalchemize.com/governance-lab-series/index.html?review=github-header)

A GitHub brand icon and **Star on GitHub** action appear in all 492 page headers.
The link opens https://github.com/cyberAlchemyAI/CyberAlchemy-lab using normal
link navigation. The homepage uses a shorter GitHub label on phones/tablets;
the docs action remains visible outside the collapsible navigation. The link
is static HTML, works without JavaScript, and has a descriptive accessible name.
Approved Paper & crimson styling, both themes, existing menus/footer/sidebar
links, and all existing content remain.

Release: `lab-20261015T140327Z-763217708bee`.
ZIP SHA-256: `9a70c5173101b5c7492a9eee9202c5d23b6b0fd8b73a5cf833b88025297c6064`.
Manifest SHA-256: `763217708bee2496769ba51912cd94374a09f8a8d1db00cf36a3dfab82e736cf`.

- Local browser: 112 layouts, 360 checks, eight header axe audits; zero failures,
  runtime errors or accessibility violations. Seven widths from 320 to 1440 px,
  both themes, eight page families. Tablet overflow caught and corrected.
- Search, mobile menus, theme switching and expanded map: 11 interaction states pass.
- No-JavaScript CTA: three representative pages pass at 320 px. A pre-existing
  387 px docs page width is unchanged from baseline; this is outside the header update.
- Live browser: 24 layouts, 84 checks, eight header axe audits; zero failures,
  runtime errors or accessibility violations. Chromium viewport emulation;
  physical devices and other browser engines were not tested.
- All 498 routes and original prose, links and fragment IDs remain; 454 formal
  bodies, 14 runtime bodies, 552 source captures and 66 visual/font/download assets
  are exact. All 23,923 local references resolve. No duplicate IDs.
- Search retains 806 entries; existing 59-query regression and sync/async
  checks pass. Build, release manifest and ZIP integrity pass.
- All 1,241 public release files match reviewed bytes over verified HTTPS.
  Ten existing public/protected routes preserve status, content and security headers.
  Combined live tree: 1,252 files. Hosting configuration, credentials, image,
  sibling pages and unrelated containers remain unchanged.

The isolated source reproduced live bytes exactly before edits. Unrelated
runtime-doc3 work and a newer search script were excluded from this publication
and remain in the shared workspace. The candidate was built through the normal
pipeline in `../../playwright/github-header-20261015/workspace/website/`.
The shared `website/dist` was not overwritten. Preview: http://127.0.0.1:8769/.

Rollback is private at `/srv/co-op-engine/deployments/lab-20261015T140327Z-763217708bee/rollback`.
No Git commit/push was performed. Existing Impeccable font/palette advisories
refer to the approved identity; the new controls reuse its tokens.
