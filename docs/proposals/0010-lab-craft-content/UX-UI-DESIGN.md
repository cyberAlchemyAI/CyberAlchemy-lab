# CyberAlchemy Lab and Craft: UX and UI design specification

Date: **16 October 2026**  
Status: **recommended design for review; information architecture and final copy remain unselected**  
Deliverable: **design and copy documents only**. This document changes no website source, generated page, preview, service, or live content.

Read alongside the [content proposal](PROPOSAL.md), [copy deck](COPY-DECK.md), [content map](CONTENT-MAP.md), and [package review](DESIGN-REVIEW.md). The proposal owns the vision and source-backed content requirements. The copy deck owns publishable page and control wording. This specification owns composition, interaction, responsive behavior, visual roles, and verification criteria. Where a wording example here differs from the deck, reconcile it in the documents before implementation rather than introducing another competing string. Page references use the deck's H, ST, CMP, REP, HAND, TEAM, BRAIN, EVO, LEARN, AGENT, NORTH, CRAFT, SRC, RES and CON families; exact control strings belong to its UI family. The content map is canonical for proposed new route names and preservation mappings.

## 1. Design direction

**Make an unfamiliar system understandable through familiar work, then let the reader inspect what makes that work possible.**

The Lab provides an environment in which systems can develop what they know, what they can do, and how they may change. The open company brain is the organizational expression of that environment. Definitions acquire scoped authority; artifact contracts make meaning usable; provenance preserves the basis; lifecycle provides explicit conditions for change. Governing structures can themselves acquire reviewed successors. Continued growth includes correction, simplification, replacement, and retirement.

That explanation belongs inside a practical story. A visitor first sees two campaign results, then the criterion behind them, then a challenge to that criterion and its proposed successor. The result feels discoverable rather than requiring a governance vocabulary lesson before anything useful happens.

Craft has its own full proposition: **“Your new software factory, straight from the future.”** Its sequence is need → requirement → model → selected construction → observed result → later change. Routine constructed-code review becoming unnecessary is an intended consequence of an assured construction flow, not the entire product story.

### Working design rules

- Keep the approved Paper & crimson identity: warm paper, ink, monospace type, fine rules, restrained crimson, engraved illustration, quiet geometric corners.
- Give each screen one immediate job. The homepage invites exploration; documentation helps a person read and do; reference supports exact lookup.
- Use a creative headline followed by one concrete explanation. Keep navigation and controls literal.
- Show one useful result and its basis before introducing every supporting record.
- Use cards for distinct destinations and bounded example artifacts. Use continuous prose for explanations and ruled rows for contracts.
- Put uncertainty next to the claim it limits. Do not turn every paragraph into a disclaimer or hide implementation standing in the footer.
- Preserve existing direct routes. Newcomer paths must not make operators or contributors traverse a sales narrative.
- Every important diagram communicates its main relationship inline. Expansion offers more detail, not access to the only readable version.

### Scope boundary

This is a complete design specification for the proposed content architecture, including treatment of retained pages. It does not assert an implemented redesign, browser validation, accessibility conformance, a chosen IA, or new product capability. New scenarios and new mock record cards are fictional illustrations. Exact formal bodies, code, quotations, retained examples, event terms, and captured sources remain governed by their maintained owners.

## 2. Audiences, journeys, and success

| Visitor | First question | Proposed journey | Useful endpoint |
| --- | --- | --- | --- |
| Curious business reader | What would this do for our work? | Home → campaign, reply, or handoff → relevant team guide | Explain one useful output, where its basis comes from, and which action still needs a decision |
| Team specialist | Can it retain the method and its exceptions? | Practical guide → inputs → method → bounded output → challenge or revision | Identify the specialist contribution and open questions without assuming a connector exists |
| Owner or manager | How do our meanings and methods change responsibly? | Campaign Q1/R1 → challenge → proposed Q2 → later assessment | Distinguish accepted meaning, evidence, record conformance, adoption, and effect permission |
| Software practitioner | How does Craft change software production? | Craft entrance → strict capacity example → responsibilities → architecture → successive changes | Identify what the model determines, what the selected construction covers, and what remains to evaluate |
| Agent-system practitioner | How does work survive temporary agents? | Northstar → session boundary → fresh context → scoped learning | Distinguish durable records, session notes, applicability, actual use, and later outcome |
| Contributor/operator | What can I inspect or run today? | Direct Runtime / Source & status / GitHub | Reach exact current source and selected evidence without mistaking documentation for admission or runtime eligibility |
| Reference reader | What does this exact term require? | Search or preserved URL → record → source and standing | Recover the full unchanged statement and its exact supporting route |

Proposed comprehension tasks, not measured results: after the newcomer path, a reader can describe why R1 remains bound to Q1; after the Craft example, a reader predicts Reject for 5 requested from 5 available; after the continuity path, a reader can say why a new session needs fresh context and permission. Evaluate these tasks separately from click completion or reading-progress marks.

## 3. Information architecture and navigation

The parent proposal retains three alternatives: problem first, use case first, and story first. This specification recommends a **practical homepage plus a shared guide library**, with the campaign available immediately and deeper topics always accessible. This is an implementation-ready candidate for comparison, not a silent selection of a final IA.

### Global shell

