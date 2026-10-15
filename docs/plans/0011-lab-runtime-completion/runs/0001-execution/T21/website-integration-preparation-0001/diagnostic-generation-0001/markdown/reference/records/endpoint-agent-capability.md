[Documentation home](../../README.md)

# Agent capability

<a id="endpoint-agent-capability"></a>

[Reference](../README.md#reference) / [Endpoint kinds](../endpoint-kinds.md#catalog-endpoints) / Agent capability

# Agent capability

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Agent capability · v1](type-cal-artifact-type-agent-capability-v1.md#type-cal-artifact-type-agent-capability-v1)

**Connection rules where it may be the source:** [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [affects](rel-relation-affects.md#rel-relation-affects) · [challenges](rel-relation-challenges.md#rel-relation-challenges) · [declares-effect-on](rel-relation-declares-effect-on.md#rel-relation-declares-effect-on) · [has-capability](rel-relation-has-capability.md#rel-relation-has-capability) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

<a id="endpoint-agent-capability-section-1"></a>

## One declared connection for this kind

[failure-occurrence](endpoint-failure-occurrence.md#endpoint-failure-occurrence) **affects**Required: impact_scope, evidence_posture [agent-capability](endpoint-agent-capability.md#endpoint-agent-capability)

Open [affects](rel-relation-affects.md#rel-relation-affects) for all its permitted pairs and qualifier rules.

[Return to Endpoint kinds](../endpoint-kinds.md#catalog-endpoints)
