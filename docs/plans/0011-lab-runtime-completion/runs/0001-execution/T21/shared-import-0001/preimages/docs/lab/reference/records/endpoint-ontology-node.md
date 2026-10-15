[Documentation home](../../README.md)

# Ontology node

<a id="endpoint-ontology-node"></a>

[Reference catalog](../endpoint-kinds.md#catalog-endpoints) / Exact record

# Ontology node

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Ontology node · v2](type-cal-artifact-type-ontology-node-v2.md#type-cal-artifact-type-ontology-node-v2)

**Connection rules where it may be the source:** [governed-by](rel-relation-governed-by.md#rel-relation-governed-by) · [member-of](rel-relation-member-of.md#rel-relation-member-of) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

## One declared connection for this kind

[challenge-event](endpoint-challenge-event.md#endpoint-challenge-event) **challenges**Required: challenge_contract_ref, challenge_mode, challenged_version_ref [ontology-node](endpoint-ontology-node.md#endpoint-ontology-node)

Open [challenges](rel-relation-challenges.md#rel-relation-challenges) for all its permitted pairs and qualifier rules.

[Return to this catalog](../endpoint-kinds.md#catalog-endpoints)
