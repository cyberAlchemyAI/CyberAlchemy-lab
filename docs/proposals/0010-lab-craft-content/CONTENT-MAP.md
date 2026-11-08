# Content, journeys, and destination ownership

Date: **16 October 2026**  
Standing: **proposed whole-site content map; no routes implemented**.

Use this alongside the [UX/UI design](UX-UI-DESIGN.md), [copy deck](COPY-DECK.md), and [content proposal](PROPOSAL.md). The map keeps one maintained story per task, with department and industry entrances pointing into it. Copy IDs identify content families in the deck; they are not artifact identities or runtime contracts.

## 1. The organizing rule

**Recognizable work → inspectable example → the environment underneath → the next useful depth.** This describes a reader journey. It is not a Lab governance lifecycle.

The common campaign thread connects a selected criterion to a report, then to an observation challenging that criterion, a proposed successor, and separately assessed later use. The homepage shows an excerpt; the campaign guide owns the complete story. The company-brain and model explanations link to that guide instead of copying or changing its criterion.

Authority, provenance, and lifecycle remain parallel questions on each named subject. Definition acceptance, report correctness, domain adoption, and permission to spend stay distinguishable at every entry.

## 2. Core destinations

Paths in this document are relative to the future deployment root. A candidate path is a design assignment, not a working hyperlink. Existing paths were checked against the local `website/dist` snapshot during preparation; that check is not live verification.

| Content family | Destination | Standing | Reader's outcome |
| --- | --- | --- | --- |
| H · Lab home | `governance-lab-series/index.html` | Existing; proposed explanatory revision | Recognize the open company brain, see useful work, and choose an example |
| ST · Start here | `governance-lab-series/start-here.html` | Existing; A/B/C composition remains unselected | Choose a problem, task, or story while retaining direct technical lookup |
| TEAM · Examples hub | `governance-lab-series/team-examples.html` | Candidate | Find work through familiar department labels |
| CMP / EVO · Campaign and meaning evolution | `governance-lab-series/campaign-comparison.html` | Candidate; one canonical story | Follow Q1, R1, a challenge, candidate Q2, and a separately bound later assessment |
| REP · Customer reply | `governance-lab-series/customer-reply.html` | Candidate | Recover a customer's context, prepare a reply, and retain uncertainty and next work |
| HAND · Sales handoff | `governance-lab-series/sales-handoff.html` | Candidate | Follow a promise with its conditions, owner, and unresolved dependency |
| BRAIN · Company brain | `governance-lab-series/company-brain.html` | Existing | Understand the connected organizational environment and how it can develop |
| MODEL · Model guide | `governance-lab-series/governance-lab-reference.html` | Existing | Read the complete model and reach its exact contracts |
| MODEL · Authority lens | `governance-lab-series/governance-authority.html` | Existing retained route | Reach the applicable authority explanation and exact definition |
| MODEL · Provenance lens | `governance-lab-series/governance-provenance.html` | Existing retained route | Inspect the basis and origin of the selected subject |
| MODEL · Lifecycle lens | `governance-lab-series/governance-lifecycle.html` | Existing retained route | Inspect the subject's state and conditions for change |
| NORTH · Incident | `governance-lab-series/incident-walkthrough.html` | Existing maintained illustration | Inspect Northstar's exact fixed-snapshot omission and open questions |
| AGENT · Continue work | `governance-lab-series/resume-agent-work.html` | Existing | Recover relevant state and recheck context and permission |
| LEARN · Operational learning | `governance-lab-series/governance-lab-reference.html#learning` | Existing | Distinguish observations, advice, actual application, and assessed outcomes |
| REF · Reference library | `governance-lab-series/lab-reference-library.html` | Existing | Find exact definitions, types, and connections |
| Record specimens | `governance-lab-series/record-examples.html` | Existing | Inspect the teaching examples with their own standing |
| Prepare a definition | `governance-lab-series/prepare-definition.html` | Existing | Assemble a candidate meaning and its declared review material |
| Prepare an assessment | `governance-lab-series/prepare-incident-assessment.html` | Existing | Connect the criterion, result, support, limits, and next review |
| Read a record | `governance-lab-series/read-record.html` | Existing | Identify the record, contract, standing, and support |
| CRAFT · Software factory | `craft-documentation-proposal/craft-model.html` | Existing; proposed introduction and reading treatment | Follow explicit behavior into selected construction and later change |
| RUN · Build and run | `governance-lab-series/runtime-overview.html` | Existing | Select an implementation and reach its retained operational scope and evidence |
| SRC · Source and status | `governance-lab-series/source-and-status.html` | Existing | Identify the selected edition, implementation standing, and source |
| RES · Research and culture | `governance-lab-series/research.html` | Existing | Explore inquiry, intelligence, human–machine ergonomics, and the longer ambition |
| CON · Contribute | `https://github.com/cyberAlchemyAI/CyberAlchemy-lab` | Existing selected external destination | Inspect the source and choose an available contribution route |
| EVENT · Community event | `governance-lab-series/hackathon.html` | Existing; event content retained | Reach the current event terms without changing them through this redesign |

