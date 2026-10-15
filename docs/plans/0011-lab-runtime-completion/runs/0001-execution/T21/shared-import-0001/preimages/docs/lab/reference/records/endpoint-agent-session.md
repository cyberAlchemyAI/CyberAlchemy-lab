[Documentation home](../../README.md)

# Agent session

<a id="endpoint-agent-session"></a>

[Reference catalog](../endpoint-kinds.md#catalog-endpoints) / Exact record

# Agent session

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Agent session · v1](type-cal-artifact-type-agent-session-v1.md#type-cal-artifact-type-agent-session-v1)

**Connection rules where it may be the source:** [consumes-view](rel-relation-consumes-view.md#rel-relation-consumes-view) · [governed-by](rel-relation-governed-by.md#rel-relation-governed-by) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of) · [uses-tool](rel-relation-uses-tool.md#rel-relation-uses-tool)

**Connection rules where it may be the target:** [affects](rel-relation-affects.md#rel-relation-affects) · [challenges](rel-relation-challenges.md#rel-relation-challenges) · [derives-from](rel-relation-derives-from.md#rel-relation-derives-from) · [member-of](rel-relation-member-of.md#rel-relation-member-of) · [occurs-during](rel-relation-occurs-during.md#rel-relation-occurs-during) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

## One declared connection for this kind

[failure-occurrence](endpoint-failure-occurrence.md#endpoint-failure-occurrence) **affects**Required: impact_scope, evidence_posture [agent-session](endpoint-agent-session.md#endpoint-agent-session)

Open [affects](rel-relation-affects.md#rel-relation-affects) for all its permitted pairs and qualifier rules.

[Return to this catalog](../endpoint-kinds.md#catalog-endpoints)
