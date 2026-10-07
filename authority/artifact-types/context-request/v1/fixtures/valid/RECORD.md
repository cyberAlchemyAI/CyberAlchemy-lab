<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Context Request Fixture

- Identity: `context-request:remaining-18-review`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

### Budget

```json
{
  "max_bytes": 2000000,
  "max_items": 250
}
```

- **Challenge Route**: `route:context-request-challenge`
- **Claim Ceiling**: `This request authorizes resolution only; it does not mutate Context, grant source authority, or admit Artifact Types.`
### Consumer Refs

```json
[
  "consumer:artifact-type-review"
]
```

- **Context Ref**: `context:lab-artifact-type-admission`
- **Context Version Ref**: `context:lab-artifact-type-admission@sha256:79e1`
### Exclusions

```json
[
  "Secrets",
  "Live service state",
  "Unrelated dirty work"
]
```

- **Freshness Requirement**: `All selected files must match their declared SHA-256 at resolution time.`
### Intended Uses

```json
[
  "Review the remaining 18 Artifact Type candidates as one batch"
]
```

- **Kind**: `context-request`
### Output Constraints

```json
[
  "One complete model",
  "One exact example per type",
  "One admission decision"
]
```

- **Owner Ref**: `role:artifact-type-owner`
- **Owner Route**: `role:context-request-owner`
- **Requested At**: `2026-10-05T15:00:00Z`
- **Scope Ref**: `scope:cyberalchemy-lab-model-review`
### Selectors

```json
[
  "Admitted Definition bound to each target",
  "Candidate artifact schema and fixture",
  "Existing admitted Artifact Type carriers"
]
```


## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
