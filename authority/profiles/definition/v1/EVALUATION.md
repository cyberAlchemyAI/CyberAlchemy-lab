<!-- GENERATED FILE: edit the bound JSON source and rerun render.py. -->

# Definition evaluation profile v1

> Generated from `evaluation.json`; this view is not canonical.

- Status: `candidate-unadmitted`
- Authority effect: `none`
- Owner: `role:evidence-conformance-owner`

## Outcomes

- `PASS`
- `FAIL`
- `NOT_EVALUABLE`

## Checks

| Check | Purpose | Blocked by |
| --- | --- | --- |
| `DEF-EVAL-01-SCHEMA` | Validate the closed Definition/v1 representation and exact schema binding. | nothing |
| `DEF-EVAL-02-VOICES` | Require scientific/formal, explicitly non-normative plain-language, and Lab domain-context voices. | DEF-EVAL-01-SCHEMA |
| `DEF-EVAL-03-SOURCES` | Resolve every exact source selector and require admitted source posture for promotion. | missing or stale selected source admission |
| `DEF-EVAL-04-OWNER` | Resolve semantic owner and drift owner through current role assignments. | missing or unadmitted owner assignment |
| `DEF-EVAL-05-PROJECTION` | Prove two-run deterministic generation and exact projection parity. | missing or stale generator binding |
| `DEF-EVAL-06-REGISTRY` | Validate the proposed registry postimage, unique identity, generated index, and drift audit. | missing registry postimage or drift audit |
| `DEF-EVAL-07-DECISION` | Verify that one human decision binds all admission-bound candidate and postimage digests. | no exact human admission decision |

## Admission rule

A Definition is eligible for an admission decision only when checks 01 through 06 PASS and check 07 is NOT_EVALUABLE solely because the owner decision has not yet occurred. PASS remains evidence and cannot perform the admission.

## Claim ceiling

This candidate defines collect-all evaluation semantics. An evaluation result has authority_effect none and cannot admit, publish, implement, or prove semantic truth.
