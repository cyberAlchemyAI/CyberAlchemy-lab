---
artifact_id: domainspec-v2-metatype-policy
artifact_type: companion-doc
companion_to: policy.schema.yml
intent: Human companion to the Policy meta-type machine criterion.
owner: definitions-governance
lifecycle_status: candidate
constitution_selectors: [schema-constitution, meta-type-formalization]
validation_profile: meta-type-card
boundary: PUBLIC shape criterion; the engine src/rules δ-derivation is never referenced (moat).
---

# Policy — meta-type card (Behavioral)

**Companion to** [`policy.schema.yml`](./policy.schema.yml). Prose is non-normative.

## Formal criterion
A concept declared **Policy** is well-formed IFF its `Attribute | Value` table declares
`formal_return_type = strategy` (it selects how something is handled, not whether it is allowed).

## Distinguisher vs Rule
A Policy selects a strategy; a Rule returns a boolean (blocks/allows).

## Edge participation (DS-D8 slice)
- SOURCE of: `applies`

## Fixtures
- positive: [`spec/__fixtures__/mt/policy-ok.md`](../../__fixtures__/mt/policy-ok.md)
- negative: [`spec/__fixtures__/mt/policy-bad.md`](../../__fixtures__/mt/policy-bad.md) — boolean → rejected.

## Boundary
Shape only: the strategy declaration is checked, never the decision logic's semantics (moat).
