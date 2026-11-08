# Relational theorem checker: comprehensive review

Date: 2026-10-09. Status: author review and proposed revision. Scope: the original five-layer plan, the implemented v1 candidate, its semantic-law package, both stress experiments, schemas/APIs, proof/evidence verification, CLI/CI, shadow application and pilot. This review does not record human semantic acceptance or implementation of the proposed revision.

## Outcome

The formal core and evidence workflow are a useful baseline. The most valuable next change is a proved, context-preserving graph-to-logic projection. It should be accompanied by requirement-to-definition traceability and a broader but still finite fresh-predicate extension profile. The delegation and inheritance experiments should then gain explicit source adapters before being offered as registry semantics.

We should evolve through a new candidate profile and successor plan. Rewriting accepted v1 definitions would invalidate current proof and receipt bindings. The proposal therefore preserves v1 as an exact regression baseline and names new obligations for every new guarantee.

## What this review verified

The fresh read-only receipt audit found **35 task contracts, 40 working units, 56 dependencies and 33 accepted tasks**. Every accepted receipt's exported artifacts and dependency bindings are current. Acceptance is candidate author acceptance; the two pending tasks are R06 human pilot assessment and G4 final bounded-use recommendation.

Additional checks bind the semantic-law and stress-profile sources, saved pilot outcomes and generated evidence dependencies. This review inspects definitions, theorem statements, adapter boundaries and recorded controls. It does not rerun the full Lean suites, expensive complete CLI replays, deployment tests or a production security audit. See [baseline audit](baseline-audit.json) for the exact methods and counts.

| Surface | Evidence and retained guarantee | Limit / proposed action |
|---|---|---|
| F0 semantics/checker | Three meanings, 28 ordered pairs; independent invariant; checker equivalence and addition soundness. | Keep supplied assessment truth and JSON projection boundaries explicit. Add requirements and mutation traceability. |
| Direct semantic laws | Evidence/receipt functionality, admission independence and explicit countermodels. | Reuse these as the semantic-adequacy regression seed. |
| Registry and carrier | 41 kinds, 550 relation-specific pairs, 109 node kinds; exact declared pair provenance and reconciled candidate carrier. | Structural success does not close 263 unsupported inherited semantic obligations. |
| Reference resolution and coverage | Exact bindings for selected F0 meanings; all qualifier/forbidden-inference axes accounted for. | Extend the existing ledger, rather than creating a competing coverage authority. |
| Evolution | Selected-data compatibility, general preservation and every-old-model expansion are distinct. | Current fresh kinds are pure annotations; endpoint widening and meaning changes remain unsupported. |
| Inference | Finite typed positive rules, certificates, complete checked closure, protected tuple lineage and checked non-entailment witnesses. | Generic cycles work; the captured extension's expansion proof excludes new recursive bodies and nonempty old rule baselines. |
| Projection | Validated F0 conformance edges become `Conforms(subject)`. | Exact target and scope are retained in provenance records but unavailable as arguments to logical rules. |
| Delegation stress | Snapshot effectiveness, revocation boundary and restriction laws. | Typed inputs are interpreted externally; legacy strings, clock truth and redelegation chains remain outside the profile. |
| Inheritance stress | Origin-preserving obligations, complete two-rule closure, conflicts without explosion. | Conditions are exact labels; overrides and fulfillment semantics are unsupported. |
| Schemas/APIs | Design catalog plus implemented main and stress transports. | Earlier interface/design documents describe an obsolete implementation status; actual operation contracts are spread across packages. |
| Proof/evidence checking | Exact trusted statements, dependency/axiom checks, isolated replay, full hard inventory and pre/post bindings. | Same pinned kernel via an independent path; parser/runtime/OS/issuer assumptions remain. |
| Application | Review bindings recaptured and full replay before a candidate shadow write. | Cooperative local lock; captured baseline limits repeated evolution; no live authority transaction. |
| Pilot | Four new scenarios and 33 provenance-marked predecessor observations. | Small graphs; complete rule replay 818.83 seconds, 1.30 GiB peak process RSS; human assessment pending. |

The captured reference profile supports three legacy relation meanings; **38 other legacy meanings** remain unsupported, including entries with separately proved typed stress interpretations. The 263 figure counts unsupported obligation items, not relation kinds. These counts must not be conflated.

## Findings and recommended changes

Priorities describe usefulness for this successor design. They do not assert an exploitable vulnerability or a broken Lean proof.

