[Documentation home](../../README.md)

# Ontology View

<a id="def-cal-definition-ontology-view"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Ontology View

# Ontology View

A fixed selection from one consistent recorded ontology state for an identified purpose and consumer, with source positions, exclusions and use and expiry conditions.

**When it applies**

When selecting an immutable projection of an exact consistent ontology cut for a declared purpose and consumer.

**Record formats**

[Ontology view · v1](type-cal-artifact-type-ontology-view-v1.md#type-cal-artifact-type-ontology-view-v1)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

Select an exact consistent cut of subjects and connections for the investigation’s purpose and consumer.

**Common mistake**

Making the derived graph a competing canonical source or an authority grant.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-ontology-view-section-2"></a>

## Source explanatory wording

An Ontology View is an immutable purpose-bounded projection of one exact consistent Ontology cut for a named consumer or Agent Session. An Ontology View binds one Ontology identity, exact semantic and governance cursors, event-set digest, selection purpose, consumer, exclusions, freshness, expiry, and claim ceiling.

<a id="def-cal-definition-ontology-view-section-3"></a>

## Exact governing statement

An Ontology View is an immutable purpose-bounded projection of one exact consistent Ontology cut for a named consumer or Agent Session. It is derived Project State, expires under its contract, and is never the canonical replay source or the represented subjects themselves.

````
OntologyView(x) => governed_identity_or_record(x) and bounded_scope(x); OntologyView(x) =/=> authority_effect(x).
````

- An Ontology View binds one Ontology identity, exact semantic and governance cursors, event-set digest, selection purpose, consumer, exclusions, freshness, expiry, and claim ceiling.
- It is immutable derived Project State and never the canonical semantic or governance replay source.
- A View’s nodes and edges represent subjects and relations without replacing their canonical identities or authority.
- A View authorizes no Action and cannot widen its consumer’s Assignment, Policy, or Delegation.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/1fcc7fa38a6a-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.ontology-view@1.0.0-candidate.1

**Content fingerprint · SHA-256**

1fcc7fa38a6a77e67258ae56c49719ea35f1c853868060ab58200343fde2f81e

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An Ontology View is an immutable purpose-bounded projection of one exact consistent Ontology cut for a named consumer or Agent Session.",
  "authority_scope_ref": "scope:ontology-view-definition",
  "exclusions": [
    "An Ontology View binds one Ontology identity, exact semantic and governance cursors, event-set digest, selection purpose, consumer, exclusions, freshness, expiry, and claim ceiling.",
    "It is immutable derived Project State and never the canonical semantic or governance replay source.",
    "A View’s nodes and edges represent subjects and relations without replacing their canonical identities or authority.",
    "A View authorizes no Action and cannot widen its consumer’s Assignment, Policy, or Delegation.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
