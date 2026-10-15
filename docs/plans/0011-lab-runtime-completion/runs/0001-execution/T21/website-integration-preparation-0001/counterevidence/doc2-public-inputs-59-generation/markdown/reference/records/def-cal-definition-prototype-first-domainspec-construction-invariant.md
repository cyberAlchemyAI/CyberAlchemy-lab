[Documentation home](../../README.md)

# Prototype-First DomainSpec Construction Invariant

<a id="def-cal-definition-prototype-first-domainspec-construction-invariant"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Prototype-First DomainSpec Construction Invariant

# Prototype-First DomainSpec Construction Invariant

Learn with explicit prototypes, then freeze and assess a particular product only when its model is coherent. Product approval and real-world authority decisions remain separate.

**When it applies**

Construction of a new or materially revised implementation-bearing system or capability in CyberAlchemy-lab.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Purely narrative edits with no implementation-bearing system change.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-prototype-first-domainspec-construction-invariant-section-2"></a>

## Source explanatory wording

First learn with explicit prototypes. Freeze and test one exact product only when the model is coherent. Product approval may then be considered, while every real-world authority decision remains separate.

<a id="def-cal-definition-prototype-first-domainspec-construction-invariant-section-3"></a>

## Exact governing statement

An implementation-bearing construction must begin with prototype definitions, use ontology only as non-authoritative navigation scaffolding, iterate product and implementation prototypes, freeze one exact product candidate, obtain current product-test evidence, and become eligible for product approval before any separate authority request. Product approval grants no operational authority.

````
D -> O_s -> P* -> freeze(P_c@h) -> test(P_c@h) -> eligible(product_approval) -> decision(product_approval) -> eligible(separate_authority_request); O_s.authority=none; product_approval =/=> operational_authority
````

- Prototype epochs may iterate without admission requests.
- Testing binds one exact frozen candidate.
- Changed acceptance-bound bytes require a new test and approval epoch.
- Authority decisions occur only after product approval and remain separate.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/57a3e31a6c47-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.prototype-first-domainspec-construction-invariant@1.0.0-candidate.1

**Content fingerprint · SHA-256**

57a3e31a6c47507713081a4da5c6a7c5b99f26aaf79fc40555cc448aa6c86f61

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Construction of a new or materially revised implementation-bearing system or capability in CyberAlchemy-lab.",
  "authority_scope_ref": "scope:construction",
  "exclusions": [
    "Purely narrative edits with no implementation-bearing system change.",
    "Admission, activation, publication, release, deployment, or external-effect decisions."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
