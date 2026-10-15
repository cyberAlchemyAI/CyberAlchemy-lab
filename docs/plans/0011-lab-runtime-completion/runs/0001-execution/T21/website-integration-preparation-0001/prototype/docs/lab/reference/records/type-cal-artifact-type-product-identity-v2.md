[Documentation home](../../README.md)

# Product identity · v2

<a id="type-cal-artifact-type-product-identity-v2"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Product identity · v2

# Product identity · v2

This contract specifies requirements for records of kind `product-identity`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Product](def-cal-definition-product.md#def-cal-definition-product) · [Identity Carrier](def-cal-definition-identity-carrier.md#def-cal-definition-identity-carrier)

<a id="type-cal-artifact-type-product-identity-v2-section-1"></a>

## Prepare a record

- `schema_version`
- `product_id`
- `version`
- `name`
- `status`
- `authority_effect`
- `semantic_definition_refs`
- `purpose`
- `value_promise`
- `scope`
- `semantic_owner_ref`
- `owner_route`
- `lineage_ref`
- `current_thesis_ref`
- `evidence_refs`
- `challenge_route`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** The customer-data platform promises continuing value through export capabilities. This describes the subject; a complete record must satisfy the full contract.

**Declared endpoint kinds for this exact carrier:** [product](endpoint-product.md#endpoint-product)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, product_id, version, name, status, authority_effect, semantic_definition_refs, purpose, value_promise, scope, semantic_owner_ref, owner_route, lineage_ref, current_thesis_ref, evidence_refs, challenge_route, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.product-identity/v2

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-product-identity/v2"
}
````

**Acceptance record**

Product identity successor admission

**Contract**

[Read the type contract](../../assets/d4b954ee3399-artifact.json)

**Schema**

[Read the schema](../../assets/cfe7b179ca4b-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

cfe7b179ca4b420880213843e1d0c0c56654b0c1ce632188f7c00871a2d8020e

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
