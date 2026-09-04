<!-- GENERATED FILE: edit migration.json and rerun generator.py. -->

# Context Migration Manifest: fixture.migration.example

> Generated from `migration.json`; this view is not canonical.

- Identity: `fixture.migration.example`
- Version: `1.0.0-fixture`
- Status: `candidate-unadmitted`
- Artifact type: `cal.artifact-type.context-migration-manifest/v1`
- Semantic kind: `context-migration-manifest`
- Authority effect: `none`

## Source Repository Ref

fixture:repository:source

## Source Selections

```json
[
  {
    "selector": "whole-file",
    "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
    "source_ref": "fixture:source:a"
  }
]
```

## Dispositions

```json
[
  {
    "destination_ref": "fixture:destination:a",
    "disposition": "preserve",
    "source_ref": "fixture:source:a"
  }
]
```

## Destination Candidates

```json
[
  {
    "artifact_id": "fixture:destination:a",
    "artifact_type_ref": "fixture:artifact-type",
    "path": "fixtures/destination/a"
  }
]
```

## Dependency Order

- fixture:source:a

## Preimages

```json
[
  {
    "path": "fixtures/source/a",
    "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
  }
]
```

## Expected Postimages

```json
[
  {
    "expected_condition": "Candidate bytes exist; source bytes remain preserved.",
    "path": "fixtures/destination/a"
  }
]
```

## Validation Obligations

- Exact preimage and postimage checks pass.

## Owner Gates

```json
[
  {
    "effect": "Separate execution selection only.",
    "role_ref": "fixture:role:migration-owner"
  }
]
```

## Rollback Boundary

Fixture source is never deleted.

## Exclusions

- No execution, deletion, publication, or deployment.

## Owner Ref

fixture:role:migration-owner

## Immutable

`true`

## Execution Authority

`false`

## Evidence

- fixture:evidence:migration

## Residue

- fixture:residue:execution-not-authorized

## Claim ceiling

Fixture only; the manifest does not admit sources or authorize migration execution.
