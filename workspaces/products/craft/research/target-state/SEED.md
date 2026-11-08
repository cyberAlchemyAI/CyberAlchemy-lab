# Tower Seed: Target State

Status: seed (tower not yet executed)
Date: 2026-06-11
Depth: standard
Owner: DomainSpec v2

## Underlying problem (solution-independent)

DomainSpec implies a target state everywhere — features, rules, readiness,
promotion — but never formalizes one, so specs and agents have no explicit,
checkable answer to "where are we going and what does done look like."

## Hypothesis under test (Lane Z anchor)

Make "target state" a first-class, **buildable** artifact in DomainSpec v2,
borrowing from Narrative-Driven Development (NDD): a target state should read
like a narrative you can actually build toward and check progress against, not a
vague goal.

## Primary sources

- `primary-source`: https://narrativedriven.org/what-is-ndd
- `primary-source`: https://narrativedriven.org/what-makes-a-narrative-buildable

The tower must fetch and record these with date-checked source notes before
making claims (`research-tower` source-first rule). Knowledge cutoff means the
content must be read, not assumed.

## Lane assignment

- **Lane Z (zig-zag):** Adopt NDD's "buildable narrative" as the target-state
  primitive. Build a concrete target-state artifact for one DomainSpec feature,
  then attack it: is it checkable? does it drive implementation? where does the
  narrative framing add ceremony without adding direction?
- **Lane A (alternatives):** Hold the underlying problem fixed; propose a
  different target-state formalism. Candidates: fitness functions, acceptance-
  criteria goal-trees, invariants/oracles, or outcome specifications. Argue why
  one of these beats a narrative for an agent that must verify "done."

## Promotion boundary

Local research only. Any move to add a target-state field/section to a DomainSpec
template or validator requires a later approved `task-session`.

## Non-goals

- Rewriting v1 templates.
- Treating NDD as canonical because the user likes it — it is `primary-source`
  for the narrative idea, not for DomainSpec semantics.

## Open residue (pre-execution)

- Is "target state" per-feature, per-project, or both?
- Does target-state thinking belong in the spec, the dispatch, or a new artifact?
