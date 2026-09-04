<!-- GENERATED FILE: edit normalization.json and run render.py. -->

# CyberAlchemy v2 definition migration normalization

> Human projection generated from `normalization.json`; it is not canonical.

- Normalization: `CAL-NORMALIZE-01`
- Status: `validated-draft-pending-owner-review`
- Decision posture: `owner-selected-for-draft-materialization`
- Authority effect: `none`
- Target effect: deduplicated migration planning only

## Outcome

| Revise | Reclassify | Split | Collapse | Drop | Active | Withdrawn preserved |
| --- | --- | --- | --- | --- | --- | --- |
| 17 | 19 | 23 | 6 | 4 | 69 | 12 |

## Normalization rules

1. Create a distinct artifact type only when source direction, validation closure, lifecycle, authority behavior, or relation semantics differ materially.
2. Use one lifecycle-profile artifact type with owner-selected vocabularies instead of embedding lifecycle state in stable semantic artifacts.
3. Use one evaluation envelope with evaluation profiles unless a result has a distinct authority or execution contract.
4. Use typed-relation records and relation kinds instead of redundant inverse lists or directory-inferred membership.
5. Keep construction, implementation, model-instance, and capability-realization bindings distinct because their closure and validation obligations differ.
6. Keep the machine record canonical and generate every human projection deterministically.
7. Treat Product, Project, CAV2 Context, DDD Bounded Context, capability instance, artifact type, semantic kind, authority kind, and directory as independent axes.
8. Do not import CyberAlchemy-v2 source bytes as admitted Lab authority without exact source admission and an owner decision.
9. Preserve dropped and withdrawn identifiers as lineage or tombstone evidence; never silently reuse them.

## Distill trace

Optimization goal: Minimize artifact-type duplication without erasing distinct semantic, authority, lifecycle, binding, or validation obligations.

Smallest coherent unit: **normalized migration record** — Connect one legacy decision to deduplicated semantic concepts, artifact types, profiles, relation kinds, owner scopes, derived surfaces, and migration dependencies.

### Round 1

- Proposal: Normalize repeated lifecycle, evaluation, policy, receipt, and typed-relation mechanics into reusable artifact families.
- Objection (semantic-over-collapse): A generic family could erase domain-specific closure rules and make one schema appear to validate every meaning.
- Reconciliation: Keep shared envelopes but require exact profiles and owner-local schemas; profile validity never proves domain meaning or authority.

### Round 2

- Proposal: Normalize every proposed binding into one generic binding type.
- Objection (requisite-variety): Construction, implementation, model-instance, and capability-realization bindings have different endpoint kinds, predecessor closure, invalidation rules, and conformance obligations.
- Reconciliation: Reject the generic binding type. Preserve four specialized binding artifact types over shared artifact mechanics.

Verdict: `pass-draft`

## Owner scopes

| ID | Name | DDD bounded-context status | Boundary note |
| --- | --- | --- | --- |
| scope.shared-authority | Shared semantic authority | unselected | An owner scope, not an inferred bounded context. |
| scope.repository-governance | Repository governance | unselected | Policies and repository integrity; Governance is not automatically a bounded context. |
| scope.product | Product meaning | unselected | Product is not automatically a bounded context. |
| scope.coordination | Project and goal coordination | unselected | Coordination identity is independent from domain meaning. |
| scope.knowledge-development | Research, experiment, and evidence | unselected | Candidate owner scope for knowledge-development semantics. |
| scope.context-resolution | Context resolution | unselected | CAV2 Context remains distinct from DDD Bounded Context. |
| scope.construction | Craft-governed construction | unselected | Coordinates construction artifacts without owning Craft language semantics. |
| scope.people-teams | People and teams | candidate-requires-owner-selection | No bounded-context admission is asserted here. |
| scope.ux-ui | UX and UI knowledge | candidate-requires-owner-selection | Capability ownership and bounded-context selection remain separate. |
| scope.lineage | Lineage and source admission | unselected | Owns mappings and tombstones, not imported meaning. |
| scope.craft | Craft product authority | external-product-authority | RN-2 successor of DomainSpec; legacy DS identifiers may be preserved as lineage. |

## Artifact types

