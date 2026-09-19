# Essays exact implementation context

Pinned code -> source-backed model mappings -> local checks -> candidate implementation binding.

This successor completes the preparation in 0070. All forty implementation files are bound to eleven implementation surfaces, and all eighteen system nodes are covered. Seven formerly unmapped nodes have exact file hashes, selectors and explanations in `mapping-evidence.json`. Sixteen previously unassigned files are classified as runtime support, IPC, platform identity, test material or desktop packaging. No inventory placeholders remain.

The source runtime is unchanged. Three binding records differ from the original source package: the implementation manifest, binding and traceability. All twenty traceability results remain partial. The unchanged source validator reports FLAG with 340 checks and zero errors. Its fourteen historical residue statements remain preserved; current check receipts supersede obsolete environment statements without rewriting historical evidence.

The interrupted Rust 1.94.0 installation was repaired with rustup. Locked dependencies were fetched without changing either Cargo.lock. Formatting, Clippy with warnings denied, fourteen local tests (eleven runtime and three adapter tests on Linux), and browser JavaScript syntax checks pass and are captured under `checks/`. Initial offline failures are preserved separately. Test evidence is bound to the complete unchanged implementation snapshot. The desktop check hit its four-minute limit after reporting missing `pkg-config`/DBus development prerequisites; it did not pass. Desktop build output is retained separately and does not imply packaging or native Windows validation.

Existing admitted migration header contracts validate the imported candidate context. It grants no runtime activation, admission or external-effect authority. The historical DomainSpec receipt remains selected by the source binding; execution 0068 separately records its compiler successor. No generated file is silently replaced.

Reproduce the structural import and verify the exact local test inputs from the lab root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0071-essays-implementation-context-import/verify.py
```

`checks.py` records local checks in the staging package and skips existing receipts. The archived source is sufficient to rerun those commands with the pinned toolchain and locked dependencies; compiled build outputs are not part of the archive.

## Open Questions

- Full cross-client parity, crash-point recovery, transport/reconnect behavior and independent conformance remain unproven by this bounded import.
- Native Windows, live Playwright and live Wasmtime remain unverified.
- The nested Windows adapter binding is preserved source material, not independently validated by this import.
- Next: inspect the platform adapter binding and its exact evidence, keeping Linux-local checks distinct from native Windows behavior.
