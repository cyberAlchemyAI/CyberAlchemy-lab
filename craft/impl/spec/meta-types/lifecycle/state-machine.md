---
artifact_id: domainspec-v2-metatype-state-machine
artifact_type: companion-doc
companion_to: state-machine.schema.yml
intent: Human companion to the State Machine meta-type machine criterion.
owner: definitions-governance
lifecycle_status: candidate
constitution_selectors: [schema-constitution, meta-type-formalization]
validation_profile: meta-type-card
boundary: PUBLIC shape criterion; the engine src/rules δ-derivation is never referenced (moat).
---

# State Machine — meta-type card (Lifecycle)

**Companion to** [`state-machine.schema.yml`](./state-machine.schema.yml). Prose is non-normative.

## Formal criterion
A concept declared **State Machine** is well-formed IFF its `Attribute | Value` table declares
`has_transitions = yes` (states connected by valid transitions over time).

## Distinguisher vs Enum
A State Machine has transitions between states (`has_transitions=yes`); an Enum is a flat value set.

## Edge participation (DS-D8 slice)
Deferred to MT3 edges / batch-1 R3.

## Fixtures
- positive: [`spec/__fixtures__/mt/state-machine-ok.md`](../../__fixtures__/mt/state-machine-ok.md)
- negative: [`spec/__fixtures__/mt/state-machine-bad.md`](../../__fixtures__/mt/state-machine-bad.md) — no transitions → rejected.

## Boundary
Shape only; the declared transition presence is checked, not transition reachability/guards (moat).