| ID | Name | Family | Distinct validation purpose |
| --- | --- | --- | --- |
| type.artifact-type | Artifact Type | mechanics | Defines permitted canonical record and projection mechanics. |
| type.definition | Definition | semantic-authority | Defines scoped term meaning with formal, plain-language, and domain-context voices. |
| type.axiom | Axiom | semantic-authority | Declares a foundational proposition relative to an exact theory or context. |
| type.premise | Premise | semantic-authority | Declares a defeasible proposition adopted to proceed. |
| type.hypothesis | Hypothesis | semantic-authority | Declares a testable proposition without load-bearing adoption. |
| type.invariant | Invariant | semantic-authority | Defines a scoped must-hold predicate and violation semantics. |
| type.constitution | Constitution | semantic-authority | Carries selector-bound normative authority after exact adoption. |
| type.decision | Decision | semantic-authority | Records an authorized choice bound to exact candidate bytes and scope. |
| type.schema | Schema | semantic-authority | Defines admissible representation and static constraints only. |
| type.schema-change | Schema Change | governance | Binds exact preimage, postimage, compatibility, migration, and regression obligations. |
| type.method | Method | practice | Defines a repeatable transformation independently from executions. |
| type.discipline | Discipline | practice | Defines a stewarded recurring cross-capability practice. |
| type.architecture-pattern | Architecture Pattern | practice | Defines a reusable architecture response with forces and consequences. |
| type.policy | Policy | governance | Defines scoped decision or behavior constraints through an exact policy profile. |
| type.lifecycle-profile | Lifecycle Profile | governance | Defines owner-selected status vocabulary and transitions without embedding posture in subjects. |
| type.authority-model | Authority Model | governance | Defines authority kinds, claims, operations, effects, and conflict rules. |
| type.authority-claim | Authority Claim | governance | Claims scoped authority over an exact object and operation. |
| type.responsibility | Responsibility | governance | Defines an accountable obligation without implying authority. |
| type.gate | Gate | governance | Defines an effect boundary, required checks, and decision route. |
| type.evaluation | Evaluation | evidence | Records bounded results under an exact evaluation profile; authority_effect remains none. |
| type.typed-relation | Typed Relation | mechanics | Records directed owner-qualified coupling without interpreting owner-local semantics. |
| type.source-admission | Source Admission | lineage | Binds exact external bytes and an owner admission posture. |
| type.lineage-map | Lineage Map | lineage | Maps legacy identities to active successors without transferring authority. |
| type.withdrawal-record | Withdrawal Record | lineage | Permanently reserves a retired identifier and names its successor authority. |
| type.residue | Residue | evidence | Records meaningful information not carried by the current representation. |
| type.evidence-set | Evidence Set | evidence | Aggregates exact supporting and counterevidence references without becoming a conclusion. |
| type.receipt | Receipt | evidence | Records what one bounded operation did and its exact inputs and outputs. |
| type.projection-spec | Projection Specification | mechanics | Defines deterministic generation of a non-authoritative view. |
| type.intent | Intent | coordination | Records attributable desired direction before a testable outcome is fixed. |
| type.product | Product | product | Defines stable product identity independently from repositories and projects. |
| type.product-thesis | Product Thesis | product | Defines a versioned product value proposition and revision criteria. |
| type.product-capability | Product Capability | product | Defines a stable repeatable product outcome independently from realization. |
| type.capability-instance | Capability Instance | product | Defines a locally owned specialization of an exact parent capability. |
| type.capability-realization-binding | Capability Realization Binding | binding | Maps product capability semantics to one or more realizations. |
| type.goal | Goal | coordination | Defines one desired future outcome owned by exactly one Project. |
| type.project | Project | coordination | Defines stable coordination identity without mutable membership indexes. |
| type.research-inquiry | Research Inquiry | knowledge-development | Defines a bounded question, scope, and exact method reference. |
| type.research-run | Research Run | knowledge-development | Records immutable execution of a Research Inquiry and Method. |
| type.finding | Finding | knowledge-development | Records bounded synthesis from exact evidence and counterevidence. |
| type.experiment-design | Experiment Design | knowledge-development | Defines a controlled test independently from its execution. |
| type.experiment-run | Experiment Run | knowledge-development | Records immutable execution of an exact Experiment Design. |
| type.observation | Observation | knowledge-development | Records a direct occurrence or readout without interpretation. |
| type.measurement-method | Measurement Method | knowledge-development | Defines how a property is measured under declared conditions. |
| type.measurement-result | Measurement Result | knowledge-development | Records the output and uncertainty of one exact Measurement Method execution. |
| type.ontology | Ontology | semantic-model | Defines a versioned owner-scoped semantic model and typed relations. |
| type.context | Context | context | Defines stable contextual purpose and relevance without selected source contents. |
| type.context-profile | Context Profile | context | Defines permitted anchors, cardinalities, identity fields, and successor rules. |
| type.context-request | Context Request | context | Defines one bounded request against exact Context and policy versions. |
| type.context-view | Context View | context | Records an immutable machine-canonical source selection and residue set. |
| type.construction-profile | Construction Profile | construction | Defines required construction stages and typed predecessor rules. |
| type.construction-binding | Construction Binding | binding | Binds one subject and epoch to an exact construction dependency graph. |
| type.implementation-binding | Implementation Binding | binding | Maps an admitted system model to exact implementation targets and obligations. |
| type.model-instance-binding | Model Instance Binding | binding | Separates parent and instance authority, inherited contract, and extension scope. |
| type.person-reference | Person Reference | people-teams | Represents a human minimally within one declared identity scope. |
| type.identity-claim | Identity Claim | people-teams | Claims that a reference or identifier represents a human under bounded evidence. |
| type.team | Team | people-teams | Defines stable collective coordination identity. |
| type.team-membership | Team Membership | people-teams | Records independently lifecycle-managed Person-to-Team membership. |
| type.role | Role | people-teams | Defines scoped expected functions without granting authority. |
| type.role-assignment | Role Assignment | people-teams | Binds a Person Reference or Team to a Role for an exact scope and period. |

