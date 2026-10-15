[Documentation home](../../README.md)

# User Decision Preference · Craft workflow

<a id="def-craft-definition-user-decision-preference"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / User Decision Preference · Craft workflow

# User Decision Preference · Craft workflow

A user’s preferred review position for a particular workflow, limited to the positions that workflow permits. An invalid explicit preference blocks resolution rather than silently falling back.

**When it applies**

User-owned selection of an allowed interaction checkpoint for an exact Craft Workflow type or instance scope.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Authority-role assignment.

This name is used in both Lab and Craft workflow scopes. This entry has its own identity and source; matching names do not merge the definitions.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-craft-definition-user-decision-preference-section-2"></a>

## Source explanatory wording

The user's saved choice for where a kind of Workflow should ask them, limited to positions that Workflow already permits.

<a id="def-craft-definition-user-decision-preference-section-3"></a>

## Exact governing statement

A User Decision Preference is a versioned user-owned interaction configuration selecting one preferred Decision Checkpoint for an exact Workflow type or instance scope. It applies only when allowed by the Workflow Decision Profile. An explicit invalid preference blocks resolution and never silently falls back. A preference has no authority effect and cannot waive a required decision, create standing authority, or alter an owner, target, effect, or scope.

````
Preference(u,s)=preferred_checkpoint; Applicable(p,w) iff Scope(p) matches w and preferred_checkpoint in Allowed(Profile(Type(w))); ExplicitInvalid(p,w)=>BLOCK.
````

- A preference changes interaction placement only.
- An explicit invalid preference blocks instead of falling back.
- Absence may use only an explicit valid profile default.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Craft foundation admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0005-craft-workflow-interaction/definitions/user-decision-preference/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

craft.definition.user-decision-preference@1.0.0-candidate.1

**Content fingerprint · SHA-256**

f816c7dd868e8af2bd0303fb6fe10a8576f70ad6fee8af4b1854fdbcdbfc0212

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:craft-product-workflow",
  "applicability": "User-owned selection of an allowed interaction checkpoint for an exact Craft Workflow type or instance scope.",
  "exclusions": [
    "Authority-role assignment.",
    "Workflow-type safety constraints.",
    "Decision outcome, standing authorization, or effect scope."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
