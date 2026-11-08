# Seven extensions and the remaining R06/G4 work

Reviewed 2026-10-10. This is an implementation review and proposed follow-up, not gate acceptance. The accepted extension sources, receipts and experimental stores remain unchanged. All uses discussed here are bounded local candidate/shadow uses with `authority_effect: none`.

The seven extension units fulfilled their deliberately bounded contracts. That is useful evidence, but it does not establish a single integrated, externally authenticated relational system. Six extensions have supervised proof APIs; E06 is a feasibility study. The principal remaining work is connecting the checked meanings to definitions and requirements owned outside a submitted request, composing qualification with lifecycle eligibility, and completing the original artifact-specific human review.

## What was checked in this review

The fresh [successor audit](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/execution/reviews/2026-10-10-seven-extensions-r06-g4/successor-current-audit.json) verifies 19 accepted units, 57 criteria, 19 completed final-source extension witnesses and 277 extension control records. It checks 46,147 bindings against 7,133 current files. Control records include repeated scenario/API observations; they are not 277 independent theorems. This review reused existing kernel-run evidence and checked its current bindings; it did not rerun every proof.

The [original-plan audit](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/execution/reviews/2026-10-10-seven-extensions-r06-g4/original-plan-current-audit.json) checks all 35 task contracts, their deliverables, criteria and accepted predecessor bindings: 33 tasks are accepted; R06 and G4 are pending. The [embedded closure audit](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/execution/reviews/2026-10-10-seven-extensions-r06-g4/embedded-closure-current-audit.json) separately checks the bindings inside P05's provenance report, including the original plan snapshot. Source inspection covered the formal definitions, adapters, schemas, runtime and finalizers. Three new in-process boundary observations are recorded in [boundary-observations.json](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/execution/reviews/2026-10-10-seven-extensions-r06-g4/boundary-observations.json); these are schema/normalizer observations, not new kernel qualifications or evidence of false theorem acceptance.

## E00 — condition expressions

**Meaning.** `and`, `or` and `not` operate over yes/no/unknown. Missing evidence stays unknown: `not unknown = unknown`. Activation requires positive expression meaning and preserves the full origin of every potential norm. An activated obligation does not prove fulfillment or admission. Opposing require/forbid norms may both activate; this profile chooses no winner.

**What is proved.** `evaluation_denotes` relates evaluation to an independent pair of positive/negative evidence rails. `activation_exact` states that an origin is active exactly when it was potential and the expression has positive meaning. Concrete witnesses check the supplied entire expression and mapped frame/root references. The runtime validates all supplied leaves before evaluating, so an invalid branch cannot hide behind a successful disjunction.

**Remaining gap.** The request supplies both a root condition revision and its expression. The result records their combined `definition_identity`, but no owned definition catalog resolves that revision to one authorized expression. The review observed the same root reference with an atom and its negation: both requests pass schema/normalization, yield different definition identities, and yield yes/no. This is valid input-relative behavior. A consumer that uses only the root reference would lose the distinction. Mapped mode compares root/frame with the old source; it does not establish ownership of the new expression definition.

**Improvement.** In a successor profile, resolve `(profile, condition revision)` to an immutable expression hash and owner-approved definition before qualification. Prove resolution identity and activation composition; reject a different AST under the same catalog revision. Keep supplied leaf truth explicit. Bounds remain 128 AST nodes, depth 16, 64 distinct leaf keys and 128 evaluation records. Six completed final witnesses and 101 control records support the present profile, not unrestricted expressions.

Sources: [definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/e00/ExpressionSemantics.lean), [adapter](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/e00/adapter.py), [schema](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/e00/expression.schema.json).

## E01 — multiple evidence references

**Meaning.** At least one accepted exact matching selected assessment is sufficient. Every valid accepted support is retained in source order; all selected references are validated before aggregation. The legacy token `assessment:a,b` remains one opaque reference.

**What is proved.** `projection_sound_complete` relates the selected conformance projection to its existential meaning; `all_supports_exact` preserves the complete accepted support set. No evidence collection creates an admission root. The adapter also checks exact registry definitions, all 41 registry source references, selected endpoint kinds, kind revision and frame.

**Remaining gap.** “Any accepted support” is an explicit policy choice. It does not implement quorum, trusted-issuer precedence, all-required evidence or disagreement resolution. Legacy assessments have no individual revision; collection references use token plus normalized graph identity. Currentness therefore means membership in the exact source snapshot. This selected projection does not qualify the entire legacy graph and does not authenticate assessment issuers.

