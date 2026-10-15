---
title: Relational model and theorem checker roadmap
status: proposed
updatedAt: 2026-10-07
owner: unassigned
scope: research and implementation planning
---

# Relational model and theorem checker roadmap

This proposal sequences a checker for relation instances, endpoint extensions, new relation kinds, and inference rules. All layers are not started. The document grants no admission or execution authority. Layer identifiers are local to this roadmap.

The first deliverable is a small working checker with a semantic soundness proof. Later layers add faithful registry coverage, model evolution, inference discipline, and operational integration while preserving earlier guarantees.

The [detailed analysis](ANALYSIS.md) expands the architecture, measured baseline, proof boundaries, and dependency decisions. Detailed layer descriptions are [L0](layers/L0-working-proof.md), [L1](layers/L1-faithful-baseline.md), [L2](layers/L2-model-evolution.md), [L3](layers/L3-inference-discipline.md), and [L4](layers/L4-workflow-integration.md). The [source baseline](SOURCE-BASELINE.json) records the read-only registry and schema controls supporting this proposal.

## Context and source anchors

- [Current relation registry](../../../authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json): inspected registry lists 41 kinds and exact source-record bindings. This is the selected starting snapshot, not a permanent assumption about the latest authority.
- Measured baseline: 550 relation-specific endpoint-pair entries; all 41 referenced record hashes matched. Typed Relation/v2 has only 40 conditional branches and excludes `materializes-consequence` from its enum. L0 uses a separate candidate companion input profile; L1 reconciles coverage explicitly.
- [Extension validator](../../../authority/relation-kinds/candidates/0007-governance-transaction-extension/validate.py): checks closed pairs, declarations, schemas, and deterministic output. Unique axis names and questions do not themselves establish semantic independence.
- [Conforms-to record](../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/conforms-to.json): representative exact pairs, qualifiers, and forbidden inferences.
- [Certificate kernel](../../../craft/formalization/DomainSpecMetaTypeKernel.lean): reusable certificate-checking pattern. Its current conformance conclusion is defined in terms of a supplied Boolean; relational semantics require a separate correctness theorem.
- [Formalization package](../../../craft/formalization/README.md) and [theorem evidence binding](../../../craft/formalization/schemas/theorem-evidence-binding.schema.json): candidate contracts to reuse where they fit. End-to-end execution must be implemented and verified separately.
- [Lab roadmap](../../ROADMAP.md): integration context. This proposal is an additional capability track and does not change the Lab roadmap's statuses or dependencies.

Implementation owners must be assigned before scheduling. No calendar estimate is asserted: semantic definition and proof complexity remain the main uncertainties.

## Design baseline

1. Keep relation kinds, identified assertions, evidence assessments, and inference rules separate.
2. Preserve exact ordered endpoint pairs. Source/target lists are projections, never permission to form their Cartesian product.
3. Resolve exact artifact versions and validate relation-specific qualifier contracts.
4. Define graph invariants independently of executable validation, then prove the checker satisfies them.
5. Distinguish no permitted derivation from logical negation. Conformance and admission may coexist even when conformance alone cannot justify admission.
6. Support proved, counterexample-found, bounded-check-passed, unknown, timeout, stale, malformed-input, and provider-error outcomes. Evidence class and model scope accompany every outcome.
7. Bind evidence to exact theory, registry, graph, proposal, required theorem statements, dependency closure, and toolchain versions.
8. A proof result is evidence for a stated model. Admission remains a separate governed effect.

Use Lean and the existing structural validators first. Alloy is a later counterexample aid; cvc5 remains optional until an obligation class justifies the integration cost.

## Layer decisions and boundaries

| Layer | Decision question | Minimum working unit and operator outcome | Risk reduced | Main cost drivers | Promotion decision |
| --- | --- | --- | --- | --- | --- |
| L0 — working proof | After this layer, we know whether one relation addition can be checked against independent semantics. | Three kinds, one small graph, one addition, a verified checker, and a bound receipt. | A validator being mistaken for a semantic proof. | Definitions, Lean proof, input projection. | Continue when the complete slice and hostile controls pass; narrow if a semantic ambiguity blocks it. |
| L1 — faithful baseline | After this layer, we know whether the selected registry can be reproduced faithfully and checked repeatedly. | Complete structural projection of the selected registry, semantic coverage ledger, deterministic replay. | Silent omissions, stale inputs, permissive fallback. | Qualifier interpretation, reference resolution, projection validation. | Continue with explicit supported semantics and unresolved obligations. |
| L2 — model evolution | After this layer, we know whether new pairs and kinds preserve the intended existing guarantees. | Typed change proposals, generated obligations, preservation evidence, compatibility classification. | An extension silently changing old meaning or invalidating prior evidence. | Extension semantics, consistency witnesses, compatibility proofs. | Accept a supported extension profile or narrow unsupported cases. |
| L3 — inference discipline | After this layer, we know whether declared couplings preserve forbidden-inference boundaries. | Restricted inference language, derivation checking, indirect-chain controls, independence witnesses. | Authority or other conclusions leaking through indirect inference. | Rule semantics, non-derivability proofs, countermodels. | Continue when supported rule profiles have soundness and boundary evidence. |
| L4 — workflow integration | After this layer, we know whether maintainers can use the checker reliably in relation-change review. | CLI/CI, replayable evidence bundle, proof audit, and a reviewed shadow pilot. | Operational false passes, misleading proof submissions, poor diagnostics. | Integration, isolation, evidence invalidation, realistic pilot. | Decide whether to use the checker in a bounded admission workflow. |

