<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Context Migration Manifest successor fixture

- Identity: `fixture.migration.example`
- Schema version: `cyberalchemy-lab-context-migration-manifest/v2`

## Canonical fixture

```json
{
  "authority_effect": "none",
  "claim_ceiling": "Fixture only; the manifest does not admit sources or authorize migration execution.",
  "classification": {
    "artifact_type_ref": "cal.artifact-type.context-migration-manifest/v1",
    "authority_kind": "none",
    "lifecycle_posture_ref": "candidate:cal.lifecycle.artifact/v1:candidate-authored",
    "semantic_kind": "context-migration-manifest"
  },
  "dependency_order": [
    "fixture:source:a"
  ],
  "destination_candidates": [
    {
      "artifact_id": "fixture:destination:a",
      "artifact_type_ref": "fixture:artifact-type",
      "path": "fixtures/destination/a"
    }
  ],
  "dispositions": [
    {
      "destination_ref": "fixture:destination:a",
      "disposition": "preserve",
      "source_ref": "fixture:source:a"
    }
  ],
  "evidence_refs": [
    "fixture:evidence:migration"
  ],
  "exclusions": [
    "No execution, deletion, publication, or deployment."
  ],
  "execution_authority": false,
  "expected_postimages": [
    {
      "expected_condition": "Candidate bytes exist; source bytes remain preserved.",
      "path": "fixtures/destination/a"
    }
  ],
  "immutable": true,
  "migration_manifest_id": "fixture.migration.example",
  "owner_gates": [
    {
      "effect": "Separate execution selection only.",
      "role_ref": "fixture:role:migration-owner"
    }
  ],
  "owner_ref": "fixture:role:migration-owner",
  "preimages": [
    {
      "path": "fixtures/source/a",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
    }
  ],
  "residue_refs": [
    "fixture:residue:execution-not-authorized"
  ],
  "rollback_boundary": "Fixture source is never deleted.",
  "schema_version": "cyberalchemy-lab-context-migration-manifest/v2",
  "source_direction": {
    "canonical": "migration.json",
    "generator_ref": "cal.generator.ctx01.context-migration-manifest/v1",
    "generator_sha256": "cb626a8fb4600ff1ded506abde9518378b140aa2bf4c0bf087193a85629223b5",
    "human_projection": "MIGRATION.md",
    "projection_policy": "generated-only"
  },
  "source_repository_ref": "fixture:repository:source",
  "source_selections": [
    {
      "selector": "whole-file",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
      "source_ref": "fixture:source:a"
    }
  ],
  "status": "candidate-unadmitted",
  "validation_obligations": [
    "Exact preimage and postimage checks pass."
  ],
  "version": "1.0.0-fixture"
}
```

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, migration, deletion, or runtime effect.
