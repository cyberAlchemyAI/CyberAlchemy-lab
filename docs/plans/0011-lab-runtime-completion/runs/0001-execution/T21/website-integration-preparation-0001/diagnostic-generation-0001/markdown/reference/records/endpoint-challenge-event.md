[Documentation home](../../README.md)

# Challenge event

<a id="endpoint-challenge-event"></a>

[Reference](../README.md#reference) / [Endpoint kinds](../endpoint-kinds.md#catalog-endpoints) / Challenge event

# Challenge event

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Challenge event · v1](type-cal-artifact-type-challenge-event-v1.md#type-cal-artifact-type-challenge-event-v1)

**Connection rules where it may be the source:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [governed-by](rel-relation-governed-by.md#rel-relation-governed-by) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [declares-effect-on](rel-relation-declares-effect-on.md#rel-relation-declares-effect-on) · [evidence-bears-on](rel-relation-evidence-bears-on.md#rel-relation-evidence-bears-on) · [produces](rel-relation-produces.md#rel-relation-produces) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

<a id="endpoint-challenge-event-section-1"></a>

## One declared connection for this kind

[challenge-event](endpoint-challenge-event.md#endpoint-challenge-event) **challenges**Required: challenge_contract_ref, challenge_mode, challenged_version_ref [agent-action](endpoint-agent-action.md#endpoint-agent-action)

Open [challenges](rel-relation-challenges.md#rel-relation-challenges) for all its permitted pairs and qualifier rules.

[Return to Endpoint kinds](../endpoint-kinds.md#catalog-endpoints)