Each boundary ends when its decision has sufficient evidence. Adding unrelated solvers, broad automation, or interface polish before then adds cost without closing the current uncertainty.

## L0 — working proof

Included scope:

- Select exact records for `conforms-to`, `declares-effect-on`, and `materializes-consequence`; capture their source bindings.
- Define a separate candidate companion input profile for this slice; the existing frozen Typed Relation/v2 schema excludes materialization and is not rewritten by this roadmap.
- Write normative definitions and examples for a small synthetic graph. Resolve qualifier meanings before formalizing them.
- Define `InstanceValid` and a bounded graph invariant independently from `checkAddition`.
- Generate Lean input from normalized JSON, with an explicit mapping back to the source fields.
- Prove, for the supported slice, `Inv(T,G) ∧ checkAddition(T,G,delta)=true -> Inv(T,apply(G,delta))`.
- Return actionable rejection details and an exact evidence receipt.

Exit evidence:

- A valid addition is accepted; an undeclared pair and missing qualifier are rejected for their expected causes.
- An altered source, graph, or proposal cannot reuse the original receipt.
- The soundness theorem is checked against the required statement and has an audited dependency/axiom set.
- The source-to-model mapping is reviewed; no assumption simply asserts the desired result.
- A model witness exercises the selected relations, avoiding an empty or inconsistent demonstration.

Deferred: complete registry semantics, arbitrary new kinds, inference composition, live admission integration, additional solvers, and performance optimization. Cost is medium to high, dominated by semantic agreement and the first correctness proof.

## L1 — faithful baseline

Build on L0 by projecting every kind in the selected snapshot without widening any endpoint pair. Introduce a coverage ledger separating faithfully imported declarations, executable checks, proved properties, and unresolved semantics.

Add unique instance identity, exact endpoint resolution, qualifier closure, scope/version bindings, and lifecycle interpretation where defined. Missing meanings become visible unsupported obligations. Strings such as evidence references are not treated as proof that the referenced evidence supports the claim.

Reconcile registry/carrier coverage and resolve effective admission state separately from immutable source posture. Complete declaration coverage is distinct from complete semantic proof coverage.

Exit evidence:

- Every selected registry entry has an exact source mapping; omitted or unknown entries fail explicitly.
- All declared pairs round-trip; phantom Cartesian-product pairs remain rejected.
- Repeated runs over the same inputs produce the same normalized theory and verdict.
- Differential checks against existing validators explain disagreements. Agreement is supporting evidence, not proof of semantics.
- Changes to relevant dependencies invalidate affected receipts.

Preserve all L0 correctness and identity guarantees. Defer proof of every prose-level semantic statement and optimized incremental checking. Cost is medium to high, driven by the variety of qualifier contracts and semantic gaps.

## L2 — model evolution

Introduce separate proposal classes for instance addition, endpoint-pair extension, relation-kind addition, and semantic/rule revision. Generate obligations from the actual diff; a new endpoint does not automatically qualify as a harmless extension.

For supported changes, establish:

- Type and reference closure, qualifier validity, and preservation of declared graph invariants.
- Preservation of existing instance checks for changes claiming backward compatibility.
- Consistency/non-vacuity evidence for the exact theory. A checked model witness establishes existence for its represented semantics; it does not establish unrestricted conservativity.
- Conservativity where claimed: for supported definitional extensions, construct an expansion of each base model that preserves its old interpretation.
- An impact report naming strengthened constraints, affected old facts, and proofs needing replay.

Exit evidence includes one valid new pair, one valid new kind, and rejected or explicitly incompatible controls for altered old semantics, contradictory constraints, and a changed theory presented with stale proofs.

Preserve L0/L1 guarantees. Defer arbitrary quantified-theory compatibility and automatic proof discovery. Unsupported proof obligations remain open. Cost is high; this is the first major proof-complexity frontier.

L2 generates obligations for rule changes; complete inference-boundary discharge depends on L3. A rule-changing extension cannot be declared fully ready from L2 structural evidence alone.

## L3 — inference discipline

Define a finite, function-free positive rule profile first, with explicit scope/version conditions and no invention of new identities. Specify its closure and prove a certificate checker sound for permitted derivations. Add an induction-based boundary theorem for the selected authority/effect conclusions.

