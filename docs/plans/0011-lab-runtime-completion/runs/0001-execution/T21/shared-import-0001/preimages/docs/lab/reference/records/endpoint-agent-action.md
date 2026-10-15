[Documentation home](../../README.md)

# Agent action

<a id="endpoint-agent-action"></a>

[Reference catalog](../endpoint-kinds.md#catalog-endpoints) / Exact record

# Agent action

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Agent action · v1](type-cal-artifact-type-agent-action-v1.md#type-cal-artifact-type-agent-action-v1)

**Connection rules where it may be the source:** [contributes-to](rel-relation-contributes-to.md#rel-relation-contributes-to) · [governed-by](rel-relation-governed-by.md#rel-relation-governed-by) · [instance-of](rel-relation-instance-of.md#rel-relation-instance-of) · [member-of](rel-relation-member-of.md#rel-relation-member-of) · [produces](rel-relation-produces.md#rel-relation-produces) · [responds-to](rel-relation-responds-to.md#rel-relation-responds-to) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of) · [uses-method](rel-relation-uses-method.md#rel-relation-uses-method) · [uses-tool](rel-relation-uses-tool.md#rel-relation-uses-tool)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [derives-from](rel-relation-derives-from.md#rel-relation-derives-from) · [evaluates](rel-relation-evaluates.md#rel-relation-evaluates) · [occurs-during](rel-relation-occurs-during.md#rel-relation-occurs-during) · [performs](rel-relation-performs.md#rel-relation-performs) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

## One declared connection for this kind

[challenge-event](endpoint-challenge-event.md#endpoint-challenge-event) **challenges**Required: challenge_contract_ref, challenge_mode, challenged_version_ref [agent-action](endpoint-agent-action.md#endpoint-agent-action)

Open [challenges](rel-relation-challenges.md#rel-relation-challenges) for all its permitted pairs and qualifier rules.

[Return to this catalog](../endpoint-kinds.md#catalog-endpoints)
