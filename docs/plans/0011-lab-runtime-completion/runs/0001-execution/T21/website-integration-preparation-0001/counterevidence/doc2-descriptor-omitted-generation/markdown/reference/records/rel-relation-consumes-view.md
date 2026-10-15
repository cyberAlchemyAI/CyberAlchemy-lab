[Documentation home](../../README.md)

# consumes-view

<a id="rel-relation-consumes-view"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / consumes-view

# consumes-view

The question this connection answers

Which immutable Context View or Ontology View did this Agent Session actually consume?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **consumes-view** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** view_digest, cursor, consumption_purpose

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** currentness, source-authority, memory-ownership, request-fulfillment

<a id="rel-relation-consumes-view-section-1"></a>

## Read one permitted pattern

[agent-session](endpoint-agent-session.md#endpoint-agent-session) **consumes-view**Required: view_digest, cursor, consumption_purpose [context-view](endpoint-context-view.md#endpoint-context-view)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| agent-session | context-view |
| agent-session | ontology-view |

### Exact meaning axis, effect and qualifier contract

relation.consumes-view

**Meaning axis:** `axis.view-consumption` — the distinct semantic question this rule owns.

Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "consumption_purpose": {
      "minLength": 1,
      "type": "string"
    },
    "cursor": {
      "minLength": 1,
      "type": "string"
    },
    "view_digest": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "view_digest",
    "cursor",
    "consumption_purpose"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../assets/db94a3c2f590-consumes-view.json)

### Contract content fingerprint

db94a3c2f5903a27f2ec33277ab753cd0443d3ef630e8cd6fab1a52cdb83ec72

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
