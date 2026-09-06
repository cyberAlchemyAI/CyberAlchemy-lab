# Tower Seed: Spec–Ontology Unification

Status: seed (tower not yet executed)
Date: 2026-06-11
Depth: full
Owner: DomainSpec v2

## Underlying problem (solution-independent)

The mapping from spec to code is implicit, so implementation agents are
expensive and drift-prone. Spec and code are really two forms of the same domain
taxonomy, but nothing in the toolchain treats them as one structure.

## Hypothesis under test (Lane Z anchor)

Treat the spec and the ontology as the **same object in two forms**:

- A DomainSpec feature is a **tree** of nodes (concepts, operations, rules,
  events, tests, mappings, workflows).
- Across features it is a **graph** (cross-feature edges already exist today).
- A **node maps to a code pattern**; an **edge maps to a composition rule**
  between those patterns.
- Implementation agents are then **ephemeral and bounded**: their system-prompt
  constitution is the architecture + code patterns; their context is the spec
  subgraph. They only need to know which code pattern realizes a node and how
  edges compose those patterns. This is the Arcanum planning discipline applied
  to limited-scope tasks.

Hypothesis: this makes implementation agents much cheaper and less drift-prone,
because the spec→code mapping becomes typed and explicit instead of inferred.

## Evidence sources

- `primary-source`: current DomainSpec v1 spec structure in
  [`implementation/domainspec`](../../../../implementation/domainspec) — confirm
  it already has nodes, edges, and cross-feature edges.
- `primary-source`: Arcanum planning/constitution discipline
  ([`constitution-governance`](../../../../.claude/skills/constitution-governance/),
  [`task-session`](../../../../.claude/skills/task-session/)).

## Lane assignment

- **Lane Z (zig-zag):** Build the unified node→pattern / edge→composition model
  for one real feature. Encode the architecture + code patterns as an ephemeral-
  agent constitution; run a paper toy of "spec subgraph in, code out." Attack it:
  where does node↔pattern fail to be 1:1? what breaks when a pattern needs cross-
  cutting context the subgraph doesn't carry? does the taxonomy stay closed?
- **Lane A (alternatives):** Hold the underlying problem fixed; propose a
  different solution than full unification. Candidates: keep spec and ontology
  separate with a **generated bidirectional mapping** (codegen + drift check, the
  v1 direction); or a typed code-tag contract; or a pattern catalog that agents
  query rather than carry. Argue which gets agent efficiency without forcing
  spec and code to be the same artifact.

## Promotion boundary

Local research only. No change to spec schema, code-pattern catalog, agent
constitutions, or runtime until a later approved `task-session`.

## Non-goals

- Committing to "spec == code" as canonical before the toy proves agent gains.
- Designing the ephemeral-agent runtime; this tower decides whether the typed
  graph is the right substrate, not how to ship the agents.

## Open residue (pre-execution)

- Is the taxonomy actually closed enough that node→pattern can be near-1:1?
- What carries cross-feature context into a bounded agent without leaking the
  whole graph into its prompt?
- Where does this overlap with the dcb-correctness boundary model (shared edges,
  shared tags)?
