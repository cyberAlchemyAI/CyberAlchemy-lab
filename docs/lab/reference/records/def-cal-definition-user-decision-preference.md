[Documentation home](../../README.md)

# User Decision Preference · Lab workflow

<a id="def-cal-definition-user-decision-preference"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / User Decision Preference · Lab workflow

# User Decision Preference · Lab workflow

A user’s preferred review position for a particular workflow, limited to the positions that workflow permits. An invalid explicit preference blocks resolution rather than silently falling back.

**When it applies**

User-owned selection of an interaction checkpoint for an exact workflow type or instance scope.

**Record formats**

[User decision preference · v1](type-cal-artifact-type-user-decision-preference-v1.md#type-cal-artifact-type-user-decision-preference-v1)

**A stated exclusion**

Authority-role assignment.

This name is used in both Lab and Craft workflow scopes. This entry has its own identity and source; matching names do not merge the definitions.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-user-decision-preference-section-2"></a>

## Source explanatory wording

The user's saved choice for where a particular kind of workflow should ask them. It can move the question only among places the workflow already permits.

<a id="def-cal-definition-user-decision-preference-section-3"></a>

## Exact governing statement

A User Decision Preference is a versioned user-owned interaction configuration that selects one preferred Decision Checkpoint for an exact workflow type or workflow instance scope. It is applied only when the selected checkpoint is allowed by the applicable Workflow Decision Profile. An invalid preference blocks resolution and must not silently fall back. A preference has no authority effect and cannot waive a required decision, create standing authority, or alter an owner, target, effect, or scope.

````
Preference(u,s) = preferred_checkpoint. Applicable(p,w) iff Scope(p) matches w and preferred_checkpoint in Allowed(Profile(Type(w))). ExplicitInvalid(p,w) => BLOCK; no fallback.
````

- A preference changes interaction placement only.
- An explicit invalid preference blocks instead of falling back.
- Absence of a preference may use only an explicit valid profile default.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0003-single-decision-checkpoint/definitions/user-decision-preference/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.user-decision-preference@1.0.0-candidate.1

**Content fingerprint · SHA-256**

9b557940d24ad90576944e7d1e20ee09dbddc72d3148e52ff3926a6a8f0cdd8f

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:cyberalchemy-lab-workflow-interaction",
  "applicability": "User-owned selection of an interaction checkpoint for an exact workflow type or instance scope.",
  "exclusions": [
    "Authority-role assignment.",
    "Workflow-type safety constraints.",
    "Decision outcome, standing authorization, or effect scope."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
