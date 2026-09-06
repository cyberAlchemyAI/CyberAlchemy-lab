<!-- GENERATED FILE: edit suite.json and rerun render.py. -->

# CTX01 artifact-type admission conformance

> Machine-canonical suite; this Markdown is a generated projection.

- Subject: `CAL-DECISION-0021-CTX01-ARTIFACT-TYPE-PROMOTION`
- Tests: `11`

## Commands

| Test | Command |
| --- | --- |
| `CTX01-A01-BOUNDED-CONTEXT` | `python3 authority/artifact-types/bounded-context/v1/validate.py` |
| `CTX01-A02-UBIQUITOUS-LANGUAGE` | `python3 authority/artifact-types/ubiquitous-language/v1/validate.py` |
| `CTX01-A03-CAPABILITY-INSTANCE` | `python3 authority/artifact-types/capability-instance/v1/validate.py` |
| `CTX01-A04-COORDINATION-CONTEXT` | `python3 authority/artifact-types/coordination-context/v1/validate.py` |
| `CTX01-A05-CONTEXT-MAP` | `python3 authority/artifact-types/context-map/v1/validate.py` |
| `CTX01-A06-MIGRATION-MANIFEST` | `python3 authority/artifact-types/context-migration-manifest/v1/validate.py` |
| `CTX01-A07-LINEAGE-RECORD` | `python3 authority/artifact-types/context-lineage-record/v1/validate.py` |
| `CTX01-A08-PACK` | `python3 docs/artifact-type-packs/0001-ctx01/validate.py` |
| `CTX01-A09-SUCCESSOR` | `python3 authority/artifact-types/artifact-type/v1/candidates/0002-ctx01-registration/validate.py` |
| `CTX01-A10-PROMOTION-REQUEST` | `python3 docs/decisions/0021-ctx01-artifact-type-promotion/validate.py` |
| `CTX01-A11-ADMISSION` | `python3 docs/decisions/0021-ctx01-artifact-type-promotion/validate-admission.py` |

## Protected surfaces

- `authority/artifact-types/artifact-type/v1/artifact.json` — `143577e9efa793cdf7447e38f5e25013e3006df3b21e9aa3aec4b30d10c19e56`
- `authority/definitions/registry.json` — `78284ea33543aae5d0cfecb7d5090aa8702388051486eec69ffc368c656d5e8f`
- `docs/decisions/0018-definition-and-ctx00-promotion/decision.json` — `a97f891c4d376d216841c4bbfd8f56bae2e0bd838f00c765e6ee52f8c12a32ae`
- `docs/decisions/0021-ctx01-artifact-type-promotion/decision.json` — `dd9907c6622568525eb0a237938cc88ee1958546816b60d0127212068528cc23`

## Claim ceiling

PASS confirms current post-admission artifact-type coherence and protected-surface stability. It does not bind operational owners, create context instances, authorize migration or implementation, publish, deploy, or establish a stable release.
