[Documentation home](../../README.md)

# uses-tool

<a id="rel-relation-uses-tool"></a>

[Reference catalog](../relation-kinds.md#catalog-relations) / Exact record

# uses-tool

The question this connection answers

Which Tool or Implementation does this Agent Session or Agent Action use?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **uses-tool** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** tool_version_ref, invocation_contract_ref, use_role

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** realization, conformance, ownership, authority

## Read one permitted pattern

[agent-action](endpoint-agent-action.md#endpoint-agent-action) **uses-tool**Required: tool_version_ref, invocation_contract_ref, use_role [implementation](endpoint-implementation.md#endpoint-implementation)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| agent-action | implementation |
| agent-action | tool |
| agent-session | implementation |
| agent-session | tool |

### Exact meaning axis, effect and qualifier contract

relation.uses-tool

**Meaning axis:** `axis.tool-use` — the distinct semantic question this rule owns.

Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "invocation_contract_ref": {
      "minLength": 1,
      "type": "string"
    },
    "tool_version_ref": {
      "minLength": 1,
      "type": "string"
    },
    "use_role": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "tool_version_ref",
    "invocation_contract_ref",
    "use_role"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/uses-tool.json)

### Contract content fingerprint

634d394ad29f581eef1044debed00e0a3f7d652f672dd67ed698256fdf61772b

SHA-256 identifies the captured contents, not truth or permission.

[Return to this catalog](../relation-kinds.md#catalog-relations)
