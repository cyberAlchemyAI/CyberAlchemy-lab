[Documentation home](../../README.md)

# Experiment design

<a id="endpoint-experiment-design"></a>

[Reference catalog](../endpoint-kinds.md#catalog-endpoints) / Exact record

# Experiment design

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Experiment design · v1](type-cal-artifact-type-experiment-design-v1.md#type-cal-artifact-type-experiment-design-v1)

**Connection rules where it may be the source:** [contributes-to](rel-relation-contributes-to.md#rel-relation-contributes-to) · [engages-inquiry](rel-relation-engages-inquiry.md#rel-relation-engages-inquiry) · [evaluates](rel-relation-evaluates.md#rel-relation-evaluates) · [member-of](rel-relation-member-of.md#rel-relation-member-of) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of) · [tests-hypothesis](rel-relation-tests-hypothesis.md#rel-relation-tests-hypothesis)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [realizes](rel-relation-realizes.md#rel-relation-realizes) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

## One declared connection for this kind

[challenge-event](endpoint-challenge-event.md#endpoint-challenge-event) **challenges**Required: challenge_contract_ref, challenge_mode, challenged_version_ref [experiment-design](endpoint-experiment-design.md#endpoint-experiment-design)

Open [challenges](rel-relation-challenges.md#rel-relation-challenges) for all its permitted pairs and qualifier rules.

[Return to this catalog](../endpoint-kinds.md#catalog-endpoints)
