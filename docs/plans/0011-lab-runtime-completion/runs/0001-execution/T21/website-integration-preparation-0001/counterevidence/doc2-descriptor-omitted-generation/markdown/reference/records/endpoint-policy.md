[Documentation home](../../README.md)

# Policy

<a id="endpoint-policy"></a>

[Reference](../README.md#reference) / [Endpoint kinds](../endpoint-kinds.md#catalog-endpoints) / Policy

# Policy

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Policy · v2](type-cal-artifact-type-policy-v2.md#type-cal-artifact-type-policy-v2)

**Connection rules where it may be the source:** [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [governed-by](rel-relation-governed-by.md#rel-relation-governed-by) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of) · [violates](rel-relation-violates.md#rel-relation-violates)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Governance record types admission

<a id="endpoint-policy-section-1"></a>

## One declared connection for this kind

[challenge-event](endpoint-challenge-event.md#endpoint-challenge-event) **challenges**Required: challenge_contract_ref, challenge_mode, challenged_version_ref [policy](endpoint-policy.md#endpoint-policy)

Open [challenges](rel-relation-challenges.md#rel-relation-challenges) for all its permitted pairs and qualifier rules.

[Return to Endpoint kinds](../endpoint-kinds.md#catalog-endpoints)
