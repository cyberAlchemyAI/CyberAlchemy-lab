<!-- GENERATED FILE: edit suite.json and run render.py. -->

# Test the CTX-00 semantic candidate

> Generated from `suite.json`; the suite definition is canonical.

From the CyberAlchemy Lab repository root, run:

```bash
python3 tests/conformance/ctx00/run.py
```

## Included checks

### CTX00-T01-SOURCE-ADMISSION

`python3 docs/decisions/0017-ctx00-source-admission/validate.py`

Expected exit code: `0`

### CTX00-T02-DEFINITION-CANDIDATE

`python3 authority/definitions/candidates/0001-definition-and-ctx00-v1/validate.py`

Expected exit code: `0`

### CTX00-T03-SUCCESSOR-PACK

`python3 docs/definition-packs/0004-context-migration-metamodel-post-source-admission/validate.py`

Expected exit code: `0`

### CTX00-T04-PROMOTION-REQUEST

`python3 docs/decisions/0018-definition-and-ctx00-promotion/validate.py`

Expected exit code: `0`

## Success condition

Every command exits zero and contains every exact expected stdout line. The promotion request must remain BLOCK until a human definition-owner selection is recorded.

## Claim ceiling

This suite tests semantic candidate coherence and gate preservation. It does not test context artifact types, context instances, migration execution, runtime behavior, publication, deployment, or stable release.