| Surface | Primary navigation | Supporting destinations | Presentation |
| --- | --- | --- | --- |
| Homepage | Examples, Guide, Craft | Research, Runtime, Reference, Hackathon, Source & status | Short visible set; supporting links in More; GitHub remains visible outside disclosure |
| Documentation | Start here, Practical guides, Craft | Governance, Lab model, Runtime, Expanded essays, Reference, About | Shared sidebar with selected ancestor and breadcrumb; no duplicated giant department menu |
| Craft | Overview, Worked example, Architecture | Workflows/recovery, Change/conformance, Current scope, Lab connection | Same docs shell with Craft chapters grouped together |
| Footer | Source & status, GitHub | Research & culture, event, existing project links | Ruled utility area; no second full homepage |

Use “Guide” in the compact global entry and “Start here” for the docs hub, matching the deck. “Examples” selects a practical chooser, not a simulated working application. Keep GitHub icon and readable label. A repository navigation link does not itself star the project; use the deck's neutral repository action unless an explicit star invitation is retained and clearly leads to GitHub.

### Route continuity and ownership

Route strings below are existing public paths unless explicitly marked proposed. Labels may improve; addresses and inbound purposes remain stable.

| Existing route or collection | Design role | Owner for a future implementation |
| --- | --- | --- |
| `governance-lab-series/index.html` | New vision and practical homepage composition | `paper-home.html.in`, `paper_crimson.py`, adopted prose in `editorial-copy.json` |
| `start-here.html` | Short docs hub and reading-path chooser | Start template, `reading_paths.py`, company-brain migration; retain existing fragments |
| `company-brain.html` and existing homepage forwards | Deeper open company brain and environment primer | Maintained templates/renderers and `company_brain_migration.py`; no second primer copy |
| Six `path-*.html` pages | Task-based guided reading | `reading_paths.py`; retain each path and step destination |
| `incident-walkthrough.html` | Northstar technical story and continuity anchor | Documentation example data/renderer and template |
| Existing practical-guide pages | Concrete tasks: read record, prepare definition, assessment, resume work | Maintained practical-guide templates/renderers and adopted prose |
| `governance-lab-reference.html` with `#system-map` | Model guide, exact conceptual destinations, interactive graph | Guide template, map rendering, diagram reading/canvas assets |
| `lab-reference-library.html`, existing catalog fragments and 454 selected record pages | Formal lookup and captured source library | Catalog/research selection and `reference_pages.py`; body-preservation checks remain mandatory |
| `craft-documentation-proposal/craft-model.html`, including `#architecture` | Complete Craft article and deep links from shorter entrances | Craft source Markdown and article builder; adopted prose reconciliation |
| 14 existing runtime articles and evidence namespace | Direct contributor/operator depth | Pinned runtime selector and maintained narrative; do not silently select newer evidence |
| Eight expanded essays, research/culture, linked robot-learning series | Deeper argument and wider research | Their existing selected source, renderers and routes |
| `hackathon.html`, eight existing section destinations, rules and calendars | Retained event journey | Hackathon template, JSON, renderer and downloads; terms unchanged |
| `source-and-status.html` and current GitHub target | Implementation/evidence and contribution | Site configuration and maintained source/status page |
| Campaign, reply, handoff and department/lens entrances | New proposed content surfaces, not implemented routes | Use candidate slugs and source assignment in the content map; approve before migration |

All short filenames in this table are relative to `governance-lab-series/` unless another directory is shown. Candidate additions are `team-examples.html`, `campaign-comparison.html`, `customer-reply.html`, `sales-handoff.html` and the six supporting `guides/` routes named in the content map. CMP and EVO are portions of one campaign story, not competing duplicate pages. Exact existing page and fragment inventory is a future implementation prerequisite; the table is not a substitute for a complete preserved-link manifest. The site currently documents 454 selected bodies and 14 runtime articles; recheck the selected baseline before migration.

Keep legacy anchors at the location containing the original subject or use explicit compatible forwarding. A link that lands on a generic homepage with a successful response is insufficient preservation. Search entries, breadcrumbs, previous/next links and Lab/Craft reciprocal links must follow the same canonical content.

## 4. Homepage composition

One page, seven connected sections. The canonical copy is in the deck; limits below guide layout, not mandatory word counts.

| Section | Reader's job | Composition | Action and continuation |
| --- | --- | --- | --- |
| H1 · Open company brain | Understand what this is | Small open-source descriptor; “Your company knows more than anyone in it.”; two short explanatory sentences; retained engraved knot | Primary practical-example action, quiet team-guide link, visible GitHub source link |
| H2 · Familiar work | Recognize an entrance | Three equal destination cards: campaign, customer reply, sales handoff. Situation, useful output, specific link | Each opens one canonical story; avoid six departmental carousels |
| H3 · Campaign | Follow an actual question | A/B comparison, visible arithmetic, selected Q1 criterion, R1 result; a compact reveal for the basis | Continue to challenge and proposed Q2; full story is readable without running an app |
| H4 · Underneath | Understand why the story hangs together | Three parallel lenses: authority, provenance, lifecycle, applied to named objects from H3 | Inspect exact basis or open deeper explanation; no single maturity staircase |
| H5 · Continued evolution | See beyond the first use | Q1/R1 and proposed Q2/later assessment side by side; earlier bindings remain visible | Deeper evolving-meaning guide and connection to the larger ambition |
| H6 · Craft | Meet the software specialization | Future-factory headline, explanatory deck, capacity inputs/outcomes, selected model/construction relationship | Enter factory story; open architecture or current scope |
| H7 · Next depth | Choose where to continue | Guides, continuity/learning, reference, runtime/research and source grouped by task | Short utility list or destination cards; no repeated sales argument |

