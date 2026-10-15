[Documentation home](../../README.md)

# Goal

<a id="def-cav2-d59"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Goal

# Goal

The future result a project seeks, with the conditions and evidence its owner needs before declaring achievement.

**When it applies**

When a Project needs a declared future outcome, achievement criteria, evidence and responsible owner.

**Record formats**

[Goal · v1](type-cal-artifact-type-goal-v1.md#type-cal-artifact-type-goal-v1)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

Declare the scoped repair outcome, criteria, required evidence and responsible owner.

**Common mistake**

Marking the repair goal achieved solely because investigation Work ended.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cav2-d59-section-2"></a>

## Source explanatory wording

A Goal says what future result one Project is pursuing and what evidence will let its owner honestly declare it achieved.

<a id="def-cav2-d59-section-3"></a>

## Exact governing statement

A Goal states a desired future outcome for one Project and becomes achieved only when all required success conditions have adequate evidence and the Goal owner records the lifecycle transition. Progress or passing checks alone do not achieve it.

````
Goal = (id, project_ref, outcome, rationale, scope, exclusions, owner_route, success_conditions, evidence_requirements, lifecycle_state); achieved only if evidence adequate and owner records achievement.
````

- A Goal belongs to exactly one Project in this contract.
- Evidence supports but does not perform the achievement decision.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Semantic foundation admission

**Original definition**

[Read the original record](../../assets/f43a539e5f0f-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

CAV2-D59@1.0.0-candidate.1

**Content fingerprint · SHA-256**

f43a539e5f0f4db26dab0df0cb30c523868c6fef3dbb3d061614a4d288c5ae19

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:goal-definition",
  "applicability": "A durable, attributable desired future outcome for exactly one Project, with rationale, scope, owner, success conditions, evidence requirements, and lifecycle.",
  "exclusions": [
    "Intent, Project, plan, task, work pack, evidence, deadline, or execution authority.",
    "Automatic achievement from activity, progress, validation, or agent assertion."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
