[Documentation home](../../README.md)

# Capability realization binding · v2

<a id="type-cal-artifact-type-capability-realization-binding-v2"></a>

[Reference catalog](../artifact-types.md#catalog-types) / Exact record

# Capability realization binding · v2

This contract specifies requirements for records of kind `capability-realization-binding`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Capability Realization Binding](def-cal-definition-capability-realization-binding.md#def-cal-definition-capability-realization-binding)

## Prepare a record

- `authority_effect`
- `capability_ref`
- `contract`
- `kind`
- `limitations`
- `node_id`
- `owner_ref`
- `realization_refs`
- `scope_ref`
- `status`
- `binding_version`
- `capability_version_ref`
- `binding_state`
- `adoption_decision_ref`
- `conformance_refs`
- `observation_refs`
- `successor_refs`
- `owner_route`
- `challenge_route`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [capability-realization-binding](endpoint-capability-realization-binding.md#endpoint-capability-realization-binding)

### Required fields and schema rules

**Fields required at the selected level:** authority_effect, capability_ref, contract, kind, limitations, node_id, owner_ref, realization_refs, scope_ref, status, binding_version, capability_version_ref, binding_state, adoption_decision_ref, conformance_refs, observation_refs, successor_refs, owner_route, challenge_route

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.capability-realization-binding/v2

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "capability-realization-binding"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/capability-realization-binding/v2/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/capability-realization-binding/v2/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

cf51d6d3ace1f8a9e0dfda03e52e8d0beaed628e5ca43c75a8ed1b8ad611659a

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to this catalog](../artifact-types.md#catalog-types)
