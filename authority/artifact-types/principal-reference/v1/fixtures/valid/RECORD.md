<!-- GENERATED FILE: canonical data is record.json. -->

# Principal Reference fixture

- Identity: `principal-reference:example-001`
- Kind: `principal-reference`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "integrity_digest": "sha256:principal-reference-example",
  "issuer_ref": "registry:lab-principals",
  "principal_kind": "human",
  "principal_ref": "principal:lab-owner",
  "privacy_posture": "minimal",
  "resolution_route": "route:principal-resolution"
}
```

## Declared relation roles

- `source` on `relation.asserts-identity-of` with `principal` `principal:example-001`

## Claim ceiling

Realistic Principal Reference example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
