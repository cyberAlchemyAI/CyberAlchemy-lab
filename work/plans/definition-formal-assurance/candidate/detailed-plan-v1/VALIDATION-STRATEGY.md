# Validation strategy

Candidate validation design. Authority effect: none. This distinguishes actual planning validation from future implementation and semantic evidence.

## Actual planning validation

`check_plan.py` validates the machine graph, task/unit membership, all current definition bindings, complete editorial partition, four exact units per identity, output ownership, candidate-only write scopes, explicit validation phases, source hashes, local links and reachability to closeout. It writes [planning-validation.json](planning-validation.json). It neither executes the 788 units nor claims semantic/theorem assurance.

The graph has 112 task nodes and 28 logical frontiers. A topological ordering demonstrates execution acyclicity, not semantic consistency. Exact source hash verification demonstrates current binding, not source truth. The plan manifest binds exact delivered planning files and excludes itself to avoid a digest cycle.

## Per-layer future validation

| Slice | Required validation | Expected evidence | What is not inferred |
| --- | --- | --- | --- |
| L0 preserved pilot | Reproduce exact submitted finite results; retain source/predecessor bindings | Existing witness/control evidence | Complete translation or generic soundness |
| A01–A06 contracts | Closed schemas, malformed decoding, exact capture, clause/requirements coverage | Same-unit tests and schema/policy receipts | Fidelity approval or source truth |
| A07–A10 successor pilot | Independent claim/grant choices, bound moves, provenance variants, owner correspondence | Concrete models, exact-cause controls, actual fidelity review | Real-world authorization or admission |
| C01–C03 semantics | Independent denotation, typed application, explicit closure, SCC and prohibited-cycle controls | Hand-derived models and exact graph results | Logical independence from nominal types |
| P01–P05 profiles | Fragment/strength fit; exact runtimes; checked model/proof/projection evidence | Provider capability and execution receipts | All logic decidable or all projections jointly compatible |
| E01–E04 evidence | Required-set comparison, rehashing, independent model/proof verification, hostile submission controls | Exact verifier/control results | Validity from provider summary or schema-only PASS |
| I01–I05 incremental workflow | Changed leaf/transitive/SCC invalidation; whole selected snapshot; addition/revision rehearsal | Source-linked invalidation and regression receipts | Cache hit as authority or one local result as whole theory |
| All family T/O/E/R/J tasks | Complete clauses, generated requirements, actual supported evidence, real fidelity and dependency closure | Four records per identity plus family join | A family is dependency-closed because of its name |
| Z01–Z07 full snapshot | Complete joint theory, all required inhabitants, declared distinctions/universal statements, clean replay | Full included-theory result and limitation ledger | Pairwise consistency or administrative disposition as proof |
| H01–H04 owner closeout | Concrete examples, exact effect scope, real decisions and fresh currentness | Actual dispositions and no-effect/selected-handoff receipts | Owner silence, candidate evidence or plan validation as admission |

## Required hostile matrix

| Control | Expected outcome | Task owner |
| --- | --- | --- |
| Missing required field / duplicate key / extra field / wrong type | Typed malformed/unresolved, no crash or silent default | A01, E04 |
| Changed source/lookup or capture race | Stale attempt; old result unusable for current meaning | A02, I01, Z06 |
| Missing declaration/translation/dependency | Explicit incomplete/unknown; no semantic readiness | A04, C03, G02 |
| False alias / subtype inclusion violated | Named relation requirement fails | A05, F-family O/E |
| Legitimate alias / subtype overlap / declared coupling | Correct obligations and allowed models preserved | A05, S02, Z05 |
| Deliberate collapse | Distinction obligation fails while satisfiability may remain | A09, E04 |
| Contradictory assumptions | Joint satisfiability fails; distinction checks not credited | A09, I03, Z02 |
| Empty required population | Satisfiable theory fails joint inhabitation | A09, Z02 |
| Pairwise satisfiable `p`, `q`, `not(p and q)` | Combined theory fails | I03, Z03 |
| Claim without grant / wrong-scope root | Claim expressible; authority not inferred | A07–A09 |
| Move/record mismatch / silent status or grant change | Exact transition requirement fails | A07–A09 |
| Explicit semantic SCC / prohibited value cycle | Joint declaration accepted; forbidden cycle still fails | C03, F07 |
| Required statement omitted/weakened/substituted | Denominator or statement mismatch rejected | A06, E03 |
| Forged model / assumed target theorem / wrong proof dependency | Verification fails at selected strength | E03, P04 |
| Unsupported quantifier/temporal construct | Unsupported, not false or passed | P01–P05 |
| Resource timeout / cancellation / exhausted memory budget | Unknown/timeout; no absence theorem | P02–P05 |
| Old proof or changed toolchain/profile | Old evidence historical; current applicability fails | I01, Z06 |
| Separate SAT projections with conflicting shared meanings | Whole-theory readiness fails until compatibility established | P05, Z01–Z02 |
| Rejected or absent owner fidelity review | Candidate results retained; semantic readiness pending/failed | A10, family R/J |
| No owner admission selection | Valid no-effect handoff/closeout; no registry mutation | H02–H04 |

## Validation phases and reproducibility

Pre-execution: rehash exact source and prior receipts; check selected profile, closure, protected scope and absent outputs. Post-produce: validate actual created artifacts and named criterion results. Closeout: compare declared versus actual output inventory, bind evidence/currentness, preserve prior snapshots and synchronize only project-owned status.

Future validation commands in the unit manifest are explicitly marked as future producers or same-unit outputs. They do not need to exist for a planning-structure PASS. A missing actual runtime during later execution remains a missing-provider result. Review units use reviewable exact criteria rather than fake command-line approval.

Only evidence changed by actual source, interpretation, requirement, provider or failure should be rerun. Full combined theory regression remains required when a relevant change can affect it. Repeating all unrelated tests is not a substitute for checking the correct dependency closure.
