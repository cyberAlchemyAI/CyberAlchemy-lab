# K09 — challenges

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded challenge**.

**Meaning in plain language.** A challenge event targets a revision under an exact contract and permitted mode. The target continues to need separate suspension or reversal decisions.

**Question answered.** Which exact governed subject revision does this Challenge Event challenge?

**Formal definition.**

```text
Meaning_K09(W,e,f) := ∃ w ∈ W.ChallengeTarget. Base_K09(W,e,f,w) ∧ (w.challenge = s ∧ w.target = t ∧ t = resolve(q.challenged_version_ref) ∧ w.contract = resolve(q.challenge_contract_ref) ∧ w.mode = code(q.challenge_mode) ∧ ChallengePermitted(W,w,f))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a ChallengeTarget record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `challenge` | Challenge Event exact revision |
| `target` | challenged exact revision |
| `contract` | Challenge Contract exact revision |
| `mode` | contract-permitted challenge constructor |
| `posture` | recorded challenge request or assessment posture |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

`ChallengePermitted`: The exact contract admits the challenge target kind, mode and challenger in this scope; the challenge body names the target revision and recorded posture. This predicate contains no suspension, reversal or contradiction proof.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `challenge_contract_ref` | `w.contract` | exact contract permitting this target kind, challenger and challenge mode |
| `challenge_mode` | `w.mode` | contract-permitted request/assessment challenge mode; no suspension constructor |
| `challenged_version_ref` | `w.target` | exact challenged artifact revision |

**Operational behavior.** Append the challenge against t under its contract; preserve the target's operational status and existing decisions.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Challenge C questions Subject S@1 while S remains active and no contradiction proof exists.

**Insufficient case.** A challenge to S@2 cannot suspend or establish a challenge against S@1.

**Useful correction.** Retarget the challenge to the correct revision under a contract permitting that target kind and mode; obtain separate suspension/reversal evidence if needed.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| suspension | A qualified suspension transition changes the subject's lifecycle posture. | `relation.challenges:forbidden:0` |
| reversal | A separately qualified reversal changes an earlier selected decision or state. | `relation.challenges:forbidden:1` |
| contradiction-proof | A checked exact proof derives the owned logical negation of the challenged statement under the pinned theory. | `relation.challenges:forbidden:2` |
| authority | An authenticated authority root or valid bounded delegation chain permits this holder/action/scope at the frame epoch. | `relation.challenges:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** All 100 target-kind branches must refine their contract target interpretation. Challenge-of-challenge is allowed only as an explicit record, not an inference loop.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/challenges.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K09-challenges.json)

