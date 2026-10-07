<!-- GENERATED FILE: canonical data is pack.json and the instance records. -->

# CyberAlchemy Lab reference instance slice

- Status: `candidate-owner-review-open`
- Authority effect: `none`
- Artifact instances: `91`
- Typed Relation instances: `44`
- Ontology nodes: `12`
- Ontology edges: `9`
- Runtime activations: `0`

## Concrete story

`product:cyberalchemy-lab` is the Product. `project:cyberalchemy-v2-to-lab-migration` is the bounded migration Project that contributes to it. `product-capability:cyberalchemy-lab:governed-knowledge-lifecycle` is the Product outcome, while `implementation:cyberalchemy-lab-governed-repository-toolchain` is one replaceable realization. `research-inquiry:v2-to-lab-semantic-preservation` asks a bounded question; `experiment-design:reference-slice-contract-validation` specifies a test; `experiment-run:reference-slice-contract-validation:2026-10-06` records its execution; `evidence-set:reference-slice-validation` aggregates the output; and `finding:reference-slice-schema-and-relation-closure` states only the supported bounded conclusion.

`agent-instance:reference-slice-authoring:2026-10-06` is ephemeral and acts within `agent-session:reference-slice-authoring:2026-10-06`. Its short memory is embedded in that session and expires with it. Durable continuity remains `project-state:cyberalchemy-v2-to-lab-migration:decision-0070`, selected through `context-view:reference-slice-authoring:2026-10-06` and the ontology view rather than owned by the Agent.

## Artifact instances

