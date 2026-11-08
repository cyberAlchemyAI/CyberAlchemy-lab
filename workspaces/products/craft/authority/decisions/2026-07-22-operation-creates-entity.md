---
node_type: decision
is_session: false
status: superseded
boundary: INTERNAL — DomainSpec v2 DS-D2 and DS-D8 relationship authority
created: 2026-07-22
timestamp: 2026-07-22T16:10:09Z
decision_id: DEC-DSV2-OPERATION-CREATES-ENTITY
superseded_by: DEC-DSV2-CANONICAL-CREATION-RESPONSIBILITY
target_scope: same-feature Operation-to-Entity creation semantics
source: operator choices in decision-gate, 2026-07-22
---

# Decision: Operation creates Entity

> Superseded by
> [`DEC-DSV2-CANONICAL-CREATION-RESPONSIBILITY`](./2026-07-22-canonical-creation-responsibility.md).
> This file remains the historical record of the initial `creates` admission; its
> dual-authored `creation_targets` contract and `many_to_many` multiplicity are no
> longer active authority.

## Consequential work

The accepted obvious-edge completeness review confirmed that the current
`produces-for` signature is cross-feature and foreign-Entity-only while two
feature graphs use it for same-feature creation. Canonical relationship,
validator, compiler, fixture, and generated-graph work could not proceed until
the owner selected the semantic repair and its non-vacuous proof contract.

This decision resolves those choices. It records owner intent but does not by
itself mutate or promote DS-D2 or DS-D8 authority.

## Decision 1: relationship partition

### Blocking question

Should same-feature `Operation -> Entity` creation be a distinct relationship,
or should `produces-for` become a generic same/cross-feature write relation?

### Considered options

1. Add a distinct same-feature `creates` relationship.
2. Widen and likely rename `produces-for` as a generic same/cross-feature write
   relationship.
3. Defer the semantic choice and fail the current same-feature uses closed.
4. Explain / more context without selecting an option.

### Selected option

**Option 1 — add a distinct `creates` relationship.**

### Authority binding

- Candidate verb: `creates`.
- Source type: `Operation`.
- Target type: `Entity`.
- Feature scope: same-feature.
- Meaning: an Operation declares that successful execution brings one or more
  runtime instances of the target Entity type into existence with new stable
  identity. The authored graph edge relates model concepts; runtime instances
  do not become graph nodes.
- Exclusions: update, upsert, delete, read, Event production, generic
  persistence, and cross-feature write/projection do not count as `creates`.
- `produces-for` retains its current cross-feature, foreign-Entity write or
  projection meaning.
- `instantiates` is not selected. No reviewed evidence established a separate
  type/template-to-instance relationship in the current graph model.

### Rationale and consequence

The owner selected creation as a first-class semantic distinction rather than
collapsing it into a generic write. Downstream work must replace the two invalid
same-feature `produces-for` witnesses with `creates` only after its complete
machine contract is admitted. Existing cross-feature `produces-for` authority
must not be silently widened or renamed by that work.

## Decision 2: creation proof contract

### Blocking question

How must `creates` prove actual creation instead of becoming an unchecked label
on any `Operation -> Entity` edge?

### Considered options

1. Require a machine-checkable creation effect on the source Operation that is
   bound to the exact Entity target.
2. Treat the authored edge alone as the creation assertion and validate only
   endpoint kinds and scope.
3. Preserve the `creates` selection but defer promotion until a creation-effect
   contract is designed.
4. Explain / more context without selecting an option.

### Selected option

**Option 1 — require a machine-checkable, target-bound creation effect.**

### Proof binding

Before `creates` may become active authority, its machine contract must:

1. give the source Operation a structured creation effect that names or
   unambiguously resolves the exact target Entity concept;
2. accept `Operation --[creates]--> Entity` only when the edge, effect, endpoint
   kinds, and same-feature identity agree;
3. reject a missing creation effect, mismatched target, non-Operation source,
   non-Entity target, cross-feature endpoint pair, and update/upsert operation
   mislabeled as creation;
4. require the inverse consistency check: a declared target-bound creation
   effect cannot silently omit its required `creates` edge;
5. exercise both current positive witnesses, Create Player and Financial
   Settlement, after their source specifications carry the machine effect; and