## Profiles

| ID | Name | Artifact type |
| --- | --- | --- |
| profile.repository-layout-policy | Repository Layout Policy | type.policy |
| profile.source-selection-policy | Source Selection Policy | type.policy |
| profile.authority-aware-navigation | Authority-Aware Navigation Policy | type.policy |
| profile.challenge | Challenge Policy | type.policy |
| profile.retention | Retention Policy | type.policy |
| profile.semantic-consistency | Semantic Consistency Policy | type.policy |
| profile.publication | Publication Policy | type.policy |
| profile.cross-context-generalization | Cross-Context Generalization Policy | type.policy |
| profile.context-resolution | Context Resolution Policy | type.policy |
| profile.recursion | Recursion Policy | type.policy |
| profile.architecture-pattern-promotion | Architecture Pattern Promotion Profile | type.lifecycle-profile |
| profile.ux-authority-promotion | UX/UI Authority Promotion Profile | type.lifecycle-profile |
| profile.ux-evidence-compatibility | UX/UI Evidence Compatibility Profile | type.evaluation |
| profile.authority-lifecycle | Authority Lifecycle Profile | type.lifecycle-profile |
| profile.goal-lifecycle | Goal Lifecycle Profile | type.lifecycle-profile |
| profile.project-lifecycle | Project Lifecycle Profile | type.lifecycle-profile |
| profile.product-thesis-lifecycle | Product Thesis Lifecycle Profile | type.lifecycle-profile |
| profile.context-lifecycle | Context Lifecycle Profile | type.lifecycle-profile |
| profile.capability-lifecycle | Capability Lifecycle Profile | type.lifecycle-profile |
| profile.team-lifecycle | Team Lifecycle Profile | type.lifecycle-profile |
| profile.gate-evaluation | Gate Evaluation Profile | type.evaluation |
| profile.goal-evaluation | Goal Evaluation Profile | type.evaluation |
| profile.project-evaluation | Project Evaluation Profile | type.evaluation |
| profile.product-thesis-evaluation | Product Thesis Evaluation Profile | type.evaluation |
| profile.model-instance-binding-evaluation | Model Instance Binding Evaluation Profile | type.evaluation |
| profile.construction-evaluation | Construction Evaluation Profile | type.evaluation |
| profile.capability-conformance | Capability Conformance Profile | type.evaluation |

## Typed relation kinds

