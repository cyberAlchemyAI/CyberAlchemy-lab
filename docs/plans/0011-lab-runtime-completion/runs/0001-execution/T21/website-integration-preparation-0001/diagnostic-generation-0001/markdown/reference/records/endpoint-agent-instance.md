[Documentation home](../../README.md)

# Agent instance

<a id="endpoint-agent-instance"></a>

[Reference](../README.md#reference) / [Endpoint kinds](../endpoint-kinds.md#catalog-endpoints) / Agent instance

# Agent instance

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Agent instance · v1](type-cal-artifact-type-agent-instance-v1.md#type-cal-artifact-type-agent-instance-v1)

**Connection rules where it may be the source:** [acts-for](rel-relation-acts-for.md#rel-relation-acts-for) · [assigned-to](rel-relation-assigned-to.md#rel-relation-assigned-to) · [governed-by](rel-relation-governed-by.md#rel-relation-governed-by) · [has-capability](rel-relation-has-capability.md#rel-relation-has-capability) · [instance-of](rel-relation-instance-of.md#rel-relation-instance-of) · [member-of](rel-relation-member-of.md#rel-relation-member-of) · [performs](rel-relation-performs.md#rel-relation-performs) · [profiled-by](rel-relation-profiled-by.md#rel-relation-profiled-by) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

<a id="endpoint-agent-instance-section-1"></a>

## One declared connection for this kind

[agent-instance](endpoint-agent-instance.md#endpoint-agent-instance) **acts-for**Required: delegation_ref, scope_ref, effective_period, revocation_state [principal](endpoint-principal.md#endpoint-principal)

Open [acts-for](rel-relation-acts-for.md#rel-relation-acts-for) for all its permitted pairs and qualifier rules.

[Return to Endpoint kinds](../endpoint-kinds.md#catalog-endpoints)
