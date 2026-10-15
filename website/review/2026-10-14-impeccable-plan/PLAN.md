# Website improvement plan using Impeccable

14 October 2026 · Proposed implementation plan · Target: the existing CyberAlchemy Lab website in this repository

Improve the paths from discovering the Lab to understanding a concrete example, finding an exact record, or joining the hackathon. Preserve the approved centered homepage, orb, editorial voice, existing documentation structure and static delivery. Start with the event's unavailable actions and mobile wayfinding; then improve first value, reading hierarchy and search responsiveness. Add expressive detail only where it helps those jobs.

Impeccable is downloaded at `/home/vlad_/projects/impeccable`, from [pbakaus/impeccable](https://github.com/pbakaus/impeccable), commit `2f98774f86bc05563876643db37e6c37c322850f`. The checkout has package version 4.5.2 and engine 0.1.14. Its 24 commands, 59-rule registry, browser tools, context model and integration surfaces are accounted for in [the capability map](IMPECCABLE-CAPABILITIES.md). This plan uses those resources; it does not claim that all 24 workflows were executed.

## Design direction

The existing identity is the starting point. Marketing uses a warm paper ground (`#fdfaf3`), dark ink (`#151515`), crimson action accent (`#bd1230`), the supplied orb and logo, and a centered homepage opening. Documentation uses its established white reading canvas, blue wayfinding, consistent header, side navigation and readable text. Treat these as related surface systems with different jobs. Avoid forcing a single background or accent onto every page.

| Surface | Impeccable mode | Visitor success | Proposed improvement |
| --- | --- | --- | --- |
| Homepage, company and research entrances | Persuade | Understand the Lab and choose a useful next step | Preserve the opening; bring a concrete example into the early journey |
| Hackathon | Persuade, with task controls | Understand the challenge and reach the currently available action | Honest phase status, working links and a direct action path |
| Start, guide, essays, Craft and robot articles | Read | Understand the topic and continue without losing context | Predictable reading frame, purposeful hierarchy and useful next steps |
| Catalogs and exact records | Read, with Operate controls | Find and inspect the right identity and version | Faster entry into lookup; clear summaries and complete records |
| Search, maps and local reader form | Operate within the page | Complete a lookup, inspect a relationship or save a response | Visible state, keyboard operation, recovery and responsive controls |

Working audience assumptions are newcomers evaluating the Lab, developers exploring Craft, returning readers looking for exact contracts, and event participants on phones. These are planning assumptions derived from existing content, not a completed audience study. Use the prepared reader sessions to refine their priority. Do not delay the known event and navigation work on that study.

## Current evidence and what it means

The existing site already has a shared token file, responsive typography, six vector role illustrations, a working system map, static exact-record pages, deferred complete search and a substantial review. Keep those gains. The 13 October documentation report records 454 preserved record bodies and improved record navigation; its results belong to that edition. New work must recheck affected behavior against its own exact output.

This inspection used the current `website/dist`, with 478 HTML files and 708 search entries. The existing build receipt identifies archive SHA-256 `89c6316fc8309faabb1c73c41f48a9d6cf0b928b05e0b2877ed0d2c3356f6bc6`; this plan does not rebuild the site or independently certify that archive. [BASELINE.json](BASELINE.json) binds the source and rendered files inspected here.

Seven page families were inspected in Chromium at 1440 and 390 CSS pixels: home, hackathon, start, guide, catalog, exact Definition record and Craft. All fourteen measured states had no page-level horizontal overflow. The screenshots establish these rendered states, not physical touch behavior, reader comprehension or complete accessibility conformance.

| Priority | Finding or opportunity | Evidence and qualification | Planned response |
| --- | --- | --- | --- |
| P1 | Event actions are unavailable during the scheduled registration/build phase | `hackathon.json` opens registration on 13 October at 18:00 UTC−3; registration, submission, gallery and voting URLs are all null. Missing future gallery/voting URLs are not themselves current failures. | W1: expose an honest current phase and connect organizer-supplied, tested links |
| P1 | Homepage label may lose contrast over the orb | Rendered Impeccable scan at 1440 reports 4.2:1 for `div.product-hero-copy > p.eyebrow`. This is a pixel-based detector candidate requiring focused contrast verification. | W2: verify the actual composited background; darken the label or stabilize its background within the existing identity |
| P2 | Later mobile navigation links are clipped with weak discovery | At 390px, the marketing navigation has 440px scroll width inside 356px; documentation has 371px inside 356px. Horizontal scrolling exists, but screenshots cut off Documentation or Craft. | W2: visible overflow affordance or a native disclosure, preserving direct access and keyboard order |
| P2 | The first concrete example arrives after a long abstract introduction | Homepage screenshot shows a strong opening and two actions; its four subject links lead into the model. The incident example is in the later Explore section. A newcomer benefit from moving it earlier is a hypothesis. | W3: early, compact example entry; test whether it improves first useful destination |
| P2 | Catalog entry emphasizes scope before the lookup task | At 390px, the first viewport contains the title, explanation and identity totals; category lookup is a later step. Global search is already present. | W3: make lookup/category access easier to find without removing scope or complete text |
| P2 | Some reading roles and mobile section rhythm deserve adjustment | Rendered scan reports an approximately 96-character line in catalog helper copy and five mobile heading-rhythm warnings. Current browser measurements also find a few 11.69px home labels. These are review candidates, not a reason to reduce the established body scale. | W4: tune measured roles and section spacing in the owning stylesheets |
| P2 | Search latency remains a known optimization target | Earlier local simulated-phone report records 3.76–5.67 seconds for first global search. This is historical local evidence, not a fresh measurement or hosted percentile. | W5: reproduce a cold/warm baseline and optimize the measured bottleneck |
| P2 | Accessibility and reader evidence remain incomplete | Existing review retains incomplete contrast/illustration/ARIA checks and manual screen-reader/device follow-ups. | W6: close relevant residues with recorded observations and reader sessions |

### Detector interpretation

The seven-file static scan returned 858 rows: 857 warnings and one advisory. Of these, 794 are `cramped-padding`. Rendered scans of five routes returned 11 rows at 1440px and 13 at 390px. The rendered route set is smaller, so these totals are not a controlled reduction score.

Static size findings such as the hackathon's alleged 9.92px brand text and Craft's tiny controls did not reproduce in the sampled rendered text. Treat those as unconfirmed cascade/visibility artifacts. Full-width section wrappers with padded inner containers are also poor candidates for blanket padding edits. Preserve raw findings and document representative dispositions before changing styles.

The cream-palette, numbered-section-label, tracked eyebrow and Craft eyebrow warnings are aesthetic prompts. They do not override the existing brand or an approved composition. Inspect whether each helps hierarchy; retain it with a reason where it does. The desktop contrast candidate and catalog line length deserve focused verification. Do not make "zero detector warnings" the success metric.

## Implementation work

Suggested effort below is focused engineering/design work by one implementer, not a calendar promise. Reader availability and organizer-owned form setup are separate. Work in small reviewed changes, in the existing Python/HTML/CSS/JavaScript stack.

### W0 — Capture product and visual context

**Priority:** foundation · **Estimate:** half a day · **Dependencies:** none

Record a website-scoped `PRODUCT.md` and `DESIGN.md`, with shared context and separate briefs for home, docs, reference and event surfaces. Use Impeccable `init` and `document` when adopting its persistent workflow. Confirm only material audience or product gaps; extract visual facts from actual CSS and rendered pages. Never use Impeccable's own PRODUCT.md or DESIGN.md as CyberAlchemy truth.

The context loader currently finds no PRODUCT.md or DESIGN.md and reports no visual implementation for the `.html.in` target. Direct inspection establishes that the site has a mature implementation. Resolve its website boundary and template/rendered target mapping before relying on that detection. Prefer website-scoped context over giving the entire Lab repository a website identity.

Capture the existing palette, type roles, body scale, selected-state styling, focus treatment, spacing, diagrams and supplied assets. Record the approved prose workflow, source capture dates, formal-body preservation rule, complete-search requirements and hosting modes. Add a short token ownership table rather than a competing design system.

**Completion:** context points to the actual website; assumptions are labeled; the four briefs name audience, task, layout, states and preserved assets; the existing identity is reproducible from source. W1 can proceed from current configuration while this context is recorded.

### W1 — Repair event status and the action path

**Priority:** P1 · **Estimate:** half to one day of site work · **Dependencies:** organizer supplies and tests live links for activation

**Files:** `website/hackathon.json`; `website/source/governance-lab-series/research_pages.py`; `templates/lab-landing.html.in`; `templates/hackathon.html.in`; `assets/hackathon.css`; relevant entries in `website/editorial-copy.json`.

1. Define pre-opening, registration/building, submission-closed, voting, review and results states from the confirmed UTC−3 schedule. Account for null URLs separately from time: an open date does not prove a form is available.
2. Replace the permanently future-tense announcement with phase-appropriate copy. While a required form is absent, say registration details are pending and offer the existing organizer contact; keep the challenge/rules usable.
3. Put the currently available primary action with eligibility, deadline and essential prize explanation. Keep full terms in the existing rules/disclosures. Do not invent URLs, form controls, winners or changed prize terms.
4. With organizer-provided links, test access as an ordinary participant. Activation requires confirmed roster/submission/ballot controls; drafting UI can proceed beforehand.
5. Preserve deterministic builds: use a declared build-phase timestamp, or a progressively enhanced browser status with explicit timezone and a useful static fallback. Test schedule boundaries; never make builds vary accidentally with wall-clock time.

**Completion:** no current action leads to a fake or missing destination; homepage and event agree on phase; registration availability is honest; deadlines and calendar files agree; keyboard/no-JavaScript paths remain useful. A missing organizer URL stays a named operational dependency, not a reason to hold unrelated UI work.

### W2 — Improve mobile navigation and verify hero contrast

**Priority:** P1/P2 · **Estimate:** one day · **Dependencies:** current source baseline

**Files:** `assets/research-site.css`, `assets/lab-docs.css`, `assets/site-typography.css`, `assets/site-search.js` under the Lab source; shared header generation in `research_pages.py` and existing templates; `website/reference_pages.py` where the record shell uses the same header.

Keep the logo, search and current section discoverable. First try a visible scrolling cue and correct scroll-into-view for the selected link; if that remains unclear in a phone check, use a named native menu disclosure. Do not increase header height indiscriminately or bury search. Preserve all five destinations and focus order. Apply the same decision to marketing, guide, Craft and record headers.

Verify the homepage eyebrow's foreground against the actual orb/background at desktop and phone sizes, including fallback fonts. Fix any confirmed normal-text contrast failure through the existing accent/background tokens and local treatment; retain the orb and centered composition. Check hover, focus and selected states as well.

**Completion:** a phone user can discover Documentation and Craft without guessing; keyboard traversal exposes hidden links; the current destination remains apparent; search and skip links work; header/anchor offsets still match; verified contrast pairs and screenshots are retained. Test 320, 390, 768, 1024 and 1440px plus 200%/400% zoom for affected shells.

### W3 — Make the first useful destination easier to reach

**Priority:** P2 · **Estimate:** one to two days · **Dependencies:** W0 direction, W2 header decision

**Files:** `templates/lab-landing.html.in`, `templates/start-here.html.in`, `templates/incident-walkthrough.html.in` if present, `assets/research-site.css`, `assets/start-here.css`, `assets/lab-library-docs.css`, catalog generation in `research_pages.py`, and `website/editorial-copy.json`. Resolve renderer-owned pages to their generating module before editing.

Preserve “An open company brain” and its approved opening. Make “Follow an incident” available earlier as a compact secondary path or the first useful section after the topic row. Show one existing relationship—meaning, work, evidence, decision—with the existing incident and diagrams; distinguish illustrative material from an admitted record. Avoid adding a second competing hero or another repeated card grid.

Keep newcomer and returning-reader paths legible: understand the model, follow a worked example, find an exact definition. The reference entrance should expose a clear lookup/category action before extensive catalog totals while keeping capture scope and complete records available. Existing global search remains the cross-site route.

For Craft, make the smallest existing modeling example easier to enter from its 45-minute article. Reuse the established Calculation/Operation explanation and exact section links. Do not imply a public stable release, ready hosted product or a capability absent from the current implementation.

**Completion:** each entrance has one primary next step; example and exact-lookup routes are discoverable; all existing destinations still resolve; readers can return to the parent topic. Use a small formative reader session to compare first choice and explanation of the Lab/Craft relationship. Record mistakes as well as successes; do not call expert review comprehension evidence.

### W4 — Consolidate hierarchy and reusable presentation roles

**Priority:** P2 · **Estimate:** one to two days · **Dependencies:** W0, W2; final W3 composition

**Files:** `assets/kep/design-system.css`, `assets/site-typography.css`, `assets/research-site.css`, `assets/lab-docs.css`, `assets/lab-library-docs.css`, `assets/reference-reading.css`, `assets/reference-record-page.css`, and Craft's `assets/craft-article.css`.

Audit computed styles before editing. Preserve roughly 20px desktop and 19px compact reading text and the current readable navigation. Correct small home labels, long catalog helper lines and the heading-to-paragraph rhythm where the rendered evidence warrants it. Keep headings grouped with the text they introduce. Use comfortable reading measures; account for actual font metrics instead of applying a global character count blindly.

Extract only repeated patterns with the same job, generally three or more uses: header action, metadata row, disclosure, catalog entry, next-step link and focus treatment. Keep the current semantic tokens as the source; name genuine missing roles and remove obsolete overrides only after comparing all affected page families. Small controlled changes are preferable to replacing the CSS cascade in one pass.

Keep distinct colors for action, selection, evidence roles and status; accompany meaning with text or shape. Use colorize for semantic consistency and quieter for excessive reading-frame noise. Use bolder only for a specific weak hierarchy in marketing; do not turn reference text into promotional typography.

**Completion:** repeated roles agree across home, guide, Craft, catalogs and records; no unexplained sub-12px functional label remains in affected views; long titles, code, tables and enlarged text reflow; a before/after comparison confirms the current identity and formal content.

### W5 — Reduce measured search and interaction waits

**Priority:** P2 · **Estimate:** one to two days · **Dependencies:** fresh cold/warm measurements; can run alongside W3/W4

**Files:** `assets/site-search.js`, `assets/search-engine.js`, `assets/site-search.css`, `build_site_search.py`, `search_relevance.py`, `upgrade_search_delivery.py` in the Lab source; `website/build.py` only for packaging changes supported by measurements.

Reproduce first-use search with a fixed network/CPU profile, separate download/decompression/parse/index/query/render time, and record warm queries independently. Announce loading immediately and distinguish no results, an unavailable index and a successful search. Preserve keyboard selection, Escape and focus return.

Choose optimization after attribution: prewarm on genuine search intent, move expensive indexing/query work off the critical interaction path, or separate a small title index from a complete-text index. Preserve the complete corpus and loading fallback, file-origin compatibility and project-path URLs. Avoid adding a framework or hosted service. Do not force a worker path onto `file:` origins that cannot support it; retain a tested fallback.

Proposed acceptance budgets: warm query response within 200ms locally; first useful cold results within two seconds on the agreed simulated phone profile, with immediate truthful loading feedback. These are project targets to validate, not current measurements or field INP claims. Compare at least five reproducible samples and report the range and median. If the target is impractical while preserving complete delivery, document the measured tradeoff before changing the contract.

**Completion:** cold/warm measurements improve without relevance or corpus regressions; frozen expected destinations remain independent of ranking vocabulary; held-out reader queries stay out of tuning until evaluation; gzip/plaintext payloads and file-origin delivery still match.

### W6 — Harden controls and close accessibility residues

**Priority:** P1 for confirmed task blockers; otherwise P2 · **Estimate:** one to two days plus human sessions · **Dependencies:** affected UI changes

**Files:** shared search/navigation controls; `assets/hackathon-carousel.js`; map controls in the owning `assets/system-map*` files; reference disclosure scripts; the existing local reader-form sources and review collectors. Resolve exact source ownership before mutation.

Exercise real states: open/closed menus, loading/empty/error search, direct fragments into a formal disclosure, long record names, font failure, reduced motion, increased text size and no JavaScript. Keep the reader form's download behavior explicit; do not imply a network submission. Expose recovery adjacent to the failed action.

Review the carousel's existing Pause/Play, focus pause, reduced-motion behavior and touch cancellation before adding behavior. Test swipe with synthesized touch and interruption, then with an actual phone when available; viewport emulation alone does not establish gestures. Preserve relationship lists and standard keyboard alternatives on maps.

Use the retained incomplete-node register to select focused manual checks: search popup announcements, skip destinations, illustrated/overlapping contrast and diagram alternatives. Record actual screen-reader and Safari/device sessions separately from Chromium or Playwright WebKit. Apply at least 44px hit areas where practical as a design target, while interpreting standards according to the retained WCAG source rather than treating every smaller link as a violation.

**Completion:** primary flows are keyboard-operable with visible focus and meaningful announcements; reduced motion retains useful state feedback; confirmed relevant findings have either a fix or a concrete remaining manual check; no claim of full accessibility conformance comes from a clean detector scan.

### W7 — Optional signature detail and bounded finishing pass

**Priority:** P3 · **Estimate:** half to one day · **Dependencies:** W1–W6 accepted for their scope

Use animate/delight for one useful moment: visibly connect a selected model node to its inspector, clarify a search state transition, or make the event idea control respond cleanly. Preserve immediate reading and a stable reduced-motion state. The current vector icons and orb are supplied assets; reuse them before generating replacements.

Reserve overdrive for a separate optional experiment, such as a guided incident path through the existing map. It must preserve the exact model and text alternative, have a static fallback and demonstrate a comprehension or interaction benefit. It is outside the core delivery estimate. No shader, global motion layer or new image campaign is required by this plan.

Finish with polish on the entire changed journey. Run one batched desktop/phone review, fix confirmed defects together, then one confirmation pass. Further iterations require a concrete remaining defect. If alternatives are useful, generate no more than three variants of one scoped element; carry the accepted result back to maintained templates/CSS before rebuilding.

**Completion:** purposeful detail survives reduced-motion/performance review; no generated wrappers or temporary overlays ship; final screenshots represent the actual built source; the release checks below pass.

## Sequence and delivery slices

| Slice | Work | Outcome | Indicative effort |
| --- | --- | --- | --- |
| A | W0 context plus W1 event and W2 navigation/contrast | Honest current actions and easier phone access | 2–3 days of site work; link activation depends on organizer inputs |
| B | W3 first value and W4 hierarchy | More useful entrances and consistent reading | 2–4 days |
| C | W5 search and W6 control resilience | Faster lookup and verified interaction paths | 2–4 days plus reader/device sessions |
| D | W7 finish | One coherent, reviewed candidate | Half to one day; experimental overdrive excluded |

Dependencies: W0 informs W3/W4; W1 and W2 can start from known evidence; W5 can proceed independently after baseline capture; W6 verifies each changed journey; W7 closes the selected scope. Use a separate change per slice so layout, lookup and event behavior can be reviewed and rolled back independently.

## Release checks

1. Build using `website/.venv/bin/python website/build.py`. Edit maintained templates, renderer modules, assets and adopted prose; never ship direct edits made only to `website/dist`.
2. Compare all 454 formal record bodies against the fixed preservation baseline. Preserve identities, code, quotations, formal terms, capture scope and legacy routes. Do not run `build_research.py` or refresh repository-readable docs as a side effect.
3. Reuse the existing structural, search, delivery and documentation-consistency checks. Cover changed families at 320, 390, 768, 1024 and 1440px; search/map/disclosure states; 200%/400% zoom; root, project-subdirectory, file-origin and no-JavaScript delivery where applicable.
4. Run Impeccable on representative built HTML and the corresponding rendered URLs at desktop/phone sizes. Retain raw output and adjudicate rule/selector examples. Add only narrowly justified ignores; never silence whole classes to pass.
5. Keep visual checks, automated accessibility, actual assistive-technology/device observations and reader findings separate. Report unrun checks as outstanding, with their exact scope.
6. Compare before/after performance under the same declared conditions. Preserve independent search judgments and full-text parity.
7. Rebuild and verify archive/manifest integrity and deterministic bytes for unchanged inputs. Review only intended source changes; preserve unrelated dirty work.

Plan completion means a concrete implementation backlog and baseline, achieved here. Website improvement completion requires implementing and checking the selected work. Deployment and publication remain separate operations against an exact reviewed candidate and the intended host.

## Inputs and open dependencies

- Organizer-owned registration/submission/gallery/voting destinations and access controls. Do not create or message participant accounts as part of website styling.
- Reader feedback to test whether the early example and catalog changes help newcomers; existing facilitator materials are reusable.
- Actual screen-reader, Safari and physical-phone availability for the corresponding manual checks.
- A chosen public base URL before absolute hosted sharing metadata is finalized. `site.json.public_url` is currently null.
- Any request to replace the approved visual identity or factual copy requires an explicit updated brief. This plan proposes refinement inside the current website.

## Evidence and source locations

- Current website instructions: `website/README.md`, `site.json`, `hackathon.json`, maintained templates, shared assets and build scripts.
- Existing local evidence: `website/review/2026-10-12-site-fixes/REPORT.md`, `ACCESSIBILITY-RESIDUES.md`, and `website/review/2026-10-13-documentation-consistency/REPORT.md`.
- Current inspection: `output/playwright/impeccable-plan-20261014/`: fourteen screenshots, `browser-inspection.json`, `controls-inspection.json`, raw static and rendered detector JSON, and collector logs. These are local review outputs, excluded from deployment.
- Impeccable guidance: `skill/SKILL.src.md`, command references, `skill/scripts/command-metadata.json`, `crates/live/assets/antipatterns.json`, README, engine documentation and CLI help in the pinned external checkout.
- Workflow: Arcanum selected `CA2-ROUTE-PLAN`, whose ceiling is planning candidates. Its shared Goals registry reports an admission blocker; this standalone review plan is not registered as admitted execution state. Native inline planning and browser inspection were used. No sigil observer or lifecycle admission is claimed.
