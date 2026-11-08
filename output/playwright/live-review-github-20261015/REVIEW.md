# Live review, mobile repairs and GitHub link

Status: **deployed and verified** at <https://cyberalchemize.com/>.

Used the local Impeccable repository and an independent sub-agent to review the live site and confirm the repairs while preserving the approved Paper & crimson identity.

## Changes

- Added <https://github.com/cyberAlchemyAI/CyberAlchemy-lab> to the homepage More menu and footer, plus shared documentation navigation. The static sidebar fallback includes the same ordinary anchor; 484 delivered documentation sidebars have it.
- Fixed the homepage hackathon announcement's missing horizontal padding: 20px on mobile, 24px on desktop, with wrapping, deliberate spacing and a 44px link target. Its event copy and availability are unchanged.
- Fixed the More dropdown extending off the left edge at 320px when the navigation wraps. At widths up to 370px it now anchors to the header frame. The approved menu appearance remains.

## Verification

- Independent reviewer inspected mobile live route families, navigation, docs and images, and identified the two reproducible defects above. Its initial broad run was interrupted to fix the findings; no completed aggregate broad matrix is claimed. Twelve focused local homepage/docs states initially passed 30 of 32 checks, with only the two light/dark 320px menu bounds cases failing. After the final normal build, all six targeted menu/theme/no-script confirmations passed. Original intermediate failures remain in the evidence.
- Final build: 41,828 checks passed. All 498 routes, existing prose, hrefs and fragment IDs are retained. The 454 formal record bodies, 14 runtime articles, 552 captured source files and 61 image/font assets remain exact. The portable ZIP matches delivered files.
- 23,909 local references: no missing resources or duplicate IDs. All 59 curated search queries and full/quick, build/browser, sync/async, fallback and negative-query regressions pass. Search still contains 806 entries.
- Final live Chromium: 44 mobile/desktop light/dark states covering homepage, docs, paths, graphs, exact record, runtime, event, Craft and Robot learning. Zero overflow, broken rendered images, CSP violations, console/runtime errors or HTTP failures. Ten real interaction checks and four accessibility states pass with zero violations.
- Nine additional actual live narrow-menu/no-script checks passed at 320, 360 and 390px, including GitHub visibility, menu bounds, CTA geometry and static documentation navigation.
- All 1,235 public release files downloaded over verified HTTPS match the local release exactly. One initial file-check attempt hit a temporary local DNS resolution error; the successful rerun cached the resolver answer for the verification run, retaining the domain hostname and TLS verification. The first failure log is preserved.
- Required Impeccable detector scan reported one warning for the already approved Roboto Mono identity; retained intentionally. A later targeted menu CSS repair was verified with actual rebuilt and live browser geometry rather than an additional detector loop.

## Deployment boundary and rollback

Release: `lab-20261015T044607Z-819f60b5a819`.

ZIP SHA-256: `2415ccb5806a51c255fa7a569a198bf24f0103b842f4384f4b5aaf28892fc8a1`.

Manifest SHA-256: `819f60b5a8195dcf63aa8bfe0838378c4c71653e21a6167e68ae15bebd8868d1`.

Staged 1,244 files with a new verified rollback. The final live Nginx configuration, Compose, routing environment, authentication file, eight secondary static files and all unrelated containers remain unchanged. Only the static website container was recreated, using its existing image without a pull. Ten existing public/protected route probes preserve their content and headers; DomainSpec remains protected with anonymous 401 responses.

Private rollback: `/srv/co-op-engine/deployments/lab-20261015T044607Z-819f60b5a819/rollback`. Previous rollbacks, including the original co-op homepage, remain retained outside the web root. The earlier pre-menu-fix stage was superseded without being served; its metadata is retained in superseded-stage and its remote candidate directory is left private.

No Git commit, push, repository publication, database change or unrelated-service restart occurred. The GitHub destination was checked as an accessible repository link; no remote repository content was modified. Browser-engine checks do not imply physical-device or assistive-technology user sessions.

Evidence: RECEIPT.json, public-verification.json, live-browser.json, live-menu-edges.json, screenshots and logs here; independent reports under output/playwright/live-review-github-20261015/agent/.
