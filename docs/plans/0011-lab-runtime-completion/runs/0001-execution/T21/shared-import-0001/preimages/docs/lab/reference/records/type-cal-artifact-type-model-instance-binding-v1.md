[Documentation home](../../README.md)

# Model instance binding · v1

<a id="type-cal-artifact-type-model-instance-binding-v1"></a>

[Reference catalog](../artifact-types.md#catalog-types) / Exact record

# Model instance binding · v1

This contract specifies requirements for records of kind `model-instance-binding`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Model Instance Binding](def-cal-definition-model-instance-binding.md#def-cal-definition-model-instance-binding)

## Prepare a record

- `authority_effect`
- `kind`
- `node_id`
- `owner_ref`
- `scope_ref`
- `status`
- `parent_model_ref`
- `parent_model_version_ref`
- `instance_ref`
- `parent_owner_route`
- `instance_owner_route`
- `inherited_contract_refs`
- `parent_authority_scope`
- `instance_authority_scope`
- `extension_scope`
- `local_override_refs`
- `conformance_refs`
- `binding_state`
- `successor_refs`
- `owner_route`
- `challenge_route`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [model-instance-binding](endpoint-model-instance-binding.md#endpoint-model-instance-binding)

### Required fields and schema rules

**Fields required at the selected level:** authority_effect, kind, node_id, owner_ref, scope_ref, status, parent_model_ref, parent_model_version_ref, instance_ref, parent_owner_route, instance_owner_route, inherited_contract_refs, parent_authority_scope, instance_authority_scope, extension_scope, local_override_refs, conformance_refs, binding_state, successor_refs, owner_route, challenge_route, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.model-instance-binding/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "model-instance-binding"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/model-instance-binding/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/model-instance-binding/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

cd3399dcabf88dd3bd0feaf1b1b5803e46cf39f935753345a1078b7750fef45b

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to this catalog](../artifact-types.md#catalog-types)
