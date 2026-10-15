[Documentation home](../../README.md)

# Governance Event History

<a id="def-cal-definition-governance-event-history"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Governance Event History

# Governance Event History

A history retaining complete governance observations linked to particular semantic events and upstream evidence. It records governance state; it does not create policies or decisions.

**When it applies**

A Governance Event History is the canonical append-only observation history of complete resulting governance states bound to exact semantic events and upstream Governance evidence.

**Record formats**

[Governance event history · v1](type-cal-artifact-type-governance-event-history-v1.md#type-cal-artifact-type-governance-event-history-v1)

**A stated exclusion**

It records governance state but does not originate or replace Policy, challenge, admission, or other authority decisions.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-governance-event-history-section-2"></a>

## Source explanatory wording

A Governance Event History is the canonical append-only observation history of complete resulting governance states bound to exact semantic events and upstream Governance evidence. It records governance state but does not originate or replace Policy, challenge, admission, or other authority decisions.

<a id="def-cal-definition-governance-event-history-section-3"></a>

## Exact governing statement

A Governance Event History is the canonical append-only observation history of complete resulting governance states bound to exact semantic events and upstream Governance evidence. It records governance state but does not originate or replace Policy, challenge, admission, or other authority decisions.

````
GovernanceEventHistory(x) => governed_identity_or_record(x) and bounded_scope(x); GovernanceEventHistory(x) =/=> authority_effect(x).
````

- A Governance Event History is the canonical append-only observation history of complete resulting governance states bound to exact semantic events and upstream Governance evidence.
- It records governance state but does not originate or replace Policy, challenge, admission, or other authority decisions.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/29da47008390-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.governance-event-history@1.0.0-candidate.1

**Content fingerprint · SHA-256**

29da47008390e0ebfd8a4b3828858dcf9170df3a3414e2ffe1fcfbfd653fbe2a

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Governance Event History is the canonical append-only observation history of complete resulting governance states bound to exact semantic events and upstream Governance evidence.",
  "authority_scope_ref": "scope:governance-event-history-definition",
  "exclusions": [
    "It records governance state but does not originate or replace Policy, challenge, admission, or other authority decisions.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
