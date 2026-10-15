[Documentation home](../../README.md)

# Artifact type

<a id="endpoint-artifact-type"></a>

[Reference catalog](../endpoint-kinds.md#catalog-endpoints) / Exact record

# Artifact type

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Artifact type · v1](type-cal-artifact-type-repository-migration-manifest-v1.md#type-cal-artifact-type-repository-migration-manifest-v1)

**Connection rules where it may be the source:** [carries-definition](rel-relation-carries-definition.md#rel-relation-carries-definition) · [governed-by](rel-relation-governed-by.md#rel-relation-governed-by) · [originates-from](rel-relation-originates-from.md#rel-relation-originates-from) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [affects](rel-relation-affects.md#rel-relation-affects) · [challenges](rel-relation-challenges.md#rel-relation-challenges) · [declares-effect-on](rel-relation-declares-effect-on.md#rel-relation-declares-effect-on) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

## One declared connection for this kind

[failure-occurrence](endpoint-failure-occurrence.md#endpoint-failure-occurrence) **affects**Required: impact_scope, evidence_posture [artifact-type](endpoint-artifact-type.md#endpoint-artifact-type)

Open [affects](rel-relation-affects.md#rel-relation-affects) for all its permitted pairs and qualifier rules.

[Return to this catalog](../endpoint-kinds.md#catalog-endpoints)
