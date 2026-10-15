[Documentation home](../../README.md)

# Improvement Target

<a id="def-cal-definition-improvement-target"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Improvement Target

An owner-reviewed, deduplicated statement of a recurring weakness or opportunity routed into research, experiments or technical changes. It does not authorize automatic self-modification.

**When it applies**

An Improvement Target is an owner-reviewed deduplicated statement of a recurring weakness or opportunity routed into Research, Experiment, Profile, Policy, validation, or Implementation work.

**Record formats**

[Improvement target · v1](type-cal-artifact-type-improvement-target-v1.md#type-cal-artifact-type-improvement-target-v1)

**A stated exclusion**

It is neither a self-upgrade authorization nor proof of cause, feasibility, or benefit.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

An Improvement Target is an owner-reviewed deduplicated statement of a recurring weakness or opportunity routed into Research, Experiment, Profile, Policy, validation, or Implementation work. It is neither a self-upgrade authorization nor proof of cause, feasibility, or benefit.

## Exact governing statement

An Improvement Target is an owner-reviewed deduplicated statement of a recurring weakness or opportunity routed into Research, Experiment, Profile, Policy, validation, or Implementation work. It is neither a self-upgrade authorization nor proof of cause, feasibility, or benefit.

````
ImprovementTarget(x) => governed_identity_or_record(x) and bounded_scope(x); ImprovementTarget(x) =/=> authority_effect(x).
````

- An Improvement Target is an owner-reviewed deduplicated statement of a recurring weakness or opportunity routed into Research, Experiment, Profile, Policy, validation, or Implementation work.
- It is neither a self-upgrade authorization nor proof of cause, feasibility, or benefit.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/improvement-target/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.improvement-target@1.0.0-candidate.1

**Content fingerprint · SHA-256**

9f37b63646e4dcd88e6ddb34eae0aad0e688634ca9af563508fab890f1ef3dd6

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An Improvement Target is an owner-reviewed deduplicated statement of a recurring weakness or opportunity routed into Research, Experiment, Profile, Policy, validation, or Implementation work.",
  "authority_scope_ref": "scope:improvement-target-definition",
  "exclusions": [
    "It is neither a self-upgrade authorization nor proof of cause, feasibility, or benefit.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