**Improvement.** Keep the existing policy as its own version. Add individually versioned, owner-resolved assessments and explicit issuer/policy identities before offering other aggregation policies. Prove each policy separately and retain the legacy opaque-token adapter. Four completed final witnesses and 54 controls cover the current migration; the collection is capped at 64 references.

Sources: [definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/e01/EvidenceCollectionSemantics.lean), [mapper](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/e01/mapper.py), [migration review](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/e01/migration-review.md).

## E02 — bounded redelegation

**Meaning.** Every hop must permit the query's scope, action and epoch. Children cannot widen parent scopes, actions or validity intervals; parents must permit redelegation. Explicit revocation or a no gate prevents that path; missing information may leave it unknown. A separate valid path can still establish yes.

**What is proved.** `non_amplification` and `reported_path_non_amplification` retain every ancestor restriction. `universe_exact` and `support_exact` characterize all source-edge words within the selected depth and the effective joined simple paths. Neither an empty path nor a cycle manufactures representation.

**Remaining gap.** Enumeration generates all edge words before filtering joined paths. Its cost is `sum(E^d, d=1..D)`, capped at 4,096 words, alongside 32 nodes, 64 hops and depth 4. These limits interact: 64 hops at depth 2 already require 4,160 words; 8 hops at depth 4 require 4,680. Even a sparse graph with few useful paths can refuse. A no result is absence within the declared depth/source, not absence of every unbounded delegation chain. Gate/revocation and clock facts are supplied snapshot truths.

**Improvement.** Prove an adjacency-based bounded traversal equivalent to the present simple-path universe before replacing enumeration. Carry a visited set, restrictions and unknown-state provenance; retain complete absence certificates and refuse on incomplete traversal. Authentication/live revocation needs a separate source adapter. Three completed final witnesses and 29 controls do not provide large-graph performance evidence.

Sources: [definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/e02/ChainSemantics.lean), [adapter](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/e02/chain_adapter.py), [review](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/e02/chain-review.md).

## E03 — verified fulfillment

**Meaning.** A link states intent. Fulfillment requires an accepted action, its owned accepted output and a yes evaluation for every named criterion at the exact request, requirement and frame. Missing evidence gives unknown; an explicit failed criterion gives no.

**What is proved.** `fulfillment_exact` relates the checker to quantified support for every criterion in the bound source. `every_named_criterion` prevents dropping a criterion during checking. `linkage_alone_is_not_fulfillment` supplies an explicit counterexample to treating intent as completion.

**Remaining gap.** The complete criterion universe comes from the caller's source snapshot, rather than an owned requirement registry. The review reduced a two-criterion source to one criterion, removed the corresponding evaluation and recomputed source identity. Both snapshots pass validation and report fulfillment. Their identities differ, so there is no same-input contradiction; the missing guarantee is that the chosen universe equals the owner's requirement. Action/output/evaluation acceptance also remains supplied evidence. Only one evaluation per criterion is accepted; richer disagreement or multi-output aggregation is absent.

**Improvement.** Resolve the exact requirement revision to an owner-bound criterion universe, and prove the submitted universe equals it. Independently bind action execution/output provenance and assessment policy. Prove requirement-change invalidation: evidence for one universe cannot establish fulfillment for another. Two completed final witnesses and 23 controls support the supplied-snapshot profile.

Sources: [definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/e03/FulfillmentSemantics.lean), [adapter](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/e03/fulfillment_adapter.py), [review](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/e03/fulfillment-review.md).

## E04 — lifecycle transitions

**Meaning.** Declaration, eligibility, review and commitment are separate. A transition requires an exact current head/generation, yes eligibility and an accepted review bound to the same successor/context/epoch. The candidate store serializes cooperating writers; one wins and the other gets a conflict. Recovery recognizes recorded state without issuing a fresh event.

**What is proved.** `transition_exact` characterizes the policy, `history_and_evidence_preserved` appends history/evidence and advances one generation, and `no_historical_reactivation` excludes prior heads. Public commit requires the original fresh E04 client/result. The evidence includes competing writers and crash observations.

**Remaining gap.** `eligibility.value = yes` and `review.accepted = true` are supplied exact keyed inputs. E04 does not consume the complete core obligation inventory or actual owner review; a fresh E04 proof establishes the transition policy under those inputs. History preservation alone does not establish semantic preservation by the successor. Locks/SQLite/host durability assume cooperating callers. Python's private transaction method is not a hostile-code access-control barrier. Crash probes tested that storage primitive in isolated child stores after separately testing the public freshness gate; they did not exercise fresh proof creation through a process crash.

