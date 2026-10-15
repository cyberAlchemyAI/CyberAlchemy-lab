[Documentation home](../../README.md)

# Authority Boundary

<a id="def-cal-definition-authority-boundary"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Authority Boundary

# Authority Boundary

Records the exact limits of an owner’s decision rights. It determines what may be authorized, separately from where a workflow asks the owner.

**When it applies**

Owner-scoped semantic and effect authority used by CyberAlchemy Lab workflows and governance decisions.

**Record formats**

[Authority boundary · v1](type-cal-artifact-type-authority-boundary-v1.md#type-cal-artifact-type-authority-boundary-v1)

**A stated exclusion**

Workflow interaction placement.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-authority-boundary-section-2"></a>

## Source explanatory wording

The exact limit around what a particular owner is allowed to decide. It says who can decide what; it does not say when a workflow asks them.

<a id="def-cal-definition-authority-boundary-section-3"></a>

## Exact governing statement

An Authority Boundary is the explicit owner-scoped limit within which one role may make Governance Decisions about named meanings, targets, and effects. It binds an owner role, an accountable principal binding, an authority scope, allowed effects, excluded effects, and a challenge route. An Authority Boundary is independent of where a workflow requests a decision, and no workflow profile or user preference may create, move, merge, or widen it.

````
AuthorityBoundary(b) = (owner_role, principal_binding, authority_scope, allowed_effects, excluded_effects, challenge_route). MayDecide(p,d,b) iff Holds(p,b.owner_role) and Target(d) in b.authority_scope and Effect(d) in b.allowed_effects and Effect(d) not in b.excluded_effects.
````

- One principal holding multiple roles does not merge their Authority Boundaries.
- A Decision Checkpoint does not grant authority.
- Validation evidence cannot substitute for an owner decision.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0003-single-decision-checkpoint/definitions/authority-boundary/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.authority-boundary@1.0.0-candidate.1

**Content fingerprint · SHA-256**

e6928339ebf6cbd41966e268da7eeee32d395da382522da086f98c3e2737896c

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:cyberalchemy-lab-shared-governance",
  "applicability": "Owner-scoped semantic and effect authority used by CyberAlchemy Lab workflows and governance decisions.",
  "exclusions": [
    "Workflow interaction placement.",
    "Evidence quality or validation outcomes.",
    "Authority inferred from repository location, automation, or principal identity alone."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
