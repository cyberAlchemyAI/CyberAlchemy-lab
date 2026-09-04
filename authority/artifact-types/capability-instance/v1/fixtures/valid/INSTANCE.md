<!-- GENERATED FILE: edit instance.json and rerun generator.py. -->

# Capability Instance: fixture.capability-instance.example

> Generated from `instance.json`; this view is not canonical.

- Identity: `fixture.capability-instance.example`
- Version: `1.0.0-fixture`
- Status: `candidate-unadmitted`
- Artifact type: `cal.artifact-type.capability-instance/v1`
- Semantic kind: `capability-instance`
- Authority effect: `none`

## Capability Version Ref

fixture.product-capability.example/v1

## Coordination Context Ref

fixture.coordination.example/v1

## Bounded Context Refs

- fixture.context.example/v1

## Parent Authority Claim Ref

fixture:authority-claim:parent

## Instance Authority Claim Ref

fixture:authority-claim:instance

## Inherited Contract Ref

fixture:contract:inherited

## Extension Scope

```json
{
  "exclusions": [
    "No parent mutation."
  ],
  "statement": "Fixture-only local specialization."
}
```

## Adoption Decision Ref

fixture:decision:adoption

## Construction Binding Ref

fixture:construction-binding

## Conformance Refs

None declared.

## Drift Route

fixture:route:instance-drift

## Recomposition Route

fixture:route:recomposition

## Recursion Stop

```json
{
  "budget": 1,
  "condition": "Stop after one fixture level.",
  "kind": "budget"
}
```

## Terminal Handoff Ref

fixture:handoff:terminal

## Owner Ref

fixture:role:capability-instance-owner

## Evidence

- fixture:evidence:instance

## Residue

- fixture:residue:parent-capability-unadmitted

## Claim ceiling

Fixture only; it does not instantiate, adopt, bind, or conform a Product Capability.
