<!-- GENERATED FILE: edit registry-postimage.json and run render.py. -->

# CTX06 proposed Definition index

> Generated candidate projection; the live canonical registry remains unchanged.

- Record: `CAL-DEFINITION-REGISTRY-POSTIMAGE-CTX06-0002`
- Status: `candidate-postimage`
- Authority effect: `none`

| ID | Version | Term | Lifecycle | Predecessor | Path | Digest |
| --- | --- | --- | --- | --- | --- | --- |
| `cal.definition.bounded-context` | `1.0.0-candidate.1` | Bounded Context | `admitted` | `-` | `authority/definitions/candidates/0001-definition-and-ctx00-v1/definitions/bounded-context/v1/definition.json` | `8068ba1bee6f685b3a96911f8a6de28e6a1bc186925301cbd6ed9b085dffd6f4` |
| `cal.definition.bounded-context` | `2.0.0-candidate.1` | Bounded Context | `candidate-unadmitted` | `cal.definition.bounded-context@1.0.0-candidate.1` | `authority/definitions/candidates/0002-ctx06-context-map-reference-normalization/definitions/bounded-context/v2/definition.json` | `6ee155d2e7427e33357e55e56bc5228c2b584ea435bb9dc516ddb66385f590c0` |
| `cal.definition.capability-instance` | `1.0.0-candidate.1` | Capability Instance | `admitted` | `-` | `authority/definitions/candidates/0001-definition-and-ctx00-v1/definitions/capability-instance/v1/definition.json` | `d1e0140d47887b3f8c49334e81c33bd105edaecaf02f3df3df841885340505a5` |
| `cal.definition.context-lineage-record` | `1.0.0-candidate.1` | Context Lineage Record | `admitted` | `-` | `authority/definitions/candidates/0001-definition-and-ctx00-v1/definitions/context-lineage-record/v1/definition.json` | `0e843dc8932020004432bf49f0f765f89e44c9e1f52e08b92037340a49c4b2d6` |
| `cal.definition.context-map` | `1.0.0-candidate.1` | Context Map | `admitted` | `-` | `authority/definitions/candidates/0001-definition-and-ctx00-v1/definitions/context-map/v1/definition.json` | `b0350b536b4bc7ca976eaef474b8427137c1ae85a4121977203b078eeb7cb14d` |
| `cal.definition.context-map` | `2.0.0-candidate.1` | Context Map | `candidate-unadmitted` | `cal.definition.context-map@1.0.0-candidate.1` | `authority/definitions/candidates/0002-ctx06-context-map-reference-normalization/definitions/context-map/v2/definition.json` | `677ff95db15b30a80e2d59673286142337c3a513e52fd27dd033fe710f8de050` |
| `cal.definition.context-migration-manifest` | `1.0.0-candidate.1` | Context Migration Manifest | `admitted` | `-` | `authority/definitions/candidates/0001-definition-and-ctx00-v1/definitions/context-migration-manifest/v1/definition.json` | `bcfadcf568fe77a4e410e96ca86ba76f34bf8fdefdff2dfeb8cd12ac67022beb` |
| `cal.definition.coordination-context` | `1.0.0-candidate.1` | Coordination Context | `admitted` | `-` | `authority/definitions/candidates/0001-definition-and-ctx00-v1/definitions/coordination-context/v1/definition.json` | `547a714a9552f83985de78b2ce228421f5102c40cacf8c1edfb48ef46366a8aa` |
| `cal.definition.definition` | `1.0.0-candidate.1` | Definition | `admitted` | `-` | `authority/definitions/candidates/0001-definition-and-ctx00-v1/definitions/definition/v1/definition.json` | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` |
| `cal.definition.ubiquitous-language` | `1.0.0-candidate.1` | Ubiquitous Language | `admitted` | `-` | `authority/definitions/candidates/0001-definition-and-ctx00-v1/definitions/ubiquitous-language/v1/definition.json` | `17ac271d5e741ce65645bfcdb280ca047abdb2f5460c7fad94064770f37349a7` |

## Proposed current lookup

- `cal.definition.bounded-context` -> `cal.definition.bounded-context@2.0.0-candidate.1`
- `cal.definition.capability-instance` -> `cal.definition.capability-instance@1.0.0-candidate.1`
- `cal.definition.context-lineage-record` -> `cal.definition.context-lineage-record@1.0.0-candidate.1`
- `cal.definition.context-map` -> `cal.definition.context-map@2.0.0-candidate.1`
- `cal.definition.context-migration-manifest` -> `cal.definition.context-migration-manifest@1.0.0-candidate.1`
- `cal.definition.coordination-context` -> `cal.definition.coordination-context@1.0.0-candidate.1`
- `cal.definition.definition` -> `cal.definition.definition@1.0.0-candidate.1`
- `cal.definition.ubiquitous-language` -> `cal.definition.ubiquitous-language@1.0.0-candidate.1`

## Activation rule

An exact definition-owner decision must bind both successor Definition digests and this complete postimage. On admission, the two successor entries become admitted current lookup targets and their v1 predecessors remain immutable historical versions; no artifact type or instance changes automatically.

## Claim ceiling

This proposed postimage preserves eight admitted versions and adds two unadmitted successor candidates. It does not change the live registry, supersede a predecessor, admit an artifact type or context, authorize migration, or establish a stable release.
