[Documentation home](../../README.md)

# Project State

<a id="def-cal-definition-project-state"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Project State

The project’s saved records, definitions, decisions, evidence, histories and connections. It belongs to the project and its record owners, not private agent memory. Included records retain their own standing; accepting the state does not automatically promote its sources.

**When it applies**

When preserving governed project knowledge outside any individual agent or session.

**Record formats**

[Project state · v2](type-cal-artifact-type-project-state-v2.md#type-cal-artifact-type-project-state-v2)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

Persist permitted observations, evidence, proposals and decisions with their exact standing.

**Common mistake**

Assuming a saved candidate proposal has been accepted.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

Project State is the durable governed external state of a Project, including versioned artifacts, Definitions, decisions, evidence, event histories, relations, and other records. Project State belongs to the governed Project and its artifact owners, never to an Agent or model.

## Exact governing statement

Project State is the durable governed external state of a Project, including versioned artifacts, Definitions, decisions, evidence, event histories, relations, and other records. Project State is not owned by an Agent and is not hidden cross-session Machine Agent memory.

````
ProjectState(P,t) = governed durable records admitted or retained by P at t; AgentMemoryLongTerm(a,s) := Select(ProjectState(P,t), ContextView(s), OntologyView(s)); owns(a,ProjectState)=false.
````

- Project State belongs to the governed Project and its artifact owners, never to an Agent or model.
- Only explicit governed writes of artifacts, events, evidence, receipts, Decisions, and relations change Project State.
- Context Views and Ontology Views select Project State for a consumer; they do not create a competing canonical store.
- Hidden model state, caches, conversation recall, and expired Session Memory are excluded unless explicitly persisted through the governed Project path.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/project-state/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.project-state@1.0.0-candidate.1

**Content fingerprint · SHA-256**

40e00c926c7ca2a9143c321e1681ebb7df480c71d4b8950e5524849758b4e784

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Project State is the durable governed external state of a Project, including versioned artifacts, Definitions, decisions, evidence, event histories, relations, and other records.",
  "authority_scope_ref": "scope:project-state-definition",
  "exclusions": [
    "Project State belongs to the governed Project and its artifact owners, never to an Agent or model.",
    "Only explicit governed writes of artifacts, events, evidence, receipts, Decisions, and relations change Project State.",
    "Context Views and Ontology Views select Project State for a consumer; they do not create a competing canonical store.",
    "Hidden model state, caches, conversation recall, and expired Session Memory are excluded unless explicitly persisted through the governed Project path.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
