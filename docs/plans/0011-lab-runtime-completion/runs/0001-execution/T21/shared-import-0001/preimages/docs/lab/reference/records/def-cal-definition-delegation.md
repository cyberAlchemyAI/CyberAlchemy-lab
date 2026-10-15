[Documentation home](../../README.md)

# Delegation

<a id="def-cal-definition-delegation"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Delegation

An explicit permission from an authorized owner or principal for an agent to perform named actions within stated scope and time limits. The delegator must possess the permission being delegated.

**When it applies**

When recording a grant of scoped authority with its effective period and revocation conditions.

**Record formats**

[Delegation · v1](type-cal-artifact-type-delegation-v1.md#type-cal-artifact-type-delegation-v1)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

The recorded 30-minute scope permits inspection, comparison and preparation of candidate material.

**Common mistake**

Treating the grant as indefinite or unrestricted authority.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

A Delegation is an explicit scope-bounded and time-bounded authorization from a Principal or authority owner to an Agent or Agent Instance for named action kinds under exact Policies, gates, evidence, revocation, and claim ceilings. The delegator must possess delegable authority for every included action kind, subject, scope, and time interval.

## Exact governing statement

A Delegation is an explicit scope-bounded and time-bounded authorization from a Principal or authority owner to an Agent or Agent Instance for named action kinds under exact Policies, gates, evidence, revocation, and claim ceilings. Delegation transfers neither identity nor ownership and creates no authority outside its exact envelope.

````
Delegation(d,p,a,q,t) => Authority(p,q,t) and scope(d)=q and recipient(d)=a and active(d,t); Delegation(d,...) =/=> identityTransfer or ownershipTransfer.
````

- The delegator must possess delegable authority for every included action kind, subject, scope, and time interval.
- Delegation names the eligible Agent Profile or concrete Agent Instance, exact action kinds, Policies, approval gates, evidence, claim ceiling, period, revocation, and residue handling.
- Delegation transfers neither identity nor ownership and grants nothing outside its exact envelope.
- Redelegation is forbidden unless explicitly included and independently bounded.
- Expiry or revocation prevents later Actions from relying on the Delegation while preserving the historical record.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/delegation/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.delegation@1.0.0-candidate.1

**Content fingerprint · SHA-256**

186a8706dfeaddd2b37a95d00942e3a590ee2aac13fd4e42500739cc13832ecd

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Delegation is an explicit scope-bounded and time-bounded authorization from a Principal or authority owner to an Agent or Agent Instance for named action kinds under exact Policies, gates, evidence, revocation, and claim ceilings.",
  "authority_scope_ref": "scope:delegation-definition",
  "exclusions": [
    "The delegator must possess delegable authority for every included action kind, subject, scope, and time interval.",
    "Delegation names the eligible Agent Profile or concrete Agent Instance, exact action kinds, Policies, approval gates, evidence, claim ceiling, period, revocation, and residue handling.",
    "Delegation transfers neither identity nor ownership and grants nothing outside its exact envelope.",
    "Redelegation is forbidden unless explicitly included and independently bounded.",
    "Expiry or revocation prevents later Actions from relying on the Delegation while preserving the historical record.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
