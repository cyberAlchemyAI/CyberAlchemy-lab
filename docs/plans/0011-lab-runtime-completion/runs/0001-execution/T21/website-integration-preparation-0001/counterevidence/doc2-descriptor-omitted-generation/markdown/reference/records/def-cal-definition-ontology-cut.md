[Documentation home](../../README.md)

# Ontology Cut

<a id="def-cal-definition-ontology-cut"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Ontology Cut

# Ontology Cut

A rebuilt, fixed and consistent recorded ontology state at particular positions in its semantic and governance histories. It does not replace those histories as reconstruction sources.

**When it applies**

An Ontology Cut is a derived immutable consistent state of one Ontology at exact semantic and governance cursors with an event-set digest.

**Record formats**

[Ontology cut · v1](type-cal-artifact-type-ontology-cut-v1.md#type-cal-artifact-type-ontology-cut-v1)

**A stated exclusion**

It is rebuildable, never a canonical replay source, and cannot silently mix incompatible event positions.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-ontology-cut-section-2"></a>

## Source explanatory wording

An Ontology Cut is a derived immutable consistent state of one Ontology at exact semantic and governance cursors with an event-set digest. It is rebuildable, never a canonical replay source, and cannot silently mix incompatible event positions.

<a id="def-cal-definition-ontology-cut-section-3"></a>

## Exact governing statement

An Ontology Cut is a derived immutable consistent state of one Ontology at exact semantic and governance cursors with an event-set digest. It is rebuildable, never a canonical replay source, and cannot silently mix incompatible event positions.

````
OntologyCut(x) => governed_identity_or_record(x) and bounded_scope(x); OntologyCut(x) =/=> authority_effect(x).
````

- An Ontology Cut is a derived immutable consistent state of one Ontology at exact semantic and governance cursors with an event-set digest.
- It is rebuildable, never a canonical replay source, and cannot silently mix incompatible event positions.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/4fcb9ad5200e-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.ontology-cut@1.0.0-candidate.1

**Content fingerprint · SHA-256**

4fcb9ad5200ed0e0a6d1d91acea8ce6236bed6800724c8896cc0d4dd7b9a4417

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An Ontology Cut is a derived immutable consistent state of one Ontology at exact semantic and governance cursors with an event-set digest.",
  "authority_scope_ref": "scope:ontology-cut-definition",
  "exclusions": [
    "It is rebuildable, never a canonical replay source, and cannot silently mix incompatible event positions.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
