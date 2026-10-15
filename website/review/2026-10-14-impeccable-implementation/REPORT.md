# Website improvement implementation and local verification

14 October 2026 · CyberAlchemy Lab · Verified local candidate

The website improvements in the accepted [Impeccable plan](../2026-10-14-impeccable-plan/PLAN.md) are implemented in maintained source. The centered homepage, supplied orb and logo, warm paper and crimson marketing palette, white and blue documentation, robot article theme, approved editorial copy and captured formal records are preserved. Organizer form activation and human reader, device and assistive technology sessions remain external follow-ups.

Open the local preview at [127.0.0.1:8767](http://127.0.0.1:8767/). The frozen candidate is [impeccable-reviewed-20261014.zip](../../artifacts/impeccable-reviewed-20261014.zip), with [its receipt](../../artifacts/impeccable-reviewed-20261014.json). Its SHA-256 is `cd302c528d4992a76a4a68027816b3ba2a2b69046459f2dece9eb3f33ddb0c4d`. Two consecutive full builds produced identical archive bytes. No deployment was performed.

## Implemented changes

| Plan work | Result |
| --- | --- |
| W0 Product and visual context | Website-scoped PRODUCT.md, DESIGN.md and four native Impeccable surface briefs describe the actual templates, audiences, tasks, states, preserved assets and style ownership. Native context read-back verified their discovery. |
| W1 Event status and actions | Timezone-aware build and browser states distinguish scheduled phases from available links. The current homepage and event page say registration details are pending. Deadline, eligibility and next step appear together. Unconfigured actions remain unavailable; configured links require HTTPS, and the ballot also requires verified access. Browser status updates at the next event boundary and when the tab becomes visible. |
| W2 Navigation and contrast | Native compact menu disclosure exposes all existing destinations and the current section while keeping search accessible. The same behavior covers marketing, documentation, Craft, records and robot articles. The homepage eyebrow uses the existing darker accent. Robot search placeholder contrast is corrected. |
| W3 First useful destinations | An early homepage incident path, Start here shortcuts, an immediate Craft example entry and an earlier reference category index make existing material easier to enter. Illustrative examples retain their status. Scope explanations and complete records remain available. |
| W4 Reading hierarchy | Shared control, metadata and reading roles improve small labels, line measure and mobile heading rhythm. Existing body text scale and separate surface identities are retained. |
| W5 Search performance | A small first-pass index covers every identity and alias, followed by complete text. Versioned lexical features and corpus statistics are compiled during the build; the browser yields between preparation chunks. Initial results render in a bounded list with access to the remaining matches. Complete loading status and focused destinations survive refinement. |
| W6 Control resilience | Search and catalog failures offer retry; loading, empty and error states are distinct. Keyboard navigation, Escape, focus return, disclosures, fragments, legacy routes, reduced motion, carousel swipe cancellation and the local reader download are verified. Carousel semantics and empty-fragment lookups were corrected. |
| W7 Finishing detail | Selecting a company map node briefly connects its inspector through existing color. Reduced motion retains selection and text feedback without the animation. The optional overdrive experiment remains outside the core plan. |

Impeccable is downloaded at `/home/vlad_/projects/impeccable`, commit `2f98774f86bc05563876643db37e6c37c322850f`, package 4.5.2, engine 0.1.14. Its design guidance, context model, native surface briefs, static detector and rendered browser detector informed the work. The [capability map](../2026-10-14-impeccable-plan/IMPECCABLE-CAPABILITIES.md) accounts for all 24 workflows and 59 rules; this implementation does not claim execution of every command or a new audience interview.

## Local verification

The [verification receipt](VERIFICATION.json) summarizes the candidate. Detailed collectors, raw results, screenshots, before snapshots, a source patch and failure history are retained in `output/playwright/impeccable-implementation-20261014` at the repository root.

| Check | Result |
| --- | --- |
| Formal content | All 454 record identities and body fingerprints match the fixed pre-change baseline. Captured edition remains 8 October 2026. Adopted editorial-copy bytes are unchanged. |
| Search correctness | All 708 complete and first-pass identities, URLs and aliases agree. Complete lexical features and global statistics match the browser algorithm for every entry. All 39 frozen relevance judgments pass, with identical raw, compiled, synchronous and asynchronous rankings. Negative queries and the literal word `constructor` regression pass. |
| Delivery and packaging | Three compressed/plaintext payload pairs are identical after decoding. All 1,124 ZIP members match the built site; ZIP integrity passes. All 1,123 manifest-listed HTTP resources match their hashes. Repeat archive bytes are identical. |
| Responsive Chromium | 33 routes at 320, 390, 768, 1024 and 1440px: 165 states, no failed checks or runtime errors. |
| Exact record browser sweep | All 454 record pages at 390 and 1440px: 908 states, no failed checks or runtime errors. This geometry and record sweep preceded the final lexical data optimization; final search and delivery checks exercised the compiled payloads. |
| Firefox and WebKit | Seven page families at 390 and 1440px in each engine: 28 final states, no failed checks or runtime errors, including search. Playwright WebKit is distinct from an actual Safari session. |
| Interaction recovery | 12 final checks pass, covering menus, early paths, search focus and recovery, scopes, pending loads, catalog errors, formal disclosure fragments, map reduced motion, carousel controls and long multilingual input. |
| Hosting modes | 47 final scenarios without collected errors: root and project paths, file origins, legacy redirects, full search, plaintext fallback and nine no-JavaScript cases. |
| Maps and keyboard | Ten map layouts pass fit, zoom and clipping checks. All 87 native-picker node selections show the expected inspector heading, with no missing relationship text alternatives. Keyboard selection passes. This is not a claim that 87 SVG pointer targets were individually clicked. Skip destinations across five families and catalog recovery also pass. |
| Browser zoom | Actual Chromium 200% and 400% settings across five families: ten states without page overflow. A dedicated scratch profile was used and zoom reset afterward. |
| Event boundaries | Seven fixed timezone boundaries, ballot readiness, unsafe URL rejection, safe JSON embedding and UTC calendar checks pass. A browser virtual-clock test confirms an open page changes phase at the deadline. |
| Accessibility | Seven representative desktop axe scans plus compact open-menu and open-search scans report zero violations. Incomplete nodes remain in the raw reports for manual review, including popup relationships and illustrated contrast. Keyboard and reduced-motion checks supplement the scans; these results do not establish full accessibility conformance. |
| Reader form | A clearly marked synthetic response downloads locally and remains explicitly non-participant evidence. No real reader response or network submission is claimed. |

Initial collector failures are retained alongside confirmations. They include an assumption that a disclosure started closed, a WebKit visibility assertion before the documented startup frames completed, a browser zoom attempt without a persistent profile and a Firefox SVG point-click automation limitation. The corrected collectors verify actual state, startup completion, real zoom and the native map picker respectively.

## Search timing and tradeoffs

Five final samples used Chromium at a 390 × 844 CSS viewport, fourfold CPU slowdown, 100ms network latency and 200,000 bytes/s download. Each sample used a fresh tab with network cache disabled; the operating system cache remained available. The local static server sent uncompressed files. These are local simulations, not physical phone results, field percentiles or INP measurements. Search interaction timing begins after page load.

| Measurement | Median | Range |
| --- | --- | --- |
| Input to first useful cold results | 1.43s | 1.29–2.09s |
| Input to warm result paint | 309ms | 160–362ms |
| First interaction to complete corpus readiness, collector wall time | 8.98s | 8.03–11.51s |
| Complete feature preparation | 96ms | 78–152ms |

The proposed cold target is met by the median, with one sample above two seconds. The warm 200ms target remains unmet by the median under this profile; result ranking itself measured tens of milliseconds, while paint includes the control and browser scheduling. The frozen raw algorithm is retained as a verified fallback. Compiled lexical metadata increases the compressed full-index script from roughly 368KB to 759KB while removing expensive browser tokenization. The first-pass script is approximately 93KB and contains abbreviated body text; complete body text becomes searchable when loading finishes, which the interface announces explicitly.

The pre-change first-result collector median was 11.08 seconds; the final comparable collector wall-time median is 2.52 seconds, stored separately from input-to-paint in `performance-compiled.json`. Historical and intermediate profiles are retained to avoid substituting one timing definition for another. Isolated raw-versus-compiled preparation also confirms the CPU improvement with identical lexical inputs. Heavy initial documentation DOM work remains visible in the retained startup traces and is not presented as solved by search compilation.

## Detector findings and visual identity

The final static scan retained 888 rows, chiefly padding heuristics and partial-context palette or size findings. Representative rendered desktop and compact scans were reviewed with the actual cascade. Confirmed homepage contrast, robot placeholder contrast, small robot labels and mobile heading rhythm were corrected. Cream backgrounds, tracked editorial labels and numbered sections remain intentional parts of the approved identity. No broad ignores were added to obtain a zero count.

Screenshots of home, event, Start here, catalog, exact record and Craft at desktop and compact widths are retained with the evidence. Detector warnings are review prompts rather than a quality score; the static and rendered counts cover different surfaces and cannot be interpreted as a controlled reduction percentage.

## Remaining external checks

Registration, submission, gallery and voting URLs remain null in `website/hackathon.json`. The site honestly reports pending availability and retains the organizer contact and complete rules. Supply the real addresses and verify ordinary participant access before activating them. Set `voting_access_verified` only after ballot access has been checked.

Real reader comprehension sessions, held-out participant search queries, physical phone gestures, actual Safari and screen-reader observations remain outstanding. The retained local form, protocols and recordings support those follow-ups; synthetic browser checks do not replace them. These dependencies do not prevent review of the complete local website candidate.

## Maintenance and reproduction

Build with `website/.venv/bin/python website/build.py`, then run `website/.venv/bin/python website/review/2026-10-14-impeccable-implementation/verify_static.py` and `node website/review/2026-10-14-impeccable-implementation/verify_search.cjs`. Browser collectors in this folder use the retained local server paths and Playwright CLI; their result files identify the exercised states.

Edit maintained templates, renderer modules and assets. Keep `status_as_of` deliberate for deterministic static event copy; browser JavaScript calculates the live phase separately. Rebuild after link or schedule changes. Update the lexical version and parity checks together if tokenization changes. Preserve complete corpus delivery, the captured formal-body baseline, file-origin fallback and independent relevance judgments. Do not refresh research or import documentation as an incidental build step.

Thirty maintained source and context files changed, including 21 existing files; the exact patch and hashes are in the evidence directory. Unrelated repository changes were preserved. The original plan and its baseline remain intact. The frozen ZIP excludes development context and review evidence.
