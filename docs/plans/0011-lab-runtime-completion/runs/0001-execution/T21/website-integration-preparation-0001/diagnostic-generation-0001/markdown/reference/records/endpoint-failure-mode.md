[Documentation home](../../README.md)

# Failure mode

<a id="endpoint-failure-mode"></a>

[Reference](../README.md#reference) / [Endpoint kinds](../endpoint-kinds.md#catalog-endpoints) / Failure mode

# Failure mode

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Failure mode · v1](type-cal-artifact-type-failure-mode-v1.md#type-cal-artifact-type-failure-mode-v1)

**Connection rules where it may be the source:** [governed-by](rel-relation-governed-by.md#rel-relation-governed-by) · [instance-of](rel-relation-instance-of.md#rel-relation-instance-of) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [controls](rel-relation-controls.md#rel-relation-controls) · [declares-effect-on](rel-relation-declares-effect-on.md#rel-relation-declares-effect-on) · [instance-of](rel-relation-instance-of.md#rel-relation-instance-of) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

<a id="endpoint-failure-mode-section-1"></a>

## One declared connection for this kind

[challenge-event](endpoint-challenge-event.md#endpoint-challenge-event) **challenges**Required: challenge_contract_ref, challenge_mode, challenged_version_ref [failure-mode](endpoint-failure-mode.md#endpoint-failure-mode)

Open [challenges](rel-relation-challenges.md#rel-relation-challenges) for all its permitted pairs and qualifier rules.

[Return to Endpoint kinds](../endpoint-kinds.md#catalog-endpoints)