Retain the event announcement as a compact separate strip above or below the header in its incumbent position. Its schedule and links remain event-owned. Do not use an event countdown to imply that the Lab product is generally available.

### Above-the-fold hierarchy

The main promise, open-source descriptor, one useful explanation and primary action come before a large decorative illustration on small screens. The additional conversational paragraphs in H-01 belong in the supporting opening below the primary action, not as extra prerequisites before that action. Retain the knot, but allow its mobile size/placement to make room for understanding. A word wrap is preferable to reducing the headline below a readable size. Do not require the entire hero to fit a single viewport; do require that the first viewport explains the subject rather than containing only art and navigation.

Replace record-count emphasis with meaningful orientation if counts distract from the story. If retained, counts remain actual derived values and link to the relevant collection. No adoption, outcome, time-saving or throughput counter is invented.

### Narrative interaction

Use discrete, user-controlled steps rather than auto-animation. Each step has a complete visible heading, a short explanation, one sample object and the direct destination. The full story remains in source order without JavaScript. Do not make all three governance lenses appear as successive steps whose completion advances the subject.

## 5. Documentation hub and reading paths

The docs hub answers **“Where can I begin?”** It does not repeat the homepage's full pitch. Opening: one short sentence, a primary practical chooser, then direct lookup.

1. Featured worked story: campaign comparison and changing meaning, visibly fictional.
2. Three familiar work choices: campaign, reply, handoff.
3. Existing six paths, retained and grouped clearly: Understand the Lab; Investigate an incident; Read a record; Prepare a definition; Resume agent work; Explore Craft.
4. Direct routes: Model guide, Reference library, Runtime, Source & status.

Where a path starts with the deeper company-brain primer, a short introductory note can offer the campaign first; it must not remove the maintained Northstar, reference, definition, or session steps. Exact updated step order remains a comparison choice.

### Guide page anatomy

Every practical guide uses: breadcrumb → clear title and short deck → illustrative/current standing → situation and useful output → selected inputs → method → output with basis → unresolved questions/decisions → next reading. A local outline lists real sections. An end-of-article next step offers one natural continuation and a quiet link back to the collection.

Descriptions expand in place when needed; the key result and its main limit remain visible. Do not close every section by default or hide the useful output behind tabs. Long formal material belongs behind a named link to its canonical reference, not inside nested disclosures three levels deep.

### Common campaign story specification

| Frame | Visible content | Required reading distinction |
| --- | --- | --- |
| Comparison | A/B spend US$1,200 each; 120/60 leads; 12/15 qualified under Q1; unit costs 10/20 and 100/80 | Choice of question changes interpretation; this is not causal superiority |
| Basis | Q1: business email plus demo request; declared reporting scope, owner/decision and selected sources | Accepted meaning differs from observation truth and permission to spend |
| Report R1 | Exact Q1 binding, selected period, source/method; completed illustrative comparison | Later Q2 does not reinterpret R1 |
| Challenge | Later progression observations, alternatives, affected consumers | Evidence can motivate change without making it accepted |
| Q2 proposal | Q1 conditions plus recorded target-segment fit assessment; L42 cannot yet qualify without that assessment | Candidate status and missing assessment remain visible |
| Later use | R2 proposed assessment, then separately illustrated possible completion following required acceptance/adoption; counts remain pending until assessed | A new assessment has its own inputs and bindings; a changed criterion need not change the schema |

Render the numeric comparison as a semantic table on wide screens. On narrow screens use two labeled campaign summaries and repeated row labels or an accessible stacked table view; preserve row relationships for assistive technology. Show Q1 and Q2 in a vertical reading order on mobile. Always label Q2 “proposed” until the specific later illustration explicitly includes its required decisions. Never place a generic “Approved” badge across the whole diagram.

## 6. Guide coverage: departments and industry lenses

One canonical guide per task. Department and industry entrances point to it and optionally choose a developed example. Filters are navigation aids, not claims of supported integrations or sector qualification.

| Department entry | Familiar problem and useful artifact | Composition emphasis | Proposed coverage standing |
| --- | --- | --- | --- |
| Customer support / email | Reconstruct a refund request; prepare a sourced reply | Correspondence → bounded export observation → draft → finance question; sending is a separate effect | Developed fictional guide |
| Sales / customer success | Carry a conditional promise into delivery | Promise/condition/source/role/open dependency rows; Friday discussion is not unconditional commitment | Developed fictional guide |
| Marketing | Examine a campaign and supported material | Canonical Q1/Q2 story; metric definitions, source rows, uncertainty; no spend/publish action | Developed fictional guide |
| Finance / operations | Explain why two reports disagree | Small selected reconciliation, unexplained remainder, proposed investigation | Expansion brief; no fabricated completed workflow |
| People / onboarding | Give a new colleague an accountable starting point | Role, dated source answers, access questions, first-week checklist | Expansion brief |
| Legal / contract operations | Recover what was actually agreed | Supplied revisions, approval sources, obligations and specialist review | Expansion brief; no legal assessment automation claim |
| Procurement / supply | Recover why a supplier was chosen | Declared criteria, offer comparison, missing evidence, recommendation vs approval | Expansion brief |
| Research / strategy | Separate confident answers from their support | Question, sources, alternatives, evidence map and unresolved disagreement | Expansion brief; connect existing research depth |
| Risk / suspicious activity | Investigate a flag before calling it fraud | Selected signal, alternative explanations, bounded evidence and escalation | Expansion brief; no automatic verdict |
| Engineering / software | Keep meaning through successive changes | Requirement/context → Craft model → construction/evidence → integration obligations | Existing supported capacity anchor plus labeled future extensions |

