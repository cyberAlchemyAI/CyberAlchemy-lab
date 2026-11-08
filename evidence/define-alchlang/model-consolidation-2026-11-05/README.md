# Define model consolidation

The maintained model now lives directly in
`implementation/define-cli/alchlang/`, organized by module and use case.
Refinements update that model in place.

`authored-snapshots.tar.gz` preserves all 104 authored files from the earlier
numbered attempts, the previous index and the CLI wrapper before consolidation.
`manifest.json` records every member's SHA-256, size and mode plus the archive's
SHA-256. Every archived member was read back and checked before the editable
copies were retired.

The CLI host moved into `alchlang/runtime/`. Existing journals retain model digest
`32b8c217268c4fbcdc13be5e45e05e514f7e5a28a4aa6c97461ce917c81a86aa`.
The host extracts the exact three frozen compiler inputs from this archive into
ignored cache and verifies their identities. It does not reinterpret those
journals using a newly edited model.

Ignored generated files, qualification stores, fixture credentials and example
Work journals were excluded from this authored snapshot. They remain at their
original physical paths, including the former numbered directories' `.local/`
contents. No native Lab owner identity, grant, store or journal was migrated.

The two current source selections describe authoring and preparation compositions
of the same maintained model. They are not parallel versioned models. Historical
paths inside the snapshot and earlier evidence describe the original executions.
