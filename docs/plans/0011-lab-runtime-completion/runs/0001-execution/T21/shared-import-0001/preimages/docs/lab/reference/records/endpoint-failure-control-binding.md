[Documentation home](../../README.md)

# Failure control binding

<a id="endpoint-failure-control-binding"></a>

[Reference catalog](../endpoint-kinds.md#catalog-endpoints) / Exact record

# Failure control binding

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Failure control binding · v1](type-cal-artifact-type-failure-control-binding-v1.md#type-cal-artifact-type-failure-control-binding-v1)

**Connection rules where it may be the source:** [controls](rel-relation-controls.md#rel-relation-controls) · [governed-by](rel-relation-governed-by.md#rel-relation-governed-by) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [declares-effect-on](rel-relation-declares-effect-on.md#rel-relation-declares-effect-on) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

## One declared connection for this kind

[challenge-event](endpoint-challenge-event.md#endpoint-challenge-event) **challenges**Required: challenge_contract_ref, challenge_mode, challenged_version_ref [failure-control-binding](endpoint-failure-control-binding.md#endpoint-failure-control-binding)

Open [challenges](rel-relation-challenges.md#rel-relation-challenges) for all its permitted pairs and qualifier rules.

[Return to this catalog](../endpoint-kinds.md#catalog-endpoints)
