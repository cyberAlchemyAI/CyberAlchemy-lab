[Documentation home](../../README.md)

# Project Governance Event History

<a id="def-cal-definition-project-governance-event-history"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Project Governance Event History

# Project Governance Event History

Retains why particular Project State changes were accepted, linking authorization and evidence to exact change events. It does not alter the resulting state or originate authority.

**When it applies**

A Project Governance Event History is the canonical append-only governance history for Project State transitions, binding each governance event to one exact semantic event tuple, owner decision, authorization, Policy, Challenge Contract, and upstream evidence.

**Record formats**

[Project governance event history · v2](type-cal-artifact-type-project-governance-event-history-v2.md#type-cal-artifact-type-project-governance-event-history-v2)

**A stated exclusion**

It records why and under which authority a Project State transition was accepted; it cannot patch semantic state or originate authority by itself.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-project-governance-event-history-section-2"></a>

## Source explanatory wording

A Project Governance Event History is the canonical append-only governance history for Project State transitions, binding each governance event to one exact semantic event tuple, owner decision, authorization, Policy, Challenge Contract, and upstream evidence. It records why and under which authority a Project State transition was accepted; it cannot patch semantic state or originate authority by itself.

<a id="def-cal-definition-project-governance-event-history-section-3"></a>

## Exact governing statement

A Project Governance Event History is the canonical append-only governance history for Project State transitions, binding each governance event to one exact semantic event tuple, owner decision, authorization, Policy, Challenge Contract, and upstream evidence. It records why and under which authority a Project State transition was accepted; it cannot patch semantic state or originate authority by itself.

````
ProjectGovernanceEventHistory(x) => append_only(x) and digest_bound(x); ProjectGovernanceEventHistory(x) =/=> authority_effect(x).
````

- A Project Governance Event History is the canonical append-only governance history for Project State transitions, binding each governance event to one exact semantic event tuple, owner decision, authorization, Policy, Challenge Contract, and upstream evidence.
- It records why and under which authority a Project State transition was accepted; it cannot patch semantic state or originate authority by itself.
- Identity, evidence, authority, and lifecycle effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Initial Project State admission

**Original definition**

[Read the original record](../../assets/febee304934b-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.project-governance-event-history@1.0.0-candidate.1

**Content fingerprint · SHA-256**

febee304934b8b341feac5564ad06a0631e5163d04c414e63a29a704304ff1a5

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Project Governance Event History is the canonical append-only governance history for Project State transitions, binding each governance event to one exact semantic event tuple, owner decision, authorization, Policy, Challenge Contract, and upstream evidence.",
  "authority_scope_ref": "scope:project-governance-event-history-definition",
  "exclusions": [
    "It records why and under which authority a Project State transition was accepted; it cannot patch semantic state or originate authority by itself.",
    "This Definition does not create an Artifact Type, instance, Typed Relation, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