Campaign and evolution copy may have separate deck IDs while sharing one article. A new heading or deep-link anchor should be selected at implementation; preserve old anchors in retained articles. Do not invent a duplicate “governance evolution” page merely to mirror a copy heading.

## 3. Department guide coverage

All new domain scenarios are proposed teaching material. None establishes an email, CRM, ERP, banking, or other connector, a live integration, a specialist professional judgment, or an authorized external action.

| Department | Content family and canonical destination | Unique question and artifact |
| --- | --- | --- |
| Customer support / email | TEAM support → REP · `customer-reply.html` | What has already happened? A sourced draft and an open investigation |
| Sales / customer success | TEAM sales → HAND · `sales-handoff.html` | What was promised and under which conditions? A recoverable handoff |
| Marketing | TEAM marketing → CMP / EVO · `campaign-comparison.html` | What are we counting, and should the criterion change? Two separately bound reports |
| Finance / operations | TEAM finance → `guides/finance-discrepancy.html` | Why do these selected records disagree? A reconciliation and unexplained remainder |
| People / onboarding | TEAM people → `guides/onboarding.html` | What should this colleague know? A role-specific, dated starting pack |
| Legal / contract operations | TEAM legal → `guides/contract-history.html` | Which supplied version and approval support this obligation? A comparison for specialist review |
| Procurement / supply | TEAM procurement → `guides/supplier-comparison.html` | Which offer meets the declared needs? A criteria matrix and separate recommendation |
| Research / strategy | TEAM research → `guides/research-decision.html` | What supports this answer? A bounded evidence and alternatives brief |
| Risk / suspicious activity | TEAM risk → `guides/suspicious-activity.html` | What does this signal establish? An investigation with alternatives and an escalation proposal |
| Engineering / software delivery | TEAM engineering → existing Craft article and Lab context | What behavior must survive the change? A modeled requirement with its selected checks |

The first three guides carry the main public story. The other guides have copy in the deck and a documented proposed composition, with their implementation standing visible. A future implementation should not create empty destinations to make the catalog appear complete.

Industry lenses are secondary views inside these guides: software/SaaS, retail/commerce, services/agencies, manufacturing/logistics, and financial-services operations. They reuse the applicable guide and vary meaningful inputs, vocabulary, records, and requirements. They are not five new platform products or implied sector qualifications.

## 4. Reading paths and deeper destinations

Keep the existing six paths available. New introductions can route to the shared campaign explanation without erasing the path's particular purpose or renaming its URL.

| Existing path | Retained purpose | Proposed connection to the new narrative |
| --- | --- | --- |
| `governance-lab-series/path-understand-lab.html` | Understand the Lab | Company brain, campaign's governed meaning, deeper model; retain the Northstar and map links |
| `governance-lab-series/path-investigate-incident.html` | Investigate an incident | Keep Northstar, specimens, and assessment preparation; point to the shared model where needed |
| `governance-lab-series/path-read-record.html` | Read a record | Keep exact-reference reading; compare a teaching report with its exact contract |
| `governance-lab-series/path-prepare-definition.html` | Prepare a definition | Link to Q1/Q2 as a readable example; preserve the real candidate-preparation obligations |
| `governance-lab-series/path-resume-agent-work.html` | Resume agent work | Show what persists and which views and permissions need checking |
| `governance-lab-series/path-explore-craft.html` | Explore Craft | Factory introduction, strict capacity example, selected architecture, and Lab boundary |

Three entrance alternatives remain available for comparison: problem first, task/department first, and story first. Each uses the same examples, technical destinations, and current-status access. Their difference is the first choice the reader makes, not the underlying product truth.

