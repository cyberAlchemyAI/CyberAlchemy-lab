[Documentation home](../../README.md)

# Artifact Type

<a id="def-cal-definition-artifact-type"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Artifact Type

# Artifact Type

The contract for records of a particular kind: their meaning bindings, designated machine format, human views and checks. Accepting the type does not accept every record using it.

**When it applies**

When declaring or inspecting the requirements for a particular kind of record.

**Record formats**

[Artifact type request · v1](type-cal-artifact-type-artifact-type-request-v1.md#type-cal-artifact-type-artifact-type-request-v1) · [Artifact type · v3](type-cal-artifact-type-artifact-type-v3.md#type-cal-artifact-type-artifact-type-v3) · [Canonical package manifest · v1](type-cal-artifact-type-canonical-package-manifest-v1.md#type-cal-artifact-type-canonical-package-manifest-v1) · [Artifact type · v1](type-cal-artifact-type-repository-migration-manifest-v1.md#type-cal-artifact-type-repository-migration-manifest-v1)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

The Work contract specifies how investigation records identify their kind and carry the required information.

**Common mistake**

Assuming a record conforms because its filename says “work.”

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-artifact-type-section-2"></a>

## Source explanatory wording

An Artifact Type is the contract for a kind of file: what it means, which machine shape is canonical, how people see it, how it is checked, and what a passing check does not prove.

<a id="def-cal-definition-artifact-type-section-3"></a>

## Exact governing statement

An Artifact Type is a versioned contract T for one artifact kind. T binds at least one semantic Definition, a closed machine schema, canonical-source direction, deterministic human projection, validation rules, owner route, lifecycle posture, and claim ceiling. Registration of T neither defines its subject meaning nor admits T or any instance.

````
T = (type_id, version, semantic_definition_refs, schema@digest, canonical_direction, projection_contract, validation_contract, owner_route, lifecycle, claim_ceiling); valid_new_registration(T) only if semantic_definition_refs(T) != empty; registered(T) =/=> admitted(T).
````

- The Artifact Type and every artifact instance retain separate identities.
- A schema constrains representation but cannot supply missing semantic meaning.
- A candidate Definition reference may support candidate authoring but must be admitted before Artifact Type admission.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Semantic foundation admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0007-cml07-semantic-closure/definitions/artifact-type/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.artifact-type@1.0.0-candidate.1

**Content fingerprint · SHA-256**

90c61c2fa5a5f1d5d0a96d8e6c1f4b1f902e8ad57d85ef1e315e549470abb69f

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:artifact-type-definition",
  "applicability": "The versioned contract that determines the admissible machine representation, semantic Definition bindings, generated human projection, validation surface, ownership, and claim ceiling for one artifact kind.",
  "exclusions": [
    "An artifact instance.",
    "A Definition of the artifact's subject meaning.",
    "An admission decision, validator execution, or authority grant."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
