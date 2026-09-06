---
artifact_id: domainspec-v2-metatype-calculation
artifact_type: companion-doc
companion_to: calculation.schema.yml
intent: Human companion to the Calculation meta-type machine criterion.
owner: definitions-governance
lifecycle_status: candidate
constitution_selectors: [schema-constitution, meta-type-formalization]
validation_profile: meta-type-card
boundary: PUBLIC shape criterion; the engine src/rules δ-derivation is never referenced (moat).
---

# Calculation — meta-type card (Behavioral)

**Companion to** [`calculation.schema.yml`](./calculation.schema.yml). Prose is non-normative.

## Formal criterion
A concept declared **Calculation** is well-formed IFF its `Attribute | Value` table declares
`formal_return_type = value` (a pure function deriving a value).

## Distinguisher vs Rule
A Calculation returns a value (`formal_return_type=value`); a Rule returns a boolean.

## Edge participation (DS-D8 slice)
- SOURCE of: `calculates`
- TARGET of: `applies`

A Calculation consumes explicit values. Entity input provenance is not inferred as a `reads` edge; that would
couple a pure function to repository access rather than model its declared inputs.

## Fixtures
- positive: [`spec/__fixtures__/mt/calculation-ok.md`](../../__fixtures__/mt/calculation-ok.md)
- negative: [`spec/__fixtures__/mt/calculation-bad.md`](../../__fixtures__/mt/calculation-bad.md) — boolean → rejected.

## Boundary
The discriminator is the **declared** `formal_return_type` — shape only; the formula is never evaluated (moat).