| ID | Direction | Inverse projection |
| --- | --- | --- |
| relation.belongs-to-product | subject-to-product | contains-capability-or-thesis |
| relation.belongs-to-project | subject-to-project | project-members |
| relation.originates-from | artifact-to-source | source-derivatives |
| relation.successor-of | successor-to-predecessor | successors |
| relation.supersedes | new-to-old | superseded-by |
| relation.uses-method | execution-to-method | method-executions |
| relation.derives-from | derived-to-source | derived-artifacts |
| relation.supports | evidence-to-claim | supported-by |
| relation.contradicts | evidence-to-claim | counterevidence |
| relation.evaluates | evaluation-to-subject | evaluations |
| relation.governed-by | subject-to-policy-or-constitution | governed-subjects |
| relation.authorizes | decision-to-effect | authorized-by |
| relation.adopts | decision-to-version | adopted-by |
| relation.realizes | realization-to-capability | realizations |
| relation.instance-of | instance-to-parent | instances |
| relation.compiles-to | authored-source-to-generated-output | compiled-from |
| relation.binds-implementation | implementation-to-system-model | implementation-bindings |
| relation.frames | context-to-subject | contexts |
| relation.references-bounded-context | cav2-context-to-ddd-context | referencing-contexts |
| relation.member-of | person-reference-to-team | team-roster |
| relation.assigned-role | assignee-to-role | role-assignees |
| relation.assigned-responsibility | assignee-to-responsibility | responsible-parties |
| relation.represents-person | person-reference-to-person | person-references |
| relation.identity-link | person-reference-to-person-reference | linked-identities |
| relation.claims-authority-over | authority-claim-to-object | authority-claims |

## Semantic concepts

