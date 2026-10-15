[Documentation home](../../README.md)

# Preference Application Assessment

<a id="def-cal-definition-preference-application-assessment"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Preference Application Assessment

Checks whether a particular communication preference applies to one output, conflicts, is overridden or cannot be followed. It does not prove satisfaction or rewrite the preference.

**When it applies**

A Preference Application Assessment is a request-bound determination of whether one exact Communication Preference revision applies, conflicts, is overridden, or is infeasible for one output.

**Record formats**

[Preference application assessment · v1](type-cal-artifact-type-preference-application-assessment-v1.md#type-cal-artifact-type-preference-application-assessment-v1)

**A stated exclusion**

It neither rewrites the preference nor proves user satisfaction or authorization.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

A Preference Application Assessment is a request-bound determination of whether one exact Communication Preference revision applies, conflicts, is overridden, or is infeasible for one output. It neither rewrites the preference nor proves user satisfaction or authorization.

## Exact governing statement

A Preference Application Assessment is a request-bound determination of whether one exact Communication Preference revision applies, conflicts, is overridden, or is infeasible for one output. It neither rewrites the preference nor proves user satisfaction or authorization.

````
PreferenceApplicationAssessment(x) => governed_identity_or_record(x) and bounded_scope(x); PreferenceApplicationAssessment(x) =/=> authority_effect(x).
````

- A Preference Application Assessment is a request-bound determination of whether one exact Communication Preference revision applies, conflicts, is overridden, or is infeasible for one output.
- It neither rewrites the preference nor proves user satisfaction or authorization.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/preference-application-assessment/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.preference-application-assessment@1.0.0-candidate.1

**Content fingerprint · SHA-256**

6fc0b80234091c228c51207d5c7117db1d54980266b7ec958b1e53cdda1ca88e

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Preference Application Assessment is a request-bound determination of whether one exact Communication Preference revision applies, conflicts, is overridden, or is infeasible for one output.",
  "authority_scope_ref": "scope:preference-application-assessment-definition",
  "exclusions": [
    "It neither rewrites the preference nor proves user satisfaction or authorization.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
