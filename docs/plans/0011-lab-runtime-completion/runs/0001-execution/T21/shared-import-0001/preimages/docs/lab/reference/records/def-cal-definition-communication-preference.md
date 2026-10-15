[Documentation home](../../README.md)

# Communication Preference

<a id="def-cal-definition-communication-preference"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Communication Preference

Records a preference about presentation, language, detail or interaction under stated conditions, including expiry and overrides. It does not grant authority or become a policy by being saved.

**When it applies**

A Communication Preference is a scoped expression preference for presentation, language, detail, ordering, or interaction style, with source, audience, target, conditions, strength, expiry, and override rules.

**Record formats**

[Communication preference · v1](type-cal-artifact-type-communication-preference-v1.md#type-cal-artifact-type-communication-preference-v1)

**A stated exclusion**

It is distinct from current instruction, User Decision Preference, Policy, Operational Lesson, and authority.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

A Communication Preference is a scoped expression preference for presentation, language, detail, ordering, or interaction style, with source, audience, target, conditions, strength, expiry, and override rules. It is distinct from current instruction, User Decision Preference, Policy, Operational Lesson, and authority.

## Exact governing statement

A Communication Preference is a scoped expression preference for presentation, language, detail, ordering, or interaction style, with source, audience, target, conditions, strength, expiry, and override rules. It is distinct from current instruction, User Decision Preference, Policy, Operational Lesson, and authority.

````
CommunicationPreference(x) => governed_identity_or_record(x) and bounded_scope(x); CommunicationPreference(x) =/=> authority_effect(x).
````

- A Communication Preference is a scoped expression preference for presentation, language, detail, ordering, or interaction style, with source, audience, target, conditions, strength, expiry, and override rules.
- It is distinct from current instruction, User Decision Preference, Policy, Operational Lesson, and authority.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/communication-preference/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.communication-preference@1.0.0-candidate.1

**Content fingerprint · SHA-256**

6f7ad247a5cb652075707a105e151bec6f88948ea5c795841ca08b67b20a8135

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Communication Preference is a scoped expression preference for presentation, language, detail, ordering, or interaction style, with source, audience, target, conditions, strength, expiry, and override rules.",
  "authority_scope_ref": "scope:communication-preference-definition",
  "exclusions": [
    "It is distinct from current instruction, User Decision Preference, Policy, Operational Lesson, and authority.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