Formalize each selected `forbidden_inferences` entry as a specific prohibited justification, rather than a generic negation of the destination fact. Legal bridges must be named, typed, and included in the audited theory.

Use countermodels to establish selected non-entailments. Add Alloy only where small-model exploration improves this work. Record object and trace bounds; absence of a bounded counterexample remains bounded evidence. Replay found witnesses against the exact normalized semantics.

Exit evidence:

- A permitted inference produces a checked derivation.
- Conformance alone cannot derive admission under the supported profile, including indirect chains.
- A conformant-and-admitted artifact is allowed when admission has independent justification.
- A candidate coupling that breaches the boundary is detected.
- Every required non-entailment has a checked witness or an explicit unresolved status.

Preserve previous guarantees. Defer unrestricted negation, temporal reasoning, arithmetic automation, and claims of universal independence across all relation pairs. Cost is high and depends on the selected inference profile.

## L4 — workflow integration

Package proposed `check-instance`, `check-extension`, and `check-proof` CLI operations; these are interface candidates, not existing commands. Integrate evidence receipts with the existing formalization contracts after validating their fit.

Pin dependencies, audit transitive axioms, reject unfinished proofs, replay proofs, and compare them with independently supplied required statements. Keep proof generation separate from acceptance of a supplied proof. Use isolated execution for submitted Lean code; select stronger external replay according to the submission trust boundary.

Run a shadow pilot over proposed relation changes. Compare checker findings with semantic review before selecting any effect on admission. Admission application must revalidate the exact authorized proposal and baseline; proof evidence cannot authorize a different change.

Exit evidence includes deterministic clean replay, stale-baseline rejection, a proof of the wrong statement, unfinished proof dependencies, missing tool/provider, timeout, an existing relation regression, and a realistic valid extension. Record runtime and graph sizes without claiming unsupported scale.

Preserve all earlier guarantees. Defer autonomous admission, proof search as a product feature, distributed checking, and broad solver orchestration. Cost is medium to high, dominated by workflow and proof-validation integration.

## Execution backbone

| Wave | Ordered work | Reviewable outputs |
| --- | --- | --- |
| W0 | Semantic slice -> independent Lean semantics -> checker -> soundness -> complete demo | Theory definitions, mapping, checker, theorem, controls, receipt |
| W1 | Registry projection -> coverage ledger -> reference/qualifier closure -> replay | Normalized snapshot, coverage ledger, projection checks, replay evidence |
| W2 | Proposal classes -> obligation generation -> preservation/consistency -> compatibility | Proposal contract, obligations, proofs/witnesses, impact report |
| W3 | Restricted rule semantics -> derivation checker -> boundary theorem -> countermodels | Rule profile, certificates, semantic proofs, scope-labelled findings |
| W4 | CLI/CI -> proof audits -> evidence integration -> shadow pilot | Candidate package, review reports, replay evidence, pilot assessment |

Promotion depends on the preceding layer's evidence, not merely completion of its implementation files. Any new semantic ambiguity can reopen the affected definition and proofs; unrelated work may continue with clearly scoped inputs.

## Non-regression requirements

- Exact pair semantics never widen through projection or fallback.
- Formal invariants remain independent of the checker implementation.
- Unknown, unsupported, stale, and bounded evidence never become unrestricted proof success.
- Changes to theory, statements, proposal, or relevant source bindings require affected evidence replay.
- Proofs and assertions never silently acquire admission or runtime authority.
- Existing admitted records, historical receipts, and frozen runtime packages are not rewritten by this capability.

## Recommended next work and open decisions

Start W0 by drafting the three-kind semantic slice and its required theorem statement. That is the first bounded implementation task, followed by its end-to-end checker proof.

Resolve before dependent work: implementation/semantic review ownership; exact graph invariant and qualifier-reference meanings for L0; the first supported extension profile for L2; and the submission trust boundary for L4. These are task design decisions, not evidence that the roadmap is blocked.

Validation of this proposal: relevant sources were inspected, registry/source identities measured, and five schema-only synthetic controls executed without mutating source fixtures. The saved package is checked for local links, required layer sections, and placeholders. No relation-checker implementation, theorem compilation, solver run, or runtime test is claimed.

## Research references

- [Lean proof validation](https://lean-lang.org/doc/reference/latest/ValidatingProofs/): theorem meaning, dependency audits, replay, and statement comparison.
- [Lean axiom dependencies](https://lean-lang.org/doc/reference/latest/Axioms): transitive assumption auditing.
- [Alloy specification](https://alloytools.org/spec.html): relational semantics and bounded counterexample search.
- [cvc5 quantifier limitations](https://cvc5.github.io/tutorials/beginners/theories.html): why arbitrary quantified obligations cannot always be decided automatically.
- [cvc5 proof production](https://cvc5.github.io/docs/latest/proofs/proofs.html): optional later proof-producing solver integration.
