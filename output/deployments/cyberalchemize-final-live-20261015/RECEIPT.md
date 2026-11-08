# Final whole-site review — deployed and verified

[Open the live website](https://cyberalchemize.com/governance-lab-series/index.html?review=final-live)

Independent subagent review covered the open-source hero, GitHub header,
search, documentation, reading path, formal reference, Craft architecture,
robot article, hackathon, library, diagrams and images in 64 live layouts at
320/390/768/1440 px and both themes.49 interaction checks and four whole-page
axe audits pass. The main review complemented this with 96 live layouts across
all six reading paths, runtime documentation, source/status, reader study,
company brain, library, formal records and Craft architecture.

Two confirmed issues were fixed:

1. Overflowing code panes were not keyboard-focusable in some documentation.
  28 previously unannotated pre blocks now have static tabindex fallback.
  The shared enhancement adds named keyboard regions and a crimson focus ring
  only while a pane scrolls, and removes extra stops when the pane fits.
2. Without JavaScript, mobile overview navigation exceeded 320 px (387 px page
  width). Native links now wrap within the header and retain the GitHub action.

The approved Paper & crimson appearance, hero, header/search behavior,
reading paths, diagrams, illustrations, page contents and URLs remain.

Release: `lab-20261015T160928Z-bcb0331e6778`.
ZIP SHA-256: `f73e325c01136d5066d07ff37aa5977ca13b4bd865d3fa879978e42c792307c5`.
Manifest SHA-256: `bcb0331e6778f87839214accdd8503cf37d59baf1dee9b749498adaf7fa4af1e`.

## Final verification

- Local:96 layouts across 16 routes, both themes;32 whole-page axe audits.
  Zero overflow, missing routes, broken images, missing alts, runtime errors
  or accessibility violations.
- Independent focused candidate check:10 checks and two whole-page axe audits,
  all passing. Actual ArrowRight scroll and visible focus, desktop removal of
  unnecessary tab stop,320 px script-free navigation/static code focus, and
  Craft architecture route all pass.
- After deployment:36 layouts/six page families,12 whole-page axe audits;
  zero failures. Ten additional actual keyboard/fallback/Craft checks and two
  whole-page runtime audits pass over HTTPS.
- Build, ZIP and manifest checks pass. All 498 routes remain, with 23,923 local
  references resolving and no duplicate IDs. All 13,946 local anchor links
  resolve; the two JavaScript-created destinations were verified in-browser.
- All 525 image references have alt attributes. All 66 original visual/font/
  download/calendar assets,454 formal record bodies and 552 captured sources
  remain byte-for-byte exact. Runtime article bodies retain all content;
  six of 14 receive only the explicit code-focus attributes. Original prose,
  headings, links, fragment IDs and navigation URLs are preserved.
- Search retains 806 entries and passes all 59 existing regression queries and
  payload/constructor/sync/async parity checks.
- All 1,241 public release files match reviewed bytes over verified HTTPS.
  Ten public/protected routes retain content, status and security headers.
  The combined live tree contains 1,252 files; secondary pages, credentials,
  hosting configuration, static image and unrelated containers remain intact.

The local candidate was built from the previous reviewed source snapshot to
exclude unrelated runtime-doc3 work in the shared workspace. The maintained
source contains the fixes; shared `website/dist` was not overwritten.
Local preview remains at http://127.0.0.1:8771/.
No Git commit/push was performed.

Private rollback: `/srv/co-op-engine/deployments/lab-20261015T160928Z-bcb0331e6778/rollback`.
The native metadata's leading branch glyph is its original CSS decoration,
not clipped content; it was retained. Impeccable palette advisories concern
existing approved tokens; no design-document or palette repair was performed.

Evidence uses Chromium viewport emulation and actual mouse/keyboard input,
not physical devices, Safari or assistive-technology sessions. Axe results
cover the tested states rather than establishing whole-site conformance.

[Independent review](../../playwright/final-live-20261015/subagent/REVIEW.md).
