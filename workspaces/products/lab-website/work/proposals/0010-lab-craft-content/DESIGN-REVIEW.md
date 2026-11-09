# Design and copy review

Date: **16 October 2026**  
Scope: **the local design and copy documents**.

This record accompanies the [package index](README.md), [UX/UI design](UX-UI-DESIGN.md), [copy deck](COPY-DECK.md), and [destination map](CONTENT-MAP.md). It distinguishes document review from implementation and browser evidence.

## 1. Review responsibilities

| Reviewer | Responsibility |
| --- | --- |
| `ux_ui_design_documents` | Draft UX/UI behavior and composition from the proposal, current source owners, and effective paper/crimson styles; check copy against design |
| `website_copy_documents` | Draft page-ready English in the existing natural editorial voice; check design and route assignments against the copy |
| `design_copy_review` | Independently review the assembled package for coherence, model accuracy, accessibility requirements, navigation, copy completeness, and claim limits |
| Primary agent | Reconcile findings, maintain the route map, check local references and source preservation, and record the actual delivery boundary |

The design work uses Impeccable's shape principles for planning within an established visual identity. The source site and this session supply product and visual context. No new root-level product/design authority file or interface implementation is introduced by these documents.

## 2. Review criteria

- The public story connects practical work to continuing development through governed meaning, scoped authority, artifacts, provenance, and lifecycle.
- The open company brain remains central. Craft retains its distinct software-factory proposition and its broader construction/evolution ambition.
- The copy preserves English, varied sentence rhythm, concrete reasoning, and creative headlines followed by clear explanation.
- A reader can find the campaign, reply, and handoff, as well as meaningful examples for all ten department entries.
- Q1, R1, candidate Q2, acceptance/adoption, later assessment, and permission to spend remain distinguishable.
- The current design system is recorded accurately; new spacing/layout decisions are labeled as proposals rather than claims about shipped behavior.
- Cards have explicit internal spacing; search, compact navigation, reading paths, and diagram expansion have meaningful states and keyboard behavior.
- New routes are candidates, old routes and anchors have a preservation plan, and one task has one canonical story.
- Formal statements, code, quotations, exact example conditions, runtime evidence, and event rules retain their owners and standing.
- Browser, accessibility, performance, or live-site outcomes are claimed only if actually exercised. This document-only delivery supplies no such outcome claims.

## 3. Accessibility reference basis

The specification uses [W3C's reflow explanation](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) to define a later check at 320 CSS pixels. Two-dimensional content exceptions apply to the relevant content, not the whole page. The existing user requirement remains stronger for overview diagrams: their main meaning should be understandable inline without mandatory panning.

The proposed 44-pixel control target is a design choice. [WCAG's minimum-target explanation](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) describes the AA requirement and its exceptions; it should not be paraphrased as a universal 44-pixel requirement.

The expanded graph's proposed modal behavior follows the [WAI-ARIA dialog pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/): meaningful initial focus, contained keyboard focus, an operable close action, inactive background, and focus restoration. The future implementation still needs actual keyboard and assistive-technology review.

## 4. Findings and reconciliation

The independent reviewer read the assembled index, UX/UI specification, copy deck, and content map. The design author also cross-checked the copy against the specified interactions. The following findings were repaired in one reconciliation pass:

| Finding | Repair |
| --- | --- |
| Technical sample-data language leaked into ordinary reader copy | Replaced “fixture” with sample-record language and explained supplied matching without implying automatic identity resolution |
| Contract example mentioned three drafts but supplied two | Made the opening agree with the two supplied drafts |
| Editorial insertion instructions appeared inside public copy | Clearly marked the shared example-standing component's placement instructions as editorial |
| Search wording suggested a dialog despite the nonmodal design | Used a search-region heading, ordinary Tab navigation, Escape dismissal, retained query, and direct browsing without JavaScript |
| Some accessible names omitted the visible control label | Kept “menu” and “expand diagram” in their corresponding accessible names |
| Reading progress lacked a reverse action | Added “Mark this step as unread,” with local-storage and reset language |
| Filter and canvas mechanics lacked final strings | Added department/industry counts, empty and cleared states, View/Lens labels, and Show/Hide details |
| Some candidate destination strings were abbreviated | Expanded the destination contract's paths and pinned the existing learning fragment |
| The longer docs navigation could be mistaken for a crowded header row | Identified it as documentation browse navigation; retained the short Examples/Guide/Craft header and More disclosure |
| Appearance copy implied unselected extra controls | Kept the current compact light/dark toggle and initial device preference; removed the unselected selector and reading-options disclosure |

The independent assembled review found no remaining actionable issues within its document/source scope. The primary agent reconciled the design author's final header/appearance findings and verified the resulting labels. The package retains the creative voice and practical narrative while preserving the model's exact distinctions and the existing design identity.

## 5. Local checks and effect boundary

The preparation inspected the current source ownership and effective design overrides. The map's existing destinations and selected anchors were checked against the current local generated output; the fourteen runtime routes and 454 reference pages were counted there. These checks describe local files, not the live host.

A baseline covers the content proposal and 54 selected maintained website source/configuration files. All 54 website files match their preparation hashes. The proposal receives only a package cross-link and the correction of its accidental “worknow” heading typo.

Final local document checks passed:

- All 96 local Markdown-link occurrences across the six package documents resolve; table headers and code fences are structurally consistent.
- Copy families cover the complete page plan, including all ten department entries and seven interaction-copy groups; the 59 numbered copy-heading IDs are unique.
- All ten candidate guide/directory route assignments agree between the copy deck and destination map.
- Twenty existing mapped destinations and selected fragments resolve in the local output. All fourteen named runtime routes exist, and the selected reference directory contains 454 pages.
- Campaign and reconciliation arithmetic, strict capacity cases, and required reversible/filter/canvas labels are consistent with the examples and design.
- The 54 selected maintained website source/configuration files remain unchanged. No site build or browser test was run.

These are document, source-integrity, arithmetic, and local-file checks. They do not establish rendered layout, accessibility conformance, reader comprehension, or runtime behavior.

No website code, stylesheet, template, generated website output, runtime state, event rule, or deployment is part of this delivery. There is no clickable preview, browser test run, new screenshot, or visual-conformance verdict. Those belong to a later implementation request.
