# Craft implementation

This is the imported current Craft source. Core and AlchLang build locally; AI profiles resolve this local Core. Dependency packages, Node, Cargo and shared application sources remain linked or explicitly referenced. Shared installations are never modified by configuration.

From the Lab root:

```sh
node workspaces/products/craft/implementation/run.mjs build
node workspaces/products/craft/implementation/run.mjs check
node workspaces/products/craft/implementation/run.mjs verify
node workspaces/products/craft/implementation/run.mjs views product
```

The entry point selects the existing Node 26.12.1 runtime and TypeScript 6.0.3. Core's original build owners check authored data, source capsules and schemas, then compile local source. `build-core.mjs` reuses the upstream mutable-build procedure with local roots. Explicit source bindings preserve expected normative hashes; they do not refresh old authority.

Checks exercise generated protected HTTP/Auth/SQLite commit, replay, read and denial; reject an unknown Entry; verify local package imports; and verify native ontology import/replay plus eight named readers and their rejection cases. These are Linux x64 fixture results, with no listener or provider invocation. The generated consumer links the local Core; this is not a clean archive-install certification.

`verify` runs the [broader local matrix](verification/README.md): an isolated unpacked package installation, the existing connected/portfolio test owners, full TDE tests, EVF workspace tests and pure Body War reference checks. The offline consumer uses temporary archives of the exact shared dependencies, so registry installation remains separate. [Current broader results](../work/outcomes/current-verification/broader-qualification.json) preserve failed and pending checks.

Build outputs, dependency links and current diagnostic logs stay in ignored `dist`, `node_modules` and `.local` directories. Configuration is repeatable and refuses conflicting dependency links. The original import apply script deliberately refuses to overwrite later local edits.

- [Source mappings](source-layout.json)
- [TypeScript build inputs](build-inputs.json)
- [Component bindings](bindings.json)
- [Current qualification](../work/outcomes/current-verification/lab-qualification.json)
- [Broader verification](verification/README.md)
- [Ontology application](../ontology/application/README.md)

## Open questions

Unrestricted TDE has [remaining input/test gaps](../work/blockers/blockers.json): 381 passed, 77 failed and 17 pending. The installed preference repair passed its three focused tests; all six portfolio tests passed their complete rerun. Original failures remain in the report, with no aggregate post-repair full-matrix pass claimed. Body War's complete no-effect suite passed 49 tests and validators; it remains a reference application. EVF's eight kernel tests do not qualify live providers. Real providers, measured model quality, production identity, deployment, optional agent integration, registry installation and global consumer cutover remain separate. Current reviewed semantic pins are checked by [ontology reconciliation](../ontology/sources/reconciliation.json).
