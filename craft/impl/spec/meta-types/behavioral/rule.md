---
artifact_id: domainspec-v2-metatype-rule
artifact_type: companion-doc
companion_to: rule.schema.yml
intent: Human companion to the Rule meta-type machine criterion.
owner: definitions-governance
lifecycle_status: candidate
constitution_selectors: [schema-constitution, meta-type-formalization]
validation_profile: meta-type-card
boundary: PUBLIC shape criterion; the engine src/rules δ-derivation is never referenced (moat).
---

# Rule — meta-type card (Behavioral)

**Companion to** [`rule.schema.yml`](./rule.schema.yml). Prose is non-normative.

## Formal criterion
A concept declared **Rule** is well-formed IFF its `Attribute | Value` table declares
`formal_return_type = boolean` (a guard that blocks/allows an operation).

The boolean-ness is the **declared** return type, **not** inferred by parsing the Formal cell — that
semantic check is the engine moat (a DEFINE-FALSIFIED boundary for the public validator).

## Distinguisher vs Policy
A Rule returns a boolean (blocks/allows); a Policy selects a strategy.

## Edge participation (DS-D8 slice)
- SOURCE of: `enforces` (never a TARGET of `applies` — that is a Policy inbound; per `domainspec-v2-D3`)

## Fixtures
- positive: [`spec/__fixtures__/mt/rule-ok.md`](../../__fixtures__/mt/rule-ok.md)
- negative: [`spec/__fixtures__/mt/rule-bad.md`](../../__fixtures__/mt/rule-bad.md) — strategy → rejected.

## Boundary
Shape only: `formal_return_type=boolean` is a declaration, never a satisfiability/typing proof (moat).
