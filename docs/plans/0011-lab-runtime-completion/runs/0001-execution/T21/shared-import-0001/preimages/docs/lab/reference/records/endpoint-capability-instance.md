[Documentation home](../../README.md)

# Capability instance

<a id="endpoint-capability-instance"></a>

[Reference catalog](../endpoint-kinds.md#catalog-endpoints) / Exact record

# Capability instance

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Capability instance · v2](type-cal-artifact-type-capability-instance-v2.md#type-cal-artifact-type-capability-instance-v2)

**Connection rules where it may be the source:** [conforms-to](rel-relation-conforms-to.md#rel-relation-conforms-to) · [inherits-contract](rel-relation-inherits-contract.md#rel-relation-inherits-contract) · [instance-of](rel-relation-instance-of.md#rel-relation-instance-of) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

## One declared connection for this kind

[challenge-event](endpoint-challenge-event.md#endpoint-challenge-event) **challenges**Required: challenge_contract_ref, challenge_mode, challenged_version_ref [capability-instance](endpoint-capability-instance.md#endpoint-capability-instance)

Open [challenges](rel-relation-challenges.md#rel-relation-challenges) for all its permitted pairs and qualifier rules.

[Return to this catalog](../endpoint-kinds.md#catalog-endpoints)
