[Documentation home](../../README.md)

# Product capability · v1

<a id="type-cal-artifact-type-product-capability-v1"></a>

[Reference catalog](../artifact-types.md#catalog-types) / Exact record

# Product capability · v1

This contract specifies requirements for records of kind `product-capability`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Product Capability](def-cal-definition-product-capability.md#def-cal-definition-product-capability)

## Prepare a record

- `acceptance_conditions`
- `authority_effect`
- `exclusions`
- `kind`
- `node_id`
- `outcome`
- `owner_ref`
- `product_ref`
- `scope_ref`
- `status`
- `name`
- `product_thesis_ref`
- `thesis_outcome_refs`
- `participant_refs`
- `consumer_refs`
- `input_contract_refs`
- `output_contract_refs`
- `context_policy_refs`
- `owner_routes`
- `lifecycle_posture`
- `realization_binding_refs`
- `evidence_refs`
- `revision_history`
- `successor_refs`
- `challenge_route`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** Export eligible customer data is a promised Product outcome that an implementation can realize. This describes the subject; a complete record must satisfy the full contract.

**Declared endpoint kinds for this exact carrier:** [product-capability](endpoint-product-capability.md#endpoint-product-capability)

### Required fields and schema rules

**Fields required at the selected level:** acceptance_conditions, authority_effect, exclusions, kind, node_id, outcome, owner_ref, product_ref, scope_ref, status, name, product_thesis_ref, thesis_outcome_refs, participant_refs, consumer_refs, input_contract_refs, output_contract_refs, context_policy_refs, owner_routes, lifecycle_posture, realization_binding_refs, evidence_refs, revision_history, successor_refs, challenge_route

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.product-capability/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "product-capability"
}
````

**Acceptance record**

Product Capability contract admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/product-capability/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/product-capability/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

f818577e9c6e676a1b07b5726db12cdaf06805d3fc903dcb02eadf2c539083da

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to this catalog](../artifact-types.md#catalog-types)
