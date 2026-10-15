[Documentation home](../../README.md)

# Ontology Manifest

<a id="def-cal-definition-ontology-manifest"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Ontology Manifest

# Ontology Manifest

The designated identity and configuration record for an ontology, identifying its model, owners, policies, connection registry and runtime choices. It is not a snapshot of all represented objects.

**When it applies**

An Ontology Manifest is the canonical stable identity and configuration record for one Ontology, binding its Definition, owner, state model, Relation Kind registry, Policies, runtime, projections, and challenge route.

**Record formats**

[Ontology manifest · v1](type-cal-artifact-type-ontology-manifest-v1.md#type-cal-artifact-type-ontology-manifest-v1)

**A stated exclusion**

It is not a mutable snapshot, event history, consistent cut, transport package, or the Ontology’s represented subjects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-ontology-manifest-section-2"></a>

## Source explanatory wording

An Ontology Manifest is the canonical stable identity and configuration record for one Ontology, binding its Definition, owner, state model, Relation Kind registry, Policies, runtime, projections, and challenge route. It is not a mutable snapshot, event history, consistent cut, transport package, or the Ontology’s represented subjects.

<a id="def-cal-definition-ontology-manifest-section-3"></a>

## Exact governing statement

An Ontology Manifest is the canonical stable identity and configuration record for one Ontology, binding its Definition, owner, state model, Relation Kind registry, Policies, runtime, projections, and challenge route. It is not a mutable snapshot, event history, consistent cut, transport package, or the Ontology’s represented subjects.

````
OntologyManifest(x) => governed_identity_or_record(x) and bounded_scope(x); OntologyManifest(x) =/=> authority_effect(x).
````

- An Ontology Manifest is the canonical stable identity and configuration record for one Ontology, binding its Definition, owner, state model, Relation Kind registry, Policies, runtime, projections, and challenge route.
- It is not a mutable snapshot, event history, consistent cut, transport package, or the Ontology’s represented subjects.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/34289df770ad-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.ontology-manifest@1.0.0-candidate.1

**Content fingerprint · SHA-256**

34289df770ad7df33a9bc26109f485b18ce40e4cb72b50872cb1be3785195b58

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An Ontology Manifest is the canonical stable identity and configuration record for one Ontology, binding its Definition, owner, state model, Relation Kind registry, Policies, runtime, projections, and challenge route.",
  "authority_scope_ref": "scope:ontology-manifest-definition",
  "exclusions": [
    "It is not a mutable snapshot, event history, consistent cut, transport package, or the Ontology’s represented subjects.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
