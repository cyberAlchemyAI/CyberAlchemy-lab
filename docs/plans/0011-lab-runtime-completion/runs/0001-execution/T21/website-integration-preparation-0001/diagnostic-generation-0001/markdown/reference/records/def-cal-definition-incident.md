[Documentation home](../../README.md)

# Incident

<a id="def-cal-definition-incident"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Incident

# Incident

Coordinates response and accountability for related failures or uncertain impacts, with ownership, timeline, decisions and closure. Closing it retains evidence and unresolved obligations.

**When it applies**

When related failure occurrences require coordinated ownership, investigation, containment, recovery, communication and closure.

**Record formats**

[Incident · v1](type-cal-artifact-type-incident-v1.md#type-cal-artifact-type-incident-v1)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

The customer-data service owner coordinates investigation and response under the open incident.

**Common mistake**

Closing the incident merely because the agent prepared a proposal.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-incident-section-2"></a>

## Source explanatory wording

An Incident is a governed response and accountability envelope for related Failure Occurrences whose impact or uncertainty requires coordinated ownership, timeline, containment, recovery, communications, decisions, evidence, and closure. Closure does not erase occurrences, residue, unknown delivery, causal uncertainty, or follow-up obligations.

<a id="def-cal-definition-incident-section-3"></a>

## Exact governing statement

An Incident is a governed response and accountability envelope for related Failure Occurrences whose impact or uncertainty requires coordinated ownership, timeline, containment, recovery, communications, decisions, evidence, and closure. Closure does not erase occurrences, residue, unknown delivery, causal uncertainty, or follow-up obligations.

````
Incident(x) => governed_identity_or_record(x) and bounded_scope(x); Incident(x) =/=> authority_effect(x).
````

- An Incident is a governed response and accountability envelope for related Failure Occurrences whose impact or uncertainty requires coordinated ownership, timeline, containment, recovery, communications, decisions, evidence, and closure.
- Closure does not erase occurrences, residue, unknown delivery, causal uncertainty, or follow-up obligations.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/41801c4c7b27-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.incident@1.0.0-candidate.1

**Content fingerprint · SHA-256**

41801c4c7b273c03f73fd40a45d66806d9ff809761026d03da609cd3872953ab

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An Incident is a governed response and accountability envelope for related Failure Occurrences whose impact or uncertainty requires coordinated ownership, timeline, containment, recovery, communications, decisions, evidence, and closure.",
  "authority_scope_ref": "scope:incident-definition",
  "exclusions": [
    "Closure does not erase occurrences, residue, unknown delivery, causal uncertainty, or follow-up obligations.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