**Improvement.** Define a composed eligibility certificate containing current exact qualification, independent complete obligations, preservation evidence and owner review. Prove eligible transition implies those premises. Add an end-to-end public-commit crash harness and formal well-formed-state preservation. Handle orphan retention explicitly. Three final witnesses and 32 controls support one owned local store, not distributed authority.

Sources: [definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/e04/LifecycleSemantics.lean), [adapter](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/e04/lifecycle_adapter.py), [store](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/e04/store.py).

## E05 — checked canonical IR

**Meaning.** Typed IR distinguishes null, Boolean, natural, scalar-string, array and record. Keys are strictly ordered/unique; Unicode scalar sequences are exact. There is no Unicode normalization and no float-to-natural conversion in this profile.

**What is proved.** `import_exact` and `imported_denotation` establish exact typed denotation after successful canonical import. Concrete witnesses compare seven whole decoded values, including the core graph and E00–E04 semantic results. Scalars are emitted by `ord` and compared with an expectation built from UTF-32 bytes.

**Remaining gap.** The theorem starts after byte decoding and Python emission. The raw parser, emitter, hashes and host remain trusted. Whole-value finite witnesses narrow that boundary but do not universally verify it. IR checks a transported value; it does not independently reauthenticate source facts or turn recorded extension evidence into a fresh event. A structural denotation theorem also needs future composition with each domain semantic importer.

**Improvement.** Specify byte-decoder-to-IR refinement and profile-specific semantic import contracts first. Add proof-producing parsing or an independently checked parse certificate, then domain-import composition theorems. Retain differential malformed-byte/duplicate-key/type/Unicode controls. Do not remove old exact-input checks until equivalence is evidenced. One final batch took 125.951 seconds, with a 43.091-second concrete compile and 991.5 MiB observed peak aggregate RSS. Earlier designs timed out. Limits of 16 items, 8,192 tree visits and depth 32 do not promise every admitted batch finishes.

Sources: [IR](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/e05/CanonicalIR.lean), [import theorem](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/e05/ImportCorrectness.lean), [adapter](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/e05/adapter.py), [transport review](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/e05/transport-review.md).

## E06 — independent checker feasibility

**Meaning and evidence.** The standalone Rust nanoda checker checked one actual theorem, `tNot unknown = unknown`, and its complete 18-declaration exported closure. This is separately implemented checking, rather than another run of the Lean kernel. The sample permits no axioms and disables Nat/String extensions.

**Remaining gap.** It covers no complete core qualification and supplies no E06 runtime adapter. The exporter and trusted-challenge plumbing are not universally verified. A tiny millisecond sample cannot estimate large closure/certificate costs. In a decisive control, changing `tNot` to the constant unknown function leaves the equation provable: nanoda accepts that valid proof, while the original definition-closure pin rejects the substitution. Valid proof and intended definition identity are separate obligations.

