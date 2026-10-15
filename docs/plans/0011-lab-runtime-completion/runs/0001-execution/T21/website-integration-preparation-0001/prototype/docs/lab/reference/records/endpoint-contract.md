[Documentation home](../../README.md)

# Contract

<a id="endpoint-contract"></a>

[Reference](../README.md#reference) / [Endpoint kinds](../endpoint-kinds.md#catalog-endpoints) / Contract

# Contract

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Contract · v1](type-cal-artifact-type-contract-v1.md#type-cal-artifact-type-contract-v1)

**Connection rules where it may be the source:** [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [conforms-to](rel-relation-conforms-to.md#rel-relation-conforms-to) · [inherits-contract](rel-relation-inherits-contract.md#rel-relation-inherits-contract) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of) · [violates](rel-relation-violates.md#rel-relation-violates)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

<a id="endpoint-contract-section-1"></a>

## One declared connection for this kind

[challenge-event](endpoint-challenge-event.md#endpoint-challenge-event) **challenges**Required: challenge_contract_ref, challenge_mode, challenged_version_ref [contract](endpoint-contract.md#endpoint-contract)

Open [challenges](rel-relation-challenges.md#rel-relation-challenges) for all its permitted pairs and qualifier rules.

[Return to Endpoint kinds](../endpoint-kinds.md#catalog-endpoints)
