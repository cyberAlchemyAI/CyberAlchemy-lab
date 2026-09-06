<!-- GENERATED FILE: edit suite.json and rerun render.py. -->

# CTX01 artifact-type candidate conformance

> Generated from `suite.json`; this view is not canonical.

- Suite: `CAL-CONFORMANCE-CTX01-ARTIFACT-TYPES-001`
- Subject: `CAL-ARTIFACT-TYPE-PACK-CTX01-0001`
- Status: `candidate-test-suite`

## Tests

| Test | Command | Expected output |
| --- | --- | --- |
| `CTX01-T01-BOUNDED-CONTEXT` | `python3 authority/artifact-types/bounded-context/v1/validate.py` | `CTX01_BOUNDED_CONTEXT_VALIDATION=PASS ; CHECKS=25/25` |
| `CTX01-T02-COORDINATION-CONTEXT` | `python3 authority/artifact-types/coordination-context/v1/validate.py` | `CTX01_COORDINATION_CONTEXT_VALIDATION=PASS ; CHECKS=24/24` |
| `CTX01-T03-UBIQUITOUS-LANGUAGE` | `python3 authority/artifact-types/ubiquitous-language/v1/validate.py` | `CTX01_UBIQUITOUS_LANGUAGE_VALIDATION=PASS ; CHECKS=24/24` |
| `CTX01-T04-CONTEXT-MAP` | `python3 authority/artifact-types/context-map/v1/validate.py` | `CTX01_CONTEXT_MAP_VALIDATION=PASS ; CHECKS=25/25` |
| `CTX01-T05-CAPABILITY-INSTANCE` | `python3 authority/artifact-types/capability-instance/v1/validate.py` | `CTX01_CAPABILITY_INSTANCE_VALIDATION=PASS ; CHECKS=25/25` |
| `CTX01-T06-MIGRATION-MANIFEST` | `python3 authority/artifact-types/context-migration-manifest/v1/validate.py` | `CTX01_CONTEXT_MIGRATION_MANIFEST_VALIDATION=PASS ; CHECKS=26/26` |
| `CTX01-T07-LINEAGE-RECORD` | `python3 authority/artifact-types/context-lineage-record/v1/validate.py` | `CTX01_CONTEXT_LINEAGE_RECORD_VALIDATION=PASS ; CHECKS=26/26` |
| `CTX01-T08-AGGREGATE-CLOSURE` | `python3 docs/artifact-type-packs/0001-ctx01/validate.py` | `CTX01_ARTIFACT_TYPE_PACK_VALIDATION=PASS ; PROMOTION_ELIGIBILITY=eligible-for-exact-artifact-type-owner-review ; CHECKS=23/23` |

## Run

```bash
python3 tests/conformance/ctx01/run.py
```

## Success condition

All seven local validators and the aggregate cross-type validator exit zero with exact expected output. Local receipts must remain current before aggregate closure is evaluated.

## Claim ceiling

PASS establishes CTX01 candidate coherence only. It does not admit artifact types, bind owners, create contexts, select a relationship pattern, execute migration, publish, deploy, or establish a stable release.