| ID | Term | Kind | Carrier | Owner scope |
| --- | --- | --- | --- | --- |
| semantic.stable-repository | Stable Repository | definition | type.definition | scope.repository-governance |
| semantic.source-ledgered-consolidation | Source-Ledgered Consolidation | method | type.method | scope.lineage |
| semantic.authority-surface | Authority Surface | definition | type.definition | scope.shared-authority |
| semantic.stable-repository-stewardship | Stable Repository Stewardship | discipline | type.discipline | scope.repository-governance |
| semantic.cyberalchemy-repository-identity | CyberAlchemy Repository Identity | definition | type.definition | scope.lineage |
| semantic.typed-coupling-invariant | Typed Coupling Invariant | invariant | type.invariant | scope.shared-authority |
| semantic.residue-escalation-method | Residue Escalation Method | method | type.method | scope.shared-authority |
| semantic.residue | Residue | definition | type.definition | scope.shared-authority |
| semantic.ontology | Ontology | definition | type.definition | scope.shared-authority |
| semantic.craft-method | Craft Method | method | type.method | scope.craft |
| semantic.cyberalchemy-construction-method | CyberAlchemy Construction Method | method | type.method | scope.construction |
| semantic.work-state-continuity-capability | Work-State Continuity Capability | product-capability | type.product-capability | scope.product |
| semantic.four-facet-artifact-invariant | Four-Facet Artifact Invariant | invariant | type.invariant | scope.shared-authority |
| semantic.classification-orthogonality-invariant | Classification Orthogonality Invariant | invariant | type.invariant | scope.shared-authority |
| semantic.classification-axis | Classification Axis | definition | type.definition | scope.shared-authority |
| semantic.governance-axis-independence-invariant | Governance-Axis Independence Invariant | invariant | type.invariant | scope.shared-authority |
| semantic.schema-evolution-invariant | Schema Evolution Invariant | invariant | type.invariant | scope.shared-authority |
| semantic.append-only-event-ledger-pattern | Append-Only Event Ledger | architecture-pattern | type.architecture-pattern | scope.repository-governance |
| semantic.residue-measurement | Residue Measurement | definition | type.definition | scope.knowledge-development |
| semantic.constraint-cycle-safety-invariant | Constraint-Cycle Safety Invariant | invariant | type.invariant | scope.shared-authority |
| semantic.root-axis-independence-invariant | Root-Axis Independence Invariant | invariant | type.invariant | scope.shared-authority |
| semantic.bounded-self-application-invariant | Bounded Self-Application Invariant | invariant | type.invariant | scope.shared-authority |
| semantic.semantic-primitive | Semantic Primitive | definition | type.definition | scope.shared-authority |
| semantic.method | Method | definition | type.definition | scope.shared-authority |
| semantic.definition | Definition | definition | type.definition | scope.shared-authority |
| semantic.authority | Authority | definition | type.definition | scope.shared-authority |
| semantic.authority-claim | Authority Claim | definition | type.definition | scope.shared-authority |
| semantic.responsibility | Responsibility | definition | type.definition | scope.shared-authority |
| semantic.provenance | Provenance | definition | type.definition | scope.lineage |
| semantic.traceability | Traceability | definition | type.definition | scope.lineage |
| semantic.gate | Gate | definition | type.definition | scope.shared-authority |
| semantic.claim-support-compatibility-invariant | Claim-Support Compatibility Invariant | invariant | type.invariant | scope.shared-authority |
| semantic.intent | Intent | definition | type.definition | scope.coordination |
| semantic.contestability-policy | Contestability Policy | policy | type.policy | scope.shared-authority |
| semantic.authority-model | Authority Model | definition | type.definition | scope.shared-authority |
| semantic.projection-specification | Projection Specification | definition | type.definition | scope.shared-authority |
| semantic.govern-ux-ui-knowledge-capability | Govern UX/UI Knowledge | product-capability | type.product-capability | scope.ux-ui |
| semantic.experience-evidence-formation-method | Experience Evidence Formation Method | method | type.method | scope.ux-ui |
| semantic.interface-claim-support-compatibility-invariant | Interface Claim-Support Compatibility Invariant | invariant | type.invariant | scope.ux-ui |
| semantic.authority-promotion | Authority Promotion | definition | type.definition | scope.shared-authority |
| semantic.closed-authority-kind-invariant | Closed Authority-Kind Invariant | invariant | type.invariant | scope.shared-authority |
| semantic.discipline | Discipline | definition | type.definition | scope.shared-authority |
| semantic.artifact | Artifact | definition | type.definition | scope.shared-authority |
| semantic.canonical-representation-invariant | Canonical Representation Invariant | invariant | type.invariant | scope.shared-authority |
| semantic.artifact-lifetime | Artifact Lifetime | definition | type.definition | scope.shared-authority |
| semantic.axiom | Axiom | definition | type.definition | scope.shared-authority |
| semantic.invariant | Invariant | definition | type.definition | scope.shared-authority |
| semantic.premise | Premise | definition | type.definition | scope.shared-authority |
| semantic.hypothesis | Hypothesis | definition | type.definition | scope.shared-authority |
| semantic.schema | Schema | definition | type.definition | scope.shared-authority |
| semantic.exact-publication-authorization-invariant | Exact Publication Authorization Invariant | invariant | type.invariant | scope.repository-governance |
| semantic.constitution | Constitution | definition | type.definition | scope.shared-authority |
| semantic.goal | Goal | definition | type.definition | scope.coordination |
| semantic.project | Project | definition | type.definition | scope.coordination |
| semantic.research-inquiry | Research Inquiry | definition | type.definition | scope.knowledge-development |
| semantic.research-run | Research Run | definition | type.definition | scope.knowledge-development |
| semantic.evidence-set | Evidence Set | definition | type.definition | scope.knowledge-development |
| semantic.finding | Finding | definition | type.definition | scope.knowledge-development |
| semantic.experiment-design | Experiment Design | definition | type.definition | scope.knowledge-development |
| semantic.experiment-run | Experiment Run | definition | type.definition | scope.knowledge-development |
| semantic.observation | Observation | definition | type.definition | scope.knowledge-development |
| semantic.product | Product | definition | type.definition | scope.product |
| semantic.product-thesis | Product Thesis | definition | type.definition | scope.product |
| semantic.parent-instance-authority-separation-invariant | Parent-Instance Authority Separation Invariant | invariant | type.invariant | scope.shared-authority |
| semantic.craft-governed-construction-invariant | Craft-Governed Construction Invariant | invariant | type.invariant | scope.construction |
| semantic.context | Context | definition | type.definition | scope.context-resolution |
| semantic.context-request | Context Request | definition | type.definition | scope.context-resolution |
| semantic.context-view | Context View | definition | type.definition | scope.context-resolution |
| semantic.product-capability | Product Capability | definition | type.definition | scope.product |
| semantic.capability-instance | Capability Instance | definition | type.definition | scope.product |
| semantic.person | Person | definition | type.definition | scope.people-teams |
| semantic.person-reference | Person Reference | definition | type.definition | scope.people-teams |
| semantic.identity-claim | Identity Claim | definition | type.definition | scope.people-teams |
| semantic.team | Team | definition | type.definition | scope.people-teams |
| semantic.team-membership | Team Membership | definition | type.definition | scope.people-teams |
| semantic.role | Role | definition | type.definition | scope.people-teams |
| semantic.role-assignment | Role Assignment | definition | type.definition | scope.people-teams |

