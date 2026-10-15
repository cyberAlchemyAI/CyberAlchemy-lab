[Documentation home](../../README.md)

# Artifact Type Request

<a id="def-cal-definition-artifact-type-request"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Artifact Type Request

# Artifact Type Request

A request explaining a gap when no available type contract fits. The request starts review; it does not itself supply the missing accepted type.

**When it applies**

Recording a non-authoritative request to define and test a genuinely new artifact kind after deterministic resolution finds no admitted fit.

**Record formats**

[Artifact type request · v1](type-cal-artifact-type-artifact-type-request-v1.md#type-cal-artifact-type-artifact-type-request-v1)

**A stated exclusion**

Serving as the requested subject artifact.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-artifact-type-request-section-2"></a>

## Source explanatory wording

When no existing contract fits, write a typed request explaining the gap. Do not create the new kind of record first and hope to classify it later.

<a id="def-cal-definition-artifact-type-request-section-3"></a>

## Exact governing statement

An Artifact Type Request Q is a candidate-only intake record created only after resolve_R(a) is unresolved and compatibility analysis rejects exact reuse. Q describes intended semantics, owner, package home, representation direction, validation purpose, proposed discriminator, and dependencies. Q is neither subject artifact a nor Artifact Type T, cannot satisfy a subject dependency, and has no authority effect.

````
create(Q,a) only if M_R(a)=empty and no_exact_fit(a); Q != a; Q != T; authority_effect(Q)=none; consumed_as_subject(Q)=false.
````

- The requested subject remains unauthored until its exact type exists.
- Draft schemas are attachments or declared request components, not admitted type contracts.
- The request expires or is superseded when resolved, rejected, or replaced.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/ba76127c0cc5-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.artifact-type-request@1.0.0-candidate.2

**Content fingerprint · SHA-256**

ba76127c0cc5c883c53ea2dc91a3618f2aa17bba921b04098c45b1ca2a11c912

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Recording a non-authoritative request to define and test a genuinely new artifact kind after deterministic resolution finds no admitted fit.",
  "authority_scope_ref": "scope:artifact-type-request",
  "exclusions": [
    "Serving as the requested subject artifact.",
    "Self-registering or self-admitting a type.",
    "Widening an existing type by convenience."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
