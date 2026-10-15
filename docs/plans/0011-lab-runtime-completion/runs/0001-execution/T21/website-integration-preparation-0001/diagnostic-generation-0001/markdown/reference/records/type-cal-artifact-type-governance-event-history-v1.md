[Documentation home](../../README.md)

# Governance event history · v1

<a id="type-cal-artifact-type-governance-event-history-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Governance event history · v1

# Governance event history · v1

This contract specifies requirements for records of kind `governance-event-history`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Governance Event History](def-cal-definition-governance-event-history.md#def-cal-definition-governance-event-history)

<a id="type-cal-artifact-type-governance-event-history-v1-section-1"></a>

## Prepare a record

- `schema_version`
- `node_id`
- `kind`
- `name`
- `record_state`
- `authority_effect`
- `owner_ref`
- `scope_ref`
- `evidence_refs`
- `challenge_route`
- `successor_refs`
- `payload`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [governance-event-history](endpoint-governance-event-history.md#endpoint-governance-event-history)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, record_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.governance-event-history/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-governance-event-history/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../assets/05a48000eb57-artifact.json)

**Schema**

[Read the schema](../../assets/b39e5b97dfc9-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

b39e5b97dfc908e0d6685c39ad0864cb7c3c479522ae3c83995da83e191834d5

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
