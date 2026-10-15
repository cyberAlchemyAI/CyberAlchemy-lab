[Documentation home](../../README.md)

# Validation Receipt

<a id="def-cal-definition-validation-receipt"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Validation Receipt

# Validation Receipt

Records what was checked, against which requirements, with which tool and results. It is evidence of validation, not an approval stamp.

**When it applies**

The immutable evidence record emitted for one Validation, binding its exact subject, profile, validator, inputs, environment, outcomes, residue, and claim ceiling.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

The Validation procedure itself.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-validation-receipt-section-2"></a>

## Source explanatory wording

A Validation Receipt is the detailed record of what was checked, against what, with which tool, and what happened. It is a receipt, not an approval stamp.

<a id="def-cal-definition-validation-receipt-section-3"></a>

## Exact governing statement

A Validation Receipt is an immutable record R of one validation event. R binds exact identities and digests for the subject, criteria profile, validator, inputs, environment, complete outcomes, evidence, causal blockers, and claim ceiling. Recording R preserves traceability but cannot change the subject's authority or lifecycle by itself.

````
R = (receipt_id, subject@digest, profile@digest, validator@digest, inputs@digests, environment, outcomes, evidence_refs, blockers, emitted_at, claim_ceiling, authority_effect=none); exists(R) =/=> conforms(subject) or admitted(subject).
````

- The receipt is bound to exact evaluated bytes and profile.
- Every declared check outcome and causal blocker is preserved.
- The receipt authority effect is none.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Semantic foundation admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0007-cml07-semantic-closure/definitions/validation-receipt/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.validation-receipt@1.0.0-candidate.1

**Content fingerprint · SHA-256**

7df65f1254c26f05ad7f030f0616085d7842cbd746751d52bddb8fe72da9fd5e

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:validation-receipt-definition",
  "applicability": "The immutable evidence record emitted for one Validation, binding its exact subject, profile, validator, inputs, environment, outcomes, residue, and claim ceiling.",
  "exclusions": [
    "The Validation procedure itself.",
    "A Conformance assertion unless separately assessed.",
    "An admission, acceptance, authority, publication, or deployment decision."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
