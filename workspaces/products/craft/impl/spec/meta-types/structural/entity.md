---
artifact_id: domainspec-v2-metatype-entity
artifact_type: companion-doc
companion_to: entity.schema.yml
intent: Human companion to the Entity meta-type machine criterion (entity.schema.yml).
owner: definitions-governance
lifecycle_status: candidate
constitution_selectors: [schema-constitution, meta-type-formalization]
validation_profile: meta-type-card
boundary: PUBLIC shape criterion; the engine src/rules δ-derivation is never referenced (moat).
---

# Entity — meta-type card (Structural)

**Companion to** [`entity.schema.yml`](./entity.schema.yml) — the machine criterion the validator loads.
This prose is non-normative; the `.schema.yml` is the checked contract.

## Formal criterion
A concept declared **Entity** is well-formed IFF (a decidable table-walk over its fields table):

1. **has identity** — ≥1 field row whose `Identity` cell is truthy (`yes` / `true` / `✓`).
2. **typedness** — every field row declares a non-empty `Type`.

## Required structure
A fields table with columns `Field | Type | Required | Identity | Description`, ≥1 row, with at least one
row flagged as identity.

## Edge participation (DS-D8 slice)
- SOURCE of: `belongs-to`, `contains`, `emits`, `owns`, `performs`
- TARGET of: `belongs-to`, `creates`, `derives`, `maps`, `owns`,
  `produces-for`, `reads`

## Distinguisher vs Value Object
An Entity **has identity** (an `Identity`-flagged field); a Value Object has **none** and declares an
**Equality** clause. An Entity-declared concept with no identity field is a mis-typed Value Object →
**rejected as Entity**.

## Fixtures (the discriminating pair)
- positive: [`spec/__fixtures__/mt/entity-ok.md`](../../__fixtures__/mt/entity-ok.md) — passes.
- negative: [`spec/__fixtures__/mt/entity-bad.md`](../../__fixtures__/mt/entity-bad.md) — VO-shaped
  (no identity + an Equality clause) → rejected as Entity.

## Boundary
This card + schema validate **shape**, never **meaning**. A criterion that could only be checked by
running derivation (satisfiability, semantic purity) is a DEFINE-FALSIFIED boundary, not a public check —
it belongs to the private engine, and is never built here.
