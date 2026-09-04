<!-- GENERATED FILE: edit context-pack.json and rerun render.py. -->

# Governance and Ontology Lifecycle candidate pack

> Generated from `context-pack.json`; this view is not canonical.

- Pack: `CAL-CONTEXT-PACK-CTX03-0001`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Objective

Author separate Governance and Ontology Lifecycle Bounded Context and Ubiquitous Language candidates without selecting their cross-context relationship.

## Canonical artifacts

| Kind | Identity | Canonical | Projection |
| --- | --- | --- | --- |
| `bounded-context` | `cal.context.governance` | `contexts/governance/v1/context.json` | `contexts/governance/v1/CONTEXT.md` |
| `ubiquitous-language` | `cal.language.governance` | `contexts/governance/v1/language.json` | `contexts/governance/v1/LANGUAGE.md` |
| `bounded-context` | `cal.context.ontology-lifecycle` | `contexts/ontology-lifecycle/v1/context.json` | `contexts/ontology-lifecycle/v1/CONTEXT.md` |
| `ubiquitous-language` | `cal.language.ontology-lifecycle` | `contexts/ontology-lifecycle/v1/language.json` | `contexts/ontology-lifecycle/v1/LANGUAGE.md` |

## Four facets

### Identity

Each context and language has a stable, versioned, non-overlapping identity and a reciprocal context-language reference.

### Structure

Each context binds one selected domain model and explicit scope; each language binds every selected source concept and its current expression.

### Relationships

Each language binds every selected source relation, while inter-context mappings remain absent until a separate Context Map decision.

### Lifecycle And Evidence

All four artifacts remain candidate-unadmitted and authority-effect none, carry exact evidence and residue, and expose only generated human projections.

## Orthogonality contract

- Governance owns authority meaning and decisions; Ontology Lifecycle owns event history, replay, and reconstructed ontology state.
- A Governance Event is not a Governance Decision and cannot grant authority.
- Ontology Semantic State, Ontology Governance State, and Ontology Lifecycle State are independent axes.
- A Context Projection is not a Bounded Context and never becomes canonical ontology truth.
- No cross-context term equivalence or relationship pattern is inferred from shared words.

## Exact selected inputs

| Input | Root | Path | SHA-256 | Purpose |
| --- | --- | --- | --- | --- |
| `bounded-context-definition` | `lab` | `authority/definitions/candidates/0001-definition-and-ctx00-v1/definitions/bounded-context/v1/definition.json` | `8068ba1bee6f685b3a96911f8a6de28e6a1bc186925301cbd6ed9b085dffd6f4` | Admitted canonical meaning of Bounded Context. |
| `ubiquitous-language-definition` | `lab` | `authority/definitions/candidates/0001-definition-and-ctx00-v1/definitions/ubiquitous-language/v1/definition.json` | `17ac271d5e741ce65645bfcdb280ca047abdb2f5460c7fad94064770f37349a7` | Admitted canonical meaning of Ubiquitous Language. |
| `bounded-context-artifact-type` | `lab` | `authority/artifact-types/bounded-context/v1/artifact.json` | `8b5ac09c50e74225aabe0354c83530578656cecd54e1683bad71f5cac39f0c27` | Admitted representation contract for Bounded Context instances. |
| `ubiquitous-language-artifact-type` | `lab` | `authority/artifact-types/ubiquitous-language/v1/artifact.json` | `9933bad7c87850836cfa6c320b2e7dcb53a13780baee5019ead8e98c22da3a6d` | Admitted representation contract for Ubiquitous Language instances. |
| `ctx01-instance-schema` | `lab` | `tooling/schemas/ctx01/v1/schema.json` | `a82455314d7e9007b09c3ba47ce64cb8bb6e1115ba1c8ce3be4a132d428c2075` | Executable structure validation for both artifact kinds. |
| `ctx01-shared-generator` | `lab` | `tooling/generators/ctx01_artifact.py` | `cd036841d1af5107ddc8fba3f172000c9f274c72d7b28e81a9acc0291f4bb59b` | Deterministic human projection renderer. |
| `context-operational-owners` | `lab` | `authority/owners/foundation-01/v1/candidates/0002-context-operations/owners.json` | `0c4af98990c6cc9df0a7949237d8ebf2a6b11669ec8002a815d9aa5e91ecbcc2` | Admitted separate context and language owner role bindings. |
| `definition-admission` | `lab` | `docs/decisions/0018-definition-and-ctx00-promotion/decision.json` | `a97f891c4d376d216841c4bbfd8f56bae2e0bd838f00c765e6ee52f8c12a32ae` | Admission evidence for the two canonical definitions. |
| `artifact-type-admission` | `lab` | `docs/decisions/0021-ctx01-artifact-type-promotion/decision.json` | `dd9907c6622568525eb0a237938cc88ee1958546816b60d0127212068528cc23` | Admission evidence for the two artifact types. |
| `operational-owner-admission` | `lab` | `docs/decisions/0022-context-operational-owner-promotion/decision.json` | `4066222836d20e53c1b7a3eedff00690de0032e504d9369071aba87d2cc533ec` | Admission evidence for the separate operational owner roles. |
| `governance-profile` | `domainspec-core` | `cyberAlchemy-v2/ontology/governance/profile.json` | `426605a8673c451b2c09237481fbb22ba75834cdc93b16e48c1d5358709a1b99` | Selected Governance source-model identity and posture. |
| `governance-nodes` | `domainspec-core` | `cyberAlchemy-v2/ontology/governance/nodes.json` | `ea967526a77b8cdb4779bd3641399f7b1f825e0c5e5af17099a8d41dea87cb2d` | Complete selected Governance concept surface. |
| `governance-relations` | `domainspec-core` | `cyberAlchemy-v2/ontology/governance/relations.json` | `1bf82b1323db71699729188b9c3f4d3656acf6c371c4c2c1d5914fa5a69fc85c` | Complete selected Governance relation surface. |
| `ontology-lifecycle-business-model` | `lab` | `ontology-lifecycle/business-ontology.json` | `3ea266238a33616da279a5b3434a5e3b3482deac22ecee0ddc6ae65e67826eac` | Complete selected Ontology Lifecycle concept, relation, and invariant surface. |

## Unselected successors

- Exact owner admission decisions for both Bounded Context candidates.
- Exact owner admission decisions for both Ubiquitous Language candidates.
- A separately authored and selected Governance-to-Ontology-Lifecycle Context Map.
- Any migration manifest, source import, implementation binding, runtime enforcement, publication, deployment, or stable release.

## Claim ceiling

A passing CTX03 validation proves candidate representation, exact selected-input closure, four-facet coverage, source-surface coverage, owner-role separation, cross-context non-collapse, and projection parity only. It does not admit either context or language, select a Context Map, authorize migration or implementation, publish, deploy, or establish a stable release.
