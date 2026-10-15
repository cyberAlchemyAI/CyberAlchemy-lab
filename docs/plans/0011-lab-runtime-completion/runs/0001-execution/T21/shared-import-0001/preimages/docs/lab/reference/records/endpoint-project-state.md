[Documentation home](../../README.md)

# Project state

<a id="endpoint-project-state"></a>

[Reference catalog](../endpoint-kinds.md#catalog-endpoints) / Exact record

# Project state

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Project state · v2](type-cal-artifact-type-project-state-v2.md#type-cal-artifact-type-project-state-v2)

**Connection rules where it may be the source:** [member-of](rel-relation-member-of.md#rel-relation-member-of) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [materializes-consequence](rel-relation-materializes-consequence.md#rel-relation-materializes-consequence) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Governance record types admission

## One declared connection for this kind

[challenge-event](endpoint-challenge-event.md#endpoint-challenge-event) **challenges**Required: challenge_contract_ref, challenge_mode, challenged_version_ref [project-state](endpoint-project-state.md#endpoint-project-state)

Open [challenges](rel-relation-challenges.md#rel-relation-challenges) for all its permitted pairs and qualifier rules.

[Return to this catalog](../endpoint-kinds.md#catalog-endpoints)
