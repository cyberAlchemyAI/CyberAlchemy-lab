<!-- GENERATED FILE: edit map-pack.json and rerun render.py. -->

# Governance to Ontology Lifecycle Context Map candidate pack

> Generated from `map-pack.json`; this view is not canonical.

- Pack: `CAL-CONTEXT-MAP-PACK-CTX04-0001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Selected candidate pattern

`cal.context.governance/v1` → `cal.context.ontology-lifecycle/v1`

Pattern: `candidate:ddd.upstream-downstream.published-language.anticorruption-layer/v1`

Governance publishes exact owner-decision envelopes. Ontology Lifecycle protects its local model through a downstream Anti-Corruption Layer that records the envelope as a local Governance Event while preserving the exact upstream identity and authority boundary.

Reverse dependency: `forbidden-unless-separately-authored-and-owner-selected`

## Four facets

### Classification

Map identity, relationship kind, endpoint roles, direction, owner roles, lifecycle posture, and authority effect remain independent classifications.

### Schema

One closed Context Map/v1 record names exactly two endpoint context versions and one non-reflexive Governance-to-Ontology-Lifecycle relationship.

### Human Continuation

Generated MAP.md exposes the pattern, contracts, translation references, information boundary, authority boundary, evidence, residue, and drift route.

### Machine Checkable

Schema, exact endpoint admission, input hashes, direction, relationship cardinality, language-reference closure, owner-role closure, non-authority transfer, reverse-edge absence, hostile mutations, and projection parity are executable.

## Orthogonality contract

- The map relates two admitted contexts but does not merge their identities, languages, models, owners, or lifecycle states.
- A Governance Decision remains an upstream authority artifact; the downstream Governance Event is a record and never an equivalent decision.
- Information may cross while authority, ownership, admission, and enforcement permission do not.
- The absence of a reverse edge is a deliberate constraint, not an inferred bidirectional dependency.
- The DDD relationship pattern is map-local and candidate until a separate Context Map owner decision admits it.

## Exact selected inputs

| Input | Path | SHA-256 | Purpose |
| --- | --- | --- | --- |
| `context-map-definition` | `authority/definitions/candidates/0001-definition-and-ctx00-v1/definitions/context-map/v1/definition.json` | `b0350b536b4bc7ca976eaef474b8427137c1ae85a4121977203b078eeb7cb14d` | Admitted canonical Context Map meaning. |
| `context-map-artifact-type` | `authority/artifact-types/context-map/v1/artifact.json` | `509a46dbcb60af7b930ba7b171672c08c92fc35c1391594743adaf88d6a0e48d` | Admitted Context Map representation contract. |
| `context-map-schema-wrapper` | `authority/artifact-types/context-map/v1/schema.json` | `d182ff3eea0b6ed4d16616181399dcf27aed016240db5b41ea090acd3252a7cc` | Artifact-local schema binding. |
| `ctx01-instance-schema` | `tooling/schemas/ctx01/v1/schema.json` | `a82455314d7e9007b09c3ba47ce64cb8bb6e1115ba1c8ce3be4a132d428c2075` | Executable closed Context Map schema. |
| `ctx01-shared-generator` | `tooling/generators/ctx01_artifact.py` | `cd036841d1af5107ddc8fba3f172000c9f274c72d7b28e81a9acc0291f4bb59b` | Deterministic MAP.md renderer. |
| `context-operational-owners` | `authority/owners/foundation-01/v1/candidates/0002-context-operations/owners.json` | `0c4af98990c6cc9df0a7949237d8ebf2a6b11669ec8002a815d9aa5e91ecbcc2` | Admitted map and endpoint owner roles. |
| `artifact-type-admission` | `docs/decisions/0021-ctx01-artifact-type-promotion/decision.json` | `dd9907c6622568525eb0a237938cc88ee1958546816b60d0127212068528cc23` | Admission evidence for Context Map/v1. |
| `owner-admission` | `docs/decisions/0022-context-operational-owner-promotion/decision.json` | `4066222836d20e53c1b7a3eedff00690de0032e504d9369071aba87d2cc533ec` | Admission evidence for context-map-owner and endpoint roles. |
| `endpoint-admission` | `docs/decisions/0023-governance-and-ontology-lifecycle-context-promotion/decision.json` | `0990e6b9606549ae9e8c53f2dddbf78ace8bf95d5dfa62df5fc46d17071008fb` | Admission overlay for both endpoint context-language pairs. |
| `endpoint-admission-validation` | `docs/decisions/0023-governance-and-ontology-lifecycle-context-promotion/receipts/admission-validation.json` | `cfaa74bf7d5599c8853a6c83d99aeae804e5b1c8fbdd18a8f45fef5a13d71295` | PASS evidence for the exact endpoint admission overlay. |
| `governance-context` | `contexts/governance/v1/context.json` | `e4d8ffb21383276b7f5a0d84d097d02507dcc2711d7197f285308430da28c9a4` | Exact upstream endpoint identity and boundary. |
| `governance-language` | `contexts/governance/v1/language.json` | `7b6e2a22aa6c0ae1762178e22fe8c56c6c1cbe6bab4951012ba51757d3a220a5` | Exact upstream Published Language surface. |
| `ontology-lifecycle-context` | `contexts/ontology-lifecycle/v1/context.json` | `dc06e7e0b986262192f3578983368ad9c7c407d3a223e424f44c60717a6e7b0c` | Exact downstream endpoint identity and boundary. |
| `ontology-lifecycle-language` | `contexts/ontology-lifecycle/v1/language.json` | `0e1b71f658bcf0dfdcc75b7a086d41bbae525413780a675330b05316b13d3b86` | Exact downstream translation target surface. |
| `context-placement-decision` | `docs/decisions/0016-ontology-lifecycle-context-placement/decision.json` | `6fdd31fd202a0998d6105536cb1827fcdbb59980d982af4af7e9bc2f8a9710ce` | Prior owner-selected upstream/downstream direction and forbidden reverse default. |

## Unselected successors

- Exact Context Map owner admission decision.
- Any separately authored Ontology-Lifecycle-to-Governance evidence-feedback relationship.
- Runtime payload schema, adapter, transport, implementation binding, or conformance evidence.
- Endpoint context successor epochs that reference an admitted Context Map.
- Migration manifest, lineage record, migration execution, publication, deployment, or stable release.

## Claim ceiling

A passing CTX04 validation proves Context Map candidate representation, exact endpoint and predecessor closure, one-way pattern selection, owner separation, authority non-transfer, hostile-case rejection, and projection parity only. It does not admit the map or relationship kind, create a reverse dependency, authorize runtime integration, migration, implementation, publication, deployment, or a stable release.
