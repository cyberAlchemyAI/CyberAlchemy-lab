[Documentation home](../../README.md)

# Responsibility

<a id="endpoint-responsibility"></a>

[Reference](../README.md#reference) / [Endpoint kinds](../endpoint-kinds.md#catalog-endpoints) / Responsibility

# Responsibility

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Responsibility · v1](type-cal-artifact-type-responsibility-v1.md#type-cal-artifact-type-responsibility-v1)

**Connection rules where it may be the source:** [member-of](rel-relation-member-of.md#rel-relation-member-of) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [assigned-to](rel-relation-assigned-to.md#rel-relation-assigned-to) · [challenges](rel-relation-challenges.md#rel-relation-challenges) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

<a id="endpoint-responsibility-section-1"></a>

## One declared connection for this kind

[agent-instance](endpoint-agent-instance.md#endpoint-agent-instance) **assigned-to**Required: assignment_kind, relation_record_ref [responsibility](endpoint-responsibility.md#endpoint-responsibility)

Open [assigned-to](rel-relation-assigned-to.md#rel-relation-assigned-to) for all its permitted pairs and qualifier rules.

[Return to Endpoint kinds](../endpoint-kinds.md#catalog-endpoints)
