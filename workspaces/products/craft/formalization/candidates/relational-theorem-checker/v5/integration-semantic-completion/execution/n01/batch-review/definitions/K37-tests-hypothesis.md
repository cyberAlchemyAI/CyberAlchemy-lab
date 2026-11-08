# K37 — tests-hypothesis

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded experimental intent**.

**Meaning in plain language.** An experiment design targets an exact hypothesis for testing. Designing the test does not run it or establish the hypothesis truth.

**Question answered.** Which exact Hypothesis is this Experiment Design constructed to test?

**Formal definition.**

```text
Meaning_K37(W,e,f) := ∃ w ∈ W.HypothesisTestDesign. Base_K37(W,e,f,w) ∧ (w.design = s ∧ w.hypothesis = t ∧ t = resolve(q.hypothesis_version_ref) ∧ w.role = code(q.test_role) ∧ w.protocol.hypothesis = t ∧ w.protocol.testRole = w.role)
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a HypothesisTestDesign record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `design` | Experiment Design exact revision |
| `hypothesis` | Hypothesis exact revision |
| `role` | owned test role |
| `protocol` | owned revision-bound experiment protocol |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `hypothesis_version_ref` | `w.hypothesis` | exact Hypothesis revision targeted by the owned protocol |
| `test_role` | `w.role` | owned experimental design test role; no execution or polarity |

**Operational behavior.** Record test-design targeting without asserting execution or hypothesis truth.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Design D targets Hypothesis H, but the experiment has not run and H is false in the model.

**Insufficient case.** A design for H@2 cannot supply evidence about H@1.

**Useful correction.** Use the protocol targeting this hypothesis revision; supply separate run observations and evidence for a test result.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| support | An admissible supporting-polarity record exists; evaluation targeting, realization and test design cannot create one. | `relation.tests-hypothesis:forbidden:0` |
| contradiction | An admissible evidence-polarity record specifically contradicts this claim. | `relation.tests-hypothesis:forbidden:1` |
| truth | The independent truth valuation makes the exact interpreted claim true; evidential polarity is not that valuation. | `relation.tests-hypothesis:forbidden:2` |
| successful-execution | The experiment actually ran and passed the exact owned execution-success criteria. | `relation.tests-hypothesis:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Protocol targeting and test-role resolution require source refinement; executed experiments and supporting/contradicting evidence are separate predicates.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/tests-hypothesis.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K37-tests-hypothesis.json)

**Exact ordered pairs (1).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| experiment-design | hypothesis | experiment-design to hypothesis: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
