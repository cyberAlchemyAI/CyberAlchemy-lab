[Documentation home](../../README.md)

# Operational observation

<a id="endpoint-operational-observation"></a>

[Reference catalog](../endpoint-kinds.md#catalog-endpoints) / Exact record

# Operational observation

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Operational observation · v1](type-cal-artifact-type-operational-observation-v1.md#type-cal-artifact-type-operational-observation-v1)

**Connection rules where it may be the source:** [evidence-bears-on](rel-relation-evidence-bears-on.md#rel-relation-evidence-bears-on) · [originates-from](rel-relation-originates-from.md#rel-relation-originates-from) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [derives-from](rel-relation-derives-from.md#rel-relation-derives-from) · [produces](rel-relation-produces.md#rel-relation-produces) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

## One declared connection for this kind

[challenge-event](endpoint-challenge-event.md#endpoint-challenge-event) **challenges**Required: challenge_contract_ref, challenge_mode, challenged_version_ref [operational-observation](endpoint-operational-observation.md#endpoint-operational-observation)

Open [challenges](rel-relation-challenges.md#rel-relation-challenges) for all its permitted pairs and qualifier rules.

[Return to this catalog](../endpoint-kinds.md#catalog-endpoints)
