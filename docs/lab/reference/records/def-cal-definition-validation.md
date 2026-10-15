[Documentation home](../../README.md)

# Validation

<a id="def-cal-definition-validation"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Validation

# Validation

Executes specified checks on specified inputs. Passing reports those checks, not every possible requirement or owner acceptance.

**When it applies**

An Evaluation against declared validation criteria that produces a Validation Receipt for an exact subject, profile, inputs, and evaluation environment.

**Record formats**

[Artifact type · v1](type-cal-artifact-type-repository-migration-manifest-v1.md#type-cal-artifact-type-repository-migration-manifest-v1)

**A stated exclusion**

Semantic truth beyond the declared checks.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-validation-section-2"></a>

## Source explanatory wording

Validation runs known checks. A PASS means those checks passed for those exact inputs—not that every possible requirement is satisfied or that anything was approved.

<a id="def-cal-definition-validation-section-3"></a>

## Exact governing statement

Validation is an Evaluation V of exact subject S against exact criteria profile P. V produces check outcomes and a receipt. A PASS establishes only that every evaluable criterion declared by P passed for the bound inputs; it becomes conformance evidence only when an applicable conformance profile declares those checks sufficient for an exact scope.

````
validate(P@digest, S@digest, I@digest) -> receipt(O); PASS(V) =/=> conforms(S,C,Q); PASS(V) =/=> admitted(S).
````

- The validation profile declares its coverage and evaluation mode.
- A PASS cannot cover omitted or NOT_EVALUABLE checks.
- Conformance and authority decisions remain separately owned.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Semantic foundation admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0007-cml07-semantic-closure/definitions/validation/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.validation@1.0.0-candidate.1

**Content fingerprint · SHA-256**

f21ca27867379eb3389588313208a5db37cf0449b79bb5c7f644c3b9a89a2af8

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:validation-definition",
  "applicability": "An Evaluation against declared validation criteria that produces a Validation Receipt for an exact subject, profile, inputs, and evaluation environment.",
  "exclusions": [
    "Semantic truth beyond the declared checks.",
    "Conformance outside the profile's complete coverage.",
    "Admission, acceptance, implementation, publication, or deployment authority."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
