<!-- GENERATED FILE: edit map-pack.json and rerun validate.py. -->

# Governance to Ontology Lifecycle v2 Context Map prototype

- Pack: `CAL-CONTEXT-MAP-PACK-CTXMAP2-0004`
- Stage: `CTXMAP2-S1`
- Status: `testable-prototype-candidate`
- Authority effect: `none`

## Objective

Prove that the admitted Governance and Ontology Lifecycle v2 endpoints can be related by an additive one-way Context Map without changing the admitted v1 map or transferring authority.

## Two-lane frontier

- Product lane: `product-construction`
- Current frontier: `CTXMAP2-S1`
- Continuation: `runnable`
- Operational blockers: none

## Selected inputs

| Input | Path | SHA-256 |
| --- | --- | --- |
| `context-map-v2-definition` | `authority/definitions/candidates/0002-ctx06-context-map-reference-normalization/definitions/context-map/v2/definition.json` | `677ff95db15b30a80e2d59673286142337c3a513e52fd27dd033fe710f8de050` |
| `context-map-v2-artifact-type` | `authority/artifact-types/context-map/v2/artifact.json` | `d0c8474eabefeea9a7b9cb18c8c0a80282a82eaae564d4f1c73ef4b60578626c` |
| `context-map-v2-schema-wrapper` | `authority/artifact-types/context-map/v2/schema.json` | `c8ff952c4bdbab31dafb293ee3077eca882ffc51ba87b4d2a088e8f5a71ccdfa` |
| `context-map-v2-shared-schema` | `tooling/schemas/ctx07/v2/schema.json` | `e15aee32c5781ca0d25c9c6c4e5c58caab5a5f5f286b6389298d18c2208696ec` |
| `context-map-v2-generator` | `tooling/generators/ctx07_artifact.py` | `2b1d0a04c58a44522710cf2197ffe5ed78bda970afe6997781985eaf85e32eb4` |
| `context-map-v2-artifact-type-admission` | `docs/decisions/0027-ctx07-normalized-context-artifact-type-promotion/decision.json` | `bd77f9ebc901a3d1bbfaa27d4a8e73a03d56d4d83f5015eeae4e877d4d754fd3` |
| `v2-endpoint-admission` | `docs/decisions/0025-governance-ontology-lifecycle-successor-promotion/decision.json` | `ee7e937511235eb458a48120b0c51aceafb9d1e395d295e0ac839831aeb775b0` |
| `governance-context-v2` | `contexts/governance/v2/context.json` | `5c59ae8dc12807ad8996749a82e1f9b0c1f624b3ef87aaebf4442e957d90d88f` |
| `governance-language-v2` | `contexts/governance/v2/language.json` | `ba84484be3f0d793e935ba4bbf960885ce1adcd2d2763aee940396ff290918d7` |
| `ontology-lifecycle-context-v2` | `contexts/ontology-lifecycle/v2/context.json` | `4a8ef8f3441a055aeed10e368db4bcec7bf6c098e15e2356cfd25d659df3a4b8` |
| `ontology-lifecycle-language-v2` | `contexts/ontology-lifecycle/v2/language.json` | `8d01b878d93fa1b502d57348b8c5cad3c25968504de0ef7df37b17e63dda2e55` |
| `admitted-v1-map-decision` | `docs/decisions/0024-governance-ontology-lifecycle-context-map-promotion/decision.json` | `dd9833207ab9bb152b599f2e9992572fef6216d9da8925d8a40c7eb948bf44b6` |
| `admitted-v1-map` | `contexts/maps/governance-ontology-lifecycle/v1/map.json` | `e4c339df5f2072a2a43b34ca2fe1f11ea331f53fc5a0616249d37150e2a242fd` |
| `admitted-d65-s8-decision` | `docs/decisions/0032-d65-s8-integration-admission/decision.json` | `9baae3d5dfa12e331cd5eb51e25e66cfa6018332b2cca246ce964764779f1fa0` |
| `context-artifact-architecture` | `docs/proposals/0001-context-artifact-architecture/PROPOSAL.md` | `d1e6b8f86ded1bd3e5db6d6951f06cf135140efe8b3cc341ca996a64b379cf55` |

## Claim ceiling

PASS proves a deterministic, hostile-tested v2 Context Map prototype and preservation of the selected predecessor bytes only. It does not approve, admit, activate, migrate, cut over, publish, release, deploy, or authorize an external effect.
