<!-- GENERATED FILE: edit suite.json and rerun render.py. -->

# CTX07 normalized artifact-type conformance

> Generated from `suite.json`; this view is not canonical.

- Suite: `CAL-CONFORMANCE-CTX07-ARTIFACT-TYPES-001`
- Subject: `CAL-ARTIFACT-TYPE-PACK-CTX07-0002`
- Status: `candidate-test-suite`

## Tests

| Test | Command | Expected output |
| --- | --- | --- |
| `CTX07-T01-BOUNDED-CONTEXT-V2` | `python3 authority/artifact-types/bounded-context/v2/validate.py` | `CTX07_BOUNDED_CONTEXT_VALIDATION=PASS ; CHECKS=25/25` |
| `CTX07-T02-CONTEXT-MAP-V2` | `python3 authority/artifact-types/context-map/v2/validate.py` | `CTX07_CONTEXT_MAP_VALIDATION=PASS ; CHECKS=31/31` |
| `CTX07-T03-AGGREGATE-CLOSURE` | `python3 docs/artifact-type-packs/0002-ctx07/validate.py` | `CTX07_ARTIFACT_TYPE_PACK_VALIDATION=PASS ; PROMOTION_ELIGIBILITY=eligible-for-exact-artifact-type-owner-review ; CHECKS=23/23` |

## Run

```bash
python3 tests/conformance/ctx07-artifact-types/run.py
```

## Success condition

Both local validators and the aggregate validator exit zero with exact expected output while all bound pack materials remain current.

## Claim ceiling

PASS establishes CTX07 candidate coherence only. It does not admit either artifact type or tooling runtime, create or revise contexts or maps, authorize migration, publish, deploy, or establish a stable release.