## Generated surfaces

| ID | Name | Canonical inputs |
| --- | --- | --- |
| derived.definition-graph | Definition graph and human navigation tree | canonical definitions and typed relations |
| derived.promotion-queue | Authority promotion queue | gates, evaluations, decisions, and lifecycle profiles |
| derived.source-index | External source index | source-admission and provenance relations |
| derived.artifact-graph | Artifact graph and tree views | artifact records and typed relations |
| derived.project-index | Project goals, work, evidence, and binding index | typed relations |
| derived.capability-ontology | Capability Ontology | products, capabilities, instances, realization bindings, decisions, and evaluations |
| derived.team-roster | Current and historical team roster | team-membership and assignment records |

## Migration decisions

| Legacy ID | Legacy term | Decision | Normalized targets |
| --- | --- | --- | --- |
| CAV2-D1 | Stable Repository | revise | semantic.stable-repository |
| CAV2-D2 | Source-Ledgered Amalgamation | revise | semantic.source-ledgered-consolidation |
| CAV2-D3 | Authority Layer | revise | semantic.authority-surface |
| CAV2-D4 | Source Spine | drop | profile.source-selection-policy, type.source-admission |
| CAV2-D5 | Promotion Gate | collapse | semantic.gate, type.gate, profile.gate-evaluation, profile.authority-lifecycle |
| CAV2-D6 | Stable Repository Stewardship | reclassify | semantic.stable-repository-stewardship, type.discipline |
| CAV2-D7 | Authority Import | reclassify | type.source-admission |
| CAV2-D8 | Import Candidate | collapse | type.source-admission, profile.authority-lifecycle |
| CAV2-D9 | CyberAlchemy v2 | reclassify | semantic.cyberalchemy-repository-identity, type.lineage-map |
| CAV2-D10 | Definition Tower | drop | derived.definition-graph, type.projection-spec |
| CAV2-D11 | Tower Space | drop |  |
| CAV2-D12 | Craft Execution Surface | drop | semantic.work-state-continuity-capability |
| CAV2-D13 | Authority Promotion Queue | collapse | derived.promotion-queue |
| CAV2-D14 | Source Space | collapse | type.source-admission, derived.source-index, relation.originates-from |
| CAV2-D15 | Project Space | revise | profile.repository-layout-policy |
| CAV2-D16 | Typed Coupling Invariant | reclassify | semantic.typed-coupling-invariant, type.typed-relation |
| CAV2-D17 | Reflection Tower Method | reclassify | semantic.residue-escalation-method |
| CAV2-D18 | Residue | revise | semantic.residue, type.residue |
| CAV2-D19 | Ontology | revise | semantic.ontology, type.ontology |
| CAV2-D20 | Craft Method | split | semantic.craft-method, semantic.cyberalchemy-construction-method, semantic.work-state-continuity-capability, semantic.residue-escalation-method |
| CAV2-D21 | Four-Facet Action Method | reclassify | semantic.four-facet-artifact-invariant |
| CAV2-D22 | Orthogonal Classification | reclassify | semantic.classification-orthogonality-invariant, semantic.classification-axis |
| CAV2-D23 | Authority Lifecycle Axis | reclassify | semantic.governance-axis-independence-invariant |
| CAV2-D24 | Provenance-First Navigation | reclassify | profile.authority-aware-navigation |
| CAV2-D25 | Schema Amendment Witness | reclassify | semantic.schema-evolution-invariant, type.schema-change |
| CAV2-D26 | Append-Only Event Ledger | reclassify | semantic.append-only-event-ledger-pattern |
| CAV2-D27 | Residue Entropy | split | semantic.residue-measurement, type.measurement-method, type.measurement-result |
| CAV2-D28 | Value-Cycle Edge Guard | reclassify | semantic.constraint-cycle-safety-invariant |
| CAV2-D29 | Axis Orthogonality Invariant | reclassify | semantic.root-axis-independence-invariant |
| CAV2-D30 | Bounded Recursive Self-Application | reclassify | semantic.bounded-self-application-invariant |
| CAV2-D31 | Primitive Type | revise | semantic.semantic-primitive |
| CAV2-D32 | Method | revise | semantic.method, type.method |
| CAV2-D33 | Definition | revise | semantic.definition, type.definition |
| CAV2-D34 | Authority | split | semantic.authority, semantic.authority-claim, semantic.responsibility, type.authority-claim, type.responsibility |
| CAV2-D35 | Provenance | revise | semantic.provenance, relation.originates-from |
| CAV2-D36 | Traceability | revise | semantic.traceability, type.receipt |
| CAV2-D37 | Gate | split | semantic.gate, type.gate, profile.gate-evaluation |
| CAV2-D38 | Claim-Proof Bound | reclassify | semantic.claim-support-compatibility-invariant |
| CAV2-D39 | Intent | revise | semantic.intent, type.intent |
| CAV2-D40 | Challenge Contract | reclassify | semantic.contestability-policy, profile.challenge |
| CAV2-D41 | Authority Model | split | semantic.authority-model, type.authority-model, type.decision, type.constitution |
| CAV2-D42 | Governed Artifact Tree | collapse | derived.artifact-graph, type.projection-spec |
| CAV2-D43 | Pattern Promotion Lifecycle | collapse | profile.architecture-pattern-promotion, profile.authority-lifecycle |
| CAV2-D44 | View-Bearing Concept | reclassify | semantic.projection-specification, type.projection-spec |
| CAV2-D45 | UX/UI Knowledge Governance | reclassify | semantic.govern-ux-ui-knowledge-capability |
| CAV2-D46 | Experience Evidence Lifecycle | split | semantic.experience-evidence-formation-method, profile.ux-authority-promotion |
| CAV2-D47 | Interface Evidence Boundary | split | semantic.interface-claim-support-compatibility-invariant, profile.ux-evidence-compatibility |
| CAV2-D48 | Authority Promotion Lifecycle | split | semantic.authority-promotion, profile.authority-lifecycle, profile.cross-context-generalization |
| CAV2-D49 | Closed Authority-Kind Enumeration | reclassify | semantic.closed-authority-kind-invariant, type.authority-model |
| CAV2-D50 | Discipline | revise | semantic.discipline, type.discipline |
| CAV2-D51 | Canonical Artifact | split | semantic.artifact, semantic.canonical-representation-invariant, type.artifact-type, relation.originates-from |
| CAV2-D52 | Artifact Durability | split | semantic.artifact-lifetime, profile.retention, profile.semantic-consistency |
| CAV2-D53 | Axiom | revise | semantic.axiom, type.axiom |
| CAV2-D54 | Invariant | revise | semantic.invariant, type.invariant |
| CAV2-D55 | Premise | split | semantic.premise, semantic.hypothesis, type.premise, type.hypothesis |
| CAV2-D56 | Schema | revise | semantic.schema, type.schema |
| CAV2-D57 | Exact Publication Authorization | split | semantic.exact-publication-authorization-invariant, profile.publication, type.decision, type.receipt |
| CAV2-D58 | Constitution | revise | semantic.constitution, type.constitution |
| CAV2-D59 | Goal | split | semantic.goal, type.goal, profile.goal-evaluation, profile.goal-lifecycle, type.decision |
| CAV2-D60 | Project | split | semantic.project, type.project, type.typed-relation, profile.project-evaluation, profile.project-lifecycle, derived.project-index |
| CAV2-D61 | Research | split | semantic.research-inquiry, semantic.research-run, semantic.evidence-set, semantic.finding, type.research-inquiry, type.research-run, type.evidence-set, type.finding |
| CAV2-D62 | Experiment | split | semantic.experiment-design, semantic.experiment-run, semantic.observation, type.experiment-design, type.experiment-run, type.observation, type.measurement-result, type.evidence-set, type.finding, type.decision |
| CAV2-D63 | Product Thesis | split | semantic.product, semantic.product-thesis, type.product, type.product-thesis, profile.product-thesis-evaluation, profile.product-thesis-lifecycle, type.decision |
| CAV2-D64 | Recursive Instance Ownership Invariant | split | semantic.parent-instance-authority-separation-invariant, type.model-instance-binding, profile.model-instance-binding-evaluation, profile.recursion |
| CAV2-D65 | DomainSpec-Governed Construction Invariant | split | semantic.craft-governed-construction-invariant, type.construction-profile, type.construction-binding, type.implementation-binding, profile.construction-evaluation, profile.capability-conformance |
| CAV2-D66 | Context | split | semantic.context, semantic.context-request, semantic.context-view, type.context, type.context-profile, type.context-request, type.context-view, profile.context-resolution, profile.context-lifecycle, type.receipt |
| CAV2-D67 | Product Capability | split | semantic.product-capability, semantic.capability-instance, type.product-capability, type.capability-instance, type.capability-realization-binding, profile.capability-lifecycle, profile.capability-conformance, type.evaluation, derived.capability-ontology |
| CAV2-D68 | Person | split | semantic.person, semantic.person-reference, semantic.identity-claim, type.person-reference, type.identity-claim, relation.identity-link, relation.represents-person |
| CAV2-D69 | Team | split | semantic.team, semantic.team-membership, semantic.role, semantic.role-assignment, type.team, type.team-membership, type.role, type.role-assignment, type.responsibility, type.authority-claim, profile.team-lifecycle, derived.team-roster |

