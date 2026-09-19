<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Decision Fixture

- Identity: `CAL-DECISION-SIMULATION-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

### Actor

```json
{
  "principal_ref": "simulation:reviewer",
  "role_ref": "role:product-review-owner"
}
```

- **Artifact Type Ref**: `cal.artifact-type.decision/v1`
- **Challenge Route**: `role:decision-owner`
- **Claim Ceiling**: `Simulation fixture only; not the user's approval and not authorization to adopt the Constitution.`
- **Declared Effect**: `record-review-intent`
### Proposal

```json
{
  "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0008-decision-carrier/examples/proposal.json",
  "sha256": "0d714fcdd9e30428e980cce88cb0f63ac12fec80834765ffd3153e778736af45"
}
```

- **Proposal Id**: `CAL-DECISION-DEMO-PROPOSAL-001`
- **Provenance Kind**: `simulation`
- **Rationale**: `Demonstrate exact choice binding without asserting a real owner decision.`
- **Recorded At**: `2026-09-07T00:00:00Z`
- **Schema Version**: `cyberalchemy-lab-decision/v1`
- **Scope Ref**: `scope:constitution-candidate-review`
- **Selected Option Id**: `review`
### Source Direction

```json
{
  "canonical": "decision.json",
  "human_projection": "DECISION.md",
  "projection_policy": "generated-only"
}
```

### Statement

```json
{
  "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0008-decision-carrier/examples/statement.json",
  "sha256": "13ea7952791202dda940fb1da8d6e5516e1fd216310875b51824de1b59396f35"
}
```

### Subject

```json
{
  "material_manifest": {
    "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0007-constitution-carrier/manifest.json",
    "sha256": "5fe036f364fcd10fc23de7451e6dd9243a87520469326120ad7eede72bdff922"
  },
  "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0007-constitution-carrier/candidate.json",
  "sha256": "47f300de3bcce5731956cedd088a6735624afba73e2905d300ad3d3b31c141b4",
  "subject_ref": "candidate:constitution-carrier-0007"
}
```

- **Supersession Policy**: `new-record-required-preserve-prior-bytes`

## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
