[Documentation home](../../README.md)

# Project governance event history

<a id="endpoint-project-governance-event-history"></a>

[Reference catalog](../endpoint-kinds.md#catalog-endpoints) / Exact record

# Project governance event history

An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.

**Record format · carrier:** [Project governance event history · v2](type-cal-artifact-type-project-governance-event-history-v2.md#type-cal-artifact-type-project-governance-event-history-v2)

**Connection rules where it may be the source:** None declared

**Connection rules where it may be the target:** [materializes-consequence](rel-relation-materializes-consequence.md#rel-relation-materializes-consequence)

These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.

**Acceptance record:** Governance record types admission

## One declared connection for this kind

[admission-transaction](endpoint-admission-transaction.md#endpoint-admission-transaction) **materializes-consequence**Required: application_receipt_ref, consequence_role, output_digest [project-governance-event-history](endpoint-project-governance-event-history.md#endpoint-project-governance-event-history)

Open [materializes-consequence](rel-relation-materializes-consequence.md#rel-relation-materializes-consequence) for all its permitted pairs and qualifier rules.

[Return to this catalog](../endpoint-kinds.md#catalog-endpoints)
