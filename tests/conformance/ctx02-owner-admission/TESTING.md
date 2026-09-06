<!-- GENERATED FILE: edit suite.json and rerun render.py. -->

# CTX02 owner-admission conformance

> Machine-canonical suite; this Markdown is a generated projection.

- Subject: `CAL-DECISION-0022-CONTEXT-OPERATIONAL-OWNER-PROMOTION`
- Tests: `3`

## Commands

| Test | Command |
| --- | --- |
| `CTX02-T01-OWNER-CANDIDATE` | `python3 authority/owners/foundation-01/v1/candidates/0002-context-operations/validate.py` |
| `CTX02-T02-PROMOTION-REQUEST` | `python3 docs/decisions/0022-context-operational-owner-promotion/validate.py` |
| `CTX02-T03-OWNER-ADMISSION` | `python3 docs/decisions/0022-context-operational-owner-promotion/validate-admission.py` |

## Protected surfaces

- `authority/owners/foundation-01/v1/owners.json` — `bb20cdc8ed61decba43977fafc4d04052cb59bb8e4402d6419a3d85776a3422d`
- `authority/definitions/registry.json` — `78284ea33543aae5d0cfecb7d5090aa8702388051486eec69ffc368c656d5e8f`
- `docs/decisions/0021-ctx01-artifact-type-promotion/decision.json` — `dd9907c6622568525eb0a237938cc88ee1958546816b60d0127212068528cc23`
- `docs/decisions/0022-context-operational-owner-promotion/decision.json` — `4066222836d20e53c1b7a3eedff00690de0032e504d9369071aba87d2cc533ec`

## Claim ceiling

PASS confirms current owner-admission coherence and protected-surface stability. It does not author or admit context-metamodel instances, select Context Map relationships, authorize migration or implementation, publish, deploy, or establish a stable release.
