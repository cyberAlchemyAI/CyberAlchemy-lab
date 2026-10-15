[Documentation home](../../README.md)

# Withdrawal Record

<a id="def-cal-definition-withdrawal-record"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Withdrawal Record

# Withdrawal Record

Permanently records withdrawal or retirement of an identifier, its reason, owner decision, history and any declared successor. It does not erase history, reuse the identity or automatically replace another record.

**When it applies**

A Withdrawal Record is a permanent governance and lineage record that reserves one retired or rejected identifier, binds the exact withdrawn subject and digest when available, states the reason and effective time, names any successor authority, preserves evidence and owner decision, and exposes a challenge route.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

It does not delete history, erase prior references, reuse the identifier, imply a successor exists, or automatically supersede another subject.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-withdrawal-record-section-2"></a>

## Source explanatory wording

A Withdrawal Record is a permanent governance and lineage record that reserves one retired or rejected identifier, binds the exact withdrawn subject and digest when available, states the reason and effective time, names any successor authority, preserves evidence and owner decision, and exposes a challenge route. It does not delete history, erase prior references, reuse the identifier, imply a successor exists, or automatically supersede another subject.

<a id="def-cal-definition-withdrawal-record-section-3"></a>

## Exact governing statement

A Withdrawal Record is a permanent governance and lineage record that reserves one retired or rejected identifier, binds the exact withdrawn subject and digest when available, states the reason and effective time, names any successor authority, preserves evidence and owner decision, and exposes a challenge route. It does not delete history, erase prior references, reuse the identifier, imply a successor exists, or automatically supersede another subject.

````
WithdrawalRecord(x) => governed(x) and bounded(x); WithdrawalRecord(x) =/=> authority_effect(x).
````

- The withdrawn identifier remains permanently reserved unless an explicit higher-order recovery rule permits restoration.
- A successor reference states lineage or replacement routing and does not merge identities.
- The record remains resolvable for historical consumers after the withdrawn subject becomes inactive.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Definition specialization and resolution admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0014-definition-specialization-resolution/definitions/withdrawal-record/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.withdrawal-record@1.0.0-candidate.1

**Content fingerprint · SHA-256**

f929f75cda1bf96791c2756b481ae55cb58559fdc98d105871c5b6d8b3906571

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Withdrawal Record is a permanent governance and lineage record that reserves one retired or rejected identifier, binds the exact withdrawn subject and digest when available, states the reason and effective time, names any successor authority, preserves evidence and owner decision, and exposes a challenge route.",
  "authority_scope_ref": "scope:withdrawal-record-definition",
  "exclusions": [
    "It does not delete history, erase prior references, reuse the identifier, imply a successor exists, or automatically supersede another subject.",
    "Withdrawal is distinct from deprecation, rejection, suspension, deletion, archival, and ordinary lifecycle closure.",
    "This Definition does not admit a carrier, instance, relation, runtime, consumer, publication, or deployment."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
