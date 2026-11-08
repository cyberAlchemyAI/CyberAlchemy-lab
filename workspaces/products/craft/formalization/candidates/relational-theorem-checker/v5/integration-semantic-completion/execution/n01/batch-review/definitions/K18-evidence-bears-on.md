# K18 — evidence-bears-on

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded evidential relation**.

**Meaning in plain language.** Evidence bears on a proposition with an explicit supporting or contradicting polarity. Support can be recorded without a truth or acceptance decision.

**Question answered.** What evidential polarity does this evidence have toward this claim?

**Formal definition.**

```text
Meaning_K18(W,e,f) := ∃ w ∈ W.EvidencePolarity. Base_K18(W,e,f,w) ∧ (w.evidence = s ∧ w.claimCarrier = t ∧ w.polarity = polarityValue(q.polarity) ∧ w.polarity ∈ {supports,contradicts} ∧ EvidentialCorrespondence(W,w,f))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a EvidencePolarity record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `evidence` | exact evidence carrier revision |
| `claimCarrier` | exact target containing the proposition |
| `proposition` | owned proposition selector within that target revision |
| `polarity` | supports or contradicts constructor |
| `correspondence` | admissible evidential correspondence record |

`EvidentialCorrespondence`: An owned correspondence record selects an exact proposition within the target carrier and connects this evidence revision and polarity under the selected admissibility policy. The proposition selector must be unique; acceptance decisions and independent truth valuation are not premises.

`polarityValue`: The unique owned interpretation of this raw token as supports or contradicts for the selected evidence/target proposition. It is not a truth valuation or an acceptance decision.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `polarity` | `w.polarity` | exact supports or contradicts correspondence for the selected proposition within the target |

**Operational behavior.** Record supporting or contradicting evidence; preserve claim decisions, admissions and truth valuation.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Evidence E supports Claim C but C is false in the independent model and no acceptance decision exists.

**Insufficient case.** Changing supports to contradicts changes the semantic claim and invalidates its witness.

**Useful correction.** Supply the correspondence for the selected target proposition and declared polarity; changing polarity needs a new witness.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| claim-acceptance | An actual selected claim-acceptance decision exists for this claim revision. | `relation.evidence-bears-on:forbidden:0` |
| decision | An actual owner-selected decision outcome is recorded for the exact reviewed alternatives. | `relation.evidence-bears-on:forbidden:1` |
| admission | An already authorized atomic transaction placed an endpoint in the admitted state. | `relation.evidence-bears-on:forbidden:2` |
| truth | The independent truth valuation makes the exact interpreted claim true; evidential polarity is not that valuation. | `relation.evidence-bears-on:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Seventy-two pairs need explicit proposition selectors and admissibility policies. A target artifact can contain multiple claims; the endpoint alone does not choose one.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/evidence-bears-on.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K18-evidence-bears-on.json)

