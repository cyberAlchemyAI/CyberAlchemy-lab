[Documentation home](../../README.md)

# Context · v1

<a id="type-cal-artifact-type-context-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Context · v1

# Context · v1

This contract specifies requirements for records of kind `context`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Context](def-cal-definition-context.md#def-cal-definition-context)

<a id="type-cal-artifact-type-context-v1-section-1"></a>

## Prepare a record

- `authority_effect`
- `kind`
- `node_id`
- `owner_ref`
- `scope_ref`
- `status`
- `context_kind`
- `product_ref`
- `project_ref`
- `goal_ref`
- `purpose`
- `bounded_context_refs`
- `consumer_refs`
- `intended_uses`
- `subject_scope`
- `source_policy_refs`
- `profile_ref`
- `owner_route`
- `lifecycle_state`
- `revision_history`
- `successor_refs`
- `challenge_route`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [context](endpoint-context.md#endpoint-context)

### Required fields and schema rules

**Fields required at the selected level:** authority_effect, kind, node_id, owner_ref, scope_ref, status, context_kind, product_ref, project_ref, goal_ref, purpose, bounded_context_refs, consumer_refs, intended_uses, subject_scope, source_policy_refs, profile_ref, owner_route, lifecycle_state, revision_history, successor_refs, challenge_route, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.context/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "context"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/context/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/context/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

15c73290ff7e8efbb10a3ed20248fddb8884e0e4e4aebdf187c491e87e81eb7e

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
