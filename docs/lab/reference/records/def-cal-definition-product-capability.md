[Documentation home](../../README.md)

# Product Capability

<a id="def-cal-definition-product-capability"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Product Capability

# Product Capability

An outcome the product should enable for identified consumers, separate from the technology selected to provide it.

**When it applies**

When describing an outcome promised by one Product, independently of the implementation used to realize it.

**Record formats**

[Product capability · v1](type-cal-artifact-type-product-capability-v1.md#type-cal-artifact-type-product-capability-v1)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

Export eligible customer data is a promised Product outcome that an implementation can realize.

**Common mistake**

Treating the promise as proof that a particular implementation delivers it.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-product-capability-section-2"></a>

## Source explanatory wording

A Product Capability says what useful thing the product must make possible. It does not yet say which tool or implementation will do it.

<a id="def-cal-definition-product-capability-section-3"></a>

## Exact governing statement

Product Capability is the normalized definition identified by semantic.product-capability, owned within scope.product, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D67 without silently merging it with another target.

Bound source-semantic basis:

A Product Capability is a stable, owner-qualified statement of an outcome that one Product must enable for named participants or consumers while preserving explicit scope, contracts, context policies, evidence routes, and authority limits. It states what the Product must make possible and why that behavior belongs to the Product. It does not select the agent, component, command, interface, workflow, or implementation that realizes the outcome.

Every Product Capability belongs to exactly one Product. Its identity remains stable while realizations, interfaces, evidence, and implementation technology change, provided the outcome, Product anchor, scope, and owner boundary remain the same. A material change to any of those anchors requires a successor Product Capability rather than a silent rewrite.

````
```text
ProductCapability =
  (id, product_ref, outcome, scope, exclusions, participant_refs,
   consumer_refs, input_contract_refs, output_contract_refs,
   context_policy_refs, owner_routes, lifecycle_posture,
   realization_refs, evidence_refs, revision_history,
   challenge_route, authority_effect)

|product_ref| = 1
|owner_routes| >= 1
|consumer_refs| >= 1

lifecycle_posture =
  (kind, status, status_vocabulary_ref, evidence, commitment,
   provenance, owner, residue_refs)

lifecycle_posture.kind = product-capability
status_vocabulary_ref != null

valid(c) only if
  stable(c.id)
  and bounded(c.outcome, c.scope, c.exclusions)
  and contracts_resolve(c.input_contract_refs, c.output_contract_refs)
  and context_policies_resolve(c.context_policy_refs)
  and c.authority_effect = none

material_change(product_ref, outcome, scope, owner_routes) =>
  successor_product_capability_required

adopted(c) =/=> realized(c)
realized(c) =/=> conformant(c)
conformant(c) =/=> valuable(c)
observed(c) =/=> adopted(c)
permission_for(c) =/=> product_capability(c)
```

`lifecycle_posture` applies the `CAV2-D23` axis split. `status` is meaningful
only with its owning `status_vocabulary_ref`; this definition does not impose
one lifecycle enum on every capability. Evidence, owner commitment,
provenance, and residue remain separate posture fields. Realization,
conformance, and operational availability are separate axes owned by their
respective artifacts and evidence. None may be inferred from another or
collapsed into one `status` field.
````

- A Product Capability is not the Product, Product Thesis, Project (`CAV2-D60`), Goal (`CAV2-D59`), Context (`CAV2-D66`), Agent Capability (`DEF-ARC-CAPABILITY`), Bounded Context, business rule, implementation, component, command, interface, workflow, service, permission, role, authority grant, runtime process, test, metric, evidence receipt, or release state. An adopted Product Capability is not proof of implementation. An implemented realization is not proof of conformance. A passing conformance check is not proof of customer value, product-market fit, authority transfer, publication, release, deployment, or permission to execute.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/product-capability/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.product-capability@1.0.0-candidate.1

**Content fingerprint · SHA-256**

446a5357c0dd1337c7345e9c5b14a8ff9b7c03d4ad1162384c491e3400f05431

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Define a Product Capability after the Product Thesis identifies an outcome the\nProduct must repeatedly enable. Name its consumers, scope, inputs, outputs,\ncontext policies, owners, and exclusions before selecting a realization.\nLater, bridge it to one or more Agent Capabilities or system realizations and\ntest that bridge with separate conformance and runtime evidence.\n\nKeep capability instances with the module that owns their local meaning and\nlifecycle. A central Capability Ontology may index or project those instances,\nbut it must not copy their authority or turn one registry into their owner.",
  "authority_scope_ref": "scope.product",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
