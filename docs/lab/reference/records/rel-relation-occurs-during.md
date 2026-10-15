[Documentation home](../../README.md)

# occurs-during

<a id="rel-relation-occurs-during"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / occurs-during

# occurs-during

The question this connection answers

In which exact execution envelope did this Failure Occurrence happen?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **occurs-during** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** envelope_version_ref, temporal_scope

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** cause, blame, severity, recovery

<a id="rel-relation-occurs-during-section-1"></a>

## Read one permitted pattern

[failure-occurrence](endpoint-failure-occurrence.md#endpoint-failure-occurrence) **occurs-during**Required: envelope_version_ref, temporal_scope [agent-action](endpoint-agent-action.md#endpoint-agent-action)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| failure-occurrence | agent-action |
| failure-occurrence | agent-session |
| failure-occurrence | experiment-run |
| failure-occurrence | research-run |
| failure-occurrence | work |

### Exact meaning axis, effect and qualifier contract

relation.occurs-during

**Meaning axis:** `axis.occurrence-envelope` — the distinct semantic question this rule owns.

Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "envelope_version_ref": {
      "minLength": 1,
      "type": "string"
    },
    "temporal_scope": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "envelope_version_ref",
    "temporal_scope"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/occurs-during.json)

### Contract content fingerprint

9cd76083a271f0ae9a3eb02115df8c9d1e52b7014689a899e561379383296b3a

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
