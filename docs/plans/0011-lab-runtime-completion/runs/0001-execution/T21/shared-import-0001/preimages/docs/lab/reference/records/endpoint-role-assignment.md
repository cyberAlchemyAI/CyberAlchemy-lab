[Documentation home](../../README.md)

# Role assignment

<a id="endpoint-role-assignment"></a>

[Reference catalog](../endpoint-kinds.md#catalog-endpoints) / Exact record

# Role assignment

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Role assignment · v1](type-cal-artifact-type-role-assignment-v1.md#type-cal-artifact-type-role-assignment-v1)

**Connection rules where it may be the source:** [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [scopes-authority-over](rel-relation-scopes-authority-over.md#rel-relation-scopes-authority-over) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

## One declared connection for this kind

[challenge-event](endpoint-challenge-event.md#endpoint-challenge-event) **challenges**Required: challenge_contract_ref, challenge_mode, challenged_version_ref [role-assignment](endpoint-role-assignment.md#endpoint-role-assignment)

Open [challenges](rel-relation-challenges.md#rel-relation-challenges) for all its permitted pairs and qualifier rules.

[Return to this catalog](../endpoint-kinds.md#catalog-endpoints)