## Withdrawn identifiers

| Legacy ID | Preserved successor |
| --- | --- |
| CAV2-D70 | KEP-D1 |
| CAV2-D71 | KEP-D2 |
| CAV2-D72 | KEP-D3 |
| CAV2-D73 | KEP-D4 |
| CAV2-D74 | KEP-D5 |
| CAV2-D75 | KEP-D6 |
| CAV2-D76 | KEP-D7 |
| CAV2-D77 | KEP-D8 |
| CAV2-D78 | KEP-D9 |
| CAV2-D79 | KEP-D10 |
| CAV2-D80 | KEP-D11 |
| CAV2-D81 | KEP-D12 |

## Dependency order

| Wave | Name | Requires | Outputs | Effect |
| --- | --- | --- | --- | --- |
| N0 | Normalization review |  | owner review of this exact draft | planning only |
| N1 | Shared artifact mechanics | N0 owner selection | artifact-type mechanics, projection mechanics, typed-relation envelope | candidate mechanics only |
| N2 | Foundation artifact types | N1 validated mechanics | definition, axiom, premise, hypothesis, invariant, constitution, decision, schema | candidate artifact types only |
| N3 | Source admission and lineage | N2 source-admission, decision, and schema carriers | source admissions, lineage maps, withdrawal records | no imported meaning admitted without owner decisions |
| N4 | Shared definitions and invariants | N3 exact source selections | revised shared definitions, reclassified invariants, policies and profiles | candidate semantics pending promotion |
| N5 | Owner-local semantic packages | N4 admitted predecessors | product, coordination, knowledge-development, context-resolution, people-teams, UX/UI packages | owner-local candidates |
| N6 | Craft construction bridge | N5 selected Product Capability and business ontology | Craft source, compiled graph, system ontology, specialized bindings | construction eligibility only |
| N7 | Projection and conformance closure | N1-N6 exact current inputs | generated human projections, negative witnesses, collect-all evaluations, receipts | evidence only; no automatic admission or release |

