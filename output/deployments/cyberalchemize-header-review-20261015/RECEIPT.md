# Header, search and open-source hero — deployed and verified

[Open the live website](https://cyberalchemize.com/governance-lab-series/index.html?review=header-search-final)

The homepage now says **An open-source company brain** and offers a direct
**Explore the source on GitHub** link. The existing description, two hero
actions and all existing links remain. Paper & crimson styling is preserved.

The shared documentation header gives search an authored icon, readable text
(16 px on compact layouts, 14 px on desktop), appropriately sized results and
correct highlighting after Unicode normalization. The desktop shortcut remains;
compact layouts hide it and give search its own space. Header controls have
44 px targets. A bounded mobile navigation dropdown replaces the narrow,
expanding column. Escape/outside clicks dismiss it; menu/search are mutually
exclusive. Keyboard order follows the visible responsive arrangement.

The requested independent subagent reviewed the live baseline and the candidate
across 16 states each. Its final target-width finding was corrected. The main
batched inspection also caught and corrected the hackathon logo's inherited
width overlapping the GitHub action at 320 px.

Release: `lab-20261015T154049Z-bf75e41aa33c`.
ZIP SHA-256: `efc9e8465b5036add0fcf3f0f6df48c89584387ddea2f1a5b13ca4857494fa02`.
Manifest SHA-256: `bf75e41aa33ccc8154b9996cd376780c83b1dd9ce6e62a48edbb520fc9149d4c`.

## Verification

- Local: 112 layouts, 332 checks, eight header axe audits; zero failures,
  runtime errors or accessibility violations. Eight page families, seven widths
  (320–1440 px) and both themes. Actual keyboard/menu/search interactions,
  empty states and accent/ellipsis/question-mark highlight fixtures pass.
- Live: 32 layouts, 172 checks, eight header axe audits; zero failures,
  runtime errors or accessibility violations. Phone, tablet and desktop widths.
  Eight additional actual Guide/search destination and map open/restore checks pass.
- Static/no-JavaScript GitHub actions pass on three local and live routes.
- Build, ZIP/manifest integrity and all 23,923 local references pass; no
  duplicate IDs. Search retains 806 entries and passes 59 regression queries
  with sync/async, quick/full and original-algorithm parity.
- All 498 routes and original links/fragments remain. All original prose
  remains except the explicitly requested hero heading update. All 454 formal
  bodies, 14 runtime bodies, 552 source captures and 66 original visual/font/
  download/calendar assets are exact. All 492 headers retain one GitHub CTA.
- All 1,241 public files match the reviewed bytes over verified HTTPS.
  Ten existing public/protected routes retain content/status/security headers.
  Combined live tree: 1,252 files. Hosting configuration, credentials, static
  image, secondary pages and unrelated containers remain unchanged.

The release uses an isolated snapshot of the previous reviewed source;
unrelated runtime-doc3 documentation work remains in the shared workspace.
The shared `website/dist` was not overwritten. Local preview remains at
http://127.0.0.1:8770/. No Git commit or push was performed.

Private rollback: `/srv/co-op-engine/deployments/lab-20261015T154049Z-bf75e41aa33c/rollback`.
Impeccable detector font/palette advisories concern the preserved approved
identity; no design-document or palette repair was performed.

Browser evidence uses Chromium viewport emulation and actual mouse/keyboard
input. Physical devices, Safari and assistive-technology sessions were not
used. Header axe audits do not establish whole-site accessibility conformance.

[Independent review](../../playwright/header-review-20261015/subagent/CANDIDATE-REVIEW.md).
