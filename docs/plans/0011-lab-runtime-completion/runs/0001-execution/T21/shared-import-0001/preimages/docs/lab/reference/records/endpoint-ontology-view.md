[Documentation home](../../README.md)

# Ontology view

<a id="endpoint-ontology-view"></a>

[Reference catalog](../endpoint-kinds.md#catalog-endpoints) / Exact record

# Ontology view

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Ontology view · v1](type-cal-artifact-type-ontology-view-v1.md#type-cal-artifact-type-ontology-view-v1)

**Connection rules where it may be the source:** [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

**Connection rules where it may be the target:** [challenges](rel-relation-challenges.md#rel-relation-challenges) · [consumes-view](rel-relation-consumes-view.md#rel-relation-consumes-view) · [successor-of](rel-relation-successor-of.md#rel-relation-successor-of)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Complete Lab definition model admission

## One declared connection for this kind

[challenge-event](endpoint-challenge-event.md#endpoint-challenge-event) **challenges**Required: challenge_contract_ref, challenge_mode, challenged_version_ref [ontology-view](endpoint-ontology-view.md#endpoint-ontology-view)

Open [challenges](rel-relation-challenges.md#rel-relation-challenges) for all its permitted pairs and qualifier rules.

[Return to this catalog](../endpoint-kinds.md#catalog-endpoints)