| Kind | Identity | Carrier |
|---|---|---|
| `intent` | `intent:operationalize-cyberalchemy-lab-model` | `cal.artifact-type.intent/v1` |
| `product` | `product:cyberalchemy-lab` | `cal.artifact-type.product-identity/v2` |
| `product-thesis` | `product-thesis:cyberalchemy-lab-governed-work` | `cal.artifact-type.product-thesis/v1` |
| `product-capability` | `product-capability:cyberalchemy-lab:governed-knowledge-lifecycle` | `cal.artifact-type.product-capability/v1` |
| `project` | `project:cyberalchemy-v2-to-lab-migration` | `cal.artifact-type.project-identity/v1` |
| `goal` | `goal:materialize-definition-complete-reference-slice` | `cal.artifact-type.goal/v1` |
| `capability-realization-binding` | `capability-realization-binding:governed-repository-toolchain` | `cal.artifact-type.capability-realization-binding/v2` |
| `policy` | `policy:reference-slice-governance` | `cal.artifact-type.policy/v1` |
| `challenge-contract` | `challenge-contract:cyberalchemy-lab-reference-slice` | `cal.artifact-type.challenge-contract/v1` |
| `research-inquiry` | `research-inquiry:v2-to-lab-semantic-preservation` | `cal.artifact-type.research-inquiry/v1` |
| `hypothesis` | `hypothesis:reference-slice-preserves-orthogonality` | `cal.artifact-type.hypothesis/v1` |
| `experiment-design` | `experiment-design:reference-slice-contract-validation` | `cal.artifact-type.experiment-design/v1` |
| `experiment-run` | `experiment-run:reference-slice-contract-validation:2026-10-06` | `cal.artifact-type.experiment-run/v1` |
| `implementation` | `implementation:cyberalchemy-lab-governed-repository-toolchain` | `cal.artifact-type.implementation/v1` |
| `work` | `work:materialize-reference-slice-v1` | `cal.artifact-type.work/v1` |
| `principal` | `principal:repository-owner` | `cal.artifact-type.principal/v1` |
| `agent-instance` | `agent-instance:reference-slice-authoring:2026-10-06` | `cal.artifact-type.agent-instance/v1` |
| `agent-assignment` | `agent-assignment:materialize-reference-slice-v1` | `cal.artifact-type.agent-assignment/v1` |
| `context` | `context:reference-slice-authoring` | `cal.artifact-type.context/v1` |
| `context-request` | `context-request:reference-slice-authoring` | `cal.artifact-type.context-request/v1` |
| `project-state` | `project-state:cyberalchemy-v2-to-lab-migration:decision-0070` | `cal.artifact-type.project-state/v1` |
| `context-view` | `context-view:reference-slice-authoring:2026-10-06` | `cal.artifact-type.context-view/v1` |
| `agent-session` | `agent-session:reference-slice-authoring:2026-10-06` | `cal.artifact-type.agent-session/v1` |
| `evidence-set` | `evidence-set:reference-slice-validation` | `cal.artifact-type.evidence-set/v1` |
| `finding` | `finding:reference-slice-schema-and-relation-closure` | `cal.artifact-type.finding/v1` |
| `ontology` | `ontology:cyberalchemy-lab-reference-slice` | `cal.artifact-type.ontology/v1` |
| `semantic-event-history` | `semantic-event-history:reference-slice:project-cyberalchemy-v2-to-lab-migration` | `cal.artifact-type.semantic-event-history/v1` |
| `governance-event-history` | `governance-event-history:reference-slice:project-cyberalchemy-v2-to-lab-migration` | `cal.artifact-type.governance-event-history/v1` |
| `ontology-node` | `ontology-node:reference-slice:project-cyberalchemy-v2-to-lab-migration` | `cal.artifact-type.ontology-node/v2` |
| `semantic-event-history` | `semantic-event-history:reference-slice:product-cyberalchemy-lab` | `cal.artifact-type.semantic-event-history/v1` |
| `governance-event-history` | `governance-event-history:reference-slice:product-cyberalchemy-lab` | `cal.artifact-type.governance-event-history/v1` |
| `ontology-node` | `ontology-node:reference-slice:product-cyberalchemy-lab` | `cal.artifact-type.ontology-node/v2` |
| `semantic-event-history` | `semantic-event-history:reference-slice:product-capability-cyberalchemy-lab-governed-knowledge-lifecycle` | `cal.artifact-type.semantic-event-history/v1` |
| `governance-event-history` | `governance-event-history:reference-slice:product-capability-cyberalchemy-lab-governed-knowledge-lifecycle` | `cal.artifact-type.governance-event-history/v1` |
| `ontology-node` | `ontology-node:reference-slice:product-capability-cyberalchemy-lab-governed-knowledge-lifecycle` | `cal.artifact-type.ontology-node/v2` |
| `semantic-event-history` | `semantic-event-history:reference-slice:implementation-cyberalchemy-lab-governed-repository-toolchain` | `cal.artifact-type.semantic-event-history/v1` |
| `governance-event-history` | `governance-event-history:reference-slice:implementation-cyberalchemy-lab-governed-repository-toolchain` | `cal.artifact-type.governance-event-history/v1` |
| `ontology-node` | `ontology-node:reference-slice:implementation-cyberalchemy-lab-governed-repository-toolchain` | `cal.artifact-type.ontology-node/v2` |
| `semantic-event-history` | `semantic-event-history:reference-slice:research-inquiry-v2-to-lab-semantic-preservation` | `cal.artifact-type.semantic-event-history/v1` |
| `governance-event-history` | `governance-event-history:reference-slice:research-inquiry-v2-to-lab-semantic-preservation` | `cal.artifact-type.governance-event-history/v1` |
| `ontology-node` | `ontology-node:reference-slice:research-inquiry-v2-to-lab-semantic-preservation` | `cal.artifact-type.ontology-node/v2` |
| `semantic-event-history` | `semantic-event-history:reference-slice:experiment-design-reference-slice-contract-validation` | `cal.artifact-type.semantic-event-history/v1` |
| `governance-event-history` | `governance-event-history:reference-slice:experiment-design-reference-slice-contract-validation` | `cal.artifact-type.governance-event-history/v1` |
| `ontology-node` | `ontology-node:reference-slice:experiment-design-reference-slice-contract-validation` | `cal.artifact-type.ontology-node/v2` |
| `semantic-event-history` | `semantic-event-history:reference-slice:experiment-run-reference-slice-contract-validation-2026-10-06` | `cal.artifact-type.semantic-event-history/v1` |
| `governance-event-history` | `governance-event-history:reference-slice:experiment-run-reference-slice-contract-validation-2026-10-06` | `cal.artifact-type.governance-event-history/v1` |
| `ontology-node` | `ontology-node:reference-slice:experiment-run-reference-slice-contract-validation-2026-10-06` | `cal.artifact-type.ontology-node/v2` |
| `semantic-event-history` | `semantic-event-history:reference-slice:agent-instance-reference-slice-authoring-2026-10-06` | `cal.artifact-type.semantic-event-history/v1` |
| `governance-event-history` | `governance-event-history:reference-slice:agent-instance-reference-slice-authoring-2026-10-06` | `cal.artifact-type.governance-event-history/v1` |
| `ontology-node` | `ontology-node:reference-slice:agent-instance-reference-slice-authoring-2026-10-06` | `cal.artifact-type.ontology-node/v2` |
| `semantic-event-history` | `semantic-event-history:reference-slice:work-materialize-reference-slice-v1` | `cal.artifact-type.semantic-event-history/v1` |
| `governance-event-history` | `governance-event-history:reference-slice:work-materialize-reference-slice-v1` | `cal.artifact-type.governance-event-history/v1` |
| `ontology-node` | `ontology-node:reference-slice:work-materialize-reference-slice-v1` | `cal.artifact-type.ontology-node/v2` |
| `semantic-event-history` | `semantic-event-history:reference-slice:agent-session-reference-slice-authoring-2026-10-06` | `cal.artifact-type.semantic-event-history/v1` |
| `governance-event-history` | `governance-event-history:reference-slice:agent-session-reference-slice-authoring-2026-10-06` | `cal.artifact-type.governance-event-history/v1` |
| `ontology-node` | `ontology-node:reference-slice:agent-session-reference-slice-authoring-2026-10-06` | `cal.artifact-type.ontology-node/v2` |
| `semantic-event-history` | `semantic-event-history:reference-slice:context-view-reference-slice-authoring-2026-10-06` | `cal.artifact-type.semantic-event-history/v1` |
| `governance-event-history` | `governance-event-history:reference-slice:context-view-reference-slice-authoring-2026-10-06` | `cal.artifact-type.governance-event-history/v1` |
| `ontology-node` | `ontology-node:reference-slice:context-view-reference-slice-authoring-2026-10-06` | `cal.artifact-type.ontology-node/v2` |
| `semantic-event-history` | `semantic-event-history:reference-slice:project-state-cyberalchemy-v2-to-lab-migration-decision-0070` | `cal.artifact-type.semantic-event-history/v1` |
| `governance-event-history` | `governance-event-history:reference-slice:project-state-cyberalchemy-v2-to-lab-migration-decision-0070` | `cal.artifact-type.governance-event-history/v1` |
| `ontology-node` | `ontology-node:reference-slice:project-state-cyberalchemy-v2-to-lab-migration-decision-0070` | `cal.artifact-type.ontology-node/v2` |
| `semantic-event-history` | `semantic-event-history:reference-slice:typed-relation-reference-slice-project-contributes-to-product` | `cal.artifact-type.semantic-event-history/v1` |
| `governance-event-history` | `governance-event-history:reference-slice:typed-relation-reference-slice-project-contributes-to-product` | `cal.artifact-type.governance-event-history/v1` |
| `ontology-edge` | `ontology-edge:reference-slice:01` | `cal.artifact-type.ontology-edge/v1` |
| `semantic-event-history` | `semantic-event-history:reference-slice:typed-relation-reference-slice-capability-member-of-product` | `cal.artifact-type.semantic-event-history/v1` |
| `governance-event-history` | `governance-event-history:reference-slice:typed-relation-reference-slice-capability-member-of-product` | `cal.artifact-type.governance-event-history/v1` |
| `ontology-edge` | `ontology-edge:reference-slice:02` | `cal.artifact-type.ontology-edge/v1` |
| `semantic-event-history` | `semantic-event-history:reference-slice:typed-relation-reference-slice-implementation-realizes-capability` | `cal.artifact-type.semantic-event-history/v1` |
| `governance-event-history` | `governance-event-history:reference-slice:typed-relation-reference-slice-implementation-realizes-capability` | `cal.artifact-type.governance-event-history/v1` |
| `ontology-edge` | `ontology-edge:reference-slice:03` | `cal.artifact-type.ontology-edge/v1` |
| `semantic-event-history` | `semantic-event-history:reference-slice:typed-relation-reference-slice-research-member-of-project` | `cal.artifact-type.semantic-event-history/v1` |
| `governance-event-history` | `governance-event-history:reference-slice:typed-relation-reference-slice-research-member-of-project` | `cal.artifact-type.governance-event-history/v1` |
| `ontology-edge` | `ontology-edge:reference-slice:04` | `cal.artifact-type.ontology-edge/v1` |
| `semantic-event-history` | `semantic-event-history:reference-slice:typed-relation-reference-slice-design-engages-inquiry` | `cal.artifact-type.semantic-event-history/v1` |
| `governance-event-history` | `governance-event-history:reference-slice:typed-relation-reference-slice-design-engages-inquiry` | `cal.artifact-type.governance-event-history/v1` |
| `ontology-edge` | `ontology-edge:reference-slice:05` | `cal.artifact-type.ontology-edge/v1` |
| `semantic-event-history` | `semantic-event-history:reference-slice:typed-relation-reference-slice-run-realizes-design` | `cal.artifact-type.semantic-event-history/v1` |
| `governance-event-history` | `governance-event-history:reference-slice:typed-relation-reference-slice-run-realizes-design` | `cal.artifact-type.governance-event-history/v1` |
| `ontology-edge` | `ontology-edge:reference-slice:06` | `cal.artifact-type.ontology-edge/v1` |
| `semantic-event-history` | `semantic-event-history:reference-slice:typed-relation-reference-slice-agent-performs-work` | `cal.artifact-type.semantic-event-history/v1` |
| `governance-event-history` | `governance-event-history:reference-slice:typed-relation-reference-slice-agent-performs-work` | `cal.artifact-type.governance-event-history/v1` |
| `ontology-edge` | `ontology-edge:reference-slice:07` | `cal.artifact-type.ontology-edge/v1` |
| `semantic-event-history` | `semantic-event-history:reference-slice:typed-relation-reference-slice-session-consumes-context-view` | `cal.artifact-type.semantic-event-history/v1` |
| `governance-event-history` | `governance-event-history:reference-slice:typed-relation-reference-slice-session-consumes-context-view` | `cal.artifact-type.governance-event-history/v1` |
| `ontology-edge` | `ontology-edge:reference-slice:08` | `cal.artifact-type.ontology-edge/v1` |
| `semantic-event-history` | `semantic-event-history:reference-slice:typed-relation-reference-slice-project-state-member-of-project` | `cal.artifact-type.semantic-event-history/v1` |
| `governance-event-history` | `governance-event-history:reference-slice:typed-relation-reference-slice-project-state-member-of-project` | `cal.artifact-type.governance-event-history/v1` |
| `ontology-edge` | `ontology-edge:reference-slice:09` | `cal.artifact-type.ontology-edge/v1` |
| `ontology-cut` | `ontology-cut:cyberalchemy-lab-reference-slice:2026-10-06` | `cal.artifact-type.ontology-cut/v1` |
| `ontology-view` | `ontology-view:cyberalchemy-lab-reference-slice:2026-10-06` | `cal.artifact-type.ontology-view/v1` |

