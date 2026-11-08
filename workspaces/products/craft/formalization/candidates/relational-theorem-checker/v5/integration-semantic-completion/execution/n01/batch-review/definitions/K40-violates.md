# K40 — violates

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **checked evidence of non-satisfaction**.

**Meaning in plain language.** Admissible evidence establishes that an exact boundary condition was not satisfied. This finding alone does not confirm a failure mode or its cause.

**Question answered.** Which exact expected boundary does evidence indicate was not satisfied?

**Formal definition.**

```text
Meaning_K40(W,e,f) := ∃ w ∈ W.BoundaryViolationEvidence. Base_K40(W,e,f,w) ∧ (w.occurrence = s ∧ w.boundary = t ∧ t = resolve(q.boundary_version_ref) ∧ w.posture = code(q.evidence_posture) ∧ BoundaryNotSatisfied(W,w,f))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a BoundaryViolationEvidence record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `occurrence` | Failure Occurrence exact revision |
| `boundary` | Contract, Policy, Schema or Challenge Contract exact revision |
| `posture` | owned admissible non-satisfaction evidence posture |
| `test` | owned boundary condition test |
| `evidence` | exact negative assessment supporting non-satisfaction |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

`BoundaryNotSatisfied`: The owned boundary test and admissible exact negative assessment establish non-satisfaction for this occurrence/boundary/frame under D05. A conflicting positive assessment yields conflict and cannot silently count as established non-satisfaction. Unknown is not false.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `boundary_version_ref` | `w.boundary` | exact Contract/Policy/Schema/Challenge Contract boundary revision |
| `evidence_posture` | `w.posture` | admissible exact non-satisfaction evidence posture; unknown/conflict cannot establish violation |

**Operational behavior.** Record supported non-satisfaction of the exact boundary without confirming a Failure Mode or deriving severity, cause or authority.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Evidence shows an observed boundary condition failed, while failure-mode confirmation and causal assessment remain absent.

**Insufficient case.** Evidence against an earlier boundary revision cannot refute the current expected condition.

**Useful correction.** Use admissible evidence against this boundary revision and its owned test; leave missing evidence unknown and confirm the failure mode separately.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| cause | The owned causal model supports a counterfactual/intervention dependence, beyond observation or temporal association. | `relation.violates:forbidden:0` |
| severity | A distinct admissible severity assessment assigns a grade under the owned severity policy. | `relation.violates:forbidden:1` |
| authority | An authenticated authority root or valid bounded delegation chain permits this holder/action/scope at the frame epoch. | `relation.violates:forbidden:2` |
| automatic-failure-confirmation | A distinct admissible Failure Assessment confirms the occurrence as this mode, beyond raw boundary non-satisfaction. | `relation.violates:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Four boundary constructors require distinct test semantics. Source violation evidence, criterion refutation and failure-mode confirmation must remain separate.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/violates.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K40-violates.json)

**Exact ordered pairs (4).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| failure-occurrence | challenge-contract | owned challenge-contract boundary test with exact admissible non-satisfaction evidence |
| failure-occurrence | contract | owned contract boundary test with exact admissible non-satisfaction evidence |
| failure-occurrence | policy | owned policy boundary test with exact admissible non-satisfaction evidence |
| failure-occurrence | schema | owned schema boundary test with exact admissible non-satisfaction evidence |
