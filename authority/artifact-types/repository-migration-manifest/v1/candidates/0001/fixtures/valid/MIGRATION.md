<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Repository Migration Manifest Fixture

- Identity: `fixture.repository-migration/v1`
- Status: `candidate-unapproved`
- Authority effect: `none`

## Canonical machine projection

### Architecture

```json
{
  "path": "architecture/architecture.json",
  "sha256": "2222222222222222222222222222222222222222222222222222222222222222"
}
```

- **Claim Ceiling**: `Fixture only; no effect.`
### Copy Allowlist

```json
{
  "path": "copy-allowlist.json",
  "sha256": "5555555555555555555555555555555555555555555555555555555555555555"
}
```

### Copy Semantics

```json
{
  "additive_only": true,
  "import_grants_authority": false,
  "overwrite": false,
  "source_mutation": false
}
```

### Exclusion Inventory

```json
{
  "path": "exclusion-inventory.json",
  "sha256": "4444444444444444444444444444444444444444444444444444444444444444"
}
```

- **Execution Authority**: `False`
### Expected Postimage

```json
{
  "path": "expected-postimage.json",
  "sha256": "6666666666666666666666666666666666666666666666666666666666666666"
}
```

### Mapping Rules

```json
{
  "path": "mapping-rules.json",
  "sha256": "3333333333333333333333333333333333333333333333333333333333333333"
}
```

### Rollback Ref

```json
{
  "path": "rollback.json",
  "sha256": "7777777777777777777777777777777777777777777777777777777777777777"
}
```

- **Schema Version**: `cyberalchemy-lab-repository-migration-manifest/v1`
### Semantic Definition Refs

```json
[
  "cal.definition.repository-migration-manifest@1.0.0-candidate.1"
]
```

### Source Direction

```json
{
  "canonical": "migration.json",
  "generator_ref": "build.py",
  "human_projection": "MIGRATION.md",
  "projection_policy": "generated-only"
}
```

### Source Repository

```json
{
  "inventory": {
    "path": "source-inventory.json",
    "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
  },
  "path": "/source"
}
```

### Target Repository

```json
{
  "baseline": {
    "path": "target-baseline.json",
    "sha256": "1111111111111111111111111111111111111111111111111111111111111111"
  },
  "path": "/target"
}
```

### Validation Obligations

```json
[
  "complete-accounting",
  "hash-currency",
  "collision-free",
  "dry-run",
  "isolated-rehearsal",
  "rollback-closure"
]
```

- **Version**: `1.0.0-fixture`

## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
