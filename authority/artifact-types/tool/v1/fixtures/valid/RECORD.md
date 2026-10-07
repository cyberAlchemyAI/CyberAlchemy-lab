<!-- GENERATED FILE: canonical data is record.json. -->

# Tool fixture

- Identity: `tool:example-001`
- Kind: `tool`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "availability_posture": "available",
  "evidence_route_ref": "receipt:tool-call",
  "failure_boundary_refs": [
    "failure-mode:patch-context-mismatch"
  ],
  "input_contract_ref": "contract:unified-diff",
  "interface_version": "apply-patch/v1",
  "output_contract_ref": "contract:patch-receipt",
  "tool_name": "repository-patch"
}
```

## Declared relation roles

- `target` on `relation.challenges` with `challenge-event` `challenge-event:example-001`

## Claim ceiling

Realistic Tool example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
