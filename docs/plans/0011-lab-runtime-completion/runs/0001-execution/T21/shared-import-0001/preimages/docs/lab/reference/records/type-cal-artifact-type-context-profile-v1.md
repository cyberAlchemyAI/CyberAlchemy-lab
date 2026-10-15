[Documentation home](../../README.md)

# Context profile · v1

<a id="type-cal-artifact-type-context-profile-v1"></a>

[Reference catalog](../artifact-types.md#catalog-types) / Exact record

# Context profile · v1

This contract specifies requirements for records of kind `context-profile`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Context Profile](def-cal-definition-context-profile.md#def-cal-definition-context-profile)

## Prepare a record

- `authority_effect`
- `kind`
- `node_id`
- `owner_ref`
- `scope_ref`
- `status`
- `name`
- `allowed_context_kinds`
- `required_anchor_fields`
- `allowed_source_kinds`
- `consumer_requirements`
- `freshness_policy`
- `exclusion_policy`
- `output_constraints`
- `successor_rule`
- `lifecycle_state`
- `successor_refs`
- `owner_route`
- `challenge_route`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [context-profile](endpoint-context-profile.md#endpoint-context-profile)

### Required fields and schema rules

**Fields required at the selected level:** authority_effect, kind, node_id, owner_ref, scope_ref, status, name, allowed_context_kinds, required_anchor_fields, allowed_source_kinds, consumer_requirements, freshness_policy, exclusion_policy, output_constraints, successor_rule, lifecycle_state, successor_refs, owner_route, challenge_route, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.context-profile/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "context-profile"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/context-profile/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/context-profile/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

55216de3c1baf50a73c24bbb899ba4e3042e6b443ad48f13dc817cc61cdc5185

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to this catalog](../artifact-types.md#catalog-types)
