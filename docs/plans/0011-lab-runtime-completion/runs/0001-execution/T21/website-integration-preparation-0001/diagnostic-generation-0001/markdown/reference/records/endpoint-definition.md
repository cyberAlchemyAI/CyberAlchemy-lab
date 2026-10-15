[Documentation home](../../README.md)

# Definition

<a id="endpoint-definition"></a>

[Reference](../README.md#reference) / [Endpoint kinds](../endpoint-kinds.md#catalog-endpoints) / Definition

# Definition

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Definition · v2](type-cal-artifact-type-definition-v2.md#type-cal-artifact-type-definition-v2)

**Connection rules where it may be the source:** [governed-by](rel-relation-governed-by.md#rel-relation-governed-by) · [originates-from](rel-relation-originates-from.md#rel-relation-originates-from) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [carries-definition](rel-relation-carries-definition.md#rel-relation-carries-definition) · [challenges](rel-relation-challenges.md#rel-relation-challenges) · [declares-effect-on](rel-relation-declares-effect-on.md#rel-relation-declares-effect-on) · [produces](rel-relation-produces.md#rel-relation-produces) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

<a id="endpoint-definition-section-1"></a>

## One declared connection for this kind

[artifact-type](endpoint-artifact-type.md#endpoint-artifact-type) **carries-definition**Required: definition_version_ref, definition_sha256 [definition](endpoint-definition.md#endpoint-definition)

Open [carries-definition](rel-relation-carries-definition.md#rel-relation-carries-definition) for all its permitted pairs and qualifier rules.

[Return to Endpoint kinds](../endpoint-kinds.md#catalog-endpoints)
