[Documentation home](../../README.md)

# Governed model

<a id="endpoint-governed-model"></a>

[Reference](../README.md#reference) / [Endpoint kinds](../endpoint-kinds.md#catalog-endpoints) / Governed model

# Governed model

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Governed model · v1](type-cal-artifact-type-governed-model-v1.md#type-cal-artifact-type-governed-model-v1)

**Connection rules where it may be the source:** [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [conforms-to](rel-relation-conforms-to.md#rel-relation-conforms-to) · [declares-effect-on](rel-relation-declares-effect-on.md#rel-relation-declares-effect-on) · [instance-of](rel-relation-instance-of.md#rel-relation-instance-of) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

<a id="endpoint-governed-model-section-1"></a>

## One declared connection for this kind

[challenge-event](endpoint-challenge-event.md#endpoint-challenge-event) **challenges**Required: challenge_contract_ref, challenge_mode, challenged_version_ref [governed-model](endpoint-governed-model.md#endpoint-governed-model)

Open [challenges](rel-relation-challenges.md#rel-relation-challenges) for all its permitted pairs and qualifier rules.

[Return to Endpoint kinds](../endpoint-kinds.md#catalog-endpoints)
