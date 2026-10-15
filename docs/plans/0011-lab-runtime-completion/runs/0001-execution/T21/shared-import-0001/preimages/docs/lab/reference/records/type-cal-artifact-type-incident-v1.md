[Documentation home](../../README.md)

# Incident · v1

<a id="type-cal-artifact-type-incident-v1"></a>

[Reference catalog](../artifact-types.md#catalog-types) / Exact record

# Incident · v1

This contract specifies requirements for records of kind `incident`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Incident](def-cal-definition-incident.md#def-cal-definition-incident)

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

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** The customer-data service owner coordinates investigation and response under the open incident. This describes the subject; a complete record must satisfy the full contract.

**Declared endpoint kinds for this exact carrier:** [incident](endpoint-incident.md#endpoint-incident)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.incident/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-incident/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/incident/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/incident/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

0c9055c7fa14c5cdc925e064fdc39704de1b8f78b9dd44d2a3d88607f20250ba

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to this catalog](../artifact-types.md#catalog-types)
