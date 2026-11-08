---
artifact_id: domainspec-v2-metatype-interface
artifact_type: companion-doc
companion_to: interface.schema.yml
intent: Human companion to the Interface meta-type machine criterion.
owner: definitions-governance
lifecycle_status: candidate
constitution_selectors: [schema-constitution, meta-type-formalization]
validation_profile: meta-type-card
boundary: PUBLIC shape criterion; the engine src/rules δ-derivation is never referenced (moat).
---

# Interface — meta-type card (Connective)

**Companion to** [`interface.schema.yml`](./interface.schema.yml). Prose is non-normative.

## Formal criterion
A concept declared **Interface** is well-formed IFF its `Attribute | Value` table declares
`interface_kind` (an exposed boundary — `external` or `internal`).

## Distinguisher vs Mapping
An Interface is an exposed API boundary; a Mapping is a field-by-field transform.

## Edge participation (DS-D8 slice)
Deferred to MT3 edges / batch-1 R3 (the root relationship authority `definitions/relationships/relationships.yml` is the source of truth).

## Fixtures
- positive: [`spec/__fixtures__/mt/interface-ok.md`](../../__fixtures__/mt/interface-ok.md)
- negative: [`spec/__fixtures__/mt/interface-bad.md`](../../__fixtures__/mt/interface-bad.md) — no `interface_kind` → rejected.

## Boundary
Shape only; the declared boundary kind is checked, not the request/response semantics (moat).
