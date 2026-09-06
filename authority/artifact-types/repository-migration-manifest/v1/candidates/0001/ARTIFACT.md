<!-- GENERATED FILE: edit artifact.json and run generator.py. -->

# Repository Migration Manifest Artifact Type v1

> Generated from `artifact.json`; this view is explanatory and not canonical.

- Type: `cal.artifact-type.repository-migration-manifest/v1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Canonical instance: `migration.json`
- Human projection: `MIGRATION.md`

## Semantic bindings

- `cal.definition.artifact-type@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0007-cml07-semantic-closure/definitions/artifact-type/v1/definition.json`
- `cal.definition.repository-migration-manifest@1.0.0-candidate.1` — `candidate-unadmitted` — `authority/definitions/candidates/0011-repository-migration-manifest/definitions/repository-migration-manifest/v1/definition.json`
- `cal.definition.validation@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0007-cml07-semantic-closure/definitions/validation/v1/definition.json`

## Distinct validation purpose

Proves complete repository-level byte accounting and one collision-free additive copy postimage without conflating copy selection, semantic admission, or execution authority.

## Orthogonality rules

- **RMM-01**: Copy selection, semantic admission, and execution authorization remain separate.
- **RMM-02**: Every observed source entry is selected or explicitly excluded exactly once.
- **RMM-03**: Divergent target collisions block; overwrite is never inferred.
- **RMM-04**: Rollback description grants no rollback authority.

## Four facets

- **Classification**: Repository migration is a source-to-target byte-envelope artifact, not a bounded-context succession.
- **Human Continuation**: MIGRATION.md is generated from migration.json.
- **Machine Checkable**: Schema, digest currency, total accounting, unique mapping, dry-run, rehearsal, target baseline, and rollback closure are executable.
- **Schema**: Closed schema binds repositories, inventory, mapping, exclusions, allowlist, postimage, rollback, checks, and no-effect constants.

## Typed residue

- `RMM-R1` (role:definition-owner and role:artifact-type-owner): Definition and Artifact Type owner admissions. Consequence: The migration instance remains candidate-only.
- `RMM-R2` (role:repository-migration-owner): Exact product approval and execution authorization. Consequence: No target mutation is permitted.

## Claim ceiling

PASS proves this candidate contract and fixtures only; it does not admit the type, approve or execute a migration, delete, overwrite, commit, push, publish, release, or deploy.
