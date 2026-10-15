[Documentation home](../../README.md)

# Product thesis · v1

<a id="type-cal-artifact-type-product-thesis-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Product thesis · v1

# Product thesis · v1

This contract specifies requirements for records of kind `product-thesis`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Product Thesis](def-cal-definition-product-thesis.md#def-cal-definition-product-thesis)

<a id="type-cal-artifact-type-product-thesis-v1-section-1"></a>

## Prepare a record

- `assumptions`
- `audience`
- `authority_effect`
- `kind`
- `node_id`
- `owner_ref`
- `problem`
- `product_ref`
- `revision_criteria`
- `scope_ref`
- `status`
- `value_proposition`
- `participants`
- `value_mechanism`
- `first_order_principles`
- `intended_outcomes`
- `boundaries`
- `hypotheses`
- `evidence_routes`
- `counterevidence_routes`
- `owner_route`
- `commitment_state`
- `successor_refs`
- `revision_history`
- `challenge_route`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [product-thesis](endpoint-product-thesis.md#endpoint-product-thesis)

### Required fields and schema rules

**Fields required at the selected level:** assumptions, audience, authority_effect, kind, node_id, owner_ref, problem, product_ref, revision_criteria, scope_ref, status, value_proposition, participants, value_mechanism, first_order_principles, intended_outcomes, boundaries, hypotheses, evidence_routes, counterevidence_routes, owner_route, commitment_state, successor_refs, revision_history, challenge_route

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.product-thesis/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "product-thesis"
}
````

**Acceptance record**

Product Thesis contract admission

**Contract**

[Read the type contract](../../assets/6f7de0da15cc-artifact.json)

**Schema**

[Read the schema](../../assets/26bbe2e9de44-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

26bbe2e9de44384da0fd582f592d6a9b8d98eaf52f2d4db34230beefecce9298

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
