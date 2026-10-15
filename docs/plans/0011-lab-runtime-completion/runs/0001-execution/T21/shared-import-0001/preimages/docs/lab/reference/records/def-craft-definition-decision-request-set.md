[Documentation home](../../README.md)

# Decision Request Set

<a id="def-craft-definition-decision-request-set"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Decision Request Set

Groups specific questions for one interaction while preserving each request’s owner, scope, target and intended effect.

**When it applies**

A closed presentation set of independently governed decision requests at one Decision Checkpoint.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

A merged authority grant.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

Several exact questions shown together once. The user sees one interaction, but every question keeps its own owner, target, and consequence.

## Exact governing statement

A Decision Request Set is a closed ordered set of exact decision requests presented at one Decision Checkpoint. Every member retains its independent decision identity, authority scope, owner, target, digest when bytes exist, requested effect, outcome, and invalidation conditions. Presentation reduces interaction count but cannot merge authority, infer authorization between members, or let one outcome satisfy another gate.

````
RequestSet(R,c) iff FiniteClosed(R) and forall r in R: Checkpoint(r)=c and ExactOwner(r) and ExactTarget(r) and ExactEffect(r); Authorized(R) iff forall r in R: Authorized(r).
````

- A shared principal does not collapse member roles.
- One approved member does not approve another.
- A request without its exact target cannot enter the set.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Craft foundation admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0005-craft-workflow-interaction/definitions/decision-request-set/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

craft.definition.decision-request-set@1.0.0-candidate.1

**Content fingerprint · SHA-256**

381e991d97572913bc199a0546a2334913dea13ff370d803934ecd8392435c49

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:craft-product-workflow",
  "applicability": "A closed presentation set of independently governed decision requests at one Decision Checkpoint.",
  "exclusions": [
    "A merged authority grant.",
    "A replacement for individual decision records.",
    "Requests whose exact targets do not yet exist."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
