[Documentation home](../../README.md)

# Experiment run

<a id="endpoint-experiment-run"></a>

[Reference](../README.md#reference) / [Endpoint kinds](../endpoint-kinds.md#catalog-endpoints) / Experiment run

# Experiment run

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Experiment run · v1](type-cal-artifact-type-experiment-run-v1.md#type-cal-artifact-type-experiment-run-v1)

**Connection rules where it may be the source:** [contributes-to](rel-relation-contributes-to.md#rel-relation-contributes-to) · [engages-inquiry](rel-relation-engages-inquiry.md#rel-relation-engages-inquiry) · [evaluates](rel-relation-evaluates.md#rel-relation-evaluates) · [member-of](rel-relation-member-of.md#rel-relation-member-of) · [realizes](rel-relation-realizes.md#rel-relation-realizes) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of) · [uses-method](rel-relation-uses-method.md#rel-relation-uses-method)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [derives-from](rel-relation-derives-from.md#rel-relation-derives-from) · [occurs-during](rel-relation-occurs-during.md#rel-relation-occurs-during) · [performs](rel-relation-performs.md#rel-relation-performs) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

<a id="endpoint-experiment-run-section-1"></a>

## One declared connection for this kind

[challenge-event](endpoint-challenge-event.md#endpoint-challenge-event) **challenges**Required: challenge_contract_ref, challenge_mode, challenged_version_ref [experiment-run](endpoint-experiment-run.md#endpoint-experiment-run)

Open [challenges](rel-relation-challenges.md#rel-relation-challenges) for all its permitted pairs and qualifier rules.

[Return to Endpoint kinds](../endpoint-kinds.md#catalog-endpoints)
