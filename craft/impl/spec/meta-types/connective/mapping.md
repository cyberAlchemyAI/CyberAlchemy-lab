---
artifact_id: domainspec-v2-metatype-mapping
artifact_type: companion-doc
companion_to: mapping.schema.yml
intent: Human companion to the Mapping meta-type machine criterion.
owner: definitions-governance
lifecycle_status: candidate
constitution_selectors: [schema-constitution, meta-type-formalization]
validation_profile: meta-type-card
boundary: PUBLIC shape criterion; the engine src/rules δ-derivation is never referenced (moat).
---

# Mapping — meta-type card (Connective)

**Companion to** [`mapping.schema.yml`](./mapping.schema.yml). Prose is non-normative.

## Formal criterion
A concept declared **Mapping** is well-formed IFF its `Attribute | Value` table declares
`direction` (a field-by-field transform between two shapes — `inbound` / `outbound` / `bidirectional`).

## Distinguisher vs Interface
A Mapping transforms fields between two shapes; an Interface is an exposed boundary.

## Edge participation (DS-D8 slice)
Deferred to MT3 edges / batch-1 R3.

## Fixtures
- positive: [`spec/__fixtures__/mt/mapping-ok.md`](../../__fixtures__/mt/mapping-ok.md)
- negative: [`spec/__fixtures__/mt/mapping-bad.md`](../../__fixtures__/mt/mapping-bad.md) — no `direction` → rejected.

## Boundary
Shape only; the declared direction is checked, not the transform's field-level correctness (moat).
