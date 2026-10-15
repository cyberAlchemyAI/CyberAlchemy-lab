[Documentation home](../../README.md)

# Hypothesis

<a id="endpoint-hypothesis"></a>

[Reference](../README.md#reference) / [Endpoint kinds](../endpoint-kinds.md#catalog-endpoints) / Hypothesis

# Hypothesis

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Hypothesis · v1](type-cal-artifact-type-hypothesis-v1.md#type-cal-artifact-type-hypothesis-v1)

**Connection rules where it may be the source:** [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [evidence-bears-on](rel-relation-evidence-bears-on.md#rel-relation-evidence-bears-on) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of) · [tests-hypothesis](rel-relation-tests-hypothesis.md#rel-relation-tests-hypothesis)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

<a id="endpoint-hypothesis-section-1"></a>

## One declared connection for this kind

[challenge-event](endpoint-challenge-event.md#endpoint-challenge-event) **challenges**Required: challenge_contract_ref, challenge_mode, challenged_version_ref [hypothesis](endpoint-hypothesis.md#endpoint-hypothesis)

Open [challenges](rel-relation-challenges.md#rel-relation-challenges) for all its permitted pairs and qualifier rules.

[Return to Endpoint kinds](../endpoint-kinds.md#catalog-endpoints)