An expansion brief is complete enough to commission a guide, not a public destination with an empty body. Until developed, show a concise collection entry without a misleading “Try it” action, or point to a relevant completed guide. A domain entry needs distinct inputs, decisions or vocabulary; otherwise it stays a view into the shared story.

| Industry lens | Scenario | Reuse rather than duplication |
| --- | --- | --- |
| Software / SaaS | Export incident, customer promise, later engineering change | Northstar, reply, handoff, Craft |
| Retail / commerce | Order/payment exception and earlier correspondence | Reply and discrepancy guide |
| Professional services / agencies | Campaign handoff with missing client constraints | Marketing and handoff |
| Manufacturing / logistics | Supplier or delivery exception | Procurement and operational investigation |
| Financial-services operations | Evidence around a transaction alert | Suspicious-activity guide with specialist-support standing |

Optional directory filters: department and industry, separately labeled, plus All guides and Clear filters. Display the result count and maintain a useful empty state. Native select controls are sufficient; no bespoke segmented-picker grid is required. All destinations remain discoverable without filtering or scripting.

## 7. Deeper model, governance, continuity and learning

| Page or section family | Primary question | UI treatment | Exactness requirement |
| --- | --- | --- | --- |
| Open company brain | How does company knowledge become usable work? | Existing people/agents/knowledge/work/decision map plus practical entry | Company data is inspectable within applicable access, not necessarily public |
| Governed meanings | How does a definition acquire standing and change? | Q1/Q2 trace, owner/scope/version fields, distinct decision links | Candidate completeness does not itself confer canonical authority |
| Artifacts and contracts | How does meaning become a usable record? | Human-readable record and contract explanation beside precise reference link | Artifact Type differs from artifact instance; admission differs from acceptance and execution |
| Authority/provenance/lifecycle | What basis, origin and state apply? | Three parallel questions on one selected subject; labeled relationships | Never combine the axes into a trust score or a mandatory three-step promotion |
| Evolving governing structures | Can the system change how it changes? | Earlier/successor subjects and exact route links | No automatic self-modification authority; Semantic Epoch change depends on actual normative change |
| Work and context | What is the job and which information belongs here? | Purpose, selected inputs, current view/freshness, permission side notes | Work is distinct from Craft Workflow; current context is distinct from permission |
| Temporary agents | What ends and what remains? | Session A → durable project records → fresh Session B; vertical on phone | Do not imply all private session notes persist or inherited authority survives expiry |
| Northstar incident | What does the saved export establish? | Inputs and comparison; 200 absent identifiers; unresolved cause/recovery | Preserve exact filter/snapshot; adjacent-batch lesson remains excluded |
| Operational learning | When should experience change later work? | Observation/reflection/lesson/application/outcome as distinct record roles | Selection is not actual use; success or repetition is not measured benefit |
| Narrow lessons and non-use | Why decline retained advice? | Task scope vs advice scope, exclusion reason and next permitted step | Deliberate non-use can be correct; no instruction wall or automatic policy promotion |
| Agent societies | Why can many agents repeat the same mistake? | One origin branching to several copies; source trace remains one | No claimed elimination of population-scale failure; gossip differs from enforcement |
| Candidates and effects | What can be investigated and what may be adopted? | Missing-description/evidence/authority cases with next action | Candidates may exist before completion; consequential use follows applicable contract |

The deeper pages remain readable articles. Use a short “In this example” bridge before formal vocabulary, and exact-reference links after the explanation. Preserve source-specific authority-promotion contracts as source-specific rather than universalizing them.

## 8. Craft experience

Craft receives a dedicated editorial entrance in the existing article route or a separately approved future introduction, preserving all article fragments. It uses the same visual system with a quieter factory/blueprint illustration and more space for model/behavior evidence. No new product sub-brand or contrasting neon palette.

| Sequence | Composition | Reader takeaway |
| --- | --- | --- |
| Future factory | Creative headline, concrete explanatory deck, development/closed-beta standing | Explicit modeling and selected construction change the whole production approach |
| Whole factory | Need → clarification → model → construction → evaluation → integration → later change; note waiting/rework without invented timings | Coding speed alone does not establish delivery speed |
| Capacity | Typed input snapshot, strict `<` rule, outcome table, existing excerpt | 4/5 Accept; 5/5 and 6/5 Reject; classification does not reserve capacity |
| Responsibility | Calculation, Rule, Operation, Workflow, State Machine with their own jobs | No invented catalog signatures or equivalence between responsibilities |
| Architecture | Selected meta-types/profiles/realizations; ordinary modeling inside that boundary | Architecture is mostly selected, then followed rather than re-invented for each task |
| Assurance | Model validation, artifact conformance, behavioral evaluation, completion assessment | Different checks answer different questions; handwritten/opaque extensions need their own route |
| Later changes | Preserved obligation, changed model, selected construction, observed result | Meaning and design remain involved across evolution; a diagnostic is detection, not repair |
| Frontier | Current reported scoped observations and explicitly future reservation/concurrency work | Pure comparison does not demonstrate stateful concurrency, idempotence or recovery |
| Lab bridge | Requirement's purpose/source, decision/change basis, scoped result | Connection is explicit; Lab Work and Craft Workflow stay different |

The strict boundary is the design centerpiece. Show the exact `requested_units < available_units` excerpt unchanged. Label it as an existing illustrative translation, not a newly executed compiler result. A copy-code button copies the exact code only. Do not add fictitious DSL, live editor, generated logs, latency or pass counters.

