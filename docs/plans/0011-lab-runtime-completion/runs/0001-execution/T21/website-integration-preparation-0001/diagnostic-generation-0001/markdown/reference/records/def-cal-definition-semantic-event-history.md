[Documentation home](../../README.md)

# Semantic Event History

<a id="def-cal-definition-semantic-event-history"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Semantic Event History

# Semantic Event History

Retains complete resulting meaning-bearing states for an ontology subject in order for reconstruction. Its generated snapshots do not become competing history sources.

**When it applies**

A Semantic Event History is the canonical append-only replay history of complete resulting semantic states for one Ontology subject under exact ordering and integrity rules.

**Record formats**

[Semantic event history · v1](type-cal-artifact-type-semantic-event-history-v1.md#type-cal-artifact-type-semantic-event-history-v1)

**A stated exclusion**

It does not own Governance decisions, and its calculated snapshots or views are not competing replay sources.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-semantic-event-history-section-2"></a>

## Source explanatory wording

A Semantic Event History is the canonical append-only replay history of complete resulting semantic states for one Ontology subject under exact ordering and integrity rules. It does not own Governance decisions, and its calculated snapshots or views are not competing replay sources.

<a id="def-cal-definition-semantic-event-history-section-3"></a>

## Exact governing statement

A Semantic Event History is the canonical append-only replay history of complete resulting semantic states for one Ontology subject under exact ordering and integrity rules. It does not own Governance decisions, and its calculated snapshots or views are not competing replay sources.

````
SemanticEventHistory(x) => governed_identity_or_record(x) and bounded_scope(x); SemanticEventHistory(x) =/=> authority_effect(x).
````

- A Semantic Event History is the canonical append-only replay history of complete resulting semantic states for one Ontology subject under exact ordering and integrity rules.
- It does not own Governance decisions, and its calculated snapshots or views are not competing replay sources.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/5eee07c5ba67-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.semantic-event-history@1.0.0-candidate.1

**Content fingerprint · SHA-256**

5eee07c5ba67a00b79bc331fa6d5443ab1fd7c741ff7e484a6baca3337fe6959

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Semantic Event History is the canonical append-only replay history of complete resulting semantic states for one Ontology subject under exact ordering and integrity rules.",
  "authority_scope_ref": "scope:semantic-event-history-definition",
  "exclusions": [
    "It does not own Governance decisions, and its calculated snapshots or views are not competing replay sources.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
