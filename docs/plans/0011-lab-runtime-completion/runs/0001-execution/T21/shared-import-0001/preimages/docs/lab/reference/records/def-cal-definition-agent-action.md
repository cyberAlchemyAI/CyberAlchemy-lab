[Documentation home](../../README.md)

# Agent Action

<a id="def-cal-definition-agent-action"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Agent Action

A saved record of one proposed, attempted, completed, rejected or failed operation, identifying the agent instance and session responsible.

**When it applies**

An Agent Action is an immutable attributable record of one proposed, attempted, completed, rejected, or failed operation by an Agent Instance within one Session.

**Record formats**

[Agent action · v1](type-cal-artifact-type-agent-action-v1.md#type-cal-artifact-type-agent-action-v1)

**A stated exclusion**

Every Agent Action is attributed to one exact Agent Instance inside one exact active Session.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

An Agent Action is an immutable attributable record of one proposed, attempted, completed, rejected, or failed operation by an Agent Instance within one Session. Every Agent Action is attributed to one exact Agent Instance inside one exact active Session.

## Exact governing statement

An Agent Action is an immutable attributable record of one proposed, attempted, completed, rejected, or failed operation by an Agent Instance within one Session. The Action record does not prove that its claimed output, delivery, or external effect occurred.

````
Action(x,i,s) => Active(i,s) and within(time(x),s) and InputsBound(x) and AuthorityEvidence(x); ClaimedEffect(x,e) =/=> ObservedEffect(e).
````

- Every Agent Action is attributed to one exact Agent Instance inside one exact active Session.
- Proposed, attempted, completed, rejected, failed, delivered, and effect-observed are distinct postures.
- An Action binds exact inputs, outputs, Tools, Methods, Implementations, Policies, authority evidence, approvals, receipts, and residue as applicable.
- An Action record proves attribution and recorded posture only; delivery, external effect, acceptance, correctness, and authority effect require separate evidence or Decisions.
- Corrections create successor records or linked assessments; they do not erase the original Action.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/agent-action/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.agent-action@1.0.0-candidate.1

**Content fingerprint · SHA-256**

0e44d2d49dabd6f12831757a9e004878a8101387f6542b8e8f4b0b4ea74b8313

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An Agent Action is an immutable attributable record of one proposed, attempted, completed, rejected, or failed operation by an Agent Instance within one Session.",
  "authority_scope_ref": "scope:agent-action-definition",
  "exclusions": [
    "Every Agent Action is attributed to one exact Agent Instance inside one exact active Session.",
    "Proposed, attempted, completed, rejected, failed, delivered, and effect-observed are distinct postures.",
    "An Action binds exact inputs, outputs, Tools, Methods, Implementations, Policies, authority evidence, approvals, receipts, and residue as applicable.",
    "An Action record proves attribution and recorded posture only; delivery, external effect, acceptance, correctness, and authority effect require separate evidence or Decisions.",
    "Corrections create successor records or linked assessments; they do not erase the original Action.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
