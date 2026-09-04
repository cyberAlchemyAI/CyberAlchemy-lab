<!-- GENERATED FILE: authorization.json is canonical. -->

# Canonical Package Home v1 authorization

- Principal: `person:<vrondelli>`
- Selection: `admit commit and push`
- Manifest: `ba4f0f0bd08bf2d2e60f90881464d7c3dfd065f8e37d5d8f00e76bfe3af85840`
- Receipt: `bfee651e67b0cbdfb53a5f21dbe485641a26ad4a0307c39ca2a25dc62a8519f8`

## Separation

One user interaction selects three authority-distinct requests and one scoped publication instruction. It does not merge source-admission, Definition, postimage, or publication authority and does not authorize any excluded effect.

## Claim ceiling

This authorization selects only the manifest and receipt digests above plus their dependency-closed commit and fast-forward push. It does not authorize Artifact Type enforcement, Registry Context migration, release, deployment, or unrelated workspace publication.
