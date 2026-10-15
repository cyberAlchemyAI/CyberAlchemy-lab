[Documentation home](../../README.md)

# Failure Mode

<a id="def-cal-definition-failure-mode"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Failure Mode

A reusable description of a distinct possible failure under stated conditions. It may exist before any actual failure is observed.

**When it applies**

A Failure Mode is a versioned reusable design-time contract for one distinct way a declared subject kind can fail an exact boundary under stated conditions.

**Record formats**

[Failure mode · v1](type-cal-artifact-type-failure-mode-v1.md#type-cal-artifact-type-failure-mode-v1)

**A stated exclusion**

A Failure Mode can predate occurrences and does not establish that any occurrence happened.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

A Failure Mode is a versioned reusable design-time contract for one distinct way a declared subject kind can fail an exact boundary under stated conditions. A Failure Mode can predate occurrences and does not establish that any occurrence happened.

## Exact governing statement

A Failure Mode is a versioned reusable design-time contract for one distinct way a declared subject kind can fail an exact boundary under stated conditions. A Failure Mode can predate occurrences and does not establish that any occurrence happened.

````
FailureMode(x) => governed_identity_or_record(x) and bounded_scope(x); FailureMode(x) =/=> authority_effect(x).
````

- A Failure Mode is a versioned reusable design-time contract for one distinct way a declared subject kind can fail an exact boundary under stated conditions.
- A Failure Mode can predate occurrences and does not establish that any occurrence happened.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/failure-mode/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.failure-mode@1.0.0-candidate.1

**Content fingerprint · SHA-256**

4f8ce94fb3c979ad0c25d7f493bfe6624dbc87456bcf6eaf587810780d124f52

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Failure Mode is a versioned reusable design-time contract for one distinct way a declared subject kind can fail an exact boundary under stated conditions.",
  "authority_scope_ref": "scope:failure-mode-definition",
  "exclusions": [
    "A Failure Mode can predate occurrences and does not establish that any occurrence happened.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