## Open owner decisions

### NORM-OQ-1

Which owner scopes become DDD Bounded Contexts?

Blocks: context directory creation and context-map authority

Recommended default: Do not infer any; select each with language, scope, exclusions, owner, and directional maps.

### NORM-OQ-2

Should the generic evaluation envelope use one schema plus profiles or separate subtype schemas?

Blocks: evaluation artifact-type admission

Recommended default: One envelope with owner-local subtype schemas bound through exact profiles.

### NORM-OQ-3

Which normalized artifact type is the first admitted vertical witness?

Blocks: canonical definition migration

Recommended default: Definition/v1 because all later semantic artifacts depend on its voice and projection contract.

### NORM-OQ-4

Where will durable owner decisions for D1-D69 be recorded?

Blocks: canonical promotion

Recommended default: Create one immutable normalization decision bound to this JSON digest after review.

### NORM-OQ-5

Which legacy DS identifiers remain active aliases after the Craft rename?

Blocks: Craft source and compiler migration

Recommended default: Preserve identifiers initially as lineage aliases; change display names without identity churn.


## Claim ceiling

This validated draft normalizes interactive migration selections and checks internal closure. It does not admit an artifact type, definition, source, bounded context, Product Capability, Craft profile, construction binding, implementation, conformance result, publication, release, deployment, or stable version.
