---
artifact_id: domainspec-v2-metatype-workflow
artifact_type: companion-doc
companion_to: workflow.schema.yml
intent: Human companion to the Workflow meta-type machine criterion.
owner: definitions-governance
lifecycle_status: candidate
constitution_selectors: [schema-constitution, meta-type-formalization]
validation_profile: meta-type-card
boundary: PUBLIC shape criterion; the engine src/rules δ-derivation is never referenced (moat).
---

# Workflow — meta-type card (Behavioral)

**Companion to** [`workflow.schema.yml`](./workflow.schema.yml). Prose is non-normative.

## Formal criterion
A concept declared **Workflow** is well-formed IFF its `Attribute | Value` table declares
`scope` as exactly one of `intra-feature` or `cross-feature`.

## Boundary vs Operation
A Workflow coordinates multiple ordered operations; an Operation is one state-changing action.

## Edge participation (DS-D8 slice)
- SOURCE of: `orchestrates`
- TARGET of: none

## Fixtures
- positive, intra-feature: [`spec/__fixtures__/mt/workflow-ok.md`](../../__fixtures__/mt/workflow-ok.md)
- positive, cross-feature: [`spec/__fixtures__/mt/workflow-cross-feature-ok.md`](../../__fixtures__/mt/workflow-cross-feature-ok.md)
- negative: [`spec/__fixtures__/mt/workflow-bad.md`](../../__fixtures__/mt/workflow-bad.md) — unknown scope → rejected.

## Boundary
Shape only: exact membership of the declared `scope` is checked, not the actual reachability of orchestrated operations (moat).
