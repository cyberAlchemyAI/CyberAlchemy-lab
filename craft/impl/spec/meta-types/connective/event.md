---
artifact_id: domainspec-v2-metatype-event
artifact_type: companion-doc
companion_to: event.schema.yml
intent: Human companion to the Event meta-type machine criterion.
owner: definitions-governance
lifecycle_status: candidate
constitution_selectors: [schema-constitution, meta-type-formalization]
validation_profile: meta-type-card
boundary: PUBLIC shape criterion; the engine src/rules δ-derivation is never referenced (moat).
---

# Event — meta-type card (Connective)

**Companion to** [`event.schema.yml`](./event.schema.yml). Prose is non-normative.

## Formal criterion
A concept declared **Event** is well-formed IFF its `Attribute | Value` table declares
`temporal = past` (an announcement of a change that already happened).

## Distinguisher vs Operation
An Event announces something that already happened (`temporal=past`); an Operation performs a change now.

## Edge participation (DS-D8 slice)
Deferred to MT3 edges / batch-1 R3.

## Fixtures
- positive: [`spec/__fixtures__/mt/event-ok.md`](../../__fixtures__/mt/event-ok.md)
- negative: [`spec/__fixtures__/mt/event-bad.md`](../../__fixtures__/mt/event-bad.md) — present-tense → rejected.

## Boundary
Shape only; the declared tense is checked, not the payload semantics (moat).