### F01 — Exact context is lost before logical rules use conformance (P1)

The integration adapter validates the rich graph, then projects each conformance edge to the source alone. A reviewer conforming to Contract A in `static` scope and a reviewer conforming only to Contract B produce the same unary atom. Provenance records still contain the detail, but a rule matching that atom cannot require a particular contract/scope.

This abstraction is sound for the existential meaning currently declared. It becomes inadequate for a product rule asking a more specific question. Preserve `(subject revision, contract revision, scope)` in a new `ConformsTo` predicate. Retain unary `Conforms` as an explicitly existential compatibility view. Prove both directions of the graph/fact correspondence, and retain exact supporting assertion/assessment bindings.

Evidence: [projection code](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/integration/integration.py:35), [typed predicate frontend](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/profile/frontend.py:58). Changes: C01, C02.

### F02 — Semantic adequacy needs a repeatable requirement challenge process (P1)

Independent predicates prevent a circular proof. They cannot show that an unexpressed business requirement was included. Existing countermodels already demonstrate the value of challenged premises: removing unique assessment identities permits conflicting scope claims; a recorded expired delegation is not effective; deriving an obligation does not establish conformance.

Extend the coverage ledger with requirement IDs, source selectors, independent predicate/theorem targets, assumptions, positive/negative cases and applicable mutation controls. Reject unclassified requirements. Mutants that deliberately remove version equality, uniqueness, scope binding, revocation or provenance must fail the associated required claim or expected behavior. Every inapplicable mutant needs a reason. This is a stronger review process, not a theorem that all real-world requirements were discovered.

Evidence: [semantic witnesses](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/semantic-logic/v1/SemanticWitnesses.lean), [stress witnesses](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressWitnesses.lean), [coverage ledger](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/coverage/semantics/semantic-coverage-ledger.json). Change: C01.

### F03 — The extension proof is narrower than the inference engine (P1)

The generic closure runner checks a cyclic multi-rule example. The captured rule adapter requires empty prior rules, fresh ordinary heads and exclusively old-predicate bodies. `FreshHeadExtension.added_bodies` encodes the last restriction; its one-step expansion cannot justify recursive fresh definitions.

Introduce a separate finite positive recursive-definitions profile. Preserve old declarations, domain, facts, rules and roots. Require every added head to be fresh ordinary information; old rules cannot consume the fresh vocabulary. Define fresh interpretations by least fixed point relative to an arbitrary old model, then prove every old model expands without changing old truths. Cycles without seeds must derive nothing; certificates cannot justify a fact through circular references alone.

