[Documentation home](../../README.md)

# Project Semantic Event History

<a id="def-cal-definition-project-semantic-event-history"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Project Semantic Event History

# Project Semantic Event History

Retains complete resulting Project State changes and their predecessors in order so state can be reconstructed. It records what changed, not whether the change was authorized.

**When it applies**

A Project Semantic Event History is the canonical append-only replay history of complete resulting Project State transitions for one Project, ordered by semantic cursor and bound to exact predecessor state, resulting state, source materials, and digests.

**Record formats**

[Project semantic event history · v2](type-cal-artifact-type-project-semantic-event-history-v2.md#type-cal-artifact-type-project-semantic-event-history-v2)

**A stated exclusion**

It records what durable Project State changed; it does not decide whether the change was authorized and it is not an Ontology projection or Agent memory.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-project-semantic-event-history-section-2"></a>

## Source explanatory wording

A Project Semantic Event History is the canonical append-only replay history of complete resulting Project State transitions for one Project, ordered by semantic cursor and bound to exact predecessor state, resulting state, source materials, and digests. It records what durable Project State changed; it does not decide whether the change was authorized and it is not an Ontology projection or Agent memory.

<a id="def-cal-definition-project-semantic-event-history-section-3"></a>

## Exact governing statement

A Project Semantic Event History is the canonical append-only replay history of complete resulting Project State transitions for one Project, ordered by semantic cursor and bound to exact predecessor state, resulting state, source materials, and digests. It records what durable Project State changed; it does not decide whether the change was authorized and it is not an Ontology projection or Agent memory.

````
ProjectSemanticEventHistory(x) => append_only(x) and digest_bound(x); ProjectSemanticEventHistory(x) =/=> authority_effect(x).
````

- A Project Semantic Event History is the canonical append-only replay history of complete resulting Project State transitions for one Project, ordered by semantic cursor and bound to exact predecessor state, resulting state, source materials, and digests.
- It records what durable Project State changed; it does not decide whether the change was authorized and it is not an Ontology projection or Agent memory.
- Identity, evidence, authority, and lifecycle effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Initial Project State admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0015-project-state-event-histories/definitions/project-semantic-event-history/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.project-semantic-event-history@1.0.0-candidate.1

**Content fingerprint · SHA-256**

e55d310b558282fb70c4f24a448afe1bbb01e8fa561ec5f802235b67dc216e11

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Project Semantic Event History is the canonical append-only replay history of complete resulting Project State transitions for one Project, ordered by semantic cursor and bound to exact predecessor state, resulting state, source materials, and digests.",
  "authority_scope_ref": "scope:project-semantic-event-history-definition",
  "exclusions": [
    "It records what durable Project State changed; it does not decide whether the change was authorized and it is not an Ontology projection or Agent memory.",
    "This Definition does not create an Artifact Type, instance, Typed Relation, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
