[Documentation home](../../README.md)

# Context

<a id="endpoint-context"></a>

[Reference catalog](../endpoint-kinds.md#catalog-endpoints) / Exact record

# Context

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Context · v1](type-cal-artifact-type-context-v1.md#type-cal-artifact-type-context-v1)

**Connection rules where it may be the source:** [conforms-to](rel-relation-conforms-to.md#rel-relation-conforms-to) · [frames](rel-relation-frames.md#rel-relation-frames) · [governed-by](rel-relation-governed-by.md#rel-relation-governed-by) · [member-of](rel-relation-member-of.md#rel-relation-member-of) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [derives-from](rel-relation-derives-from.md#rel-relation-derives-from) · [requests-resolution-of](rel-relation-requests-resolution-of.md#rel-relation-requests-resolution-of) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

## One declared connection for this kind

[challenge-event](endpoint-challenge-event.md#endpoint-challenge-event) **challenges**Required: challenge_contract_ref, challenge_mode, challenged_version_ref [context](endpoint-context.md#endpoint-context)

Open [challenges](rel-relation-challenges.md#rel-relation-challenges) for all its permitted pairs and qualifier rules.

[Return to this catalog](../endpoint-kinds.md#catalog-endpoints)
