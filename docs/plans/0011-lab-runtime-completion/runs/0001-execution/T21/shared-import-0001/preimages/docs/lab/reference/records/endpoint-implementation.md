[Documentation home](../../README.md)

# Implementation

<a id="endpoint-implementation"></a>

[Reference catalog](../endpoint-kinds.md#catalog-endpoints) / Exact record

# Implementation

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Implementation · v1](type-cal-artifact-type-implementation-v1.md#type-cal-artifact-type-implementation-v1)

**Connection rules where it may be the source:** [binds-implementation](rel-relation-binds-implementation.md#rel-relation-binds-implementation) · [instance-of](rel-relation-instance-of.md#rel-relation-instance-of) · [realizes](rel-relation-realizes.md#rel-relation-realizes) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [affects](rel-relation-affects.md#rel-relation-affects) · [challenges](rel-relation-challenges.md#rel-relation-challenges) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of) · [uses-tool](rel-relation-uses-tool.md#rel-relation-uses-tool)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

## One declared connection for this kind

[failure-occurrence](endpoint-failure-occurrence.md#endpoint-failure-occurrence) **affects**Required: impact_scope, evidence_posture [implementation](endpoint-implementation.md#endpoint-implementation)

Open [affects](rel-relation-affects.md#rel-relation-affects) for all its permitted pairs and qualifier rules.

[Return to this catalog](../endpoint-kinds.md#catalog-endpoints)
