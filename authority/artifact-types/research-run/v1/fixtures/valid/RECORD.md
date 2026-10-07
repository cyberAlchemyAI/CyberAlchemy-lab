<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Research Run Fixture

- Identity: `research-run:research-inquiry-v1-review:2026-10-05`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Challenge Route**: `route:artifact-type-migration-research-challenge`
- **Claim Ceiling**: `Candidate Research Run fixture only. It records one completed repository review execution and its evidence boundary; it does not establish a Finding, admission recommendation, migration completion, Definition, proof, or runtime authority.`
### Counterevidence Refs

```json
[
  "evidence:research-inquiry-original-minimal-contract"
]
```

- **Evidence Set Ref**: `evidence-set:research-inquiry-v1-review`
### Goal Refs

```json
[
  "goal:complete-governed-artifact-type-migration"
]
```

- **Inquiry Ref**: `research-inquiry:artifact-type-migration-review`
- **Inquiry Version Ref**: `research-inquiry:artifact-type-migration-review@1.0.0-candidate.1`
### Inspected Sources

```json
[
  {
    "observed_sha256": "0a5445e954049cdd5abcee276fef085f97e409ebd325e571c489c4db92efafe7",
    "selector": "whole-json",
    "source_ref": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/research-inquiry/v1/definition.json"
  },
  {
    "observed_sha256": "a30eb33d70128b5aa85fd96a2a160564ca5e257e5903eb22157b70e2b08410f7",
    "selector": "whole-json",
    "source_ref": "authority/artifact-types/research-inquiry/v1/artifact.json"
  }
]
```

- **Kind**: `research-run`
### Limitations

```json
[
  "The run inspected repository evidence only",
  "The run did not validate external systems or execute a consumer runtime"
]
```

### Method Performed

```json
{
  "deviation_refs": [],
  "method_ref": "method:definition-bound-artifact-type-review/v1",
  "procedure_summary": "Compare the materialized Artifact Type with its admitted Definition, identify missing semantic fields, revise the closed schema and fixture, and rerun deterministic package and batch validation."
}
```

### Observation Refs

```json
[
  "observation:research-inquiry-definition-gap-review",
  "observation:research-inquiry-package-validation"
]
```

- **Owner Ref**: `role:migration-research-owner`
- **Owner Route**: `role:migration-research-owner`
### Period

```json
{
  "end": "2026-10-05T13:00:00Z",
  "start": "2026-10-05T12:00:00Z"
}
```

- **Project Ref**: `CA2-PROJECT-CYBERALCHEMY-V2-MIGRATION`
- **Receipt Ref**: `receipt:research-inquiry-v1-review`
- **Run State**: `completed`
- **Scope Ref**: `scope:artifact-type-migration-review`
- **Stop Reason**: `None`

## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
