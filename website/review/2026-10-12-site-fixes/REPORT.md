# Website fixes and verification

13 October 2026. Local implementation of all 15 findings is complete. The scope covers the whole website: homepage, company story, research, guide, eight expanded essays, reference catalogs and records, practical guides, Craft, robot essays, event page and reader form.

The exact selected source repository is [CyberAlchemy-lab](https://github.com/cyberAlchemyAI/CyberAlchemy-lab). The site links to this address. Its public website address is still unset, so canonical metadata stays portable. This work did not publish the site, change GitHub visibility or admit any Lab records.

## Changes

| Finding | Applied change | Status |
| --- | --- | --- |
| F01 | Six vector role illustrations; stable dimensions and an uncrowded responsive role map. | Verified locally |
| F02 | Reserved shell space, route preparation, bounded startup fallback and readable no-JavaScript content. | Verified locally |
| F03 | Frozen exact destinations separated from explicit vocabulary; corrected capacity and authority/provenance bindings. | Verified locally |
| F04 | Question parsing, lexical weighting, inflections, bounded typo recovery and unknown-query rejection; separate answer adjudication and unrun reader prompts. | Verified locally |
| F05 | All robot essays join site navigation, shared search and the research route. | Verified locally |
| F06 | Skip links preserve the active topic, focus its visible content and continue Tab inside main. | Verified locally |
| F07 | Fit and zoom work in all ten map layouts, with matching relationship text and 87 selectable nodes. | Verified locally |
| F08 | Repaired headings, subject-specific table names, landmarks and keyboard access to record code. | Verified locally |
| F09 | Larger diagram text, recalculated wrapping/captions and corrected measured label bounds. | Verified locally |
| F10 | Source/status entrance, practical next steps and the exact user-selected repository link. | Verified locally |
| F11 | Compact catalogs, 454 exact static record pages, complete deferred search, compressed local delivery and plaintext fallback. | Verified locally |
| F12 | Predictable homepage and research links across page families. | Verified locally |
| F13 | Query/hash-preserving guide redirect and portable canonical/share metadata. | Verified locally |
| F14 | Explicitly separate the later hypothetical lesson from the fixed S1 incident; extended reader tasks are ready. | Verified locally |
| F15 | Robot series reuses the existing favicon, with no favicon request failure in the current matrix. | Verified locally |

The six editable vector illustrations total 5,060 bytes, replacing about 10.7 MB of deployed bitmap medallions. Original bitmaps remain in source. Larger reading text and icon labels fit in intrinsic rows on compact screens. Measured role/label boxes do not overlap at 1440, 1024, 640, 390 or 320 px. The desktop map retains its visual connections. These illustrations depict responsibilities rather than declaring new ontology relations.

## What was checked

- 25,531 integrated structural checks pass. The release contains 478 HTML files and 1,103 packaged files, including its manifest.
- 528 browser observations cover 480 distinct route/viewport/engine states. Chromium uses 1440, 1024, 390 and 320 px; Firefox and Playwright WebKit use 1440 and 390 px. The 480-state matrix was followed by 48 checks of affected pages after spacing and event-page edits. Their latest observations replace the earlier states. No page overflow, failed load or runtime event was recorded in these current checks.
- All ten system-map layouts Fit and zoom. All 87 selected nodes show the expected inspector heading, and the relationship lists match the diagrams. Keyboard selection, topic-preserving skip links, search keyboard movement, Escape, browser history, local response downloads and catalog recovery were exercised.
- Fourteen static figures have no measured text outside their nodes or SVG bounds in Firefox. The earlier Chromium figure pass also recorded zero such issues. Visible labels and relationship text remain available separately from diagrams.
- Five page families reflow at actual 200% and 400% Chromium browser zoom. No page-level horizontal overflow was measured. Wide technical figures still have their labeled scrolling/panning regions.
- Root hosting, a project directory, file origins and no-JavaScript reading pass 47 delivery scenarios: 21 redirects, 15 searches, two complete plaintext fallbacks and nine no-JavaScript routes. Redirects preserve the specified query/hash behavior. The reader form cannot accidentally submit answers without its script.
- All 1,102 manifest-listed deployed resources returned HTTP 200 with matching hashes. 16,958 local references have no missing or out-of-site dependency. The 479 statically unresolved fragments all target Craft's dynamically created overview; actual route checks and the readable no-JavaScript article are recorded. They are not missing files.
- All 454 reference-body fingerprints match the preserved baseline in identity order. The Markdown import reports 493 pages, 63 assets, zero unresolved links and zero changed captured-source bytes. Comparing the retained capture to current repository files finds one existing README drift among 484 compared files. The capture was preserved rather than silently refreshed.

## Search and loading

Search contains 707 entries in 13 groups. Its fixed curated judgments pass 39/39. The original broader questions retain a literal score of 21/24 and the later expert set 15/16. Each set has zero empty results. Three original misses return valid alternate destinations, and the later miss directly answers the question in the first result while its frozen target ranks fourth. These decisions are recorded in `search-adjudications.json`; they do not replace the literal scores. Four unrelated negative queries return no result.

The evaluated expert sets have been examined during development. They are not untouched holdouts or reader measurements. Eight unrun prompts in `reader-search-reserve.json` support a later reader review, with query wording and answer judgments kept out of index vocabulary.

The catalog is about 485 KB instead of 3.02 MB, with roughly 5,600 DOM nodes instead of 27,900. Exact bodies live on static record pages, and their old links resolve to those identities. Complete-record text loads when needed. Global search loads on first use.

Current complete search payloads are 1,921,487 bytes and 1,035,590 bytes. Their compressed local scripts are 367,867 and 215,184 bytes. Decoded bytes, plaintext fallback and recorded digests match. Native decompression uses [DecompressionStream](https://developer.mozilla.org/en-US/docs/Web/API/DecompressionStream); tested plaintext fallback supplies the same full content when this API is absent. File-origin delivery needs no external service or fetch request.

Forty desktop samples record zero short-window startup CLS for home, company, research, start and robot routes. Guide/library are approximately 0.0046–0.0047 and Craft about 0.000073. These are local observations over 600 ms after fonts become ready.

The latest five simulated-phone samples use 390×844 CSS pixels, 4× CPU slowdown, 100 ms latency and 1.6 Mbit/s download. First global search takes 3.76–5.67 seconds; complete catalog filtering takes 1.82–2.78 seconds. An earlier plain-payload run took roughly 10.9–14 seconds for first global search. These separate local runs, some alongside other browser checks, do not establish physical-device performance, hosted percentiles or INP.

## Accessibility and reader follow-ups

The 60 current visible desktop states have zero axe violations under WCAG tags and best-practice checks. Every incomplete node is retained in `accessibility/incomplete-node-register.json` (1205 nodes). An incomplete result is not a pass. Dynamic search controls were also exercised with the popup open, and skip navigation was checked with the keyboard.

Remaining manual work covers symbolic/illustrated content, obscured or overlapping backgrounds, dynamic popup reference interpretation and actual assistive-technology operation. Automated results do not establish full WCAG conformance. The maintained [accessibility disposition](ACCESSIBILITY-RESIDUES.md) explains these limits.

The user is arranging newcomer readers and explicitly requested continued preparation while responses take time. Their comprehension, including the distinction between a hypothetical lesson and the established incident, is deferred. Screen-reader sessions, actual Safari/physical-phone checks and hosted field performance also remain follow-ups. The site supplies a twelve-task local response form. Its synthetic download check is labeled NOT A PARTICIPANT RESPONSE.

The research guidance remains the original review's [WCAG 2.2 reference](https://www.w3.org/WAI/WCAG22/quickref/), [task-scenario guidance](https://www.nngroup.com/articles/task-scenarios-usability-testing/), [Diátaxis](https://diataxis.fr/) and [Web Vitals guidance](https://web.dev/articles/vitals). Standards checks, expert editorial judgment and actual reader evidence are reported separately.

## Release and evidence

The repeated build uses identical maintained inputs and produces the same archive, with zero differing entries and a successful ZIP integrity check. A fixed `calendar_revision_at` replaces wall-clock calendar generation. Existing concurrent event edits were preserved and checked again.

Archive SHA-256: `a71b054d3c0fa9289371bee8db236f9be5ec3196b325c5b8a4b60ff80edfb352`. The verified archive is `website/artifacts/reviewed-20261013-website.zip`, with its separate `reviewed-20261013-build.json` receipt. Its exact package is saved under the ignored review output's `verified-source/website/dist/`. The working `website/dist` remains available for ongoing edits and must not be assumed to share this snapshot's hash. Future source edits require rebuilding and renewed checks of affected surfaces.

Maintained evidence: `COMPLETION-AUDIT.json`, `FINDINGS.json`, the collectors and the independent search judgments/adjudications in this folder. Local raw evidence: `website/output/playwright/ux-validator/20261012-site-fixes/`, including screenshots, ARIA snapshots, traces, accessibility findings, measurements, console/network dispositions, hashes and residues. Generated raw evidence stays out of the deployment archive and Git.

Earlier failures remain development evidence. The missed skip selector, record heading/scroll accessibility, robot compact overflow, figure wrapping and central-label collision were repaired and checked again. A collector's missing screenshot helper and mistaken session-button expectation were collector errors; corrected probes passed. Two earlier WebKit navigation cancellations remain recorded separately from the failure-free current matrix/delivery checks. The earlier overwritten ignored search diagnostic is disclosed in `PROGRESS.md` rather than reconstructed as original evidence.
