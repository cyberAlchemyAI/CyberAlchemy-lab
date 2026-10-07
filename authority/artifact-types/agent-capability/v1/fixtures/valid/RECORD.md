<!-- GENERATED FILE: canonical data is record.json. -->

# Agent Capability fixture

- Identity: `agent-capability:example-001`
- Kind: `agent-capability`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "capability_statement": "Author and validate candidate governed artifacts",
  "evidence_contract_refs": [
    "contract:validation-receipt"
  ],
  "failure_mode_refs": [
    "failure-mode:unsupported-authority-claim"
  ],
  "implementation_refs": [
    "implementation:codex-agent"
  ],
  "input_contract_refs": [
    "contract:exact-source-input"
  ],
  "output_contract_refs": [
    "contract:candidate-artifact-output"
  ]
}
```

## Declared relation roles

- `target` on `relation.affects` with `failure-occurrence` `failure-occurrence:example-001`

## Claim ceiling

Realistic Agent Capability example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
