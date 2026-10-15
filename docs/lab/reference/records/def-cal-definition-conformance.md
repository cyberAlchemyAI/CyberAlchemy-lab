[Documentation home](../../README.md)

# Conformance

<a id="def-cal-definition-conformance"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Conformance

# Conformance

An evidence-supported statement that a particular thing meets a particular contract within stated conditions. Passing some checks does not establish broader compliance.

**When it applies**

A current, scoped, evidence-backed relation asserting that one exact subject satisfies one exact contract version under one applicable conformance profile.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

A free-standing status label.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-conformance-section-2"></a>

## Source explanatory wording

Conformance says that one exact thing meets one exact contract for a clearly named scope, backed by enough current evidence. Passing a few checks—or matching a schema—does not automatically prove a broader kind of conformance.

<a id="def-cal-definition-conformance-section-3"></a>

## Exact governing statement

Conformance is a relation among an exact subject S, exact contract C, declared scope Q, applicable profile P, current evidence set E, and assessment owner. It may be asserted only when P declares E sufficient for every obligation in Q. Different conformance scopes remain orthogonal and cannot be inferred from one another.

````
conforms(S@digest, C@digest, Q, P@version, E) only if complete(P,Q) and current(E) and satisfies(E, obligations(C,Q)); schema_conformance(S) =/=> identity_contract_conformance(S) =/=> implementation_conformance(S) =/=> runtime_conformance(S).
````

- Subject, contract, scope, profile, evidence, and owner are explicit.
- Evidence stale against either subject or contract makes the claim not current.
- Schema, identity-contract, implementation, and runtime conformance are separate scopes.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Semantic foundation admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0007-cml07-semantic-closure/definitions/conformance/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.conformance@1.0.0-candidate.1

**Content fingerprint · SHA-256**

4c5086458118bc780d0982e167432adc2b97ddbea8ffc09a36a629146813dd93

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:conformance-definition",
  "applicability": "A current, scoped, evidence-backed relation asserting that one exact subject satisfies one exact contract version under one applicable conformance profile.",
  "exclusions": [
    "A free-standing status label.",
    "A validator PASS without declared completeness for the conformance scope.",
    "Admission, semantic truth, implementation existence, runtime behavior, publication, or deployment authority."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
