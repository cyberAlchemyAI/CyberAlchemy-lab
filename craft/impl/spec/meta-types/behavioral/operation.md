---
artifact_id: domainspec-v2-metatype-operation
artifact_type: companion-doc
companion_to: operation.schema.yml
intent: Human companion to the Operation meta-type machine criterion.
owner: definitions-governance
lifecycle_status: candidate
constitution_selectors: [schema-constitution, meta-type-formalization]
validation_profile: meta-type-card
boundary: PUBLIC shape criterion; the engine src/rules δ-derivation is never referenced (moat).
---

# Operation — meta-type card (Behavioral)

**Companion to** [`operation.schema.yml`](./operation.schema.yml). Prose is non-normative.

## Formal criterion
A concept declared **Operation** is well-formed IFF its `Attribute | Value` table declares
`state_change = yes` (the write side — it mutates entity state).

## Distinguisher vs Query
An Operation changes state (`state_change=yes`); a Query is read-only (`state_change=no`).

## Edge participation (DS-D8 slice)
- SOURCE of: `creates`, `produces`, `produces-for`, `reads`
- TARGET of: `applies`, `calculates`, `enforces`, `exposes`, `mutates`,
  `orchestrates`, `performs`, `triggers-cross`

## Generated creation projection

An Operation authors its `creates` edge once. Generated semantic views derive
`creation_targets` as the finite set of exact Entity targets of that edge.
Source specifications and minted node sources must not author this projection.
`state_change = yes` alone never proves creation.

## Fixtures
- positive: [`spec/__fixtures__/mt/operation-ok.md`](../../__fixtures__/mt/operation-ok.md)
- negative: [`spec/__fixtures__/mt/operation-bad.md`](../../__fixtures__/mt/operation-bad.md) — read-only → rejected.

## Boundary
The discriminator is the **declared** `state_change` attribute — shape only, never inferred from the
operation body (that would be the engine moat).
