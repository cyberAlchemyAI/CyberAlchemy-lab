[Documentation home](../../README.md)

# Project

<a id="def-cav2-d60"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Project

# Project

A continuing coordination identity for a particular effort, keeping its goals, decisions, evidence and work together across changes to plans or files.

**When it applies**

When related goals, decisions, evidence and work need an enduring coordination identity.

**Record formats**

[Project identity · v1](type-cal-artifact-type-project-identity-v1.md#type-cal-artifact-type-project-identity-v1)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

The export-repair Project coordinates goals, decisions, evidence and work across sessions.

**Common mistake**

Equating the enduring coordination identity with one investigation task.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cav2-d60-section-2"></a>

## Source explanatory wording

A Project is the durable coordination identity that keeps related goals, decisions, evidence, and work together even when files and plans change.

<a id="def-cav2-d60-section-3"></a>

## Exact governing statement

A Project is a durable coordination identity with purpose, scope, exclusions, owner routes, Goal references, evidence index, purpose or Product connections, lifecycle, and challenge route. Its identity survives changes to plans, tasks, folders, tools, and implementations.

````
Project = (id, name, purpose, scope, exclusions, owner_routes, goal_refs, evidence_index, purpose_refs, lifecycle_state, challenge_route); |goal_refs| >= 1.
````

- A proposed Project has at least one draft or active Goal.
- An active Project has at least one active Goal.
- Directory placement and membership do not create Project identity.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Semantic foundation admission

**Original definition**

[Read the original record](../../assets/f342be625bee-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

CAV2-D60@1.0.0-candidate.1

**Content fingerprint · SHA-256**

f342be625bee345590d9d1f4f20ff14f6005c8ec9ed9108f0cf70cd0ae05ca68

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:project-definition",
  "applicability": "A durable identity-bearing coordination boundary grouping related goals, owners, evidence, decisions, artifacts, work, and lifecycle toward a declared purpose.",
  "exclusions": [
    "A Product, Goal, Method, project space, repository, directory, plan, work pack, session, team, or authority envelope."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
