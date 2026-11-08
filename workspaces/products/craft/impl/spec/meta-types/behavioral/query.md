---
artifact_id: domainspec-v2-metatype-query
artifact_type: companion-doc
companion_to: query.schema.yml
intent: Human companion to the Query meta-type machine criterion.
owner: definitions-governance
lifecycle_status: candidate
constitution_selectors: [schema-constitution, meta-type-formalization]
validation_profile: meta-type-card
boundary: PUBLIC shape criterion; the engine src/rules δ-derivation is never referenced (moat).
---

# Query — meta-type card (Behavioral)

**Companion to** [`query.schema.yml`](./query.schema.yml). Prose is non-normative.

## Formal criterion
A concept declared **Query** is well-formed IFF its `Attribute | Value` table declares
`state_change = no` (the read side — it returns a view without mutation).

## Distinguisher vs Operation
A Query is read-only (`state_change=no`); an Operation changes state (`state_change=yes`).

## Edge participation (DS-D8 slice)
- SOURCE of: `reads`

## Fixtures
- positive: [`spec/__fixtures__/mt/query-ok.md`](../../__fixtures__/mt/query-ok.md)
- negative: [`spec/__fixtures__/mt/query-bad.md`](../../__fixtures__/mt/query-bad.md) — mutates → rejected.

## Boundary
The discriminator is the **declared** `state_change` attribute — shape only (no body inference / moat).
