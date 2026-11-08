---
artifact_id: domainspec-v2-metatype-enum
artifact_type: companion-doc
companion_to: enum.schema.yml
intent: Human companion to the Enum meta-type machine criterion.
owner: definitions-governance
lifecycle_status: candidate
constitution_selectors: [schema-constitution, meta-type-formalization]
validation_profile: meta-type-card
boundary: PUBLIC shape criterion; the engine src/rules δ-derivation is never referenced (moat).
---

# Enum — meta-type card (Structural)

**Companion to** [`enum.schema.yml`](./enum.schema.yml). Prose is non-normative.

## Formal criterion
A concept declared **Enum** is well-formed IFF it provides a **value table** — a table with a `Value`
column and ≥1 row (a finite, named value set). It has no typed field table and no identity.

## Distinguisher vs Entity / Value Object
An Enum is a **finite value list** (`Value | Description`), not a typed field table. A concept declared
Enum but modeled as a field table (no `Value` column) is **rejected as Enum**.

## Edge participation (DS-D8 slice)
- TARGET of: `contains` (a field's type may be an enum)

## Fixtures
- positive: [`spec/__fixtures__/mt/enum-ok.md`](../../__fixtures__/mt/enum-ok.md)
- negative: [`spec/__fixtures__/mt/enum-bad.md`](../../__fixtures__/mt/enum-bad.md) — field table, no `Value` column → rejected.

## Boundary
Shape only (the value set is a declared table, not a proof of exhaustiveness).
