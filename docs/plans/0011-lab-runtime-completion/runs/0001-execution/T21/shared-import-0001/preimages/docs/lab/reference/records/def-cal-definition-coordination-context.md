[Documentation home](../../README.md)

# Coordination Context

<a id="def-cal-definition-coordination-context"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Coordination Context

A saved frame for work: exactly one product, optional project and goal references, a stable purpose, intended users and source rules. It can refer to independently owned domain models without merging them.

**When it applies**

Durable product-work framing and references to independently owned semantic contexts.

**Record formats**

[Coordination context · v2](type-cal-artifact-type-coordination-context-v2.md#type-cal-artifact-type-coordination-context-v2)

**A stated exclusion**

DDD semantic boundary ownership.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

The durable frame saying what a piece of work is about, why information is needed, and who will use it.

## Exact governing statement

A Coordination Context is a durable, identity-bearing, owner-qualified frame that binds exactly one Product, optional Project and Goal references, a stable purpose, intended consumers and uses, subject scope, source policies, and zero or more references to independently owned Bounded Contexts. A material change to Product, Project, Goal, or purpose requires a successor identity.

````
CoordinationContext = (id, product_ref, project_ref?, goal_ref?, purpose, consumer_refs, intended_uses, subject_scope, source_policy_refs, bounded_context_refs, owner_ref, lifecycle, revision_history, challenge_route); |product_ref|=1; |project_ref|<=1; |goal_ref|<=1; MaterialAnchorChange => SuccessorRequired.
````

- It references Bounded Contexts but never becomes one by containment.
- Directory placement cannot supply identity or ownership.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Definition and initial context promotion

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0001-definition-and-ctx00-v1/definitions/coordination-context/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.coordination-context@1.0.0-candidate.1

**Content fingerprint · SHA-256**

547a714a9552f83985de78b2ce228421f5102c40cacf8c1edfb48ef46366a8aa

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:cyberalchemy-lab-coordination",
  "applicability": "Durable product-work framing and references to independently owned semantic contexts.",
  "exclusions": [
    "DDD semantic boundary ownership.",
    "Execution authorization or transient chat/session state."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
