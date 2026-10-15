[Documentation home](../../README.md)

# Agent profile · v1

<a id="type-cal-artifact-type-agent-profile-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Agent profile · v1

# Agent profile · v1

This contract specifies requirements for records of kind `agent-profile`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Agent Profile](def-cal-definition-agent-profile.md#def-cal-definition-agent-profile)

<a id="type-cal-artifact-type-agent-profile-v1-section-1"></a>

## Prepare a record

- `schema_version`
- `node_id`
- `kind`
- `name`
- `lifecycle_state`
- `authority_effect`
- `owner_ref`
- `scope_ref`
- `evidence_refs`
- `challenge_route`
- `successor_refs`
- `relation_refs`
- `payload`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [agent-profile](endpoint-agent-profile.md#endpoint-agent-profile)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.agent-profile/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-agent-profile/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../assets/4e0d6ec73fb8-artifact.json)

**Schema**

[Read the schema](../../assets/4f4eb061d99e-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

4f4eb061d99ee759ed0030a58b39eb4b5b2aaa631ea4f5db5a818542b64bcf49

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
