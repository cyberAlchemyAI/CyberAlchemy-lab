[Documentation home](../../README.md)

# Capability realization binding

<a id="endpoint-capability-realization-binding"></a>

[Reference](../README.md#reference) / [Endpoint kinds](../endpoint-kinds.md#catalog-endpoints) / Capability realization binding

# Capability realization binding

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Capability realization binding · v2](type-cal-artifact-type-capability-realization-binding-v2.md#type-cal-artifact-type-capability-realization-binding-v2)

**Connection rules where it may be the source:** [member-of](rel-relation-member-of.md#rel-relation-member-of) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [declares-effect-on](rel-relation-declares-effect-on.md#rel-relation-declares-effect-on) · [evaluates](rel-relation-evaluates.md#rel-relation-evaluates) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

<a id="endpoint-capability-realization-binding-section-1"></a>

## One declared connection for this kind

[challenge-event](endpoint-challenge-event.md#endpoint-challenge-event) **challenges**Required: challenge_contract_ref, challenge_mode, challenged_version_ref [capability-realization-binding](endpoint-capability-realization-binding.md#endpoint-capability-realization-binding)

Open [challenges](rel-relation-challenges.md#rel-relation-challenges) for all its permitted pairs and qualifier rules.

[Return to Endpoint kinds](../endpoint-kinds.md#catalog-endpoints)
