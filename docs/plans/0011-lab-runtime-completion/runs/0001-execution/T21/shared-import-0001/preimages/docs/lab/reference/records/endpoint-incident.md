[Documentation home](../../README.md)

# Incident

<a id="endpoint-incident"></a>

[Reference catalog](../endpoint-kinds.md#catalog-endpoints) / Exact record

# Incident

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Incident · v1](type-cal-artifact-type-incident-v1.md#type-cal-artifact-type-incident-v1)

**Connection rules where it may be the source:** [affects](rel-relation-affects.md#rel-relation-affects) · [governed-by](rel-relation-governed-by.md#rel-relation-governed-by) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [declares-effect-on](rel-relation-declares-effect-on.md#rel-relation-declares-effect-on) · [member-of](rel-relation-member-of.md#rel-relation-member-of) · [responds-to](rel-relation-responds-to.md#rel-relation-responds-to) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

## One declared connection for this kind

[incident](endpoint-incident.md#endpoint-incident) **affects**Required: impact_scope, evidence_posture [agent-capability](endpoint-agent-capability.md#endpoint-agent-capability)

Open [affects](rel-relation-affects.md#rel-relation-affects) for all its permitted pairs and qualifier rules.

[Return to this catalog](../endpoint-kinds.md#catalog-endpoints)
