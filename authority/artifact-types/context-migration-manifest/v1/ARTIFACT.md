<!-- GENERATED FILE: edit artifact.json and rerun generator.py. -->

# Context Migration Manifest artifact type v1

> Generated from `artifact.json`; this view is not canonical.

- Artifact type: `cal.artifact-type.context-migration-manifest/v1`
- Candidate version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Definition: `cal.definition.context-migration-manifest`

## Representation contract

- Canonical machine file: `migration.json`
- Generated human file: `MIGRATION.md`
- Stable identity field: `migration_manifest_id`
- Schema: `cal.schema.context-migration-manifest/v1`

## Distinct validation purpose

Proves one immutable selector-bound migration plan with complete dispositions, ordering, pre/postconditions, gates, rollback, exclusions, and no execution authority.

## Orthogonality rules

| Rule | Mode | Requirement |
| --- | --- | --- |
| `CTX01-MM-01` | `deterministic` | Manifest existence never grants source admission or migration execution authority. |
| `CTX01-MM-02` | `deterministic` | Every selected source has exactly one explicit disposition and no source is inferred by glob. |
| `CTX01-MM-03` | `hybrid` | Rollback boundaries and exclusions precede execution and preserve predecessor bytes. |

## Four facets

### Classification

Plan identity, source admission, owner decision, execution authority, evidence, and lifecycle remain separate.

### Schema

The closed schema requires exact selectors, dispositions, destinations, order, preimages, expected postimages, checks, gates, rollback, and exclusions.

### Human Continuation

MIGRATION.md is generated and exposes what remains gated before any effect.

### Machine Checkable

Schema, source-disposition closure, no-execution constant, dependency, fixture, and projection checks are executable.

## Remaining residue

- `CTX01-MM-R1` — No artifact-type-owner admission decision binds this candidate. Consequence: No migration manifest may rely on this candidate as an admitted type.
- `CTX01-MM-R2` — No migration owner role or exact migration source scope is bound. Consequence: No real migration manifest can be selected or executed.

## Claim ceiling

This package is a Context Migration Manifest/v1 artifact-type candidate. PASS neither admits the type nor authorizes any migration or deletion.
