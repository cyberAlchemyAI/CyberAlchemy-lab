[Documentation home](../../README.md)

# Identity claim · v1

<a id="type-cal-artifact-type-identity-claim-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Identity claim · v1

# Identity claim · v1

This contract specifies requirements for records of kind `identity-claim`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Identity Claim](def-cal-definition-identity-claim.md#def-cal-definition-identity-claim)

<a id="type-cal-artifact-type-identity-claim-v1-section-1"></a>

## Prepare a record

- `authority_effect`
- `kind`
- `node_id`
- `owner_ref`
- `scope_ref`
- `status`
- `person_reference_ref`
- `asserted_identifier`
- `claim_scope`
- `evidence_refs`
- `assurance_policy_ref`
- `assurance_level`
- `claim_state`
- `asserted_at`
- `expires_at`
- `limitations`
- `owner_route`
- `challenge_route`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [identity-claim](endpoint-identity-claim.md#endpoint-identity-claim)

### Required fields and schema rules

**Fields required at the selected level:** authority_effect, kind, node_id, owner_ref, scope_ref, status, person_reference_ref, asserted_identifier, claim_scope, evidence_refs, assurance_policy_ref, assurance_level, claim_state, asserted_at, expires_at, limitations, owner_route, challenge_route, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.identity-claim/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "identity-claim"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../assets/c6f51fe4adc6-artifact.json)

**Schema**

[Read the schema](../../assets/3df076c01fd9-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

3df076c01fd97b130531c1dbcc5330f3646cf3c3b9053b484073bdefaab9f55a

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
