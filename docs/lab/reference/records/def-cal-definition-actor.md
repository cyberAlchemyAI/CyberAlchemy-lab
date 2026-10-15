[Documentation home](../../README.md)

# Actor

<a id="def-cal-definition-actor"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Actor

# Actor

An identifiable participant in Lab activity. Concrete participants, such as people, teams or agents, use their own governed records; Actor is the general classification.

**When it applies**

An Actor is a governed participant identity to which participation in Lab activity can be attributed.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Actor is an abstract participation classification; it does not require one universal Actor carrier when concrete actor kinds have governed carriers.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-actor-section-2"></a>

## Source explanatory wording

An Actor is a governed participant identity to which participation in Lab activity can be attributed. Actor is an abstract participation classification; it does not require one universal Actor carrier when concrete actor kinds have governed carriers.

<a id="def-cal-definition-actor-section-3"></a>

## Exact governing statement

An Actor is a governed participant identity to which participation in Lab activity can be attributed. Actor classification establishes neither agency, personhood, capability, ownership, Role, permission, nor authority.

````
Actor(x) => governed_identity_or_record(x) and bounded_scope(x); Actor(x) =/=> authority_effect(x).
````

- Actor is an abstract participation classification; it does not require one universal Actor carrier when concrete actor kinds have governed carriers.
- Actor does not imply Agent, Person, Principal, Team, Role, capability, ownership, permission, authority, or successful action.
- Attribution to an Actor preserves the independent identity, owner, lifecycle, and authority of every participating subject.
- Actor classification must resolve through an exact Classification Scheme and Assignment when applied to a concrete subject.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/actor/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.actor@1.0.0-candidate.1

**Content fingerprint · SHA-256**

dacc0380a33b9d307884b652a5eb7ee91a5ea6b1676c05ea520c80d976c240a3

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An Actor is a governed participant identity to which participation in Lab activity can be attributed.",
  "authority_scope_ref": "scope:actor-definition",
  "exclusions": [
    "Actor is an abstract participation classification; it does not require one universal Actor carrier when concrete actor kinds have governed carriers.",
    "Actor does not imply Agent, Person, Principal, Team, Role, capability, ownership, permission, authority, or successful action.",
    "Attribution to an Actor preserves the independent identity, owner, lifecycle, and authority of every participating subject.",
    "Actor classification must resolve through an exact Classification Scheme and Assignment when applied to a concrete subject.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