## Typed Relations

| Relation Kind | Source | Target |
|---|---|---|
| `relation.addresses-intent` | `product:cyberalchemy-lab` | `intent:operationalize-cyberalchemy-lab-model` |
| `relation.member-of` | `product-capability:cyberalchemy-lab:governed-knowledge-lifecycle` | `product:cyberalchemy-lab` |
| `relation.derives-from` | `product-capability:cyberalchemy-lab:governed-knowledge-lifecycle` | `product-thesis:cyberalchemy-lab-governed-work` |
| `relation.addresses-intent` | `project:cyberalchemy-v2-to-lab-migration` | `intent:operationalize-cyberalchemy-lab-model` |
| `relation.contributes-to` | `project:cyberalchemy-v2-to-lab-migration` | `product:cyberalchemy-lab` |
| `relation.member-of` | `goal:materialize-definition-complete-reference-slice` | `project:cyberalchemy-v2-to-lab-migration` |
| `relation.addresses-intent` | `goal:materialize-definition-complete-reference-slice` | `intent:operationalize-cyberalchemy-lab-model` |
| `relation.member-of` | `capability-realization-binding:governed-repository-toolchain` | `project:cyberalchemy-v2-to-lab-migration` |
| `relation.governed-by` | `challenge-contract:cyberalchemy-lab-reference-slice` | `policy:reference-slice-governance` |
| `relation.member-of` | `research-inquiry:v2-to-lab-semantic-preservation` | `project:cyberalchemy-v2-to-lab-migration` |
| `relation.addresses-intent` | `research-inquiry:v2-to-lab-semantic-preservation` | `intent:operationalize-cyberalchemy-lab-model` |
| `relation.member-of` | `experiment-design:reference-slice-contract-validation` | `project:cyberalchemy-v2-to-lab-migration` |
| `relation.engages-inquiry` | `experiment-design:reference-slice-contract-validation` | `research-inquiry:v2-to-lab-semantic-preservation` |
| `relation.tests-hypothesis` | `experiment-design:reference-slice-contract-validation` | `hypothesis:reference-slice-preserves-orthogonality` |
| `relation.evaluates` | `experiment-design:reference-slice-contract-validation` | `product-capability:cyberalchemy-lab:governed-knowledge-lifecycle` |
| `relation.member-of` | `experiment-run:reference-slice-contract-validation:2026-10-06` | `project:cyberalchemy-v2-to-lab-migration` |
| `relation.realizes` | `experiment-run:reference-slice-contract-validation:2026-10-06` | `experiment-design:reference-slice-contract-validation` |
| `relation.engages-inquiry` | `experiment-run:reference-slice-contract-validation:2026-10-06` | `research-inquiry:v2-to-lab-semantic-preservation` |
| `relation.evaluates` | `experiment-run:reference-slice-contract-validation:2026-10-06` | `product-capability:cyberalchemy-lab:governed-knowledge-lifecycle` |
| `relation.member-of` | `evidence-set:reference-slice-validation` | `project:cyberalchemy-v2-to-lab-migration` |
| `relation.derives-from` | `evidence-set:reference-slice-validation` | `experiment-run:reference-slice-contract-validation:2026-10-06` |
| `relation.derives-from` | `finding:reference-slice-schema-and-relation-closure` | `evidence-set:reference-slice-validation` |
| `relation.engages-inquiry` | `finding:reference-slice-schema-and-relation-closure` | `research-inquiry:v2-to-lab-semantic-preservation` |
| `relation.evidence-bears-on` | `evidence-set:reference-slice-validation` | `finding:reference-slice-schema-and-relation-closure` |
| `relation.evidence-bears-on` | `evidence-set:reference-slice-validation` | `hypothesis:reference-slice-preserves-orthogonality` |
| `relation.realizes` | `implementation:cyberalchemy-lab-governed-repository-toolchain` | `product-capability:cyberalchemy-lab:governed-knowledge-lifecycle` |
| `relation.member-of` | `work:materialize-reference-slice-v1` | `project:cyberalchemy-v2-to-lab-migration` |
| `relation.acts-for` | `agent-instance:reference-slice-authoring:2026-10-06` | `principal:repository-owner` |
| `relation.member-of` | `agent-instance:reference-slice-authoring:2026-10-06` | `agent-session:reference-slice-authoring:2026-10-06` |
| `relation.member-of` | `agent-assignment:materialize-reference-slice-v1` | `project:cyberalchemy-v2-to-lab-migration` |
| `relation.addresses-intent` | `agent-assignment:materialize-reference-slice-v1` | `intent:operationalize-cyberalchemy-lab-model` |
| `relation.performs` | `agent-instance:reference-slice-authoring:2026-10-06` | `work:materialize-reference-slice-v1` |
| `relation.performs` | `agent-instance:reference-slice-authoring:2026-10-06` | `experiment-run:reference-slice-contract-validation:2026-10-06` |
| `relation.member-of` | `project-state:cyberalchemy-v2-to-lab-migration:decision-0070` | `project:cyberalchemy-v2-to-lab-migration` |
| `relation.member-of` | `context:reference-slice-authoring` | `project:cyberalchemy-v2-to-lab-migration` |
| `relation.governed-by` | `context:reference-slice-authoring` | `policy:reference-slice-governance` |
| `relation.frames` | `context:reference-slice-authoring` | `product:cyberalchemy-lab` |
| `relation.frames` | `context:reference-slice-authoring` | `project:cyberalchemy-v2-to-lab-migration` |
| `relation.requests-resolution-of` | `context-request:reference-slice-authoring` | `context:reference-slice-authoring` |
| `relation.fulfills-request` | `context-view:reference-slice-authoring:2026-10-06` | `context-request:reference-slice-authoring` |
| `relation.derives-from` | `context-view:reference-slice-authoring:2026-10-06` | `context:reference-slice-authoring` |
| `relation.consumes-view` | `agent-session:reference-slice-authoring:2026-10-06` | `context-view:reference-slice-authoring:2026-10-06` |
| `relation.uses-tool` | `agent-session:reference-slice-authoring:2026-10-06` | `implementation:cyberalchemy-lab-governed-repository-toolchain` |
| `relation.consumes-view` | `agent-session:reference-slice-authoring:2026-10-06` | `ontology-view:cyberalchemy-lab-reference-slice:2026-10-06` |

## Authority boundary

This deterministic candidate demonstrates one coherent slice of the admitted model. It creates no authority or runtime effect and requires a later exact owner-reviewed admission proposal before any instance becomes authoritative.

This package is ready for owner review. It is not an admission proposal and contains no authorization file.
