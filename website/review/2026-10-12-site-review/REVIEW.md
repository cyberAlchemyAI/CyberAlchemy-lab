# Whole-site review

12 October 2026 · findings and proposed changes

The site has a coherent model and working reading paths. The next improvements should address loading, search and interaction behavior. The review found problems on the homepage and robot series as well as in the documentation.

## Main findings

| Priority | Finding | Evidence | Recommended change |
| --- | --- | --- | --- |
| P1 | Homepage icons load their full-size PNGs. | About 10.8 MB of initial resources. Six medallions account for about 10.7 MB. | Supply smaller, visually faithful variants sized for their actual display. |
| P1 | The guide and Craft visibly rearrange during startup. | Five local samples each show substantial layout shifts. Observed scores are about 0.93 for the governance deep link and 0.46–0.67 for Craft overview. | Stabilize initial route rendering and shell dimensions before first paint. Investigate sources of each shift. |
| P1 | Search judgments select their own expected answers. | The builder adds question aliases and derives acceptable destinations from the same index. “Does Accept reserve capacity?” selects a section about changing meaning. “Authority versus provenance” selects the final continue section. Both pass the current check. | Freeze independently reviewed destinations, correct these bindings and retain fresh questions outside tuning. |
| P1 | Ordinary questions still miss existing explanations. | Five of 24 exploratory queries return no results, including session handoff, definition approval and Calculation versus Operation. | Improve question tokenization, comparison terms and partial matching. Keep exact record-title ranking. |
| P1 | The robot series is an isolated page. | No shared search, no indexed robot sections and no link back to the rest of the site. Its logo points to its own top. | Join the series to shared navigation and search while preserving its exploratory format. |
| P1 | Skip links change the current topic. | From the map, essay 6 and Craft taxonomy, activating Skip switches to the guide entrance, reference entrance and Craft overview. In the guide and Craft, the next Tab returns to the header. | Make Skip preserve the current topic and move keyboard focus into its visible content. |
| P2 | Fit does not fit five map views. | A 972 px SVG remains inside a 778 px panel after selecting Fit. Governance fits because its SVG has a different nesting structure. | Separate interactive-map sizing from static-illustration minimum widths. Check all views and zoom states. |
| P2 | Chapter and region semantics need repair. | Best-practice flags in 12 states: skipped headings, repeated table-region names, duplicate library-region names and the response form's missing main landmark. | Correct rendered heading levels and label each table by its subject. Inspect skip behavior and real announcements. |
| P2 | Diagram text falls behind the larger reading scale. | Some map labels render at about 10–11 px; static diagram labels around 13 px. Fitting makes text smaller. | Improve label size and layout together. Keep the inspector and relationship-list alternatives. |
| P2 | Availability is difficult to establish from the entrance. | Homepage says open-source; current installation/product limits and Craft's closed-beta scope appear deeper in the reading paths. No repository URL appears among the site's external links. | Offer a short current-scope route near the primary action and identify the intended source/contribution destination. |
| P2 | Reference browsing carries a large document. | 3.02 MB raw HTML and roughly 27,900 DOM nodes. A theoretical gzip encoding is about 291 KB; compression does not remove DOM work. | Evaluate smaller catalog documents or separate static record pages, preserving exact bodies, direct links and offline search. |
| P3 | Page families lack one consistent route home. | Marketing, documentation and robot brand links have different destinations. | Add a predictable route to the Lab homepage and research pages. |
| P3 | Two complete guide copies are delivered. | The guide alias has identical bytes and no canonical link or redirect. | Choose one canonical guide route while preserving old deep links. |
| P3 | The learning story adds an avoidable branch. | Its speculative mutable-data lesson excludes the fixed S1 incident. The text is consistent, but readers must track the change in applicability. | Label the later hypothetical branch clearly and observe whether readers confuse advice with a causal finding. |
| P3 | Robot favicon is missing. | One recorded HTTP 404 for favicon.ico. | Reuse the site's favicon. |

P1 means address before the next reading release. P2 affects interaction, accessibility or understanding and belongs in the same improvement cycle where feasible. P3 is a smaller coherence or maintenance improvement. These priorities are review judgments, not a universal UX score.

## What was inspected