Show the intended consequence for code review once, with sufficient assurance context: routine inspection of constructed code should become unnecessary within an assured supported flow. Human judgment remains visible at requirements, domain meaning, workflow descriptions, failure/recovery expectations and meaningful acceptance. Do not frame Craft as another review queue product.

## 9. Visual system: verified source values and proposed application

Sources: [appearance.css](../../../website/source/governance-lab-series/assets/paper-crimson/appearance.css), [home.css](../../../website/source/governance-lab-series/assets/paper-crimson/home.css), [palette.css](../../../website/source/governance-lab-series/assets/paper-crimson/palette.css), and [site-typography.css](../../../website/source/governance-lab-series/assets/site-typography.css). Values below were inspected in source, not measured in a browser. Later high-specificity overrides are relevant; do not lift an earlier small-size declaration in isolation.

### Color roles

| Role | Light docs | Dark docs | Use |
| --- | --- | --- | --- |
| Paper | `#fdfaf3` | `#21191b` | Page canvas |
| Surface | `#fffdf8` | `#281e21` | Cards, inputs, detail panel |
| Soft | `#f3ebe3` | `#302327` | Selected group, quote/example background |
| Panel | `#f0e7df` | `#38282d` | Larger bounded example surface |
| Ink | `#241f20` | `#faf0e8` | Text and strong rules |
| Muted | `#6c5a59` | `#c6b1ab` | Supporting text, never disabled by opacity alone |
| Line | `#d5c7c1` | `#5c454a` | Quiet dividers; not relied on as sole control boundary |
| Control border | `#a18a83` | `#98787f` | Inputs and controls |
| Accent | `#b31535` | `#f48da0` | Links, selected actions, focus |
| Accent hover | `#86132a` | `#ffd0da` | Docs interaction emphasis |
| On accent | `#ffffff` | `#25191e` | Text on filled accent controls |
| Success | `#28604e` | `#a9d2bd` | Recorded successful state with explicit label |
| Warning | `#78511a` | `#e5c38c` | Pending/attention with explicit label |
| Danger | `#a51d2d` | `#ffadb5` | Error/rejection with explicit reason |

The home palette currently shares paper, ink, muted, line, soft and accent, but its dark panel is `#2b2024` and its primary hover uses ink/paper. Retain these surface-specific mappings unless a later approved implementation explicitly harmonizes them. They are not evidence of a new palette option. Do not alias SVG tokens into cycles: the existing appearance sheet deliberately preserves resolved inherited SVG roles and geometry.

Concept colors in diagrams are inherited semantic aids; preserve each exact label and legend, including accessible dark variants. Crimson identifies navigation/selection, not every conceptual category. Color is never the only difference between a proposal, completed report and owner decision.

### Type and cascade

| Element | Incumbent source behavior | Proposed application |
| --- | --- | --- |
| Family | Roboto Mono; SFMono-Regular, Cascadia Code, Liberation Mono, Consolas, monospace fallbacks | Preserve throughout UI, display and code; do not add an unapproved display font |
| Docs root/body | Paper appearance resets root to 16px; body 17px/1.85, 16px at ≤680px | Preserve readable body baseline; do not describe old 18px root as effective current Paper scale |
| Docs H1 | `clamp(34px,4.15vw,56px)`; 34px at ≤680px | Allow long creative title to wrap naturally; max ~24ch |
| Docs H2/H3 | Desktop clamp 25–36px / 20–25px; mobile 26/22px; record headings 21px at ≤680px | Keep restrained hierarchy; exact formal headings remain unchanged |
| Home H1 | Desktop 43–64px; final mobile override 30–44px at ≤680px | Preserve editorial scale, test actual long headline at 320px; do not use the superseded 38–54px mobile rule |
| Home explanation | 17px desktop; final mobile description 14px | Proposed essential new explanatory copy 16–17px where necessary for sustained reading; this is a readability refinement to verify, not an incumbent measurement |
| Cards | Title 18px/1.5, description 14px/1.8, metadata 12px/1.6 | Preserve title/description distinction; meaning must not reside only in metadata |
| Docs search | 14px desktop; 16px in compact two-row header ≤1200px; minimum 44px control | Preserve final override; avoid earlier 10–12px search rules |
| Code | Docs pre 13px/1.8; keyboard-accessible overflow | Keep syntax unchanged; provide nearby prose for nontechnical readers |
| Metadata | Home late overrides raise many labels to 12px | No return to superseded 7–10px captions; no essential prose styled as metadata |

Use a 55–70ch prose measure as a proposed reading target; actual monospace measures must be checked with the final layouts. Spacious headlines and restrained weight are part of the identity. Bold highlights meaning, not every noun. Links inside prose remain visibly identifiable without hover.

### Spacing, cards and surfaces

Proposed spacing scale: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80px. Reuse incumbent 3px corners, 1px rules and quiet/no shadows. Docs card padding **24px desktop, 20px at ≤680px** is already explicit; retain it. Narrative example panels receive the same independent inset rather than relying on the article's gutter. Existing record normative/code panels use 24px/20px too.

Card anatomy: optional small domain label → clear title → two or three short lines explaining the situation/output → specific destination label. Use 12–16px internal gaps and 16px between cards. Equalize peer card height by layout, never by clamping or hiding unique text. Do not nest buttons or other links within a whole-card anchor. A static artifact card is not a link and must not display link-hover styling.

