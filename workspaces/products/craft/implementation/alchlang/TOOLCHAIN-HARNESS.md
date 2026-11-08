# Portable toolchain harness

## Boundary

`scripts/run-toolchain.mjs` resolves Node tools only from this package's exact
`package-lock.json` bin targets. It does not search `PATH` or borrow a sibling
package's `node_modules`. Cargo and rustc resolve either through the repository
`tools/toolchain/run` launcher or through an explicit executable whose observed
version must equal `tools/toolchain/lock.json`.

The explicit Rust form exists for a container that receives the already
installed locked sysroot as a read-only mount. It is a version-bound identity,
not an ambient fallback.

## Qualification

Run:

```sh
npm run qualify:toolchain
```

The qualifier executes the same five-test resolver suite on the host and in
the locally present Node toolchain image. Docker uses `--pull never`, no
network, a read-only root filesystem, read-only source and Rust mounts, and no
path-repair symlinks. The command prints a JSON evidence candidate; it does not
publish, install, deploy, or approve anything.

## Claim ceiling

This harness proves O01 tool identity and host/container parity only. P02 owns
clean installed-consumer flows. Product-owner testing remains deferred to L4X.

## Open Questions

- P02 decides how each clean consumer supplies its read-only locked Rust
  sysroot while preserving the same identity check.
- A changed local container image ID requires fresh O01 evidence even when its
  human-readable tag is unchanged.
