[Documentation home](../../README.md)

# Principal

<a id="endpoint-principal"></a>

[Reference](../README.md#reference) / [Endpoint kinds](../endpoint-kinds.md#catalog-endpoints) / Principal

# Principal

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Principal · v1](type-cal-artifact-type-principal-v1.md#type-cal-artifact-type-principal-v1)

**Connection rules where it may be the source:** [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [acts-for](rel-relation-acts-for.md#rel-relation-acts-for) · [asserts-identity-of](rel-relation-asserts-identity-of.md#rel-relation-asserts-identity-of) · [challenges](rel-relation-challenges.md#rel-relation-challenges) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

<a id="endpoint-principal-section-1"></a>

## One declared connection for this kind

[agent-instance](endpoint-agent-instance.md#endpoint-agent-instance) **acts-for**Required: delegation_ref, scope_ref, effective_period, revocation_state [principal](endpoint-principal.md#endpoint-principal)

Open [acts-for](rel-relation-acts-for.md#rel-relation-acts-for) for all its permitted pairs and qualifier rules.

[Return to Endpoint kinds](../endpoint-kinds.md#catalog-endpoints)