The deeper model preserves the separate explanations of meaning, authority, provenance, lifecycle, Work, context, sessions, operational learning, artifacts, and relationships. Search should find both familiar task language and the formal name. No synonym changes an exact definition or claims an equivalence between different contracts.

## 5. Material preserved rather than rewritten

The locally inspected output has **454 reference pages** and **14 runtime article routes**. These counts describe the selected local snapshot, not product completeness. Existing articles and formal bodies remain their own source-owned material.

| Collection | Required treatment |
| --- | --- |
| `governance-lab-series/reference/*.html` | Keep all selected record bodies, exact statements, identifiers, sources, and meaningful inbound links; apply the shared reading shell only through maintained generators |
| `governance-lab-series/runtime-*.html` | Retain all fourteen article routes and their selected evidence; navigation labels and a short bridge may change only without altering runtime scope or commands |
| Runtime retained evidence under `runtime/` and `research/` | Preserve exact reviewed source namespace and snapshot standing |
| Expanded essays and catalog fragments | Retain unique arguments, source captures, and exact destination purpose; keep compatibility forwarding meaningful |
| Craft article sections | Preserve formal expressions, code, quotations, supported conditions, and existing fragments including `#architecture`; revise explanatory entrances around them |
| Company-brain and homepage fragments | Retain the previous consolidation's destinations; do not collapse unique material into repeated homepage pitches |
| Robot-learning series and research pages | Retain the wider research ambition and existing links; they are not subordinate sales examples |
| Hackathon, downloads, and calendar links | Preserve approved rules, two categories, dates, prizes, voting, age limits, and operational terms; no time-sensitive status is hardcoded by this design package |

The fourteen retained runtime routes are: `runtime-overview.html`, `runtime-architecture.html`, `runtime-cli.html`, `runtime-first-inspection.html`, `runtime-local-work.html`, `runtime-maintenance.html`, `runtime-packages.html`, `runtime-paperclip.html`, `runtime-provision.html`, `runtime-recovery.html`, `runtime-sessions.html`, `runtime-state-memory.html`, `runtime-status.html`, and `runtime-work-learning.html`, all under `governance-lab-series/`.

## 6. Maintained owners for later implementation

This map assigns future work to existing owners without editing them now.

| Surface | Maintained owner |
| --- | --- |
| Homepage composition | [Paper homepage template](../../../website/source/governance-lab-series/templates/paper-home.html.in) and [Paper/crimson integration](../../../website/paper_crimson.py) |
| Existing adopted explanatory wording | [Editorial copy](../../../website/editorial-copy.json), with original/adopted passage bindings and link destinations preserved |
| New explanatory articles and page shells | The appropriate maintained templates/renderers under [the Lab website source](../../../website/source/governance-lab-series); future article ownership must be registered before generation |
| Reading path composition | [Reading paths](../../../website/reading_paths.py), with the source-side navigation and search owners kept consistent |
| Craft article | [Maintained Craft Markdown](../../../website/source/craft-documentation-proposal/craft-model.md) and its article builder |
| Effective paper/crimson appearance | [Appearance](../../../website/source/governance-lab-series/assets/paper-crimson/appearance.css), homepage CSS, palette/theme assets, and the shared typography foundation |
| Reference shells | [Reference page generator](../../../website/reference_pages.py), with exact-body checks retained |
| Search and navigation | Source-side `build_site_search.py`, `search_relevance.py`, `assets/search-engine.js`, and `assets/site-search.js`, as documented by the website owner |
| Runtime narrative and source selection | Explicit selected runtime narrative/source map and [site configuration](../../../website/site.json); no “newest file” selection |
| Imported repository Markdown | Regenerate only after a reviewed website build through the documented importer; never hand-edit generated explanations as an alternate owner |

See [website ownership/build guidance](../../../website/README.md) and [Markdown maintenance](../../../docs/lab/MAINTENANCE.md). This package is not a new canonical content engine or a license to change admitted authority records.

## 7. Handoff checks

Before future implementation is considered complete, verify that every implemented copy family has a real destination; every card's label matches its task; candidate routes are intentionally adopted; existing anchors still answer the original link's purpose; and formal/runtime bodies retain their selected bytes or declared preservation contract.

Then check complete search coverage, relative hosting paths, keyboard navigation, mobile and desktop reading, graph expansion and focus restoration, and no-JavaScript access. Reader exercises should ask which criterion governs R1, what Q2's standing permits, whether R1 changes, and how that differs from spending authority. The design documents specify these checks; this turn does not execute a website or runtime test.
