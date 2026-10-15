[Documentation home](../../README.md)

# Relation Kind

<a id="def-cal-definition-relation-kind"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Relation Kind

# Relation Kind

A versioned rule for one directional connection meaning, a finite set of allowed source–target kind pairs and required additional details. Separate lists do not permit every combination.

**When it applies**

A Relation Kind is a versioned semantic-axis contract asking one unique directional question through a finite closed set of exact ordered endpoint-kind pairs and pair-specific qualifier rules.

**Record formats**

[Relation kind · v2](type-cal-artifact-type-relation-kind-v2.md#type-cal-artifact-type-relation-kind-v2)

**A stated exclusion**

It is neither a relation instance, specialized binding, Ontology edge, wildcard endpoint family, nor inferred Cartesian product.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-relation-kind-section-2"></a>

## Source explanatory wording

A Relation Kind is a versioned semantic-axis contract asking one unique directional question through a finite closed set of exact ordered endpoint-kind pairs and pair-specific qualifier rules. It is neither a relation instance, specialized binding, Ontology edge, wildcard endpoint family, nor inferred Cartesian product.

<a id="def-cal-definition-relation-kind-section-3"></a>

## Exact governing statement

A Relation Kind is a versioned semantic-axis contract asking one unique directional question through a finite closed set of exact ordered endpoint-kind pairs and pair-specific qualifier rules. It is neither a relation instance, specialized binding, Ontology edge, wildcard endpoint family, nor inferred Cartesian product.

````
RelationKind(x) => governed_identity_or_record(x) and bounded_scope(x); RelationKind(x) =/=> authority_effect(x).
````

- A Relation Kind is a versioned semantic-axis contract asking one unique directional question through a finite closed set of exact ordered endpoint-kind pairs and pair-specific qualifier rules.
- It is neither a relation instance, specialized binding, Ontology edge, wildcard endpoint family, nor inferred Cartesian product.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/f5f1e77b4b2b-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.relation-kind@1.0.0-candidate.1

**Content fingerprint · SHA-256**

f5f1e77b4b2bbbc96a6024d4c46c54b7d183c692724a48873570f610f4b868bb

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Relation Kind is a versioned semantic-axis contract asking one unique directional question through a finite closed set of exact ordered endpoint-kind pairs and pair-specific qualifier rules.",
  "authority_scope_ref": "scope:relation-kind-definition",
  "exclusions": [
    "It is neither a relation instance, specialized binding, Ontology edge, wildcard endpoint family, nor inferred Cartesian product.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