6. emit deterministic graph, fixture, and validation evidence traceable to the
   canonical relationship tuple and source Operation effect.

The exact field name, serialization shape, and validator module boundary were
resolved by Definitions Governance as `creation_targets`, a finite set of exact
Entity concept references on the source Operation. They may not weaken target
binding or substitute free prose, operation naming, or `state_change: yes` for
the creation effect.

This is a structural specification proof: it rejects an update/upsert inferred
only from naming, prose, or generic state change, but it cannot prove that a
runtime implementation is truthful about the declared effect. Runtime
conformance requires separate execution evidence and is not promoted by DS-D8.

### D18 consequence binding

The selected proof contract makes the relationship non-collapse claim
testable:

- **D20 reject/allow:** a same-feature target-bound creation edge is accepted;
  same-feature `produces-for`, target mismatch, cross-feature `creates`, and
  update-as-create are rejected.
- **D21 derivation:** `creates` derives a creation-effect consistency obligation
  that a generic write edge does not derive.
- **D25 generated artifact:** fixtures and generated graph/provenance must retain
  the distinct `creates` edge and its source-effect trace.

No D22, D23, or D24 consequence is claimed unless later evidence names and
proves it.

## Definitions Governance resolution

- Source-effect field: `creation_targets`.
- Authored Markdown shape: a comma-delimited finite set of exact Entity concept
  names in the Operation's Attribute/Value table.
- Minted JSON shape: a non-empty, unique array of stable Entity node IDs.
- Binding rule: an Operation has `creates` to an Entity if and only if that
  exact target occurs in `creation_targets`.
- DS-D8 multiplicity: `many_to_many`. This describes graph-level concept
  connectivity—an Operation concept may create more than one Entity concept,
  and an Entity concept may be created by more than one Operation concept. It
  does not assert runtime instance cardinality.

## Deferred decisions and implementation details

- Whether a future cross-feature creation concept needs distinct treatment;
  no current witness authorizes it.
- Action-to-Binding verb and signature, which remain outside this gate.

These items do not reopen the selected semantic partition or proof requirement.

## Assumptions recorded

- `creates` describes an Operation type's capability/effect over instances of
  an Entity type; it does not add runtime instance nodes to the authored graph.
- `produces` remains `Operation -> Event`.
- Current `produces-for` semantics and cross-feature scope remain unchanged.
- This decision authorized the Definitions Governance change package recorded
  above; the complete validation evidence is recorded below.

## Remaining blockers

None. The complete tuple, three definition voices, synchronized
indexes/projections, creation-effect schema, scope-aware validation, red/green
fixtures, deterministic generation, and passing checks are present.

## Validation and next route

- Decision Gate: **PASS** — two blocker decisions resolved by the operator.
- Definitions Governance: **PASS** — `DS-D2`, `DS-D8`, and
  `domainspec-v2-D26` carry the governed relationship/effect contract and all
  required voices.
- Relationship registry: **31 active signatures**; `creates` is active and
  `produces-for` remains cross-feature-only.
- Validator/compiler/fixtures: endpoint, location-scope, exact target effect,
  and inverse effect/edge checks are exercised by positive and negative cases.
- Generated evidence: Create Player graph/provenance and the project-level
  Concept Registry read model were regenerated deterministically.
- Validation: relationship, content, documentation, TypeScript, sample lint,
  157/157 tooling tests, and 107/107 engine tests pass.
- Next: no promotion blocker. Future cross-feature creation and Action-to-Binding
  remain separate owner routes, not gaps in this decision. Runtime confirmation
  that implementations honor `creation_targets` is a separate evidence route.

## Source evidence

- `projects/domainspec-v2/definitions/reviews/2026-07-22-obvious-edge-completeness/findings.md`
- `projects/domainspec-v2/definitions/reviews/2026-07-22-obvious-edge-completeness/attacks.md`
- `projects/domainspec-v2/definitions/DEFINITIONS.md#domainspec-v2-D18`
- `projects/domainspec-v2/definitions/relationships/relationships.yml`
- `projects/domainspec-v2/impl/spec/features/ui-profile-create-player/SPEC.md`
- `projects/domainspec-v2/impl/spec/features/financial-settlement/SPEC.md`
- Operator selections `1` and `1` in the 2026-07-22 Decision Gate conversation.
