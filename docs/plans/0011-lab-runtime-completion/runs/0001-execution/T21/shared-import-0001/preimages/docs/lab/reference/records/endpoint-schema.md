[Documentation home](../../README.md)

# Schema

<a id="endpoint-schema"></a>

[Reference catalog](../endpoint-kinds.md#catalog-endpoints) / Exact record

# Schema

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Schema · v1](type-cal-artifact-type-schema-v1.md#type-cal-artifact-type-schema-v1)

**Connection rules where it may be the source:** [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [binds-implementation](rel-relation-binds-implementation.md#rel-relation-binds-implementation) · [challenges](rel-relation-challenges.md#rel-relation-challenges) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of) · [violates](rel-relation-violates.md#rel-relation-violates)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

## One declared connection for this kind

[implementation](endpoint-implementation.md#endpoint-implementation) **binds-implementation**Required: binding_role [schema](endpoint-schema.md#endpoint-schema)

Open [binds-implementation](rel-relation-binds-implementation.md#rel-relation-binds-implementation) for all its permitted pairs and qualifier rules.

[Return to this catalog](../endpoint-kinds.md#catalog-endpoints)
