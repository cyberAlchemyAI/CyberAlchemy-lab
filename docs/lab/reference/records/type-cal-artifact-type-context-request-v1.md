[Documentation home](../../README.md)

# Context request · v1

<a id="type-cal-artifact-type-context-request-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Context request · v1

# Context request · v1

This contract specifies requirements for records of kind `context-request`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Context Request](def-cal-definition-context-request.md#def-cal-definition-context-request)

<a id="type-cal-artifact-type-context-request-v1-section-1"></a>

## Prepare a record

- `authority_effect`
- `kind`
- `node_id`
- `owner_ref`
- `scope_ref`
- `status`
- `context_ref`
- `context_version_ref`
- `consumer_refs`
- `intended_uses`
- `selectors`
- `freshness_requirement`
- `exclusions`
- `output_constraints`
- `budget`
- `requested_at`
- `owner_route`
- `challenge_route`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [context-request](endpoint-context-request.md#endpoint-context-request)

### Required fields and schema rules

**Fields required at the selected level:** authority_effect, kind, node_id, owner_ref, scope_ref, status, context_ref, context_version_ref, consumer_refs, intended_uses, selectors, freshness_requirement, exclusions, output_constraints, budget, requested_at, owner_route, challenge_route, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.context-request/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "context-request"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/context-request/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/context-request/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

c4db5d934a8b5d39bd14d231e5f8353d3f1a288ba7f314f987d62ef58d767615

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
