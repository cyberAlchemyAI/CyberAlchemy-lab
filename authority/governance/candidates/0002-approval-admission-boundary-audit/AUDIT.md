# Approval and admission boundary audit

Status: **candidate awaiting owner review**

## Finding

The Lab preserved separate decision identities correctly but exposed each dependent admission as a separate human approval. This conflicts with the admitted single Decision Checkpoint interaction model. The model's Definitions are admitted, but five required interaction carriers and an Admission Transaction carrier are missing, so the rule is not executable.

## Boundary assessment

| Boundary | Decision identity | Separate checkpoint | Reason |
| --- | --- | --- | --- |
| D70 integrated semantic and carrier model | necessary | avoidable-if-packaged-upfront | It changes the admitted semantic and carrier surface and therefore retains an independent authority act. It could still have been presented in the same Decision Bundle as exact downstream decisions. |
| D71 operational foundation | necessary | avoidable-if-packaged-upfront | It admits operational instances and relations under a different effect boundary. Separate identity is correct; a separate user interaction was not required once its exact target existed. |
| D72 history contracts and first state bootstrap | necessary-under-materialized-target-rule | caused-by-late-target-materialization | The exact history carriers and successor target were produced only after D71. The admitted Decision Bundle rule excludes future unresolved targets, so the process forced another checkpoint. The work should have prepared this dependency before the prior checkpoint. |
| D73 first Agent work episode | necessary | reasonable-for-new-reviewed-work | It introduces new exact Agent, Context, Ontology, Work, classification, state, and relation instances. It is a new reviewable semantic and lifecycle effect. |
| Proposed D74 admission of the D73 Project State successor | unnecessary | reject | The successor is a deterministic governed consequence of Decision 0073. Requiring another approval creates an endless decision-to-state-to-decision chain. |

## Corrected rule

One bounded work package gets one human Decision Checkpoint. It may contain several independent Decision members in one Decision Bundle. One response authorizes one atomic Admission Transaction. Deterministic receipts, events, indexes, projections, and the resulting Project State successor are consequences of that transaction and do not create another approval.

## Carrier coverage

- `cal.artifact-type.decision/v1`: **admitted-current**
- `cal.artifact-type.decision-scope/v1`: **admitted-current**
- `cal.artifact-type.review/v1`: **admitted-current**
- `cal.artifact-type.authority-boundary/v1`: **missing**
- `cal.artifact-type.decision-bundle/v1`: **missing**
- `cal.artifact-type.decision-checkpoint/v1`: **missing**
- `cal.artifact-type.user-decision-preference/v1`: **missing**
- `cal.artifact-type.workflow-decision-profile/v1`: **missing**
- `cal.artifact-type.admission-transaction/v1`: **missing**

## Current history

Decisions 0070 through 0073 remain valid immutable history. The pending Decision 0074 pattern should not be applied. The next review package should contain the missing carriers, a single-checkpoint workflow profile, and the already materialized D73 successor as separately scoped members of one bundle.

## Claim ceiling

This audit identifies approval and admission boundary drift and proposes a corrected interaction and transaction model. It does not alter admitted decisions, admit carriers, authorize the pending successor, activate a runtime, or create an external effect.
