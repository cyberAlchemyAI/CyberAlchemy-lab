# Agentic Research Network — Lab project model v1

Status: **candidate, unadmitted** (2026-10-29). Project ID: `project:arn:research-network-001`. This is a research and product design project, not an operating token network, issued asset, approved revenue contract, or claim of research results.

## Purpose and first decision

Model a network in which human and AI-assisted contributors propose and execute bounded research for a named product. The network must make the research object, prior baseline, novelty judgment, experiment, result, contribution, and proposed economic treatment inspectable before anyone funds or builds on them. The first decision is whether this model can fairly distinguish a useful research advance from paid execution and account for rights and revenue without promising returns the project cannot control.

The Engineer Assessment project is a **reference use case**, not part of this project's ownership or a source of completed outcomes. Its [novelty method](../../../../../../engineer-assessment/research/PROGRAM-NOVELTY-METHOD.md) informs the candidate review rules here. The Lab's admitted Project, Goal, Research Inquiry, Experiment Design, Research Run, Evidence, Finding, and Decision meanings remain distinct. No local proposal changes their canonical definitions or indexes.

## Read the package

| File | Role |
| --- | --- |
| [MODEL.md](MODEL.md) | Boundaries, object flow, novelty gate, reward and revenue rules |
| [definitions.json](definitions.json) | Task-local proposed meanings; stable IDs and non-collapse boundaries |
| [artifact-types.json](artifact-types.json) | Candidate type inventory and existing Lab type reuse |
| [schemas/](schemas/) | Closed JSON Schemas for proposed record kinds |
| [records/](records/) | Initial candidate project, goals, inquiry, charter and policies |
| [validate.py](validate.py) | Structural, reference and boundary checks |
| [ADMISSION.md](ADMISSION.md) | Exact work needed for Lab admission and a first authorized pilot |
| [GAP-MAP.md](GAP-MAP.md) | Material open questions, evidence limits and dependency order across research, Product, economics, sponsor rights and governance |
| [economics/](economics/) | Formal mining, reward, token supply, transaction, attribution and settlement model with a deterministic simulation |
| [economics/CIRCULAR-ECONOMY-RESEARCH.md](economics/CIRCULAR-ECONOMY-RESEARCH.md) | Mathematical model review and cash-flow conditions for a repeatable research-to-Product loop |
| [economics/LOOP-TEST-RESULTS.md](economics/LOOP-TEST-RESULTS.md) | Synthetic comparison of Product and sponsor support, including W/U exhaustion |
| [economics/SPONSOR-PARTICIPATION.md](economics/SPONSOR-PARTICIPATION.md) | Candidate sponsor vesting, revenue, IP and no-charge Product-access terms |
| [PRODUCT-001-TERM-SHEET.md](PRODUCT-001-TERM-SHEET.md) | Engineer Assessment reference Product boundary, rights map, sponsor bundle and cash waterfall |
| [product-001-ea/](product-001-ea/) | Source-pinned whole EA candidate: Product/research crosswalk, fifteen task families, qualified-introduction/API branch, engineer E reward, W search visibility and synthetic cohort/research-to-payout cases |
| [economics/MULTI-SPONSOR-RESULTS.md](economics/MULTI-SPONSOR-RESULTS.md) | Two-sponsor exit, access, revenue and IP stress results |
| [records/research-inquiry-circular-economy.json](records/research-inquiry-circular-economy.json) | Candidate Lab Research Inquiry for testing the loop assumptions |
| [governance/](governance/) | Actors, rule registry, decision rights, appeals and a non-authorizing guard |

The type schemas are **candidate contracts**. They are not registered in `authority/artifact-types`, and their task-local definitions are not admitted into `authority/definitions`. A passing validator establishes internal coherence only.

## Open owner decisions

1. Review the [actor map](governance/ACTORS.md), [rules](governance/RULES.md) and [decision routes](governance/decision-rights.json); name and appoint the actual semantic owner, research lead, IP steward, treasury steward, independent reviewers and challenge adjudicators. Role references here are unassigned placeholders.
2. Select the first product and exact research question. Engineer Assessment can be used only under its own owner and data permissions.
3. Decide whether participation units represent a contractual revenue claim, what revenue base and costs they cover, and which entity can promise payment. Obtain jurisdiction-specific legal, tax, and IP review before offering or issuing anything.
4. Set reward budgets, token supply and utility, anti-sybil rules, conflicts policy, appeal window, and treasury controls before accepting paid work.
5. Admit definitions and types through their respective Lab owner routes before treating any record as operational.

## Claim ceiling

All initial records are proposals. There are no accepted novelty reviews, research runs, contribution awards, minted tokens, participation units, product sales, or stablecoin distributions in this package.
