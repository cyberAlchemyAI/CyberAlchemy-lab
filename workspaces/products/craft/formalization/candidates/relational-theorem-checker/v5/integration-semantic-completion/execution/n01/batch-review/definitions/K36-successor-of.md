# K36 — successor-of

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded conditional succession**.

**Meaning in plain language.** Succession records that a revision continues or supersedes its predecessor. Actual replacement requires a separately qualified lifecycle transition.

**Question answered.** Which predecessor does this successor continue or replace?

**Formal definition.**

```text
Meaning_K36(W,e,f) := ∃ w ∈ W.Succession. Base_K36(W,e,f,w) ∧ (w.successor = s ∧ w.predecessor = t ∧ kind(s)=kind(t) ∧ w.effect = successionValue(q.succession_effect) ∧ w.effect ∈ {continues,supersedes} ∧ w.record.participants = (s,t,w.effect))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a Succession record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `successor` | exact successor revision |
| `predecessor` | exact predecessor revision of the same declared kind |
| `effect` | continues or supersedes declaration |
| `record` | owned directional succession declaration |
| `replacement` | optional separate qualified lifecycle transition, not required to record a declaration |

`kind`: The independently captured governed artifact kind of an exact reference. Camel-case constructor names in formulas denote the corresponding hyphenated source kinds listed in the signature matrix.

`successionValue`: The exact owned interpretation as continues or supersedes. A supersedes declaration and a qualified replacement transition are different records; continues never becomes replacement.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `succession_effect` | `w.effect` | continues or supersedes declaration; replacement additionally needs a qualified transition |

**Operational behavior.** Append succession; a separately qualified replacement may act only for supersedes, preserving history and authority roots.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Successor S continues Predecessor P, while P remains the active predecessor and no replacement occurs.

**Insufficient case.** A continues edge cannot be relabeled as a supersedes transition.

**Useful correction.** Keep continues and supersedes distinct; obtain a qualified replacement transition before changing active-state selection.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| automatic-supersession | A qualified replacement transition makes the successor active in place of the predecessor; continues alone cannot satisfy it. | `relation.successor-of:forbidden:0` |
| identity-equality | The independent governed identity model equates these endpoints, beyond lineage or succession. | `relation.successor-of:forbidden:1` |
| authority-transfer | A separately authorized transfer changes the authority holder for this envelope. | `relation.successor-of:forbidden:2` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** All 100 same-kind branches need lineage/lifecycle adapters. Whether to reject self-links or cycles is proposed validation policy, not silently added to inherited meaning.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/successor-of.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K36-successor-of.json)

**Exact ordered pairs (100).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| agent-action | agent-action | directional same-kind agent-action succession declaration; preserve identities, continues/supersedes and history |
| agent-assignment | agent-assignment | directional same-kind agent-assignment succession declaration; preserve identities, continues/supersedes and history |
| agent-capability | agent-capability | directional same-kind agent-capability succession declaration; preserve identities, continues/supersedes and history |
| agent-instance | agent-instance | directional same-kind agent-instance succession declaration; preserve identities, continues/supersedes and history |
| agent-profile | agent-profile | directional same-kind agent-profile succession declaration; preserve identities, continues/supersedes and history |
| agent-reflection | agent-reflection | directional same-kind agent-reflection succession declaration; preserve identities, continues/supersedes and history |
| agent-session | agent-session | directional same-kind agent-session succession declaration; preserve identities, continues/supersedes and history |
| artifact-type | artifact-type | directional same-kind artifact-type succession declaration; preserve identities, continues/supersedes and history |
| artifact-type-request | artifact-type-request | directional same-kind artifact-type-request succession declaration; preserve identities, continues/supersedes and history |
| authority-claim | authority-claim | directional same-kind authority-claim succession declaration; preserve identities, continues/supersedes and history |
| bounded-context | bounded-context | directional same-kind bounded-context succession declaration; preserve identities, continues/supersedes and history |
| canonical-package-manifest | canonical-package-manifest | directional same-kind canonical-package-manifest succession declaration; preserve identities, continues/supersedes and history |
| capability-instance | capability-instance | directional same-kind capability-instance succession declaration; preserve identities, continues/supersedes and history |
| capability-realization-binding | capability-realization-binding | directional same-kind capability-realization-binding succession declaration; preserve identities, continues/supersedes and history |
| challenge-contract | challenge-contract | directional same-kind challenge-contract succession declaration; preserve identities, continues/supersedes and history |
| challenge-event | challenge-event | directional same-kind challenge-event succession declaration; preserve identities, continues/supersedes and history |
| classification-assignment | classification-assignment | directional same-kind classification-assignment succession declaration; preserve identities, continues/supersedes and history |
| classification-scheme | classification-scheme | directional same-kind classification-scheme succession declaration; preserve identities, continues/supersedes and history |
| classification-value | classification-value | directional same-kind classification-value succession declaration; preserve identities, continues/supersedes and history |
| communication-preference | communication-preference | directional same-kind communication-preference succession declaration; preserve identities, continues/supersedes and history |
| constitution | constitution | directional same-kind constitution succession declaration; preserve identities, continues/supersedes and history |
| context | context | directional same-kind context succession declaration; preserve identities, continues/supersedes and history |
| context-lineage-record | context-lineage-record | directional same-kind context-lineage-record succession declaration; preserve identities, continues/supersedes and history |
| context-map | context-map | directional same-kind context-map succession declaration; preserve identities, continues/supersedes and history |
| context-migration-manifest | context-migration-manifest | directional same-kind context-migration-manifest succession declaration; preserve identities, continues/supersedes and history |
| context-profile | context-profile | directional same-kind context-profile succession declaration; preserve identities, continues/supersedes and history |
| context-request | context-request | directional same-kind context-request succession declaration; preserve identities, continues/supersedes and history |
| context-view | context-view | directional same-kind context-view succession declaration; preserve identities, continues/supersedes and history |
| contract | contract | directional same-kind contract succession declaration; preserve identities, continues/supersedes and history |
| decision | decision | directional same-kind decision succession declaration; preserve identities, continues/supersedes and history |
| decision-scope | decision-scope | directional same-kind decision-scope succession declaration; preserve identities, continues/supersedes and history |
| definition | definition | directional same-kind definition succession declaration; preserve identities, continues/supersedes and history |
| delegation | delegation | directional same-kind delegation succession declaration; preserve identities, continues/supersedes and history |
| drift-assessment | drift-assessment | directional same-kind drift-assessment succession declaration; preserve identities, continues/supersedes and history |
| effect | effect | directional same-kind effect succession declaration; preserve identities, continues/supersedes and history |
| evaluation | evaluation | directional same-kind evaluation succession declaration; preserve identities, continues/supersedes and history |
| evidence-set | evidence-set | directional same-kind evidence-set succession declaration; preserve identities, continues/supersedes and history |
| experiment-design | experiment-design | directional same-kind experiment-design succession declaration; preserve identities, continues/supersedes and history |
| experiment-run | experiment-run | directional same-kind experiment-run succession declaration; preserve identities, continues/supersedes and history |
| failure-assessment | failure-assessment | directional same-kind failure-assessment succession declaration; preserve identities, continues/supersedes and history |
| failure-control-binding | failure-control-binding | directional same-kind failure-control-binding succession declaration; preserve identities, continues/supersedes and history |
| failure-mode | failure-mode | directional same-kind failure-mode succession declaration; preserve identities, continues/supersedes and history |
| failure-occurrence | failure-occurrence | directional same-kind failure-occurrence succession declaration; preserve identities, continues/supersedes and history |
| feedback-record | feedback-record | directional same-kind feedback-record succession declaration; preserve identities, continues/supersedes and history |
| finding | finding | directional same-kind finding succession declaration; preserve identities, continues/supersedes and history |
| generated-output | generated-output | directional same-kind generated-output succession declaration; preserve identities, continues/supersedes and history |
| goal | goal | directional same-kind goal succession declaration; preserve identities, continues/supersedes and history |
| governance-event-history | governance-event-history | directional same-kind governance-event-history succession declaration; preserve identities, continues/supersedes and history |
| governed-model | governed-model | directional same-kind governed-model succession declaration; preserve identities, continues/supersedes and history |
| hypothesis | hypothesis | directional same-kind hypothesis succession declaration; preserve identities, continues/supersedes and history |
| identity-claim | identity-claim | directional same-kind identity-claim succession declaration; preserve identities, continues/supersedes and history |
| implementation | implementation | directional same-kind implementation succession declaration; preserve identities, continues/supersedes and history |
| improvement-signal | improvement-signal | directional same-kind improvement-signal succession declaration; preserve identities, continues/supersedes and history |
| improvement-target | improvement-target | directional same-kind improvement-target succession declaration; preserve identities, continues/supersedes and history |
| incident | incident | directional same-kind incident succession declaration; preserve identities, continues/supersedes and history |
| intent-resolution | intent-resolution | directional same-kind intent-resolution succession declaration; preserve identities, continues/supersedes and history |
| lesson-application | lesson-application | directional same-kind lesson-application succession declaration; preserve identities, continues/supersedes and history |
| lesson-outcome-assessment | lesson-outcome-assessment | directional same-kind lesson-outcome-assessment succession declaration; preserve identities, continues/supersedes and history |
| measurement-method | measurement-method | directional same-kind measurement-method succession declaration; preserve identities, continues/supersedes and history |
| measurement-result | measurement-result | directional same-kind measurement-result succession declaration; preserve identities, continues/supersedes and history |
| method | method | directional same-kind method succession declaration; preserve identities, continues/supersedes and history |
| model-instance-binding | model-instance-binding | directional same-kind model-instance-binding succession declaration; preserve identities, continues/supersedes and history |
| observation | observation | directional same-kind observation succession declaration; preserve identities, continues/supersedes and history |
| ontology | ontology | directional same-kind ontology succession declaration; preserve identities, continues/supersedes and history |
| ontology-cut | ontology-cut | directional same-kind ontology-cut succession declaration; preserve identities, continues/supersedes and history |
| ontology-edge | ontology-edge | directional same-kind ontology-edge succession declaration; preserve identities, continues/supersedes and history |
| ontology-manifest | ontology-manifest | directional same-kind ontology-manifest succession declaration; preserve identities, continues/supersedes and history |
| ontology-node | ontology-node | directional same-kind ontology-node succession declaration; preserve identities, continues/supersedes and history |
| ontology-package | ontology-package | directional same-kind ontology-package succession declaration; preserve identities, continues/supersedes and history |
| ontology-view | ontology-view | directional same-kind ontology-view succession declaration; preserve identities, continues/supersedes and history |
| operational-lesson | operational-lesson | directional same-kind operational-lesson succession declaration; preserve identities, continues/supersedes and history |
| operational-observation | operational-observation | directional same-kind operational-observation succession declaration; preserve identities, continues/supersedes and history |
| person | person | directional same-kind person succession declaration; preserve identities, continues/supersedes and history |
| person-reference | person-reference | directional same-kind person-reference succession declaration; preserve identities, continues/supersedes and history |
| policy | policy | directional same-kind policy succession declaration; preserve identities, continues/supersedes and history |
| preference-application-assessment | preference-application-assessment | directional same-kind preference-application-assessment succession declaration; preserve identities, continues/supersedes and history |
| principal | principal | directional same-kind principal succession declaration; preserve identities, continues/supersedes and history |
| principal-reference | principal-reference | directional same-kind principal-reference succession declaration; preserve identities, continues/supersedes and history |
| product | product | directional same-kind product succession declaration; preserve identities, continues/supersedes and history |
| product-capability | product-capability | directional same-kind product-capability succession declaration; preserve identities, continues/supersedes and history |
| product-thesis | product-thesis | directional same-kind product-thesis succession declaration; preserve identities, continues/supersedes and history |
| project | project | directional same-kind project succession declaration; preserve identities, continues/supersedes and history |
| project-state | project-state | directional same-kind project-state succession declaration; preserve identities, continues/supersedes and history |
| relation-kind | relation-kind | directional same-kind relation-kind succession declaration; preserve identities, continues/supersedes and history |
| research-inquiry | research-inquiry | directional same-kind research-inquiry succession declaration; preserve identities, continues/supersedes and history |
| research-run | research-run | directional same-kind research-run succession declaration; preserve identities, continues/supersedes and history |
| responsibility | responsibility | directional same-kind responsibility succession declaration; preserve identities, continues/supersedes and history |
| review | review | directional same-kind review succession declaration; preserve identities, continues/supersedes and history |
| role | role | directional same-kind role succession declaration; preserve identities, continues/supersedes and history |
| role-assignment | role-assignment | directional same-kind role-assignment succession declaration; preserve identities, continues/supersedes and history |
| schema | schema | directional same-kind schema succession declaration; preserve identities, continues/supersedes and history |
| semantic-event-history | semantic-event-history | directional same-kind semantic-event-history succession declaration; preserve identities, continues/supersedes and history |
| source | source | directional same-kind source succession declaration; preserve identities, continues/supersedes and history |
| team | team | directional same-kind team succession declaration; preserve identities, continues/supersedes and history |
| team-membership | team-membership | directional same-kind team-membership succession declaration; preserve identities, continues/supersedes and history |
| tool | tool | directional same-kind tool succession declaration; preserve identities, continues/supersedes and history |
| typed-relation | typed-relation | directional same-kind typed-relation succession declaration; preserve identities, continues/supersedes and history |
| ubiquitous-language | ubiquitous-language | directional same-kind ubiquitous-language succession declaration; preserve identities, continues/supersedes and history |
| work | work | directional same-kind work succession declaration; preserve identities, continues/supersedes and history |
| work-outcome-assessment | work-outcome-assessment | directional same-kind work-outcome-assessment succession declaration; preserve identities, continues/supersedes and history |
