[Documentation home](../../README.md)

# Decision Bundle

<a id="def-cal-definition-decision-bundle"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Decision Bundle

Presents several specific decisions in one review while retaining each decision’s owner, targets and consequences. Shared presentation does not expand authority.

**When it applies**

A closed presentation set of independently scoped Governance Decisions at one Decision Checkpoint.

**Record formats**

[Decision bundle · v1](type-cal-artifact-type-decision-bundle-v1.md#type-cal-artifact-type-decision-bundle-v1)

**A stated exclusion**

A merged authority grant.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

Several exact decisions shown together once. The person sees one interaction, but each decision keeps its own owner, target, and consequence.

## Exact governing statement

A Decision Bundle is a closed ordered set of exact Governance Decision requests presented at one Decision Checkpoint. Every member retains an independent decision identity, Authority Boundary, owner role, accountable principal, immutable target, digest when bytes exist, requested effect, scope, outcome, and invalidation conditions. Bundling reduces human interaction count but cannot merge roles, infer authorization between members, or make one member's outcome satisfy another member's gate.

````
DecisionBundle(B,c) iff FiniteClosed(B) and forall d in B: Checkpoint(d)=c and ExactTarget(d) and ExactOwner(d) and ExactEffect(d). Authority(B) = union of no implicit authority; Authorized(B) iff forall d in B: Authorized(d).
````

- A shared principal does not collapse member owner roles.
- One approved member does not approve another member.
- A member whose exact target does not yet exist cannot enter the bundle.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0003-single-decision-checkpoint/definitions/decision-bundle/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.decision-bundle@1.0.0-candidate.1

**Content fingerprint · SHA-256**

85869ef815fcc81adf824ff6251bc215e0a624022aaa5c4838878835a932555d

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:cyberalchemy-lab-workflow-interaction",
  "applicability": "A closed presentation set of independently scoped Governance Decisions at one Decision Checkpoint.",
  "exclusions": [
    "A merged authority grant.",
    "A replacement for individual decision records.",
    "A bundle containing unresolved or future decision targets."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