**Improvement.** Inventory the actual required theorem closures; independently anchor each statement and its definitions; test universes, inductives, recursors, quotients and the allowed foundational axioms. Add owned resource limits and explicit accept/reject/disagreement/unsupported/resource states before integration. Begin with one substantial core theorem and one nontrivial semantic theorem. Retain mandatory same-kernel checks until a reviewed profile specifies stronger combined assurance. Whole-core independent validation remains a separate project, not an original R06/G4 criterion. [Lean's official validation guidance](https://lean-lang.org/doc/reference/latest/ValidatingProofs/) distinguishes replay, independent checking and challenge matching. [Lean4export](https://github.com/leanprover/lean4export) provides the exporter source; it is not a proof of translation correctness.

Sources: [feasibility](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/e06/feasibility.md), [translation contract](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/e06/translation-contract.md), [actual sample report](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/e06/sample-check-report.json).

## Cross-extension limits

| Boundary | Practical consequence | Treatment for bounded shadow use |
|---|---|---|
| Input-relative truth | A proof cannot establish that an issuer, action or supplied assessment tells the truth. | Name the fact owner and assumption in each result; add authenticated sources before broader use. |
| Separate profiles/APIs | E00 activation, E01 support, E02 representation, E03 fulfillment and E04 eligibility are not yet one composed qualification. | Review each profile separately; do not infer permission, fulfillment or semantic preservation from another result. |
| Snapshot epochs | Exact epoch equality does not establish the current real-world clock or revocation state. | Use captured snapshots; define recapture/freshness policy before live decisions. |
| Finite completeness | Bounded no/unknown and resource refusal have different meanings. | Display the universe/depth and reason; incomplete execution never establishes absence. |
| Resource enforcement | Default aggregate RSS observation is advisory. A required unavailable delegated enforcement backend refuses. | Keep the measured envelope explicit; require an actual host backend for a hard-memory claim. |
| Registry coverage | 41 kinds have structural coverage; the original matrix lists 263 inherited source-semantic obligations outside supported profiles. | Create an obligation-to-extension coverage map. Do not subtract seven from 263: no one-to-one discharge has been established. |
| Freshness | Saved/recovered evidence is recorded evidence, not a rehydrated process-local event. | New use requiring freshness runs the current qualifier again. |

These are useful limits, not all defects to remove before recommending this bounded use. A broader authority service would need a new assurance and execution scope.

## What R06 and G4 actually require

The authoritative source remains [the original R06 task](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/relational-theorem-checker/dag-plan/work-pack/tasks/R06.md) and [G4 task](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/relational-theorem-checker/dag-plan/work-pack/tasks/G4.md), backed by `docs/plans/relational-theorem-checker/PLAN-SOURCE.json`.

**R06 asks whether the original pilot covers its supported changes and failures, and whether a human finds the meanings appropriate and diagnostics useful.** Its machine pilot passed: four new public cases and 33 accepted predecessor executions cover additions, unsupported endpoint changes, kind addition, rule change, protected boundaries, invalid/stale evidence and workflow failures. The complete rule case satisfies 15 obligations; unchecked search leaves exactly one unknown witness after 14 satisfied obligations. Historical execution is not a new fresh authorization event. The remaining human judgment must name this original pilot's exact packet and use matrix.

**G4 asks whether each original layer kept its promised guarantees, and what use a human recommends after seeing the audit and remaining limits.** It follows accepted R06. It produces `l4-review.json`, `alignment-and-layering-audit.json` and `bounded-use-recommendation.md`. It can complete while unsupported meanings remain explicitly excluded. Its own task states that deployment, authority publication and admission require separate authorized scope.

Your earlier answer is recorded against the v3 P11 packet, before the seven extensions. It establishes the assessment of that packet and authorized extension implementation. It cannot be relabeled as assessment of the original v1 pilot or of the completed extension meanings. A new packet may present both, but must distinguish those scopes and record actual feedback for each.

## Additional findings that affect gate closure

**GC1 — review bindings are insufficiently constrained.** The prepared v1 `finalize_pilot.py` iterates `human['reviewed_artifacts']` but imposes no required identities, uniqueness or nonempty inventory. It accepts a nonempty quote with positive labels without checking that the original packet/matrix are among the bindings. Capture already assumes a trusted operator who observed the direct response, so this is a missing defensive check, not machine authentication of a human. Require a closed feedback contract with mandatory exact packet/matrix/pilot/audit bindings, distinct scope, criteria and original question/message provenance. Explicitly handle revisions rather than manufacturing acceptance.

**GC2 — visible state can contradict acceptance.** The finalizer includes `reviewer-feedback.md` and `supported-use-matrix.json` without updating their pending human-review fields; the prepared G4 flow does not reconcile the pilot session state. Review completion should produce consistent current feedback/use/status records while preserving historical issued questions and observations.

**GC3 — gate completion would rewrite a bound historical source.** The existing acceptance helper rewrites `PLAN-SOURCE.json` and generated DAG documents. P05's frozen provenance report binds the current original plan hash. Editing that plan makes this embedded provenance observation historical even if the mathematical proofs are unchanged. Never silently overwrite accepted closure reports or exempt the changed file from verification. Recommended design: append new gate receipts and a strictly validated status overlay bound to the original plan/tasks; add a current-state reader/view that recognizes this explicit overlay. Preserve the original captured plan. If canonical in-place status mutation is retained instead, version/requalify the affected provenance closure under a successor before claiming currentness. Writing an overlay alone is insufficient without its validated reader and receipt checks.

GC1–GC3 are proposed closure hardening. No existing human response has been rejected and no gate has been closed by this review.

## Recommended decision

Complete R06/G4 for the exact bounded original use after closure hardening, current-evidence audit and actual artifact-specific human assessment. Attach the extension review as a separately scoped annex. Keep owned definition resolution, fulfillment criterion ownership, composed lifecycle eligibility, efficient path traversal, verified transport and broader independent checking in a successor improvement track. The [proposed DAG and implementation contracts](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v3/execution/reviews/2026-10-10-seven-extensions-r06-g4/PLAN.md) separate these tracks and put formalization first.