**Exact ordered pairs (72).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| evidence-set | authority-claim | evidence-set evidential correspondence to the uniquely selected proposition in authority-claim; polarity is independent of truth |
| evidence-set | challenge-event | evidence-set evidential correspondence to the uniquely selected proposition in challenge-event; polarity is independent of truth |
| evidence-set | classification-assignment | evidence-set evidential correspondence to the uniquely selected proposition in classification-assignment; polarity is independent of truth |
| evidence-set | drift-assessment | evidence-set evidential correspondence to the uniquely selected proposition in drift-assessment; polarity is independent of truth |
| evidence-set | failure-assessment | evidence-set evidential correspondence to the uniquely selected proposition in failure-assessment; polarity is independent of truth |
| evidence-set | failure-occurrence | evidence-set evidential correspondence to the uniquely selected proposition in failure-occurrence; polarity is independent of truth |
| evidence-set | finding | evidence-set evidential correspondence to the uniquely selected proposition in finding; polarity is independent of truth |
| evidence-set | hypothesis | evidence-set evidential correspondence to the uniquely selected proposition in hypothesis; polarity is independent of truth |
| evidence-set | identity-claim | evidence-set evidential correspondence to the uniquely selected proposition in identity-claim; polarity is independent of truth |
| evidence-set | improvement-signal | evidence-set evidential correspondence to the uniquely selected proposition in improvement-signal; polarity is independent of truth |
| evidence-set | lesson-outcome-assessment | evidence-set evidential correspondence to the uniquely selected proposition in lesson-outcome-assessment; polarity is independent of truth |
| evidence-set | operational-lesson | evidence-set evidential correspondence to the uniquely selected proposition in operational-lesson; polarity is independent of truth |
| evidence-set | preference-application-assessment | evidence-set evidential correspondence to the uniquely selected proposition in preference-application-assessment; polarity is independent of truth |
| evidence-set | work-outcome-assessment | evidence-set evidential correspondence to the uniquely selected proposition in work-outcome-assessment; polarity is independent of truth |
| feedback-record | challenge-event | feedback-record evidential correspondence to the uniquely selected proposition in challenge-event; polarity is independent of truth |
| feedback-record | classification-assignment | feedback-record evidential correspondence to the uniquely selected proposition in classification-assignment; polarity is independent of truth |
| feedback-record | drift-assessment | feedback-record evidential correspondence to the uniquely selected proposition in drift-assessment; polarity is independent of truth |
| feedback-record | failure-assessment | feedback-record evidential correspondence to the uniquely selected proposition in failure-assessment; polarity is independent of truth |
| feedback-record | failure-occurrence | feedback-record evidential correspondence to the uniquely selected proposition in failure-occurrence; polarity is independent of truth |
| feedback-record | improvement-signal | feedback-record evidential correspondence to the uniquely selected proposition in improvement-signal; polarity is independent of truth |
| feedback-record | lesson-outcome-assessment | feedback-record evidential correspondence to the uniquely selected proposition in lesson-outcome-assessment; polarity is independent of truth |
| feedback-record | operational-lesson | feedback-record evidential correspondence to the uniquely selected proposition in operational-lesson; polarity is independent of truth |
| feedback-record | preference-application-assessment | feedback-record evidential correspondence to the uniquely selected proposition in preference-application-assessment; polarity is independent of truth |
| feedback-record | work-outcome-assessment | feedback-record evidential correspondence to the uniquely selected proposition in work-outcome-assessment; polarity is independent of truth |
| finding | challenge-event | finding evidential correspondence to the uniquely selected proposition in challenge-event; polarity is independent of truth |
| finding | classification-assignment | finding evidential correspondence to the uniquely selected proposition in classification-assignment; polarity is independent of truth |
| finding | drift-assessment | finding evidential correspondence to the uniquely selected proposition in drift-assessment; polarity is independent of truth |
| finding | failure-assessment | finding evidential correspondence to the uniquely selected proposition in failure-assessment; polarity is independent of truth |
| finding | failure-occurrence | finding evidential correspondence to the uniquely selected proposition in failure-occurrence; polarity is independent of truth |
| finding | improvement-signal | finding evidential correspondence to the uniquely selected proposition in improvement-signal; polarity is independent of truth |
| finding | lesson-outcome-assessment | finding evidential correspondence to the uniquely selected proposition in lesson-outcome-assessment; polarity is independent of truth |
| finding | operational-lesson | finding evidential correspondence to the uniquely selected proposition in operational-lesson; polarity is independent of truth |
| finding | preference-application-assessment | finding evidential correspondence to the uniquely selected proposition in preference-application-assessment; polarity is independent of truth |
| finding | work-outcome-assessment | finding evidential correspondence to the uniquely selected proposition in work-outcome-assessment; polarity is independent of truth |
| measurement-result | authority-claim | measurement-result evidential correspondence to the uniquely selected proposition in authority-claim; polarity is independent of truth |
| measurement-result | challenge-event | measurement-result evidential correspondence to the uniquely selected proposition in challenge-event; polarity is independent of truth |
| measurement-result | classification-assignment | measurement-result evidential correspondence to the uniquely selected proposition in classification-assignment; polarity is independent of truth |
| measurement-result | drift-assessment | measurement-result evidential correspondence to the uniquely selected proposition in drift-assessment; polarity is independent of truth |
| measurement-result | failure-assessment | measurement-result evidential correspondence to the uniquely selected proposition in failure-assessment; polarity is independent of truth |
| measurement-result | failure-occurrence | measurement-result evidential correspondence to the uniquely selected proposition in failure-occurrence; polarity is independent of truth |
| measurement-result | finding | measurement-result evidential correspondence to the uniquely selected proposition in finding; polarity is independent of truth |
| measurement-result | hypothesis | measurement-result evidential correspondence to the uniquely selected proposition in hypothesis; polarity is independent of truth |
| measurement-result | identity-claim | measurement-result evidential correspondence to the uniquely selected proposition in identity-claim; polarity is independent of truth |
| measurement-result | improvement-signal | measurement-result evidential correspondence to the uniquely selected proposition in improvement-signal; polarity is independent of truth |
| measurement-result | lesson-outcome-assessment | measurement-result evidential correspondence to the uniquely selected proposition in lesson-outcome-assessment; polarity is independent of truth |
| measurement-result | operational-lesson | measurement-result evidential correspondence to the uniquely selected proposition in operational-lesson; polarity is independent of truth |
| measurement-result | preference-application-assessment | measurement-result evidential correspondence to the uniquely selected proposition in preference-application-assessment; polarity is independent of truth |
| measurement-result | work-outcome-assessment | measurement-result evidential correspondence to the uniquely selected proposition in work-outcome-assessment; polarity is independent of truth |
| observation | authority-claim | observation evidential correspondence to the uniquely selected proposition in authority-claim; polarity is independent of truth |
| observation | challenge-event | observation evidential correspondence to the uniquely selected proposition in challenge-event; polarity is independent of truth |
| observation | classification-assignment | observation evidential correspondence to the uniquely selected proposition in classification-assignment; polarity is independent of truth |
| observation | drift-assessment | observation evidential correspondence to the uniquely selected proposition in drift-assessment; polarity is independent of truth |
| observation | failure-assessment | observation evidential correspondence to the uniquely selected proposition in failure-assessment; polarity is independent of truth |
| observation | failure-occurrence | observation evidential correspondence to the uniquely selected proposition in failure-occurrence; polarity is independent of truth |
| observation | finding | observation evidential correspondence to the uniquely selected proposition in finding; polarity is independent of truth |
| observation | hypothesis | observation evidential correspondence to the uniquely selected proposition in hypothesis; polarity is independent of truth |
| observation | identity-claim | observation evidential correspondence to the uniquely selected proposition in identity-claim; polarity is independent of truth |
| observation | improvement-signal | observation evidential correspondence to the uniquely selected proposition in improvement-signal; polarity is independent of truth |
| observation | lesson-outcome-assessment | observation evidential correspondence to the uniquely selected proposition in lesson-outcome-assessment; polarity is independent of truth |
| observation | operational-lesson | observation evidential correspondence to the uniquely selected proposition in operational-lesson; polarity is independent of truth |
| observation | preference-application-assessment | observation evidential correspondence to the uniquely selected proposition in preference-application-assessment; polarity is independent of truth |
| observation | work-outcome-assessment | observation evidential correspondence to the uniquely selected proposition in work-outcome-assessment; polarity is independent of truth |
| operational-observation | challenge-event | operational-observation evidential correspondence to the uniquely selected proposition in challenge-event; polarity is independent of truth |
| operational-observation | classification-assignment | operational-observation evidential correspondence to the uniquely selected proposition in classification-assignment; polarity is independent of truth |
| operational-observation | drift-assessment | operational-observation evidential correspondence to the uniquely selected proposition in drift-assessment; polarity is independent of truth |
| operational-observation | failure-assessment | operational-observation evidential correspondence to the uniquely selected proposition in failure-assessment; polarity is independent of truth |
| operational-observation | failure-occurrence | operational-observation evidential correspondence to the uniquely selected proposition in failure-occurrence; polarity is independent of truth |
| operational-observation | improvement-signal | operational-observation evidential correspondence to the uniquely selected proposition in improvement-signal; polarity is independent of truth |
| operational-observation | lesson-outcome-assessment | operational-observation evidential correspondence to the uniquely selected proposition in lesson-outcome-assessment; polarity is independent of truth |
| operational-observation | operational-lesson | operational-observation evidential correspondence to the uniquely selected proposition in operational-lesson; polarity is independent of truth |
| operational-observation | preference-application-assessment | operational-observation evidential correspondence to the uniquely selected proposition in preference-application-assessment; polarity is independent of truth |
| operational-observation | work-outcome-assessment | operational-observation evidential correspondence to the uniquely selected proposition in work-outcome-assessment; polarity is independent of truth |
