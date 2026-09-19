<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Invariant Fixture

- Identity: `CAL-IMPORT-COUNTS-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Artifact Type Ref**: `cal.artifact-type.invariant/v1`
### Checks

```json
[
  {
    "check_id": "nodes",
    "expected": 815,
    "field": "nodes",
    "operator": "equals"
  },
  {
    "check_id": "relations",
    "expected": 1210,
    "field": "relations",
    "operator": "equals"
  },
  {
    "check_id": "documents",
    "expected": 422,
    "field": "documents",
    "operator": "equals"
  }
]
```

- **Claim Ceiling**: `Initial imported-corpus counts only. Matching counts do not prove record content or authorized ongoing mutations correct.`
- **Evaluation Profile**: `candidate:integer-observation-comparison/v1`
### Grounding Refs

```json
[
  "semantic.claim-support-compatibility-invariant"
]
```

- **Must Hold**: `The initial imported store must preserve the manifest's node, relation and supporting-document counts.`
- **Owner Ref**: `role:repository-migration-owner`
- **Schema Version**: `cyberalchemy-lab-invariant/v1`
- **Scope Ref**: `scope:v4-sibling-import-genesis`
### Source Direction

```json
{
  "canonical": "invariant.json",
  "human_projection": "INVARIANT.md",
  "projection_policy": "generated-only"
}
```

- **Subject Kind**: `system-or-artifact`
- **Subject Ref**: `runtime:v4-sibling-import`
- **Violation Meaning**: `A count differs from the selected import corpus; investigate possible omitted or extra records.`

## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
