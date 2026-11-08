# ARE semantic runtime configuration v2 candidate

This is a separately compiled, locally testable successor. The Alch source
binds three exact inputs: the explicitly injected adapter, the semantic
runtime wrapper, and the compiled Alch prelude. It does not reuse the
historical v1 runtime admission, Rust binding or activation decision.

From the repository root:

```bash
cd language/capabilities/alchlang/plans/general-compiler-v1/implementation
TMPDIR=/var/tmp node scripts/run-toolchain.mjs tsx src/cli.ts check ../extensions/are-runtime-configuration-v2/runtime-configuration.alch
node ../extensions/are-runtime-configuration-v2/validate.mjs
TMPDIR=/var/tmp node scripts/run-toolchain.mjs tsx --test test/module-configuration.test.ts
node --test ../extensions/are-runtime-configuration-v2/validate.test.mjs ../extensions/semantic-contract-v1/consumer-parity.test.mjs
```

The validator checks generated file digests and all three source pins before
loading the pinned adapter and semantic runtime. It then composes one static
Module Port and invokes each declared entry. `PASS` is candidate conformance
only; `runtime_admitted` and `enforcement_active` remain false.

The repair dependency DAG and remaining work are in
`goals/plans/domainspec-alchlang-review-repair/ARE-MODULE-CONFIGURATION-SUCCESSOR.md`.

## Open Questions

- Which separately pinned Rust verifier and cutover candidate will govern
  this exact configuration?
- Which current P02/P03 and downstream qualification successors will bind
  the changed compiler bytes before owner validation?
