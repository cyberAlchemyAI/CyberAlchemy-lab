[Documentation home](../../README.md)

# Ontology Node

<a id="def-cal-definition-ontology-node"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Ontology Node

# Ontology Node

A separately identified representation of one particular thing and version inside an ontology, with sources and governance details. It does not replace the represented thing or prove its claims.

**When it applies**

An Ontology Node is an independently identified governed representation of one exact subject revision within one Ontology, with provenance, confidence, lifecycle, branch, and contestability state.

**Record formats**

[Ontology node · v2](type-cal-artifact-type-ontology-node-v2.md#type-cal-artifact-type-ontology-node-v2)

**A stated exclusion**

It is not the represented subject, its identity carrier, its Definition, or proof that its claims are globally true.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-ontology-node-section-2"></a>

## Source explanatory wording

An Ontology Node is an independently identified governed representation of one exact subject revision within one Ontology, with provenance, confidence, lifecycle, branch, and contestability state. It is not the represented subject, its identity carrier, its Definition, or proof that its claims are globally true.

<a id="def-cal-definition-ontology-node-section-3"></a>

## Exact governing statement

An Ontology Node is an independently identified governed representation of one exact subject revision within one Ontology, with provenance, confidence, lifecycle, branch, and contestability state. It is not the represented subject, its identity carrier, its Definition, or proof that its claims are globally true.

````
OntologyNode(x) => governed_identity_or_record(x) and bounded_scope(x); OntologyNode(x) =/=> authority_effect(x).
````

- An Ontology Node is an independently identified governed representation of one exact subject revision within one Ontology, with provenance, confidence, lifecycle, branch, and contestability state.
- It is not the represented subject, its identity carrier, its Definition, or proof that its claims are globally true.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/976d20f5da63-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.ontology-node@1.0.0-candidate.1

**Content fingerprint · SHA-256**

976d20f5da63bf6fa774859a878d3d172ccd7b44484364d8caa2fd80f4d36f3e

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An Ontology Node is an independently identified governed representation of one exact subject revision within one Ontology, with provenance, confidence, lifecycle, branch, and contestability state.",
  "authority_scope_ref": "scope:ontology-node-definition",
  "exclusions": [
    "It is not the represented subject, its identity carrier, its Definition, or proof that its claims are globally true.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