Section rhythm: preserve incumbent ~64px docs/42px compact section blocks and ~83px home/48px compact rhythm where appropriate. Full explanations need paragraphs and rules rather than a card for every sentence. Use a surface change once per major narrative transition, not an alternating stripe for every small subsection.

## 10. Responsive layout contract

The incumbent docs header's **final** compact threshold is ≤1200px; its source uses two rows with brand/GitHub/theme above and Menu/search below. Earlier ≤900/680 rules do not describe that header on their own. The docs foundation shows 250px sidebar + flexible article + 190px local outline above 1200px. This document proposes a shared predictable behavior and explicit checks; no viewport has been tested for this deliverable.

| Target width | Incumbent basis | Proposed composition and checks |
| --- | --- | --- |
| 320px | 10px external frame on compact pages; two-row compact docs header; home wraps nav | One content column, ~16px inner gutters where needed; visible brand/GitHub/theme fit without shrinking targets; Menu and usable full-width search next row; all cards stack; headline wraps; compare A then B with labels; no body overflow |
| 390px | Same compact system; docs cards 20px padding | Single-column story, 20px inner reading gutters where space permits; actions stack or wrap without truncation; visible Q1/R1 bindings; diagram vertical steps; drawer/dialog controls wrap |
| 768px | Docs compact header; sidebar/outline foundation changes around 900px | Proposed collapsed browse tree and local outline disclosures to prioritize reading; two cards only if each retains ~280–300px useful width; tables remain semantic; diagram may use two rows rather than microtype |
| 1024px | Compact header ≤1200px; base docs tree behavior may differ from proposed article shell | Proposed left browse disclosure plus wide article and local outline disclosure; no squeeze into three fixed columns; home split sections where text retains measure |
| 1440px | Full docs header and three-column foundation above 1200px | Left subject tree, bounded central reading measure, right local outline; home max frame1600px; three peer cards; campaign compare and basis panel can sit side by side |

The proposed article-shell threshold is deliberately aligned with the final compact header at 1200px. Confirm incumbent computed layout during implementation before editing; document any change rather than calling it already approved. Avoid fixed minimum widths on SVG, long record IDs and card children. Use `min-width:0`, safe wrapping and responsive asset sizing where implemented.

Touch targets: proposed minimum 44×44px for primary controls and menu/icon actions; sufficient spacing for adjacent links. Essential input text remains 16px on compact screens to avoid platform zoom surprises. At 200% text scaling and browser zoom, layout must reflow without clipped content or hidden actions. Code can scroll within its named region; the page and core diagram may not require horizontal panning.

## 11. Component behavior and states

The copy deck is canonical for visible strings. State requirements below specify what the reader must be told even if final wording changes.

| Component | Default and interaction | Other required states | Accessibility and fallback |
| --- | --- | --- | --- |
| Global brand | Link to stable Lab home | Hover, visible focus | Accessible name; decorative duplicate logo text hidden appropriately |
| GitHub action | Visible icon + GitHub/source label outside collapsed menu | Hover/focus/visited; responsive verb may shorten, destination does not change | SVG decorative; readable name; same-tab ordinary link unless explicitly disclosed otherwise |
| Menu / More | Native disclosure or equivalent button with expanded state | Open, closed, focus return after dismissal, long/wrapped content | Keyboard operable; no hover-only submenus; source links usable without JS |
| Theme | Explicit toggle showing destination theme in accessible name | Light, dark, OS initial choice, storage unavailable | Respect OS on initial unset visit; user preference persists when available; no loss of content without JS |
| Breadcrumb | Hierarchical actual ancestor links | Current page | Labeled nav; current page unlinked or current marker; wraps on mobile |
| Sidebar | Topic groups and current route | Expanded ancestor, collapsed group, compact browse disclosure | Current page indicated beyond color; no involuntary scroll on every render |
| Local outline | Real article headings | Current section, compact closed/open | Do not trap focus or hide heading behind sticky header; deep-link offsets use actual header height |
| Destination card | Single meaningful link | Hover/focus/visited | Whole card one anchor; natural text order; no nested controls |
| Artifact/example panel | Static object with identity and standing | Missing input, proposed/completed illustration, disagreement | No fake click target; explicit text status and caption |
| Filter directory | All guides initially | Selected department/industry, combined filters, no matches, cleared | Native controls/labels, count announcement; useful links remain without JS |
| Reading path | All steps and linked docs available | Mark/unmark read, partial/full/reset progress, storage blocked | Progress is browser-local reading state, not competence or evidence; optional controls hidden without JS |
| Disclosure | Short descriptive summary | Expanded, keyboard focus | Native details preferred; explain retained content, no nested disclosure maze |
| Code | Exact readable excerpt | Copy success/failure, keyboard overflow | Copy control never changes text; region label; preserved code available without JS |
| Record metadata | Identity, scope, selected version and sources | Pending/replaced/captured standing where source says so | Do not infer effective status from a historical folder name; no universal trust badge |
| Related/next links | One useful continuation and quiet alternatives | End of path | Explicit destination label rather than repeated Read more |

### Search specification

Keep the shared local index and its plaintext fallback. The current architecture loads compressed text on first use with DecompressionStream, otherwise the complete plaintext route. The plaintext fallback supports browsers lacking decompression support; it still requires JavaScript. Without JavaScript, provide ordinary guide/catalog navigation, not a claim that indexed search works. Do not introduce an external search service or AI answer synthesis as part of this content migration.

