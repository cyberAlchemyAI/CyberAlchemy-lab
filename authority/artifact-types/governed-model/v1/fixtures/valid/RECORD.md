<!-- GENERATED FILE: canonical data is record.json. -->

# Governed Model fixture

- Identity: `governed-model:example-001`
- Kind: `governed-model`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "contract_ref": "contract:registry-v2",
  "extension_policy_ref": "policy:typed-extension",
  "model_kind": "artifact-type-registry",
  "rule_refs": [
    "rule:exact-overlay-resolution"
  ],
  "version_ref": "model:registry@2"
}
```

## Declared relation roles

- `target` on `relation.conforms-to` with `capability-instance` `capability-instance:example-001`

## Claim ceiling

Example Governed Model fixture for schema and relation-role validation only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
