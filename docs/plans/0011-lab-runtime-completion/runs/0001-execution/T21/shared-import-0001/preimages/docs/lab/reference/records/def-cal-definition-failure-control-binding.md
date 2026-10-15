[Documentation home](../../README.md)

# Failure Control Binding

<a id="def-cal-definition-failure-control-binding"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Failure Control Binding

Associates a particular failure-pattern version with one control and its primary role: prevent, detect, contain, recover or compensate. It records intent, not proof of execution or effectiveness.

**When it applies**

A Failure Control Binding is a lifecycle-bearing association between one exact Failure Mode revision and one exact control with exactly one primary role: prevent, detect, contain, recover, or compensate.

**Record formats**

[Failure control binding · v1](type-cal-artifact-type-failure-control-binding-v1.md#type-cal-artifact-type-failure-control-binding-v1)

**A stated exclusion**

The binding records intended control and does not prove installation, activation, execution, effectiveness, safety, or authorization.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

A Failure Control Binding is a lifecycle-bearing association between one exact Failure Mode revision and one exact control with exactly one primary role: prevent, detect, contain, recover, or compensate. The binding records intended control and does not prove installation, activation, execution, effectiveness, safety, or authorization.

## Exact governing statement

A Failure Control Binding is a lifecycle-bearing association between one exact Failure Mode revision and one exact control with exactly one primary role: prevent, detect, contain, recover, or compensate. The binding records intended control and does not prove installation, activation, execution, effectiveness, safety, or authorization.

````
FailureControlBinding(x) => governed_identity_or_record(x) and bounded_scope(x); FailureControlBinding(x) =/=> authority_effect(x).
````

- A Failure Control Binding is a lifecycle-bearing association between one exact Failure Mode revision and one exact control with exactly one primary role: prevent, detect, contain, recover, or compensate.
- The binding records intended control and does not prove installation, activation, execution, effectiveness, safety, or authorization.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/failure-control-binding/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.failure-control-binding@1.0.0-candidate.1

**Content fingerprint · SHA-256**

35b61329166fea2e0cb7fdc4846aa8063100a2fa63d0930515de80cb3b67b3f2

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Failure Control Binding is a lifecycle-bearing association between one exact Failure Mode revision and one exact control with exactly one primary role: prevent, detect, contain, recover, or compensate.",
  "authority_scope_ref": "scope:failure-control-binding-definition",
  "exclusions": [
    "The binding records intended control and does not prove installation, activation, execution, effectiveness, safety, or authorization.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