1. **Idle:** visible label or accessible name, recognizable search icon, useful placeholder. Shortcut hint only where it fits. Search is a normal input; do not invoke a heavy modal on focus alone.
2. **Loading:** show that the index is loading, retain the query, avoid an empty-results claim while loading.
3. **Results:** title, collection/location and short relevant snippet. Group only where it improves disambiguation. Highlight matching words with accessible colors; title alone is insufficient for 454 similarly named records.
4. **No results:** echo query safely, offer a simpler term, Clear search and direct library/guide links. Do not invent a generated answer.
5. **Failure:** explain that search could not load, offer Retry plus ordinary browse links; preserve query.
6. **More results:** explicit action and result count. Keep selected result visible inside the results region, without scrolling the whole document unexpectedly.
7. **Keyboard:** Tab enters controls/results predictably; if arrows select results, expose their active state and support Enter. Escape closes suggestions, retains query and leaves focus in input. Search remains a nonmodal disclosure with ordinary tab navigation and no focus trap, including when its mobile result panel is positioned against the viewport. Do not combine incompatible combobox semantics with a generic link list; choose the supported nonmodal pattern during implementation and test it.

At ≤1200px results fit the visible viewport below the actual header, with independent vertical scrolling and a reachable dismissal. Soft keyboard opening, zoom and orientation change must not strand results behind the header. Announce counts/errors politely, not on every keystroke; labels and instructions remain available to screen readers.

## 12. Diagrams, canvas and images

### Core diagram inventory

| Asset | Main inline statement | Detail and truthful limits |
| --- | --- | --- |
| Campaign basis/evolution | R1 points to Q1; a proposed successor changes no earlier binding | Parallel authority/provenance/lifecycle questions; later R2 conditions, pending counts |
| Company brain role map | People and agents work through retained knowledge, work and decisions | Existing exact concepts/links; no omniscient autonomous brain image as evidence |
| Context/session continuity | Temporary session ends; selected durable records support a new session | Fresh views and permission checked separately |
| Narrow learning | Observation, advice, actual application and outcome have distinct jobs | Non-use and counterevidence remain visible; no automatic-policy arrow |
| Collective repetition | Several copies can have one original source | No multiplicative evidence/certainty animation |
| Craft factory | Model and selected construction remain consequential through change | No fabricated timing or universal language coverage |
| Capacity | 4/5 Accept, 5/5 Reject, 6/5 Reject | Unchanged snapshot; exact strict rule |
| Responsibility/conformance | Each responsibility owns its declared job; checks have distinct subjects | Exact permitted signatures and real scoped diagnostics only |
| Existing system map | One readable selected source–connection–destination inline | Full graph, relationship list, lens and exact inspector in optional canvas |
| Retained runtime/research figures | Preserve their original argument and evidence scope | Captured sources unchanged; improve presentation around them only |

Each figure has a purpose-led title, one sentence stating the main relationship, a text equivalent or relationship list, and links to exact relevant records. Suggested inline limit is 4–7 labeled objects per view; where the source needs more, use guided steps or subviews without discarding the full view. Do not scale a large graph to unreadable labels to claim it fits.

### Expanded canvas

Retain the existing `system-map-canvas.js` approach: original stage/inspector move into a modal rather than cloning IDs. This is a source-inspected behavior, not a claim of current browser verification.

- A visible Expand diagram button complements clicking the canvas. Do not make every node click unexpectedly open a modal when its established job is selection.
- Opening preserves selected view/lens/node, reading position and opener. Focus enters an appropriate dialog control or named canvas. Background interaction is unavailable while modal. Tab and Shift+Tab remain within the open modal until dismissal; this differs from the nonmodal search disclosure.
- Toolbar: close; view/lens selection where applicable; Zoom in/out; percentage; Fit; Focus selection; Show/Hide details. Disabled limits remain visible and explained by their context.
- Current camera range is 40–400%; Fit restores the base view. Touch drag/pinch, wheel and keyboard operate only in the active appropriate region. Do not hijack page-wide zoom or browser shortcuts.
- Current canvas supports arrows to pan, `+`/`-` to zoom, `0` to Fit. Provide visible keyboard guidance and separate navigation to a concept; a pointer drag must not be misread as a click.
- On phones the inspector begins collapsed so the graph has space; details remain a reachable control, not a hidden gesture. Keep toolbar and Close visible while internal content scrolls.
- Escape/Close restore inline view, selection, focus and prior scroll. A clicked record link follows its ordinary destination; it does not return focus to a stale page first.
- If dialog/JS/camera support is absent, keep the inline guided view, complete figure/text list and source links. Do not render an inert expansion button.

### Image briefs

Preserve the approved engraved knot as the connected-knowledge motif. Optional future images can show a factory blueprint becoming a precise artifact, or layers of evidence and changing meaning; they must read as editorial illustrations. They are not screenshots of an existing Studio. No assets are generated for this documents-only deliverable.

Use SVG for exact graphs and code-native geometry. Use raster imagery only where its expressive role warrants it. Future assets need dimensions/aspect-ratio reserved, responsive variants, meaningful alt text or decorative empty alt, light/dark behavior, and lazy loading below the opening. Avoid all-caps captions too small to explain the figure. Generated material is labeled when its nature matters to interpretation; a diagram's fictitious business records remain clearly illustrative regardless of how drawn.

## 13. Retained reference, runtime, research and event experiences

Reference is an exact reading surface: breadcrumb, selected catalog, unchanged body, local outline, sources and related subject. Keep ruled definition aids, horizontal relation patterns on desktop and vertical equivalents on mobile. Copy edits may explain a formal statement nearby; they do not replace its bytes or alter its standing.

