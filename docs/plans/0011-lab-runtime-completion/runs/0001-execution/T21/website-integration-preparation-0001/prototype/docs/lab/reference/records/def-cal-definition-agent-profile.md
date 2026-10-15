[Documentation home](../../README.md)

# Agent Profile

<a id="def-cal-definition-agent-profile"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Agent Profile

# Agent Profile

Reusable, versioned rules for expected agent behavior, inputs, outputs, tools, evidence, escalation and stopping. The profile is saved project knowledge, not a live agent or permission grant.

**When it applies**

An Agent Profile is a reusable versioned contract for allowed inputs, outputs, behavior, Policies, Context, tool classes, evidence, escalation, and stop conditions.

**Record formats**

[Agent profile · v1](type-cal-artifact-type-agent-profile-v1.md#type-cal-artifact-type-agent-profile-v1)

**A stated exclusion**

An Agent Profile is durable reusable Project State and is never the active Agent, Instance, Session, model, or Implementation.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-agent-profile-section-2"></a>

## Source explanatory wording

An Agent Profile is a reusable versioned contract for allowed inputs, outputs, behavior, Policies, Context, tool classes, evidence, escalation, and stop conditions. An Agent Profile is durable reusable Project State and is never the active Agent, Instance, Session, model, or Implementation.

<a id="def-cal-definition-agent-profile-section-3"></a>

## Exact governing statement

An Agent Profile is a reusable versioned contract for allowed inputs, outputs, behavior, Policies, Context, tool classes, evidence, escalation, and stop conditions. A Profile is neither an active Agent Instance, Session, capability grant, Implementation, model, nor authority grant.

````
AgentProfile(x) => governed_identity_or_record(x) and bounded_scope(x); AgentProfile(x) =/=> authority_effect(x).
````

- An Agent Profile is durable reusable Project State and is never the active Agent, Instance, Session, model, or Implementation.
- A Profile constrains behavior but grants no Assignment, authority, tool access, or successful performance.
- A Profile change creates a versioned successor under owner review; an active Machine Agent cannot silently rewrite or activate its own Profile.
- Profile memory or retained lessons must be explicit governed references; hidden cross-session memory is forbidden.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/0eb4347c7638-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.agent-profile@1.0.0-candidate.1

**Content fingerprint · SHA-256**

0eb4347c76387022f33d1c9165ddb5e26f89a746b3f3c73518d3d4a364bc2c2e

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An Agent Profile is a reusable versioned contract for allowed inputs, outputs, behavior, Policies, Context, tool classes, evidence, escalation, and stop conditions.",
  "authority_scope_ref": "scope:agent-profile-definition",
  "exclusions": [
    "An Agent Profile is durable reusable Project State and is never the active Agent, Instance, Session, model, or Implementation.",
    "A Profile constrains behavior but grants no Assignment, authority, tool access, or successful performance.",
    "A Profile change creates a versioned successor under owner review; an active Machine Agent cannot silently rewrite or activate its own Profile.",
    "Profile memory or retained lessons must be explicit governed references; hidden cross-session memory is forbidden.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
