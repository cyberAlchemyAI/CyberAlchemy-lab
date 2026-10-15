[Documentation home](../../README.md)

# Ubiquitous Language

<a id="def-cal-definition-ubiquitous-language"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Ubiquitous Language

# Ubiquitous Language

The shared vocabulary used to discuss and build within one Bounded Context, where its meanings are deliberately consistent.

**When it applies**

Owned expressions used to articulate one exact Bounded Context model.

**Record formats**

[Ubiquitous language · v2](type-cal-artifact-type-ubiquitous-language-v2.md#type-cal-artifact-type-ubiquitous-language-v2)

**A stated exclusion**

Repository-wide dictionaries and programming languages.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-ubiquitous-language-section-2"></a>

## Source explanatory wording

The shared vocabulary used to discuss and build one bounded part of the domain.

<a id="def-cal-definition-ubiquitous-language-section-3"></a>

## Exact governing statement

A Ubiquitous Language is the owner-governed set of expressions, concepts, relations, interpretation rules, usage surfaces, ambiguities, and revision routes used to express one Bounded Context's model. Each load-bearing expression resolves to one current concept disposition within that context or remains explicitly unresolved.

````
UbiquitousLanguage = (id, bounded_context_ref, concept_refs, expression_bindings, relation_bindings, interpretation_rules, usage_surfaces, owner_refs, ambiguity_records, revision_state); CurrentBinding => BelongsTo(bounded_context_ref); SharedSpelling does not imply SharedMeaning.
````

- The language belongs to exactly one Bounded Context identity at a time.
- Cross-context reuse needs an explicit bridge or mapping.
- Ambiguity is recorded, not silently collapsed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Definition and initial context promotion

**Original definition**

[Read the original record](../../assets/17ac271d5e74-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.ubiquitous-language@1.0.0-candidate.1

**Content fingerprint · SHA-256**

17ac271d5e741ce65645bfcdb280ca047abdb2f5460c7fad94064770f37349a7

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:cyberalchemy-lab-context-metamodel",
  "applicability": "Owned expressions used to articulate one exact Bounded Context model.",
  "exclusions": [
    "Repository-wide dictionaries and programming languages.",
    "Unowned glossaries or claims of universal shared understanding."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
