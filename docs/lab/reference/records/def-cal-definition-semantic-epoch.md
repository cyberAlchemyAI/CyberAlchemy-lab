[Documentation home](../../README.md)

# Semantic Epoch

<a id="def-cal-definition-semantic-epoch"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Semantic Epoch

# Semantic Epoch

An owner-selected version of an artifact’s governing meaning. A material meaning change requires a successor; changed encoding alone does not.

**When it applies**

Versioned semantic artifacts whose normative meaning may change independently of representation.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Schema-only or encoding-only changes preserving meaning.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-semantic-epoch-section-2"></a>

## Source explanatory wording

A new chapter of meaning. It is created because what the artifact means changed, not merely because its JSON shape or generated documentation changed.

<a id="def-cal-definition-semantic-epoch-section-3"></a>

## Exact governing statement

A Semantic Epoch is one immutable owner-selected version of an artifact's normative meaning. A successor Semantic Epoch is required exactly when the owner determines that the artifact's identity-preserving normative meaning, scope, exclusions, owned model, or semantic contracts materially changed. Representation-only revisions and derived refreshes do not create Semantic Epochs.

````
NewSemanticEpoch(a_before,a_after) iff MaterialNormativeMeaning(a_before) != MaterialNormativeMeaning(a_after). RepresentationChanged and MeaningEqual does not imply NewSemanticEpoch.
````

- A byte change alone does not prove semantic change.
- A claim that meaning is preserved is reviewable evidence, not automatic equivalence.
- A semantic successor requires explicit owner selection and applicable lineage.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Craft foundation admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0003-single-decision-checkpoint/definitions/semantic-epoch/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.semantic-epoch@1.0.0-candidate.1

**Content fingerprint · SHA-256**

e138c57bf7a69f958ca966690428bde166ff9d2137f557a14e153e94028272e3

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:cyberalchemy-lab-semantic-versioning",
  "applicability": "Versioned semantic artifacts whose normative meaning may change independently of representation.",
  "exclusions": [
    "Schema-only or encoding-only changes preserving meaning.",
    "Generated projection refreshes.",
    "Lifecycle labels inferred from filesystem paths."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
