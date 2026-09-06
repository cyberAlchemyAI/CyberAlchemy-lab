<!-- GENERATED FILE: edit suite.json and rerun render.py. -->

# CTX00 post-admission conformance

> Generated from `suite.json`; this view is not canonical.

- Suite: `CAL-CONFORMANCE-CTX00-ADMISSION-001`
- Status: `current-post-admission-suite`
- Subject: `CAL-DECISION-0018-DEFINITION-AND-CTX00-PROMOTION`

## Tests

| Test | Command | Expected output |
| --- | --- | --- |
| `CTX00-ADMISSION-T01-CURRENT-CLOSURE` | `python3 docs/decisions/0018-definition-and-ctx00-promotion/validate-admission.py` | `DEFINITION_CTX00_ADMISSION_VALIDATION=PASS; CHECKS=42/42` |
| `CTX00-ADMISSION-T02-PROJECTIONS` | `python3 tests/conformance/ctx00-admission/verify-projections.py` | `CTX00_ADMISSION_PROJECTIONS=PASS; CHECKS=11/11` |
| `CTX00-ADMISSION-T03-HOSTILE-REGISTRY` | `python3 tests/conformance/ctx00-admission/verify-hostile.py` | `CTX00_ADMISSION_HOSTILE=PASS; CHECKS=5/5` |

## Success condition

Every command exits zero and contains every exact expected stdout line. Current machine records must match the admitted decision, every human view must be generated-only and current, and each hostile registry mutation must be rejected.

## Historical suite boundary

tests/conformance/ctx00 is pre-admission epoch evidence. Its empty-live-registry guard is intentionally no longer a current-state test and that suite must not be rerun as post-admission conformance.

## Run

```bash
python3 tests/conformance/ctx00-admission/run.py
```

## Claim ceiling

PASS validates only the current eight-Definition admission and its generated projections. It does not validate or authorize successor artifact types, context instances, migration execution, runtime behavior, publication, deployment, or stable release.
