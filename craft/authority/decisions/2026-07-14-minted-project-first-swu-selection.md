---
node_type: decision
is_session: false
status: pass
boundary: INTERNAL — DomainSpec v2 minted-project execution selection
created: 2026-07-14
timestamp: 2026-07-15T00:50:53Z
decision_id: DEC-DSV2-MINTED-PROJECT-FIRST-SWU
target_scope: first executable unit in the minted-project work-pack
source: operator choice in decision-gate, 2026-07-14
---

# Decision: Select the First Minted-Project SWU

## Consequential work

The validated minted-project plan could not prepare runtime context or route a
bounded Task Session while no eligible SWU was explicitly selected.

## Considered options

1. Select `SWU-MNP-001` as the next execution unit.
2. Keep the work-pack planned and unselected.
3. Re-plan the first unit before selection.

The standing Explain / more-context path was used before selection and did not
count as consent.

## Selected option

**Option 1 — select `SWU-MNP-001`.**

## Selection binding

- Selected SWU: `SWU-MNP-001`
- Parent task: `TASK-MNP-CONTRACT`
- State: selected, not started
- Immediate next owner: Context Builder for a strict Markdown plus JSON/index
  runtime pack
- Execution owner after context passes: one bounded Task Session

## Preserved boundaries

- Selection does not execute implementation or activate W1 as a whole.
- The Task Session write scope remains limited to the paths named by
  `TASK-MNP-CONTRACT`.
- Later SWUs remain dependency-blocked.
- Release admission, fixture movement, cross-feature claims, and independent
  edge lifecycle remain separately gated.

## Rationale and consequence

`SWU-MNP-001` is the only dependency-valid first unit. It establishes the
machine contracts and experimental profile binding consumed by every later
resolver, compiler, view, minter, conformance, and admission unit. The selection
resolves execution-dispatch gate `g03-explicit-swu-selection`; gate
`g04-strict-context` remains closed until Context Builder produces complete
runtime evidence.

## Gate result

- Result: `PASS`
- Decisions resolved: 1
- Blockers remaining for selection: 0
- Deferred decisions: none
- Next step: build strict runtime context, then invoke one Task Session