This is a new conservativity proof, not permission to remove an adapter guard. Finite recursive graph rules are established in [Datalog's reference examples](https://souffle-lang.github.io/tutorial). The same source explains that unrestricted arithmetic term generation can lose termination. Evidence: [cycle control](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/closure/run_closure.py:23), [current expansion contract](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/integration/RuleConservativity.lean:20). Change: C03.

### F04 — Typed stress results do not interpret legacy registry strings (P1)

The coverage ledger already records this separation correctly. The temporal profile expects interpreted intervals/revocation/scope/action data; the source registry stores opaque qualifiers. The inheritance profile also receives interpreted contracts, norms and bindings. Their proved results cannot be counted as full legacy semantics without a mapping contract.

Add explicit adapters supplied with versioned interpretation assessments. Authenticate neither issuer nor clock by fiat. Require every legacy qualifier to be mapped, deliberately opaque or explicitly unsupported, bind source and target revisions, and reject mismatches. Add a formal correspondence layer where the mapping is decidable. Keep redelegation chains and override precedence outside the first adapter release.

Evidence: [stress semantic contract](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/SEMANTICS.md), [delegation meaning](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/DelegationSemantics.lean), [inheritance meaning](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/ObligationSemantics.lean). Change: C04.

### F05 — Conditions, unknown values and temporal context need an explicit composition contract (P1)

The temporal experiment checks supplied policy/gate assessments. The inheritance experiment matches an opaque condition label. Neither provides a general condition language, and missing evidence must not become a positive permission through negation.

Start with named, snapshot-bound condition assessments with `holds`, `does-not-hold`, and `unknown`. Positive rules consume only checked `holds` facts. Define when a supplied negative assessment may produce an explicit negative-status fact; lack of a positive fact supplies no such fact. Bind evaluation to the exact context revision/epoch. A temporal predicate is introduced only where its independent meaning is defined, not by appending an epoch to static conformance and inventing a temporal guarantee.

General negation requires a later semantics decision and independent proof profile. No generic `not-found → false` rule enters this revision. Changes: C04, C05.

### F06 — Operator status documents disagree with current implementation (P2)

`ANALYSIS.md`, `implementation-layering.md` and the initial interface README describe implementation as absent or all layers not started. Current accepted task receipts demonstrate the implemented candidate. R06 is `not-started` in the acceptance-oriented task manifest even though its machine pilot is complete. These are historical/protocol distinctions that an operator should not have to reconstruct.

Publish a generated current status/capability index, with separate machine execution, candidate acceptance, human assessment and authority posture. Link historical designs as dated inputs. Preserve their accepted bytes; any direct historical edit requires an explicit successor binding and revalidation. Align current API documentation with the main CLI and the separate stress CLI; publish no fictitious HTTP runtime.

Evidence: [original analysis](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/relational-theorem-checker/ANALYSIS.md:13), [initial interfaces](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/interfaces/README.md:3), [machine pilot](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/pilot/shadow-pilot-report.json). Change: C06.

### F07 — Contextual facts can make grounding substantially more expensive (P2)

The current formal enumerator forms all substitutions from the full domain, then filters by sorts. With domain size `d` and `k` rule variables, that enumeration is `d^k` before filtering. Richer predicates are needed for meaning, but they add variable combinations. The existing six-node pilot already spends minutes in complete replay; that cost includes registry/proof compilation and cannot be attributed entirely to grounding.

Measure compilation, hashing, proof replay, grounding, saturation, witness checking and application separately. Optimize typed candidate enumeration and indexed joins only with equivalence evidence. Any compilation cache must validate complete identities and imports before reuse; it never caches a ready label or bypasses the application checks. Keep an uncached replay path as the reference. Changes: C07, C08.

Evidence: [grounding enumeration](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/closure/ClosureAdequacy.lean:7), [pilot measurements](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/pilot/shadow-pilot-report.json).

### F08 — Current evidence explains verdicts better than it explains derivations (P2)

The main CLI has concrete repair diagnostics and the engine retains certificates. Add an `explain` capability that presents exact initial assertion, assessment, projection, rule substitution and conclusion. Display lost context when a unary view is used. Report which hard obligation blocks readiness. For absence, distinguish a checked complete closure from an incomplete search.

Provenance trees are a useful UI precedent in the [official Soufflé provenance documentation](https://souffle-lang.github.io/provenance). Its explanation trees are not imported as Lean theorem evidence. Change: C06.

### F09 — Shadow application stops at a captured baseline (P2)

The application adapter recaptures identity and performs full fresh replay correctly. It also requires the proposal's before-state to equal the selected captured baseline. After a first successful shadow application, arbitrary subsequent proposals are outside that captured profile.

Define successor snapshot registration and an explicit evidence-dependency transition. A second supported shadow edit must obtain a newly checked baseline, rather than merely incrementing an epoch or reusing the old manifest. Continue to state the cooperative lock and local-filesystem trust boundary. Change: C09.

### F10 — External truth and proof-path independence remain assumptions (P2)

Accepted assessments, authority roots, interpreted conditions and snapshots are supplied data. The proof verifier independently chooses and checks statements using the same pinned kernel, not a second implementation. The decoder and transport-to-Lean projections are tested boundaries. None of these is automatically fixed by adding more relation rules.

Expose these assumptions in every profile capability manifest and explanation. Add separate evidence adapters only when an actual issuer/context trust policy has been specified. Verified parsing, a second kernel and live authority integration remain research options with separate cost/benefit decisions. Change: C10.

## Decision on the existing plan

Retain the original evidence and the five architectural guarantees. Do not restart already accepted tasks. Do not mark R06 or G4 complete because a new review was written. New work can use the current mathematical candidate baseline while old human-use decisions remain pending.

The successor plan should start with formalization again: independent contextual/condition meanings, required theorem types and the recursive-extension contract come before schemas or runtime guard changes. The minimum useful release is contextual conformance with exact evidence and a comprehensible explanation. Recursion and stress adapters form subsequent releases; general negation and live authority are outside the committed proposal.

See [design proposal](DESIGN-PROPOSAL.md), [successor DAG and task plan](PLAN.md), [task details](WORK-PACK.md), and [exact proposed artifact deltas](REFRESH-PATCH-PROPOSAL.md).
