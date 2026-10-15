# K10 — conforms-to

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **checked supplied snapshot**.

**Meaning in plain language.** Conformance establishes the owned criteria for a particular subject, target and scope in a supplied snapshot. A later runtime state requires a new assessment.

**Question answered.** Which exact contract does this subject demonstrably conform to, and under which evidence?

**Formal definition.**

```text
Meaning_K10(W,e,f) := f.profile = typedSuccessor ∧ ∃ w ∈ W.ScopedConformance. Base_K10(W,e,f,w) ∧ (w.subject = s ∧ w.target = t ∧ t = resolve(q.exact_version_ref) ∧ w.scope = scopeValue(q.conformance_scope) ∧ w.evidence = evidenceValue(q.conformance_evidence_refs) ∧ ScopedCriteriaSatisfied(W,w,f))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a ScopedConformance record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `subject` | Capability Instance or Context exact revision |
| `target` | Contract, Governed Model or Context Profile exact revision |
| `scope` | literal F0 scope or explicitly mapped successor scope |
| `evidence` | literal F0 support reference or successor evidence-reference collection |
| `criteria` | complete owned target criteria for the selected pair/profile |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`scopeValue`: Legacy F0 selects its original exact literal-token denotation; the successor selects an explicit owned scope-catalog mapping. Profile selection is part of the meaning revision and cannot silently widen the legacy interpretation.

`evidenceValue`: Legacy F0 uses its original literal evidence-reference meaning; the successor resolves an exact bounded reference collection with declared multiplicity/duplicate policy. A string is not implicitly split into a list.

`ScopedCriteriaSatisfied`: In successor mode the complete owned criterion derivation for this exact pair/target/scope has a yes verdict for every active mandatory criterion and no unresolved potential/conflicting required criterion. D05 determines verdicts from admissible exact evidence. Legacy F0 retains its pinned original any-accepted-positive-support predicate, separately indexed by profile.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `conformance_scope` | `w.scope` | legacy literal F0 scope or separately versioned typed scope mapping |
| `exact_version_ref` | `w.target` | legacy exact target token or explicit successor exact-revision mapping |
| `conformance_evidence_refs` | `w.evidence` | legacy literal reference or successor bounded reference collection; no implicit string splitting |

**Operational behavior.** Record scoped snapshot conformance to this exact target; do not infer current runtime behavior, effectiveness or admission.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Context C meets Profile P at epoch 5 under its exact assessment; a later source change can invalidate live reuse.

**Insufficient case.** An assessment for another target profile cannot support conformance to this one.

**Useful correction.** Provide admissible support for every owned applicable criterion of this target and scope; preserve the legacy F0 profile when using its literal tokens.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| admission | An already authorized atomic transaction placed an endpoint in the admitted state. | `relation.conforms-to:forbidden:0` |
| runtime-conformance | Admissible runtime traces establish all live contract criteria at the selected runtime frame. | `relation.conforms-to:forbidden:1` |
| effectiveness | An admissible outcome assessment establishes the owned effectiveness test. | `relation.conforms-to:forbidden:2` |
| authority | An authenticated authority root or valid bounded delegation chain permits this holder/action/scope at the frame epoch. | `relation.conforms-to:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Three different target semantics need separate bridges. Existing F0 evidence strings remain literal; successor lists and negative evidence must use a new explicit profile.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/conforms-to.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K10-conforms-to.json)

**Exact ordered pairs (3).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| capability-instance | contract | inherited contract norm criteria for the Capability Instance |
| capability-instance | governed-model | governed-model conformance criteria for the Capability Instance |
| context | context-profile | exact Context projection and Context Profile criterion interpretation |

**Legacy profile boundary.** Exact original literal-token/accepted-assessment predicate. An accepted flag or nonempty literal remains supplied graph data; it is not authenticated source truth or actual application.

`LegacyQualified_k(g,e) := e.kind = k ∧ Relational.InstanceValid(g,e)`

Preserve legacy acceptance in its separately named/profile-indexed API. Do not rename LegacyQualified as the stronger Meaning, or infer typed-successor evidence, enum restrictions, execution or criteria completion from legacy acceptance.