**Exact ordered pairs (100).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| challenge-event | agent-action | Challenge Contract admits a challenge against agent-action in this mode; only that exact revision is targeted |
| challenge-event | agent-assignment | Challenge Contract admits a challenge against agent-assignment in this mode; only that exact revision is targeted |
| challenge-event | agent-capability | Challenge Contract admits a challenge against agent-capability in this mode; only that exact revision is targeted |
| challenge-event | agent-instance | Challenge Contract admits a challenge against agent-instance in this mode; only that exact revision is targeted |
| challenge-event | agent-profile | Challenge Contract admits a challenge against agent-profile in this mode; only that exact revision is targeted |
| challenge-event | agent-reflection | Challenge Contract admits a challenge against agent-reflection in this mode; only that exact revision is targeted |
| challenge-event | agent-session | Challenge Contract admits a challenge against agent-session in this mode; only that exact revision is targeted |
| challenge-event | artifact-type | Challenge Contract admits a challenge against artifact-type in this mode; only that exact revision is targeted |
| challenge-event | artifact-type-request | Challenge Contract admits a challenge against artifact-type-request in this mode; only that exact revision is targeted |
| challenge-event | authority-claim | Challenge Contract admits a challenge against authority-claim in this mode; only that exact revision is targeted |
| challenge-event | bounded-context | Challenge Contract admits a challenge against bounded-context in this mode; only that exact revision is targeted |
| challenge-event | canonical-package-manifest | Challenge Contract admits a challenge against canonical-package-manifest in this mode; only that exact revision is targeted |
| challenge-event | capability-instance | Challenge Contract admits a challenge against capability-instance in this mode; only that exact revision is targeted |
| challenge-event | capability-realization-binding | Challenge Contract admits a challenge against capability-realization-binding in this mode; only that exact revision is targeted |
| challenge-event | challenge-contract | Challenge Contract admits a challenge against challenge-contract in this mode; only that exact revision is targeted |
| challenge-event | challenge-event | Challenge Contract admits a challenge against challenge-event in this mode; only that exact revision is targeted |
| challenge-event | classification-assignment | Challenge Contract admits a challenge against classification-assignment in this mode; only that exact revision is targeted |
| challenge-event | classification-scheme | Challenge Contract admits a challenge against classification-scheme in this mode; only that exact revision is targeted |
| challenge-event | classification-value | Challenge Contract admits a challenge against classification-value in this mode; only that exact revision is targeted |
| challenge-event | communication-preference | Challenge Contract admits a challenge against communication-preference in this mode; only that exact revision is targeted |
| challenge-event | constitution | Challenge Contract admits a challenge against constitution in this mode; only that exact revision is targeted |
| challenge-event | context | Challenge Contract admits a challenge against context in this mode; only that exact revision is targeted |
| challenge-event | context-lineage-record | Challenge Contract admits a challenge against context-lineage-record in this mode; only that exact revision is targeted |
| challenge-event | context-map | Challenge Contract admits a challenge against context-map in this mode; only that exact revision is targeted |
| challenge-event | context-migration-manifest | Challenge Contract admits a challenge against context-migration-manifest in this mode; only that exact revision is targeted |
| challenge-event | context-profile | Challenge Contract admits a challenge against context-profile in this mode; only that exact revision is targeted |
| challenge-event | context-request | Challenge Contract admits a challenge against context-request in this mode; only that exact revision is targeted |
| challenge-event | context-view | Challenge Contract admits a challenge against context-view in this mode; only that exact revision is targeted |
| challenge-event | contract | Challenge Contract admits a challenge against contract in this mode; only that exact revision is targeted |
| challenge-event | decision | Challenge Contract admits a challenge against decision in this mode; only that exact revision is targeted |
| challenge-event | decision-scope | Challenge Contract admits a challenge against decision-scope in this mode; only that exact revision is targeted |
| challenge-event | definition | Challenge Contract admits a challenge against definition in this mode; only that exact revision is targeted |
| challenge-event | delegation | Challenge Contract admits a challenge against delegation in this mode; only that exact revision is targeted |
| challenge-event | drift-assessment | Challenge Contract admits a challenge against drift-assessment in this mode; only that exact revision is targeted |
| challenge-event | effect | Challenge Contract admits a challenge against effect in this mode; only that exact revision is targeted |
| challenge-event | evaluation | Challenge Contract admits a challenge against evaluation in this mode; only that exact revision is targeted |
| challenge-event | evidence-set | Challenge Contract admits a challenge against evidence-set in this mode; only that exact revision is targeted |
| challenge-event | experiment-design | Challenge Contract admits a challenge against experiment-design in this mode; only that exact revision is targeted |
| challenge-event | experiment-run | Challenge Contract admits a challenge against experiment-run in this mode; only that exact revision is targeted |
| challenge-event | failure-assessment | Challenge Contract admits a challenge against failure-assessment in this mode; only that exact revision is targeted |
| challenge-event | failure-control-binding | Challenge Contract admits a challenge against failure-control-binding in this mode; only that exact revision is targeted |
| challenge-event | failure-mode | Challenge Contract admits a challenge against failure-mode in this mode; only that exact revision is targeted |
| challenge-event | failure-occurrence | Challenge Contract admits a challenge against failure-occurrence in this mode; only that exact revision is targeted |
| challenge-event | feedback-record | Challenge Contract admits a challenge against feedback-record in this mode; only that exact revision is targeted |
| challenge-event | finding | Challenge Contract admits a challenge against finding in this mode; only that exact revision is targeted |
| challenge-event | generated-output | Challenge Contract admits a challenge against generated-output in this mode; only that exact revision is targeted |
| challenge-event | goal | Challenge Contract admits a challenge against goal in this mode; only that exact revision is targeted |
| challenge-event | governance-event-history | Challenge Contract admits a challenge against governance-event-history in this mode; only that exact revision is targeted |
| challenge-event | governed-model | Challenge Contract admits a challenge against governed-model in this mode; only that exact revision is targeted |
| challenge-event | hypothesis | Challenge Contract admits a challenge against hypothesis in this mode; only that exact revision is targeted |
| challenge-event | identity-claim | Challenge Contract admits a challenge against identity-claim in this mode; only that exact revision is targeted |
| challenge-event | implementation | Challenge Contract admits a challenge against implementation in this mode; only that exact revision is targeted |
| challenge-event | improvement-signal | Challenge Contract admits a challenge against improvement-signal in this mode; only that exact revision is targeted |
| challenge-event | improvement-target | Challenge Contract admits a challenge against improvement-target in this mode; only that exact revision is targeted |
| challenge-event | incident | Challenge Contract admits a challenge against incident in this mode; only that exact revision is targeted |
| challenge-event | intent-resolution | Challenge Contract admits a challenge against intent-resolution in this mode; only that exact revision is targeted |
| challenge-event | lesson-application | Challenge Contract admits a challenge against lesson-application in this mode; only that exact revision is targeted |
| challenge-event | lesson-outcome-assessment | Challenge Contract admits a challenge against lesson-outcome-assessment in this mode; only that exact revision is targeted |
| challenge-event | measurement-method | Challenge Contract admits a challenge against measurement-method in this mode; only that exact revision is targeted |
| challenge-event | measurement-result | Challenge Contract admits a challenge against measurement-result in this mode; only that exact revision is targeted |
| challenge-event | method | Challenge Contract admits a challenge against method in this mode; only that exact revision is targeted |
| challenge-event | model-instance-binding | Challenge Contract admits a challenge against model-instance-binding in this mode; only that exact revision is targeted |
| challenge-event | observation | Challenge Contract admits a challenge against observation in this mode; only that exact revision is targeted |
| challenge-event | ontology | Challenge Contract admits a challenge against ontology in this mode; only that exact revision is targeted |
| challenge-event | ontology-cut | Challenge Contract admits a challenge against ontology-cut in this mode; only that exact revision is targeted |
| challenge-event | ontology-edge | Challenge Contract admits a challenge against ontology-edge in this mode; only that exact revision is targeted |
| challenge-event | ontology-manifest | Challenge Contract admits a challenge against ontology-manifest in this mode; only that exact revision is targeted |
| challenge-event | ontology-node | Challenge Contract admits a challenge against ontology-node in this mode; only that exact revision is targeted |
| challenge-event | ontology-package | Challenge Contract admits a challenge against ontology-package in this mode; only that exact revision is targeted |
| challenge-event | ontology-view | Challenge Contract admits a challenge against ontology-view in this mode; only that exact revision is targeted |
| challenge-event | operational-lesson | Challenge Contract admits a challenge against operational-lesson in this mode; only that exact revision is targeted |
| challenge-event | operational-observation | Challenge Contract admits a challenge against operational-observation in this mode; only that exact revision is targeted |
| challenge-event | person | Challenge Contract admits a challenge against person in this mode; only that exact revision is targeted |
| challenge-event | person-reference | Challenge Contract admits a challenge against person-reference in this mode; only that exact revision is targeted |
| challenge-event | policy | Challenge Contract admits a challenge against policy in this mode; only that exact revision is targeted |
| challenge-event | preference-application-assessment | Challenge Contract admits a challenge against preference-application-assessment in this mode; only that exact revision is targeted |
| challenge-event | principal | Challenge Contract admits a challenge against principal in this mode; only that exact revision is targeted |
| challenge-event | principal-reference | Challenge Contract admits a challenge against principal-reference in this mode; only that exact revision is targeted |
| challenge-event | product | Challenge Contract admits a challenge against product in this mode; only that exact revision is targeted |
| challenge-event | product-capability | Challenge Contract admits a challenge against product-capability in this mode; only that exact revision is targeted |
| challenge-event | product-thesis | Challenge Contract admits a challenge against product-thesis in this mode; only that exact revision is targeted |
| challenge-event | project | Challenge Contract admits a challenge against project in this mode; only that exact revision is targeted |
| challenge-event | project-state | Challenge Contract admits a challenge against project-state in this mode; only that exact revision is targeted |
| challenge-event | relation-kind | Challenge Contract admits a challenge against relation-kind in this mode; only that exact revision is targeted |
| challenge-event | research-inquiry | Challenge Contract admits a challenge against research-inquiry in this mode; only that exact revision is targeted |
| challenge-event | research-run | Challenge Contract admits a challenge against research-run in this mode; only that exact revision is targeted |
| challenge-event | responsibility | Challenge Contract admits a challenge against responsibility in this mode; only that exact revision is targeted |
| challenge-event | review | Challenge Contract admits a challenge against review in this mode; only that exact revision is targeted |
| challenge-event | role | Challenge Contract admits a challenge against role in this mode; only that exact revision is targeted |
| challenge-event | role-assignment | Challenge Contract admits a challenge against role-assignment in this mode; only that exact revision is targeted |
| challenge-event | schema | Challenge Contract admits a challenge against schema in this mode; only that exact revision is targeted |
| challenge-event | semantic-event-history | Challenge Contract admits a challenge against semantic-event-history in this mode; only that exact revision is targeted |
| challenge-event | source | Challenge Contract admits a challenge against source in this mode; only that exact revision is targeted |
| challenge-event | team | Challenge Contract admits a challenge against team in this mode; only that exact revision is targeted |
| challenge-event | team-membership | Challenge Contract admits a challenge against team-membership in this mode; only that exact revision is targeted |
| challenge-event | tool | Challenge Contract admits a challenge against tool in this mode; only that exact revision is targeted |
| challenge-event | typed-relation | Challenge Contract admits a challenge against typed-relation in this mode; only that exact revision is targeted |
| challenge-event | ubiquitous-language | Challenge Contract admits a challenge against ubiquitous-language in this mode; only that exact revision is targeted |
| challenge-event | work | Challenge Contract admits a challenge against work in this mode; only that exact revision is targeted |
| challenge-event | work-outcome-assessment | Challenge Contract admits a challenge against work-outcome-assessment in this mode; only that exact revision is targeted |
