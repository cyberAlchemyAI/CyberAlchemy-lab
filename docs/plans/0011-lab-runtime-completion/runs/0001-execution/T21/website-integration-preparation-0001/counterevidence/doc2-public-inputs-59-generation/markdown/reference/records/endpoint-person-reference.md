[Documentation home](../../README.md)

# Person reference

<a id="endpoint-person-reference"></a>

[Reference](../README.md#reference) / [Endpoint kinds](../endpoint-kinds.md#catalog-endpoints) / Person reference

# Person reference

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Person reference · v1](type-cal-artifact-type-person-reference-v1.md#type-cal-artifact-type-person-reference-v1)

**Connection rules where it may be the source:** [asserts-identity-of](rel-relation-asserts-identity-of.md#rel-relation-asserts-identity-of) · [assigned-to](rel-relation-assigned-to.md#rel-relation-assigned-to) · [member-of](rel-relation-member-of.md#rel-relation-member-of) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [affects](rel-relation-affects.md#rel-relation-affects) · [asserts-identity-of](rel-relation-asserts-identity-of.md#rel-relation-asserts-identity-of) · [challenges](rel-relation-challenges.md#rel-relation-challenges) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

<a id="endpoint-person-reference-section-1"></a>

## One declared connection for this kind

[failure-occurrence](endpoint-failure-occurrence.md#endpoint-failure-occurrence) **affects**Required: impact_scope, evidence_posture [person-reference](endpoint-person-reference.md#endpoint-person-reference)

Open [affects](rel-relation-affects.md#rel-relation-affects) for all its permitted pairs and qualifier rules.

[Return to Endpoint kinds](../endpoint-kinds.md#catalog-endpoints)
