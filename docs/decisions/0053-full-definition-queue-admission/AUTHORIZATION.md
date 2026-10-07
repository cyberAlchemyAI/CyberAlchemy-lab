<!-- GENERATED FILE: authorization.json is canonical. -->

# Full Definition Queue Admission Authorization

- Status: `authorized`
- Principal: `person:<vrondelli>`
- Selection: `admit full queue including reconstructed definitions`

## Scope

The user expanded the admission request to the complete pending Definition queue and explicitly included reconstructed definitions.

## Separation

This authorization admits exact source selections and Definition versions only; all downstream carrier and consumer effects remain separately governed.

## Claim ceiling

Authorization is limited to the exact manifest and its seven postimages. It grants no commit, push, publication, release, deployment, migration execution, or consumer activation.