- All 22 delivered HTML files: 15 public reading pages, a response form, five redirects and one guide alias.
- Fifty-five page/chapter states: all twelve guide topics, seventeen library routes including eight essays, thirteen Craft topics and the standalone surfaces.
- 440 distinct layout observations: Chromium at 1440, 1024, 390 and 320 px; Firefox and WebKit at 1440 and 390 px. Nine initial collection timeouts were retained and successfully repeated after resetting the page between injected scans.
- All ten map layouts, 87 node selections and 87 edge-to-text comparisons. Selected concept titles match and every inspected edge has a text equivalent.
- Homepage role controls, reading-path navigation, Back/Forward, keyboard search, Escape focus return, catalog recovery, phone navigation, definition disclosure, session demonstration, Craft figure dialog and local response download.
- Ten actual Chromium zoom observations at 200% and 400%, across homepage, introduction, an essay, Craft and the robot page.
- HTTP root, project-subdirectory and local-file delivery; JavaScript redirects and the three legacy no-JavaScript fallbacks.
- Forty local performance samples across eight routes, with network cache disabled per fresh tab.

These are browser observations and expert review. They do not establish real newcomer comprehension, physical-device usability or actual Safari behavior.

## Structural and model results

All 631 manifest-listed files were served with matching digests. No local resource is missing across 3,449 inspected references. The 21 statically unresolved fragments all concern the JavaScript-created Craft overview, which was inspected in the browser. No page-level horizontal overflow remains in the 440 final layout observations; diagrams and tables use their own scroll regions.

The build reproduced archive SHA-256 `96b0f08ee90b9026523d748a71c025a2c9041fa232de546c9dd396aa67b25b29`. ZIP integrity passed. The 454 exact reference bodies match their preservation baseline. The 484 captured source files still exist; only the repository README differs from the capture.

No new contradiction was identified in the reviewed model explanations. Definition authority, action permission, evidence support, subject lifecycle, machine-session memory and durable Project State retain their distinct meanings. The capacity example still distinguishes the pure Calculation from a state-changing reservation. [Content review](CONTENT-REVIEW.md).

## Search result interpretation

The existing 39 judged queries mechanically pass. That count is weakened by coupled alias and expected-target construction, and by the two incorrect destinations listed above.

The additional 24 questions were chosen before inspecting rankings. Ten initially met their target judgments. Four more have relevant first results after explicit adjudication: the compiler overview, the three capacity boundary cases, the exact Project State record and the incident's permission scope. The original judgments and corrections are retained. This exploratory set is not participant evidence or a statistical success rate for all searches.

## Accessibility and performance limits

Fifty-five scans report zero WCAG-tagged violations in their visible states. They also report 17 best-practice rule occurrences across 12 states and 1,129 incomplete nodes. Each incomplete target and its checks remain in the evidence, with a disposition. Incompletes largely concern contrast behind images or obscured content; real announcements and assistive-technology navigation remain open. [axe explains its rule classes and incomplete results](https://github.com/dequelabs/axe-core). Heading review follows [W3C guidance](https://www.w3.org/WAI/tutorials/page-structure/headings/).

Local performance results describe one WSL/Chromium environment, fresh tabs, disabled network cache, retained OS cache and a short observation window after fonts settle. The shift measurements are startup diagnostics, not lifetime field percentiles. No INP or hosted Core Web Vitals verdict is claimed. [Web Vitals guidance](https://web.dev/articles/vitals).

The prepared GitHub workflow has not been dispatched. No publication or Lab admission occurred. The local preview remains at the same address.

## Next work

Start with media and startup rendering, then search and whole-site navigation, graph sizing, accessibility structure and reference-page cost. [Concrete change plan](NEXT-STEPS.md).

Actual reader responses, real screen-reader operation and actual Safari/device observations remain separate follow-up evidence. The reader tasks should include the homepage, availability, research and the robot series alongside the existing documentation study.

## UX Evidence Validator result

- Status: flag.
- Mode: validate-interface and report.
- Target: the full delivered website, bound to the current release manifest.
- Evidence cards: [source-cards.json](source-cards.json), W3C, NN/g, Diátaxis and primary literature.
- Browser evidence: local `website/output/playwright/ux-validator/20261012-whole-site/`, including metadata, measurements, ARIA snapshots, screenshots, traces and findings.
- Fixture calibration: existing structural preservation/calibration evidence retained. This run promotes no reusable hard gate or universal UX score.
- Findings: the prioritized table above and FINDINGS.json.
- Residue: participant comprehension, real assistive technology, actual Safari/phone and hosted field performance.
- Validation: the scoped observations and checks above.
- Next lifecycle step: apply the concrete improvement plan, then repeat affected checks and observe readers.
