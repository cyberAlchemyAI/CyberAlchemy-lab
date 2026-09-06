---
artifact_id: domainspec-v2-metatype-value-object
artifact_type: companion-doc
companion_to: value-object.schema.yml
intent: Human companion to the Value Object meta-type machine criterion.
owner: definitions-governance
lifecycle_status: candidate
constitution_selectors: [schema-constitution, meta-type-formalization]
validation_profile: meta-type-card
boundary: PUBLIC shape criterion; the engine src/rules δ-derivation is never referenced (moat).
---

# Value Object — meta-type card (Structural)

**Companion to** [`value-object.schema.yml`](./value-object.schema.yml). Prose is non-normative.

## Formal criterion
A concept declared **Value Object** is well-formed IFF:

1. **no identity** — no field row is flagged `Identity` (a VO is equal-by-fields, not by ID).
2. **typedness** — every field row declares a non-empty `Type`.
3. **equality** — the concept section declares an **Equality** clause.

## Distinguisher vs Entity
An Entity **has** an identity field; a Value Object has **none** and declares equality. An identity-bearing
concept declared Value Object is a mis-typed Entity → **rejected as Value Object**.

## Edge participation (DS-D8 slice)
- SOURCE of: none
- TARGET of: `contains`

## Fixtures
- positive: [`spec/__fixtures__/mt/value-object-ok.md`](../../__fixtures__/mt/value-object-ok.md)
- negative: [`spec/__fixtures__/mt/value-object-bad.md`](../../__fixtures__/mt/value-object-bad.md) — identity-bearing → rejected.

## Boundary
Shape only; equality is checked as a **declared clause**, never by proving semantic equality (moat).
