[Documentation home](../../README.md)

# Identity claim

<a id="endpoint-identity-claim"></a>

[Reference catalog](../endpoint-kinds.md#catalog-endpoints) / Exact record

# Identity claim

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Identity claim · v1](type-cal-artifact-type-identity-claim-v1.md#type-cal-artifact-type-identity-claim-v1)

**Connection rules where it may be the source:** [asserts-identity-of](rel-relation-asserts-identity-of.md#rel-relation-asserts-identity-of) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [evidence-bears-on](rel-relation-evidence-bears-on.md#rel-relation-evidence-bears-on) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

## One declared connection for this kind

[identity-claim](endpoint-identity-claim.md#endpoint-identity-claim) **asserts-identity-of**Required: assertion_kind, claim_scope [person-reference](endpoint-person-reference.md#endpoint-person-reference)

Open [asserts-identity-of](rel-relation-asserts-identity-of.md#rel-relation-asserts-identity-of) for all its permitted pairs and qualifier rules.

[Return to this catalog](../endpoint-kinds.md#catalog-endpoints)
