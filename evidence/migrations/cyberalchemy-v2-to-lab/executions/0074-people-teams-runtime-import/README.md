# People and Teams through the existing runtime

Verified source -> canonical event pairs -> replay -> exact records and documents.

Imported the complete 0072 People and Teams snapshot into an isolated local instance of the existing v4 source runtime. No runtime implementation changes were needed. The package contains 21 model nodes, 26 relationships and eighteen supporting documents, represented by 65 semantic/governance event pairs. These are ontology model records, not real people or teams.

The existing runtime source and lockfile were copied and built with Rust 1.94.0; all 23 runtime tests pass. Eleven import checks and four rejection cases verify exact exported records, document bytes, endpoint closure, separate-process restart equality, deterministic fresh imports, refusal to overwrite an existing target, unknown-package rejection and detection of corrupted transactions/heads. Reads do not alter either stored history or original source bytes.

Runtime store: `.local/people-teams-runtime-0074/`. It is an on-demand local CLI instance; no server or enforcement hook was started. The package manifest is separate from the frozen v4 manifest. The original People and Teams source remains unchanged, including historical evidence selections, eight unassessed obligations and six residue items.

Inspect with the exact built binary:

```sh
.local/people-teams-runtime-package-0074/runtime/target/debug/cal-ontology-source-runtime summary .local/people-teams-runtime-0074
.local/people-teams-runtime-package-0074/runtime/target/debug/cal-ontology-source-runtime export .local/people-teams-runtime-0074
```

`runtime-store.tar.gz` preserves committed store files; `package-snapshot.tar.gz` preserves runtime source, tests, lockfile and the source package. The export is also saved as `export.json`. Existing stores are never silently replaced by the verification script.

Reproduce checks from the Lab root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0074-people-teams-runtime-import/verify.py
```

## Open Questions

- This establishes exact representation and replay, not source ontology admission, execution of its business rules, or production durability.
- Source-qualified identities remain distinct; no global meaning merge occurred.
- The broader Lab runtime manifest and request/validator integration remain separate work.
- Next: audit the Shared Capability ontology registration, the next missing package identified by 0073. Use the existing runtime and preserve each package's native verdict.
