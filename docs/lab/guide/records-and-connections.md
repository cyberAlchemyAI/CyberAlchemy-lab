[Documentation home](../README.md)

# Definitions, records and connections

<a id="records"></a>

05

<a id="records-title"></a>

## Separate meaning, shape and connections

 [Explore this in the system map ↑](system-map.md#system-map) 

<a id="docs-records-heading-2"></a>

### Give the investigation a meaning and a record format

The *Work* brief is easier to read once its fields have distinct jobs. The definition explains Work’s meaning. An **Artifact Type** governs its record format, with **schema** fields and constraints. The investigation is one **artifact instance**, an identifiable versioned record using that format.

The brief illustrates the content. An actual Lab record must resolve to the applicable contract.

<a id="figure-meaning-shape-record"></a>

![Meaning, required format and the investigation record](../assets/diagram-15ef5a579afd.svg)

**Diagram labels:** Three records, three questions · Definition · What does Work mean? A bounded unit of effort. · Artifact type · What must a Work record contain? Declared fields and constraints. · One Work record · Which investigation is this? Investigate Northstar’s omission. · Meaning · Required format · This investigation

### Read this diagram as text

The definition tells us what Work means. The artifact type specifies the record format. The particular Work record describes Northstar’s omission investigation. These arrows show how the roles fit together. Permitted connections still come from their declared contracts.

- Three records, three questions
- Definition
- What does Work mean? A bounded unit of effort.
- Artifact type
- What must a Work record contain? Declared fields and constraints.
- One Work record
- Which investigation is this? Investigate Northstar’s omission.
- Meaning
- Required format
- This investigation

Figure 04 The definition explains Work; the type governs its record format; the instance identifies this investigation. Format conformance and owner acceptance retain their own requirements.

<a id="docs-records-heading-3"></a>

### Select the governing records

**Registries** select exact versions of definitions, types and connection rules. We check a record’s declared type against that selection. A familiar filename leaves its meaning and acceptance to be established from the actual records.

<a id="docs-records-heading-4"></a>

### Declare what each connection means

A **Relation Kind** declares one connection’s meaning, direction and permitted endpoint kinds. Here, the Operational Observation *originates from* Source records for S1 and E12. Their roles identify required input and observed output.

Membership of a capability in its product is a different fact and uses a different rule.

An **ontology** organizes concepts, things and relationships. An **Ontology View** chooses part of that model for a purpose. The diagram starts with the observation and sources as records, then shows a derived view of the same trail. Each node and edge stays bound to the exact versions it represents.

<a id="figure-records-and-ontology"></a>

![The incident source trail and its ontology view](../assets/diagram-18abb5859965.svg)

**Diagram labels:** SOURCE RECORDS · particular records and permitted connections · Source · S1 · Required identifiers · Observation v1 · Operational Observation · Source · E12 · Saved export output · originates-from · represent these records and connections · ONTOLOGY VIEW · a graph of these selected records · Node · Represents Source S1 · Represents the observation · Represents Source E12

### Read this diagram as text

Operational Observation version 1 comes from the Source records for S1 and E12. One is the required input; the other is the observed output. The lower graph shows those same subjects and connections, with their original standing.

- SOURCE RECORDS · particular records and permitted connections
- Source · S1
- Required identifiers
- Observation v1
- Operational Observation
- Source · E12
- Saved export output
- ONTOLOGY VIEW · a graph of these selected records
- Node
- Represents Source S1
- Node
- Represents the observation
- Node
- Represents Source E12

Figure 05 “Originates-from” is permitted from an Operational Observation to a Source. The two declared origin roles distinguish required input and observed output; exact versions and source bindings remain necessary.

<a id="docs-records-heading-5"></a>

### Extend rules and read views within their scope

The global connection catalog is closed: a proposed connection has to fit an accepted rule and its ordered pair requirements. Expanding the pairs needs review and admission of a successor rule contract. A different semantic question needs a distinct relation kind.

The **Typed Connection Extension Rule** governs that process. Registering an endpoint kind alone adds no connections.

When reading a graph, ask which records and versions it shows, what it excludes and whether it is current. Arrows help us locate related material; evidence and authority records support the claims and permissions. Local ontology connections follow their own contract and leave the global catalog unchanged.

### How the Lab checks that concepts stay distinct

The Lab calls the check **non-collapse**: do these concepts describe different facts? An assignment can precede permission. A capability can precede implementation adoption. An experiment can evaluate a product and fail.

These examples explain distinctions, rather than proving them. The inspected assurance report covers sources for 183 definition identities with partial formal translations. It reports zero verified whole-definition proofs.

<a id="craft-and-lab-records"></a>

### Keep software models and Lab records distinct

A Craft model describes software. Lab records describe its meaning, surrounding work, evidence and decisions. When a word appears at both levels, we need to identify the subject and contract behind each use.

| Lab responsibility | Craft responsibility |
| --- | --- |
| **Artifact Type** Defines the required shape and obligations of a retained record. | **Meta-type** Names a software role, such as Entity or Rule. It does not select the Lab record’s admission or lifecycle. |
| **Work** Identifies a bounded project effort, such as designing or evaluating a Workflow. | **Operation and Workflow** Model a state-changing business action and orchestration of software Operations. The Lab’s admitted Workflow definition has this same software meaning; Work records the effort around it. |
| **Capability Realization Binding** Associates exact capability and implementation revisions with roles and adoption posture. | **Realization and artifact binding** Select an implementation form and trace an output to its inputs. They do not establish adoption of a product capability. |
| **Typed Relation** Records a connection under a global Relation Kind and permitted endpoint pair. | **Software relationship** Connects modeled concepts under Craft’s catalog and architecture constraints. A local verb does not expand the global Lab catalog. |
| **Record lifecycle** Governs the states and transitions of an exact definition, model or other record. | **State Machine** Models a subject’s states inside the software’s domain. Its execution state does not describe the design’s acceptance. |

A software-model node, the record saving its declaration and a runtime object have different identities. One Entity concept can describe many running objects. An Ontology View represents selected concepts and records through exact source bindings. Their local and global connections retain their own rules.

A Craft feature organizes software responsibilities. Establishing a Bounded Context also needs its meaning, language, owner and context-map evidence.

[Compare the two models in the Craft article](../craft/model.md#governance-keep-the-two-kinds-of-model-identifiable). If a software Rule implements a governing Lab definition, record that correspondence explicitly and version it under the applicable contract. A shared name does not establish the binding.

### Definitions and sources

[Definition](../reference/records/def-cal-definition-definition.md#def-cal-definition-definition) · [Artifact Type](../reference/records/def-cal-definition-artifact-type.md#def-cal-definition-artifact-type) · [Schema](../reference/records/def-cal-definition-schema.md#def-cal-definition-schema) · [Typed Relation](../reference/records/def-cal-definition-typed-relation.md#def-cal-definition-typed-relation) · [Typed Connection Extension Rule](../reference/records/def-cal-definition-typed-connection-extension-rule.md#def-cal-definition-typed-connection-extension-rule) · [Ontology Node](../reference/records/def-cal-definition-ontology-node.md#def-cal-definition-ontology-node) · [Ontology Edge](../reference/records/def-cal-definition-ontology-edge.md#def-cal-definition-ontology-edge)

- [Integrated Lab model record](../../../authority/ontology-integration/candidates/0003-definition-complete-runtime-integration/integrated-model.json)
- [Definition realization contracts](../../../authority/artifact-types/candidates/0012-definition-complete-carrier-materialization/noncarrier-realizations.json)
- [Source and formalization coverage](../../plans/definition-formal-assurance/candidate/assurance-snapshots-v1/source-and-formalization-coverage.json)
