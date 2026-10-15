[Documentation home](../../README.md)

# Challenge Contract

<a id="def-cal-definition-challenge-contract"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Challenge Contract

# Challenge Contract

States who may contest which revisions, acceptable reasons and evidence, response ownership, timing and resolution rules. Filing a challenge does not automatically suspend a record.

**When it applies**

A Challenge Contract is a closed versioned Policy-bound mechanism defining challengeable subjects, eligible challengers, grounds, evidence, response modes, owner route, resolution gate, timing, and unresolved residue handling.

**Record formats**

[Challenge contract · v1](type-cal-artifact-type-challenge-contract-v1.md#type-cal-artifact-type-challenge-contract-v1)

**A stated exclusion**

A route string alone is not a Challenge Contract, and filing a challenge does not automatically suspend or reverse the subject.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-challenge-contract-section-2"></a>

## Source explanatory wording

A Challenge Contract is a closed versioned Policy-bound mechanism defining challengeable subjects, eligible challengers, grounds, evidence, response modes, owner route, resolution gate, timing, and unresolved residue handling. A route string alone is not a Challenge Contract, and filing a challenge does not automatically suspend or reverse the subject.

<a id="def-cal-definition-challenge-contract-section-3"></a>

## Exact governing statement

A Challenge Contract is a closed versioned Policy-bound mechanism defining challengeable subjects, eligible challengers, grounds, evidence, response modes, owner route, resolution gate, timing, and unresolved residue handling. A route string alone is not a Challenge Contract, and filing a challenge does not automatically suspend or reverse the subject.

````
ChallengeContract(x) => governed_identity_or_record(x) and bounded_scope(x); ChallengeContract(x) =/=> authority_effect(x).
````

- A Challenge Contract is a closed versioned Policy-bound mechanism defining challengeable subjects, eligible challengers, grounds, evidence, response modes, owner route, resolution gate, timing, and unresolved residue handling.
- A route string alone is not a Challenge Contract, and filing a challenge does not automatically suspend or reverse the subject.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/challenge-contract/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.challenge-contract@1.0.0-candidate.1

**Content fingerprint · SHA-256**

128f787e53c7afe5ee74b762e5c53d4e7162e94c65f5e88bc6c91d3f970e54be

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Challenge Contract is a closed versioned Policy-bound mechanism defining challengeable subjects, eligible challengers, grounds, evidence, response modes, owner route, resolution gate, timing, and unresolved residue handling.",
  "authority_scope_ref": "scope:challenge-contract-definition",
  "exclusions": [
    "A route string alone is not a Challenge Contract, and filing a challenge does not automatically suspend or reverse the subject.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
