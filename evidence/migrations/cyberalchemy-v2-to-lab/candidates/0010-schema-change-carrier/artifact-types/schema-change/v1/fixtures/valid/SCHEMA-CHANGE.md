<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Schema Change Fixture

- Identity: `EXAMPLE-REQUIRE-REVISION-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Artifact Type Ref**: `cal.artifact-type.schema-change/v1`
- **Claim Ceiling**: `Exact versions and supplied regression witnesses only. No universal compatibility, migration execution or adoption.`
- **Compatibility Claim**: `breaking-on-witnesses`
- **Migration Obligation**: `Supply revision as an integer for every artifact; validate all consumers before any rollout. Example revision 1 is fixture data only.`
- **Owner Ref**: `role:schema-owner`
### Postimage

```json
{
  "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0010-schema-change-carrier/examples/postimage.json",
  "sha256": "b423c544aca4687c7bf3ea38ddd60cb7e43d7d312ff164690e9fa331dd3a69b1"
}
```

### Preimage

```json
{
  "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0009-schema-carrier/artifact-types/schema/v1/fixtures/valid/schema-record.json",
  "sha256": "63b841df14566d66bf87c3d3ba0434b798eae1d7cb4c7f4b9d6278d47ec5a523"
}
```

- **Reason**: `Require an explicit revision number on artifact records.`
### Residue

```json
[
  {
    "consequence": "Only supplied witnesses are assessed; rollout and migration are not executed.",
    "missing": "Complete consumer inventory and universal compatibility proof.",
    "owner_ref": "role:schema-owner"
  }
]
```

- **Rollback Route**: `Restore exact preimage schema and original records together; the supplied original witness is checked against the preimage.`
- **Rollout Route**: `Owner reviews complete consumer inventory and migration outputs before requesting a separate adoption decision.`
- **Schema Version**: `cal-schema-change-record/v1`
- **Scope Ref**: `scope:artifact-owner-structure`
### Source Direction

```json
{
  "canonical": "schema-change-record.json",
  "human_projection": "SCHEMA-CHANGE.md",
  "projection_policy": "generated-only"
}
```

### Source Evidence

```json
[
  {
    "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/artifact-type/type-schema-change/v1/artifact.json",
    "sha256": "10ff9031b00e128b7a229a5156f29777e749155ee01ec6200466d45617aa062f"
  }
]
```

### Validator Ref

```json
{
  "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0009-schema-carrier/check.py",
  "sha256": "c9c0c0f23f3cfe70f1c22504ac86713b8c21341e693ec6ed6dba3224f3607927"
}
```

### Witnesses

```json
[
  {
    "after": {
      "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0010-schema-change-carrier/examples/migrated.json",
      "sha256": "40905063d4fc373f64f98268c286d2e77cd5f497b4bfeda918b1865be478f075"
    },
    "before": {
      "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0009-schema-carrier/examples/conforming.json",
      "sha256": "81028566f6c14e010024808244bbbf4ad153148dbeef5ba9c5929dce0644e7a7"
    },
    "expected_after_on_migrated": true,
    "expected_after_on_original": false,
    "expected_before": true,
    "witness_id": "artifact-owner-example"
  }
]
```


## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
