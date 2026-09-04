<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Context Migration Manifest

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.context-migration-manifest`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-context-migration`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Context Migration Manifest is an immutable candidate plan that binds exact source repository selectors and digests to explicit artifact dispositions, proposed destination identities and paths, dependency order, preimages, expected postimages, validation obligations, owner gates, rollback boundaries, exclusions, and unresolved residue for one bounded migration scope.

```text
ContextMigrationManifest = (id, source_repository, source_selections, dispositions, destination_candidates, dependency_order, preimages, expected_postimages, validation_obligations, owner_gates, rollback_boundary, exclusions, residue, lifecycle); ManifestExists does not imply SourceAdmitted or MigrationAuthorized or Migrated.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| destination_candidates | Proposed identities and paths that have no authority until separately selected. |

### Boundary conditions

- Every source is selector- and digest-bound.
- Every destination has explicit identity and path.
- Rollback and exclusions are declared before execution.

### Testable conditions

- No source or destination is inferred from a directory glob.
- Dependency order and validation obligations cover every selected item.
- The manifest explicitly denies execution authority.

## Plain-language voice

The exact reviewable plan for what context material might move, where it would go, what would change, and how to stop or reverse safely.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

The future Ontology Lifecycle manifest will bind exact bytes from the current root vertical to candidate context destinations without broad copying or implicit admission.

### Examples

- A manifest can propose moving one schema while explicitly retaining its source until lineage and rollback checks pass.

## Applicability

Immutable planning candidates for one exact context migration epoch.

### Exclusions

- Source admission, execution authorization, file-copy commands, and migration receipts.

## Boundaries

- A Context Migration Manifest is not source admission, execution authorization, a file-copy command, lineage proof, migration receipt, context admission, publication, or deployment.
- Manifest existence never permits deletion of predecessor bytes.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| CAL-SOURCE-ADMISSION-CTX00-CAV2-D29 | CAV2-D29 | `f47b8ae8dcbfcc97d624871a5aab03cbf3ffdea2b341046a0bba1edbb59740be` | `admitted` |

## Primary consumers

- authority/lineage
- contexts
- docs/migrations

## Lookup and drift

- Index: `candidate:authority/definitions/registry.json` / `cal.definition.context-migration-manifest`
- Drift owner: `role:definition-owner`
- Audit: `drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | cal.definition.context-migration-manifest@1.0.0-candidate.1 | role:definition-owner | role:definition-owner |

## Evidence

- CAL-DECISION-0016-ONTOLOGY-LIFECYCLE-CONTEXT-PLACEMENT
- CAL-DECISION-0017-CTX00-SOURCE-ADMISSION

## Residue

- context-migration-manifest-artifact-type-required
- migration-owner-binding-required

## Claim ceiling

This candidate defines Context Migration Manifest meaning only; it is not a migration plan for any selected bytes and grants no migration authority.
