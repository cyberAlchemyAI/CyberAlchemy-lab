[Documentation home](../../README.md)

# Agent profile

<a id="endpoint-agent-profile"></a>

[Reference](../README.md#reference) / [Endpoint kinds](../endpoint-kinds.md#catalog-endpoints) / Agent profile

# Agent profile

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Agent profile · v1](type-cal-artifact-type-agent-profile-v1.md#type-cal-artifact-type-agent-profile-v1)

**Connection rules where it may be the source:** [governed-by](rel-relation-governed-by.md#rel-relation-governed-by) · [has-capability](rel-relation-has-capability.md#rel-relation-has-capability) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [declares-effect-on](rel-relation-declares-effect-on.md#rel-relation-declares-effect-on) · [profiled-by](rel-relation-profiled-by.md#rel-relation-profiled-by) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

<a id="endpoint-agent-profile-section-1"></a>

## One declared connection for this kind

[challenge-event](endpoint-challenge-event.md#endpoint-challenge-event) **challenges**Required: challenge_contract_ref, challenge_mode, challenged_version_ref [agent-profile](endpoint-agent-profile.md#endpoint-agent-profile)

Open [challenges](rel-relation-challenges.md#rel-relation-challenges) for all its permitted pairs and qualifier rules.

[Return to Endpoint kinds](../endpoint-kinds.md#catalog-endpoints)
