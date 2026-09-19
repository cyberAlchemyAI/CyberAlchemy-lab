<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Receipt Fixture

- Identity: `LOCAL-EVIDENCE-CHECK-RECEIPT-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Artifact Type Ref**: `cal.artifact-type.receipt/v1`
- **Challenge Route**: `route:receipt-review`
- **Claim Ceiling**: `Exact local operation inputs, code, captured streams and replay agreement only; no external execution, publication or authority proof.`
### Execution Snapshot

```json
{
  "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0023-evidence-set-carrier/manifest.json",
  "sha256": "b0d95087a6d414e4f6bfde4a1fbc6877e1fba99efa3c73b5d28d5d3e5859eee6"
}
```

- **Exit Code**: `0`
### Implementation

```json
{
  "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0023-evidence-set-carrier/check.py",
  "sha256": "5e65e03fd80899aa49e344e84b407e8657343f7f51137f1bc32b355d7ce3034b"
}
```

### Input

```json
{
  "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0023-evidence-set-carrier/artifact-types/evidence-set/v1/fixtures/valid/evidence-set-record.json",
  "sha256": "0f36cd45fff6aaad395b9ca3cdb091157bc92e67d548870236c431cd2ec7f0a2"
}
```

- **Limitations**: `Records one local checker invocation. It neither establishes evidence truth nor proves publication, external execution or actor authority.`
- **Operation Ref**: `operation:check-evidence-inventory`
- **Owner Route**: `route:local-validation-owner`
- **Profile**: `candidate:evidence-check-replay/v1`
- **Python Version**: `3.14.4 (main, Apr  8 2026, 04:02:31) [GCC 15.2.0]`
- **Reported Result**: `passed`
- **Schema Version**: `cal-receipt-record/v1`
- **Scope Ref**: `scope:local-evidence-inventory-check`
### Source Direction

```json
{
  "canonical": "receipt-record.json",
  "human_projection": "RECEIPT.md",
  "projection_policy": "generated-only"
}
```

### Stderr

```json
{
  "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0024-receipt-carrier/examples/stderr.txt",
  "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

### Stdout

```json
{
  "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0024-receipt-carrier/examples/stdout.json",
  "sha256": "77fdf65a9962d00750e4fdc086d6b8bfc74729cf647103f58e1f2bd0719a2691"
}
```


## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