Runtime is direct and operational: source selector, retained snapshot, commands, unsuccessful observations and qualification limits remain visible. Dates and evidence editions must not be replaced by a generic “Latest” chip. Documentation is not authority to activate anything.

Research/culture and the robot-learning series keep their wider arguments and links. Apply shared shell, image and reading improvements without forcing all research into the campaign narrative. Research results retain their actual setting and unresolved limitations, including the unverified epidemic-algorithm passage.

Hackathon remains a separate event destination with its approved two categories, rules, dates, prize/vote structure, form availability and downloads. Preserve the calendar source and eight section destinations. A missing form remains visibly unavailable with no dead call to action. This specification proposes presentation consistency, not new rules or an operational registration system.

## 14. Accessibility and graceful behavior

Target WCAG 2.2 AA for a future implementation and record checks honestly; this document establishes neither conformance nor screen-reader/browser success. W3C's [reflow guidance](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) explains the 320 CSS-pixel target and scoped exceptions. The [AA target-size criterion](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) uses 24 CSS pixels with specified exceptions; this design's 44px target is a deliberate, more spacious design choice, not a misstatement of that AA requirement. The [modal-dialog pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) informs initial focus, inert background, Escape and focus return.

| Area | Proposed acceptance requirement |
| --- | --- |
| Landmarks/headings | One main region and meaningful H1; headings follow content hierarchy, not font size; labeled navigation and skip link |
| Focus | Visible focus in both themes; no header clipping; modal/menu return; logical order preserved after responsive rearrangement |
| Controls | Accessible names/roles/state; ≥44px target design where practical; disabled/pending meaning explicit |
| Contrast | Measure actual text/surface combinations: 4.5:1 ordinary text, 3:1 large text and required non-text UI; line color alone not used for controls |
| Reflow | 320px viewport and 200% text scaling/zoom tasks; no page overflow; long IDs and control text wrap |
| Motion | Respect prefers-reduced-motion; no autoplay, timed story changes, parallax or essential animated relationship |
| Color/forced colors | Every status/category has a text label; high-contrast/forced-color paths remain readable, with usable SVG labels |
| Reading alternatives | Figures have equivalent relationship prose/list; tables retain meaningful headers; code remains text |
| Search/live regions | Polite meaningful counts/errors, no repeated announcement flood; results and actions reachable by keyboard |
| Storage/privacy | Theme/progress degrade if storage unavailable; local progress does not imply account sync or assessment |
| No JavaScript | All article content, guide destinations, direct navigation, exact records and text/figure alternatives available; optional controls hidden if unsupported |
| Print | Expand essential disclosure content; include titles/source links; hide controls, progress and modal-only chrome |

## 15. Future implementation verification plan

**These are proposed checks, not checks executed for this document.** A future implementation records selected release identity, actual pages, browser/device, viewport, result and unresolved issue.

1. Reconcile source owners, copied formal scope and all legacy routes/fragments before moving prose. Capture exact reference/code/quotation/runtime baselines.
2. Build only after implementation is separately authorized. Confirm adopted editorial bindings, duplicate IDs, relative dependencies, root/subpath navigation, search extraction and final fingerprint checks.
3. Review representative home, hub, campaign, reply, handoff, department directory, company brain, definition evolution, continuity/learning, Craft, exact record, runtime, research and event pages at 320/390/768/1024/1440px in both themes.
4. Exercise the full task chain, not screenshots alone: homepage → campaign → Q1/R1 → proposed Q2 → exact reference → back; Craft → strict boundary → architecture → current scope; search → record → parent catalog; reading path → mark → reload → reset.
5. Check overflow and text/card padding, header wrapping, search with soft keyboard, long record IDs, diagrams inline, expanded canvas and restoration. Include long translated/system text only as resilience testing; public editorial language remains English.
6. Keyboard-only: skip, nav, search, filters, disclosures, copy, path controls, canvas selection/zoom/details/close and returning focus. Verify with an actual screen reader and real Safari as separate checks rather than inferring them from Chromium automation.
7. Disable JS and storage; simulate index failure/plaintext fallback and missing optional image. Every article still answers its question, and navigation has a direct route.
8. Recheck event terms/downloads, all 454 selected bodies, 14 runtime articles and their exact chosen evidence namespace. Check old fragments by subject, not HTTP response alone.
9. Conduct reader tasks from section 2. Record misunderstandings and revise the explanation rather than treating completion clicks as proof of comprehension.
10. Keep the resulting site local and unpublished until the separately authorized migration/publication decision. Document outcome limits and remaining issues.

## 16. Design handoff and document review

The deliverable is ready for editorial/design comparison once the proposal, this specification and copy deck agree on section purposes, labels, story numbers and standing. The next decision is which entrance architecture and page extent to implement; producing this document does not make that decision or authorize implementation.

Preserved design assets and source ownership are described in [website README](../../../website/README.md); guided path generation is in [reading_paths.py](../../../website/reading_paths.py). During implementation, work through maintained source owners rather than editing `dist` or imported Markdown. No design shortcut may change an exact formal statement, `<` boundary, event term or old-link purpose.

Document review should verify: coherent vision → practical examples → governed environment → Craft specialization; clear difference between incumbent values and proposed refinements; complete responsive and interaction states; accessibility and no-JS requirements; and honest separation of current evidence, illustration and product direction. Actual review findings and their resolution belong in the package review record, not as invented browser-test claims here.
