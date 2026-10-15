[Documentation home](../../README.md)

# Bounded Context

<a id="def-cal-definition-bounded-context"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Bounded Context

# Bounded Context

A named area of a domain model in which terms and rules have a deliberately consistent meaning. Separate Context Maps record relationships to other areas.

**When it applies**

Explicit owner-scoped semantic boundaries and their versioned models.

**Record formats**

[Bounded context · v3](type-cal-artifact-type-bounded-context-v3.md#type-cal-artifact-type-bounded-context-v3)

**A stated exclusion**

Repository folders or packages without context identity.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-bounded-context-section-2"></a>

## Source explanatory wording

A named boundary within which words and domain rules have one deliberately consistent meaning. It describes itself; the separate Context Maps describe how it relates to other boundaries.

<a id="def-cal-definition-bounded-context-section-3"></a>

## Exact governing statement

A Bounded Context is a versioned, owner-scoped semantic boundary inside which one declared domain model and one Ubiquitous Language are intended to remain internally consistent for an explicit scope and set of exclusions. It owns its identity, model, language, scope, contracts, semantic owner, lifecycle, evidence, and challenge route. A Bounded Context does not canonically own map membership or backreferences to Context Maps. Cross-context endpoint membership and directional relationships are owned only by separately governed Context Maps; reverse membership for a context is a generated projection derived from those maps.

````
BoundedContext = (id, version, domain_model_ref, ubiquitous_language_ref, scope, exclusions, semantic_owner_ref, contract_refs, lifecycle, evidence_refs, challenge_route); Unique(id,version); ContextMapMembership(c) = {m | c in m.context_refs}; CanonicalOwner(ContextMapMembership) = ContextMap; ReverseMembershipIndex(c) = Generate(ContextMapRegistry,c).
````

- A folder name cannot establish context identity.
- Shared spelling across contexts does not imply shared meaning.
- A Bounded Context cannot carry a canonical Context Map backreference.
- Absence from a generated reverse-membership index does not amend any Context Map.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Reference normalization definition promotion

**Original definition**

[Read the original record](../../assets/6ee155d2e742-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.bounded-context@2.0.0-candidate.1

**Content fingerprint · SHA-256**

6ee155d2e7427e33357e55e56bc5228c2b584ea435bb9dc516ddb66385f590c0

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:cyberalchemy-lab-context-metamodel",
  "applicability": "Explicit owner-scoped semantic boundaries and their versioned models.",
  "exclusions": [
    "Repository folders or packages without context identity.",
    "Coordination frames, products, teams, deployment units, and databases.",
    "Canonical ownership of cross-context endpoint membership and directional relationships."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
