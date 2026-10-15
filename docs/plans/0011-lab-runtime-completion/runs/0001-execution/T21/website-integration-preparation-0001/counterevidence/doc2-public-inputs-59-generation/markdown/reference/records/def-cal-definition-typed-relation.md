[Documentation home](../../README.md)

# Typed Relation

<a id="def-cal-definition-typed-relation"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Typed Relation

# Typed Relation

One identified global connection between specific source and target versions under an accepted Relation Kind and allowed pair, with required details and governance. A graph projection does not create or validate it.

**When it applies**

When connecting governed subjects through a declared meaning, ordered endpoint pair and required qualifiers.

**Record formats**

[Typed relation · v3](type-cal-artifact-type-typed-relation-v3.md#type-cal-artifact-type-typed-relation-v3)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

A source-bound observation can originate from a Source under a declared ordered pair and qualifier contract.

**Common mistake**

Drawing a convenient connection without a declared signature and required qualifiers.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-typed-relation-section-2"></a>

## Source explanatory wording

A Typed Relation is one independently identified global connection between exact source and target instances under one admitted Relation Kind version, exact allowed pair, qualifiers, owner, evidence, lifecycle, and contestability contract. It neither merges endpoint identities nor becomes valid from schema fields, shared paths, Ontology projection, or candidate validation.

<a id="def-cal-definition-typed-relation-section-3"></a>

## Exact governing statement

A Typed Relation is one independently identified global connection between exact source and target instances under one admitted Relation Kind version, exact allowed pair, qualifiers, owner, evidence, lifecycle, and contestability contract. It neither merges endpoint identities nor becomes valid from schema fields, shared paths, Ontology projection, or candidate validation.

````
TypedRelation(x) => governed_identity_or_record(x) and bounded_scope(x); TypedRelation(x) =/=> authority_effect(x).
````

- A Typed Relation is one independently identified global connection between exact source and target instances under one admitted Relation Kind version, exact allowed pair, qualifiers, owner, evidence, lifecycle, and contestability contract.
- It neither merges endpoint identities nor becomes valid from schema fields, shared paths, Ontology projection, or candidate validation.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/e9799dbdbb40-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.typed-relation@1.0.0-candidate.1

**Content fingerprint · SHA-256**

e9799dbdbb40a9de8fe44eb73c813c256c04206d0956b4417e1371ec7f72dec5

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Typed Relation is one independently identified global connection between exact source and target instances under one admitted Relation Kind version, exact allowed pair, qualifiers, owner, evidence, lifecycle, and contestability contract.",
  "authority_scope_ref": "scope:typed-relation-definition",
  "exclusions": [
    "It neither merges endpoint identities nor becomes valid from schema fields, shared paths, Ontology projection, or candidate validation.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
