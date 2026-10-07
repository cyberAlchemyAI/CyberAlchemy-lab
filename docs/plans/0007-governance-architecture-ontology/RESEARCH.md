# Governance architecture ontology: research baseline

Status: research and planning only, 2026-10-06. Authority effect: none.

## Question and scope

The requested result is a persistent, source-bound graph that can start at
Authority, Provenance, or Lifecycle and show the definitions, contracts,
governed records, implementation components, evidence, and gaps connected to
that lens. The graph must support current-state inspection after repository
changes. It must not become a second admission registry, event history, or
permission evaluator.

This research uses the local repository as the source of its current-state
claims. External standards below are comparisons, not imported Lab contracts.

## Current repository evidence

| Surface | What exists | Boundary for this plan |
| --- | --- | --- |
| [Definition registry](../../../authority/definitions/registry.json) and [index](../../../authority/definitions/DEFINITIONS-INDEX.md) | Authority, Provenance, the governance-axis independence invariant, ontology carriers, event histories, Policy, Decision, and Project State have effective admitted Definition entries. | The source Definition JSON may still contain candidate wording; effective admission must be resolved through registry and decisions. No standalone canonical Definition named `Lifecycle` was found in the index. The Lifecycle lens is currently a composition in the candidate governance module. |
| [D70 relation registry](../../../authority/admissions/definition-complete-lab-model/v1/relation-kind-registry.json) | 40 admitted Relation Kinds with closed endpoint pairs, including `relation.scopes-authority-over`, `relation.declares-effect-on`, `relation.originates-from`, `relation.derives-from`, and `relation.successor-of`. | A lens label is not a global Relation Kind. An architecture edge does not extend an admitted endpoint pair. |
| [Typed Connection Extension Rule](../../../authority/definitions/candidates/0012-typed-connection-extension-rule/definitions/typed-connection-extension-rule/v1/DEFINITION.md) | Global extensions need an exact effective predecessor, ordered endpoint pair, qualifier schema, owner, evidence, contestability, and admission. Ontology-local edges remain local. | The architecture graph must keep local traceability edges and global Typed Relations in separate namespaces. |
| [D70 Artifact Type registry](../../../authority/admissions/definition-complete-lab-model/v1/artifact-type-registry.json) and [D72 additions](../../../authority/admissions/project-state-bootstrap/v1/registries/artifact-type-registry.json) | Ontology Node/v2, Ontology Edge/v1, Manifest/v1, Cut/v1, View/v1, and Project history carriers are admitted contracts. | Carrier admission does not admit a new governance ontology instance or its edges. Inspect exact schema fit before proposing a new carrier. |
| [D71 foundation](../../../authority/admissions/cyberalchemy-lab-operational-foundation/v1/bundle.json), [D72 bootstrap](../../../authority/admissions/project-state-bootstrap/v1/bundle.json), [D73 Agent episode](../../../authority/admissions/first-governed-agent-work-episode/v1/bundle.json) | Exact admitted instances and relations establish an initial Project State, two successors through Decision 0072, Project semantic/governance event histories, and one bounded Agent episode. D73 has zero runtime activations. | These are the first real graph subjects. D73 source copies retain candidate fields; its admission overlay supplies effective state. The last admitted Project State covers Decision 0072, not its own admission Decision 0073. |
| [D73 operational ontology](../../../authority/admissions/first-governed-agent-work-episode/v1/instances/artifacts/ontology.json) | A bounded Agent view has two Ontology Nodes, one projected `member-of` edge, one Cut, and one View. | It is an operational-context projection, not the requested repository governance architecture graph. |
| [Governance module candidate 0001](../../../authority/governance/candidates/0001-three-lens-module/MODULE.md) and [repository map](../../../authority/governance/candidates/0001-three-lens-module/REPOSITORY-MAP.md) | Read-only Authority, Provenance, Lifecycle posture projection over D71-D72 instances; 44 navigation zones over the inventory. The module is unadmitted. | The projector does not yet include D73 or implementation-level traceability. Path classification is not semantic mapping or lifecycle status. |
| [Repository inventory](../../../.arcanum/inventory/README.md) | Generated file and content indexes, including code declarations and digests; the saved manifest reports 10,797 files. | Refresh before claiming current coverage. A file path or code declaration is a discovery candidate, not automatically an Ontology Node. |
| [DomainSpec product ontology](../../../craft/ontology/README.md) | A separate, canonical business/system/bridge traceability package with source digests, explicit residue, and validation receipts. | Reuse its evidence-bound pattern, not its DomainSpec identity or authority. |
| [Ontology graph read-model prototype](../../../ontology-lifecycle/runtime-candidates/cal-ontology-graph-read-model/v1/README.md) | An isolated, disposable Rust query model supports incoming/outgoing traversal and bounded multi-hop reads over canonical ontology events. | It is candidate technology for a later adapter evaluation. It is not an admitted governance graph implementation or authority source. |
| [Ontology lifecycle integration plan](../0003-d65-native-ontology-integration/PLAN.md) and [v4 source runtime](../../../implementation/bindings/ontology-product-event-runtime/v4/README.md) | Event-sourced ontology work, product approval, bindings, and local prototype evidence exist at distinct stages. | This plan creates no activation, migration cutover, or claim of a persistent service. |

## Non-collapse constraints

1. A Definition, Artifact Type, instance, Ontology Node, code symbol, and file are different identities.
2. A global Typed Relation and an Ontology Edge projection are different records. An ontology-local architecture edge grants no global endpoint connection.
3. Semantic and governance event histories are replay sources where their contracts apply; Cuts, Views, inventories, and graph indexes are derived.
4. Authority, Provenance, and Lifecycle are inspection lenses over independently reported kind, status, evidence confidence, commitment, provenance, owner, and residue.
5. Candidate validation, source presence, a code symbol, or a passing receipt never grants admission, action permission, domain fulfillment, or runtime activation.
6. Business meaning and system behavior need separate evidence; an alignment bridge cites both sides or remains an explicit gap.

## Findings that shape the DAG

- The smallest proof is a Lifecycle traversal over D71-D73 Project State, its transition evidence, and the implementation that reports it. This has exact admitted subjects and observable gaps.
- Authority and Provenance can be built as separate slices after the shared graph contract and exact-state resolver exist; they converge at the implementation bridge and unified query.
- A fresh source inventory and explicit coverage obligations are needed for ongoing understanding. Indexing every file as an ontology subject would create false semantics.
- No reusable Project history writer, general permission evaluator, or live runtime observer is established by governance module candidate 0001. The graph can show these as gaps.
- Review of the graph contract, ontology instance, and any proposed global Relation Kind extension must remain separate decisions. A read-only candidate can be useful before admission.

## External comparisons

- [W3C PROV-O](https://www.w3.org/TR/prov-o/) separates entities, activities, agents, derivation, and attribution. It supports the plan's decision to keep source, transformation, and actor identities distinct; Lab Definitions and Relation Kinds control actual semantics.
- [W3C SHACL](https://www.w3.org/TR/shacl/) separates a data graph, a shapes graph, and a validation report. It is a possible validation pattern, not a decision to adopt RDF or SHACL in the first slice.

## Research limits

This is a source inspection, not a fresh repository validation, runtime test, or proof that the saved inventory is current. No conventions, admissions, implementations, or runtime states were changed.
