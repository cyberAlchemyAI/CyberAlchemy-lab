<!-- GENERATED FILE: edit artifact.json and run generator.py. -->

# Artifact Type Request Artifact Type v1

> Generated from `artifact.json`; this view is explanatory and not canonical.

- Type: `cal.artifact-type.artifact-type-request/v1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Canonical instance: `request.json`
- Human projection: `REQUEST.md`

## Semantic bindings

- `cal.definition.artifact-type@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0007-cml07-semantic-closure/definitions/artifact-type/v1/definition.json`
- `cal.definition.artifact-type-request@1.0.0-candidate.2` — `candidate-unadmitted` — `authority/definitions/candidates/0010-artifact-surface-foundation-revision/definitions/artifact-type-request/v1/definition.json`
- `cal.definition.artifact-type-resolution@1.0.0-candidate.2` — `candidate-unadmitted` — `authority/definitions/candidates/0010-artifact-surface-foundation-revision/definitions/artifact-type-resolution/v1/definition.json`

## Distinct validation purpose

Proves an unmatched artifact-kind request is justified by zero admitted matches, preserves candidate-only posture, and cannot substitute for the requested subject or self-register a type.

## Orthogonality rules

- **ASF-ATQ-01**: Request identity, requested semantic kind, future Artifact Type, and future subject remain distinct.
- **ASF-ATQ-02**: A request is eligible only after deterministic resolution returns zero admitted matches.
- **ASF-ATQ-03**: The request always has no authority effect and cannot satisfy subject dependencies.

## Four facets

- **Classification**: The request is an intake Artifact Type candidate, not a generic artifact fallback.
- **Human Continuation**: REQUEST.md is generated from request.json.
- **Machine Checkable**: Zero-match evidence, compatibility analysis, expiry, hostile substitution, and projection parity are executable.
- **Schema**: schema.json rejects matches, authority effects, subject substitution, and undeclared fields.

## Typed residue

- `ASF-ATQ-R1` (role:definition-owner): The request and resolution Definitions remain candidate-unadmitted. Consequence: The type cannot be admitted.
- `ASF-ATQ-R2` (role:artifact-type-owner): No Artifact Type Request instance is created for existing unresolved Product or implementation surfaces. Consequence: Current unresolved surfaces remain audit findings only.

## Claim ceiling

Candidate intake contract only. PASS does not authorize a new subject artifact, type admission, or migration.
