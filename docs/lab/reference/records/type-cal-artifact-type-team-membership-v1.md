[Documentation home](../../README.md)

# Team membership · v1

<a id="type-cal-artifact-type-team-membership-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Team membership · v1

# Team membership · v1

This contract specifies requirements for records of kind `team-membership`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Team Membership](def-cal-definition-team-membership.md#def-cal-definition-team-membership)

<a id="type-cal-artifact-type-team-membership-v1-section-1"></a>

## Prepare a record

- `authority_effect`
- `kind`
- `node_id`
- `owner_ref`
- `scope_ref`
- `status`
- `person_reference_ref`
- `team_ref`
- `membership_state`
- `period`
- `basis_ref`
- `owner_route`
- `challenge_route`
- `successor_refs`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [team-membership](endpoint-team-membership.md#endpoint-team-membership)

### Required fields and schema rules

**Fields required at the selected level:** authority_effect, kind, node_id, owner_ref, scope_ref, status, person_reference_ref, team_ref, membership_state, period, basis_ref, owner_route, challenge_route, successor_refs, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.team-membership/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "team-membership"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/team-membership/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/team-membership/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

adcb4e7074ca82ad082612f1b2578b7eba405838592212a109d7633125fdf674

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
