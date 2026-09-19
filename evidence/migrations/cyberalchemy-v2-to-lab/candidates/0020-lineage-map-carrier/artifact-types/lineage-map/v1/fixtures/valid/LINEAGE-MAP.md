<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Lineage Map Fixture

- Identity: `EXAMPLE-NORMALIZED-LINEAGE-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Artifact Type Ref**: `cal.artifact-type.lineage-map/v1`
- **Challenge Route**: `route:migration-lineage-review`
- **Claim Ceiling**: `Exact selected normalization mappings and successor scaffold identities only; no identity equivalence, authority transfer or successor admission.`
### Coverage

```json
[
  "CAV2-D9",
  "CAV2-D34"
]
```

### Mappings

```json
[
  {
    "disposition": "reclassify",
    "legacy_id": "CAV2-D9",
    "successors": [
      {
        "binding": {
          "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-cyberalchemy-repository-identity/v1/artifact.json",
          "sha256": "7a31d492ed24839eb136608953b52ef6fe92838990689fa53ad77d618aa7fdad"
        },
        "target_id": "semantic.cyberalchemy-repository-identity"
      },
      {
        "binding": {
          "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/artifact-type/type-lineage-map/v1/artifact.json",
          "sha256": "a9dec165e1070ade4b72819af73c258d27112191fdf220e16e25d7ff66d5f087"
        },
        "target_id": "type.lineage-map"
      }
    ]
  },
  {
    "disposition": "split",
    "legacy_id": "CAV2-D34",
    "successors": [
      {
        "binding": {
          "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-authority/v1/artifact.json",
          "sha256": "c997d63b2bb8e8531d69016787518c34639f5e672bfb11ff75c73b41d590e2a7"
        },
        "target_id": "semantic.authority"
      },
      {
        "binding": {
          "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-authority-claim/v1/artifact.json",
          "sha256": "a8568c2247cf0dc1a6ccccf97b03c7bae98ef401726d679fc8b76ae04562b04a"
        },
        "target_id": "semantic.authority-claim"
      },
      {
        "binding": {
          "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-responsibility/v1/artifact.json",
          "sha256": "e12967dceeeb3e0277cbc0707265a2633c56856879e5c2086a355fa108e20dca"
        },
        "target_id": "semantic.responsibility"
      },
      {
        "binding": {
          "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/artifact-type/type-authority-claim/v1/artifact.json",
          "sha256": "eb2da458eb8a8c3a1672b6a327a9e363754ff85dd6f06f227188eac0015b2ff3"
        },
        "target_id": "type.authority-claim"
      },
      {
        "binding": {
          "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/artifact-type/type-responsibility/v1/artifact.json",
          "sha256": "bec4502f35af8e85c2f22436dfff5923ea379fea31d8d876c770351c233cda63"
        },
        "target_id": "type.responsibility"
      }
    ]
  }
]
```

### Normalization

```json
{
  "path": "docs/normalizations/0001-definition-migration-model/normalization.json",
  "sha256": "c1021431d8d33ee1e7c8bc6caf3ca0e89cba20e840a9360a2cefbff240cb5016"
}
```

- **Owner Route**: `route:migration-owner`
- **Profile**: `candidate:normalized-successor-map/v1`
- **Schema Version**: `cal-lineage-map-record/v1`
- **Scope Ref**: `scope:selected-normalized-identities`
### Source Direction

```json
{
  "canonical": "lineage-map-record.json",
  "human_projection": "LINEAGE-MAP.md",
  "projection_policy": "generated-only"
}
```

### Target Index

```json
{
  "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidate-index.json",
  "sha256": "28f6ff69a2996d33f0383339880d8da7d2b207dea41beffd77c6a34242a253b1"
}
```


## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
