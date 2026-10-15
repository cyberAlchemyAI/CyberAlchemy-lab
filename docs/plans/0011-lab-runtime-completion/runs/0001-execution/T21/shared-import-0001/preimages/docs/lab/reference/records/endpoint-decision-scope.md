[Documentation home](../../README.md)

# Decision scope

<a id="endpoint-decision-scope"></a>

[Reference catalog](../endpoint-kinds.md#catalog-endpoints) / Exact record

# Decision scope

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Decision scope · v2](type-cal-artifact-type-decision-scope-v2.md#type-cal-artifact-type-decision-scope-v2)

**Connection rules where it may be the source:** [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [scopes-authority-over](rel-relation-scopes-authority-over.md#rel-relation-scopes-authority-over) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Governance record types admission

## One declared connection for this kind

[challenge-event](endpoint-challenge-event.md#endpoint-challenge-event) **challenges**Required: challenge_contract_ref, challenge_mode, challenged_version_ref [decision-scope](endpoint-decision-scope.md#endpoint-decision-scope)

Open [challenges](rel-relation-challenges.md#rel-relation-challenges) for all its permitted pairs and qualifier rules.

[Return to this catalog](../endpoint-kinds.md#catalog-endpoints)
