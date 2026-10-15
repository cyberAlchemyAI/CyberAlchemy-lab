# K03 — affects

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **checked observation under named provenance**.

**Meaning in plain language.** Evidence supports a specific observed impact on a subject. Impact can be established while cause, severity and responsibility remain unsettled.

**Question answered.** Which exact subject was affected, under what declared scope?

**Formal definition.**

```text
Meaning_K03(W,e,f) := ∃ w ∈ W.ScopedImpactObservation. Base_K03(W,e,f,w) ∧ (w.source = s ∧ w.affected = t ∧ w.scope = resolve(q.impact_scope) ∧ w.posture = code(q.evidence_posture) ∧ ObservedImpact(W,w,f))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a ScopedImpactObservation record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `source` | Failure Occurrence or Incident revision |
| `affected` | exact affected subject revision |
| `scope` | scope of the observed impact |
| `posture` | observed-impact evidence posture |
| `observations` | exact admissible impact observations with source and affected participant joins |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

`ObservedImpact`: At least one admissible exact observation identifies the source occurrence/incident, affected subject, scope and observed impact in the frame under the selected observation policy. A forecast or declared possibility is not an observation.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `impact_scope` | `w.scope` | owned scope of the observed affected-subject impact |
| `evidence_posture` | `w.posture` | observed-impact evidence posture under the exact observation policy; prediction does not qualify |

**Operational behavior.** Record the supported scoped impact observation; preserve causation, assessed severity, blame and ownership as separate claims.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** A shared-service disruption coincides with an observed delay for subject T; a common cause remains possible and blame is unassigned.

**Insufficient case.** A predicted impact with no observation cannot qualify as an observed affected subject.

**Useful correction.** Attach an admissible observation of this subject and impact scope; retain a prediction as a separate unestablished impact claim.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| cause | The owned causal model supports a counterfactual/intervention dependence, beyond observation or temporal association. | `relation.affects:forbidden:0` |
| severity | A distinct admissible severity assessment assigns a grade under the owned severity policy. | `relation.affects:forbidden:1` |
| blame | An independently justified responsibility assessment attributes fault, beyond temporal occurrence or impact. | `relation.affects:forbidden:2` |
| ownership | An independently governed ownership record identifies the owner, beyond production, action or impact. | `relation.affects:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Observation admissibility and external provenance must be supplied; occurrence and incident impact constructors need separate adapters.

**Review status.** An earlier scoped meaning receipt exists. It remains bound to its original definition; this expansion is presented for batch review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/affects.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K03-affects.json)

**Exact ordered pairs (22).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| failure-occurrence | agent-capability | failure-occurrence impact observation on agent-capability: affected-subject role; source occurrence and incident provenance remain distinct |
| failure-occurrence | agent-session | failure-occurrence impact observation on agent-session: affected-subject role; source occurrence and incident provenance remain distinct |
| failure-occurrence | artifact-type | failure-occurrence impact observation on artifact-type: affected-subject role; source occurrence and incident provenance remain distinct |
| failure-occurrence | generated-output | failure-occurrence impact observation on generated-output: affected-subject role; source occurrence and incident provenance remain distinct |
| failure-occurrence | implementation | failure-occurrence impact observation on implementation: affected-subject role; source occurrence and incident provenance remain distinct |
| failure-occurrence | ontology | failure-occurrence impact observation on ontology: affected-subject role; source occurrence and incident provenance remain distinct |
| failure-occurrence | person-reference | failure-occurrence impact observation on person-reference: affected-subject role; source occurrence and incident provenance remain distinct |
| failure-occurrence | product | failure-occurrence impact observation on product: affected-subject role; source occurrence and incident provenance remain distinct |
| failure-occurrence | product-capability | failure-occurrence impact observation on product-capability: affected-subject role; source occurrence and incident provenance remain distinct |
| failure-occurrence | project | failure-occurrence impact observation on project: affected-subject role; source occurrence and incident provenance remain distinct |
| failure-occurrence | work | failure-occurrence impact observation on work: affected-subject role; source occurrence and incident provenance remain distinct |
| incident | agent-capability | incident impact observation on agent-capability: affected-subject role; source occurrence and incident provenance remain distinct |
| incident | agent-session | incident impact observation on agent-session: affected-subject role; source occurrence and incident provenance remain distinct |
| incident | artifact-type | incident impact observation on artifact-type: affected-subject role; source occurrence and incident provenance remain distinct |
| incident | generated-output | incident impact observation on generated-output: affected-subject role; source occurrence and incident provenance remain distinct |
| incident | implementation | incident impact observation on implementation: affected-subject role; source occurrence and incident provenance remain distinct |
| incident | ontology | incident impact observation on ontology: affected-subject role; source occurrence and incident provenance remain distinct |
| incident | person-reference | incident impact observation on person-reference: affected-subject role; source occurrence and incident provenance remain distinct |
| incident | product | incident impact observation on product: affected-subject role; source occurrence and incident provenance remain distinct |
| incident | product-capability | incident impact observation on product-capability: affected-subject role; source occurrence and incident provenance remain distinct |
| incident | project | incident impact observation on project: affected-subject role; source occurrence and incident provenance remain distinct |
| incident | work | incident impact observation on work: affected-subject role; source occurrence and incident provenance remain distinct |
