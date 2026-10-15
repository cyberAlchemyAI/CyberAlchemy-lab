[Documentation home](../../README.md)

# Capability Instance

<a id="def-cal-definition-capability-instance"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Capability Instance

A locally owned realization of a reusable capability, explicitly linked to its parent while retaining a separate identity and authority.

**When it applies**

Owner-local realizations or specializations of exact Product Capability versions.

**Record formats**

[Capability instance · v2](type-cal-artifact-type-capability-instance-v2.md#type-cal-artifact-type-capability-instance-v2)

**A stated exclusion**

Product Capability meaning itself.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

A locally owned realization of a reusable capability, connected to its blueprint without becoming the blueprint.

## Exact governing statement

A Capability Instance is an owner-local, version-exact realization or specialization of one Product Capability inside explicitly declared coordination and semantic contexts. It binds separate parent and instance authority lanes, inherited contract, extension scope, adoption decision, D65 construction stages, conformance evidence, lifecycle, drift and recomposition routes, recursion budget or stop, and terminal handoff.

````
CapabilityInstance = (id, capability_version_ref, coordination_context_ref, bounded_context_refs, parent_authority_claim, instance_authority_claim, inherited_contract_ref, extension_scope, adoption_decision_ref, construction_binding_ref, conformance_refs, lifecycle, drift_route, recomposition_route, recursion_stop, terminal_handoff); Instance != Parent; Conformance does not imply Authority.
````

- Exactly one parent capability version is explicit.
- Recursion includes a budget or stop and a recomposition route.
- Parent and instance authority claims remain separate.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Definition and initial context promotion

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0001-definition-and-ctx00-v1/definitions/capability-instance/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.capability-instance@1.0.0-candidate.1

**Content fingerprint · SHA-256**

d1e0140d47887b3f8c49334e81c33bd105edaecaf02f3df3df841885340505a5

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:cyberalchemy-lab-capability-recursion",
  "applicability": "Owner-local realizations or specializations of exact Product Capability versions.",
  "exclusions": [
    "Product Capability meaning itself.",
    "Directories, implementation components, deployments, and conformance results."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
