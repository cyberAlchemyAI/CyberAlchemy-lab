# Candidate package boundaries

These are construction boundaries for local candidate archives. They are not a
publication, release, installation result, product approval or authority grant.
P02 owns clean-consumer installation and execution.

## Package map

| Package | Product boundary | Public entry |
| --- | --- | --- |
| `@cyberalchemy/alchlang` | Shared application parser, exact authoring/lowering, TypeScript/Node application surface, curated schemas-through-DomainSpec guidance, and the complete three-language `application-v1` clean-consumer examples documented by `CLEAN-CONSUMER.md`. It excludes Rust/Cargo templates and local-host modules. | `alchlang`; root ESM API. |
| `@cyberalchemy/alchlang-rust` | Shared AlchLang surface plus optional Rust generation, conformance and locked Cargo templates. It excludes local-host modules. | `alchlang-rust`; Rust builder and conformance exports. |
| `@cyberalchemy/alchlang-local-host` | Experimental repository-bound host surface, including the capabilities it consumes. It is not a portable deployment package. | `alchlang-local-host`; local-host API export. |
| `@domainspec-v2/cli@1.0.0` | Separate DomainSpec compiler, CLI, stable/experimental API exports, JSON schemas, reconciled-commerce example and product documentation. | `domainspec-v2`; four declared ESM exports. |

`package-boundaries.json` is the machine-readable boundary. It expands every
candidate archive to exact file paths and records each export map, command map
and SHA-256 allowlist digest. It also snapshots the current DomainSpec manifest
and expands every declared DomainSpec directory to exact current files.

## Drift and packaging

Run:

```bash
npm run package-boundaries:check
npm run pack:release
```

The first command rebuilds and rejects any unreviewed difference between the
current outputs and committed allowlists. The second command copies only listed
files into temporary stages, forms local archives and rejects any archive whose
observed inventory differs from its allowlist. It neither installs nor
publishes the archives.

To intentionally change a boundary, run `npm run package-boundaries:write`,
review the complete manifest diff, then rerun the check and package tests.

## Checkout independence boundary

Published TypeScript declarations may use only package-local structural ports
or installed package exports. They may not import repository-relative
`craft/` or `language/` paths. At runtime the DomainSpec bridge first resolves
the installed `@domainspec-v2/cli@1.0.0` peer. The checkout-relative fallback is
development compatibility only; a P02 installed consumer must succeed without
it or fail with the documented missing-peer diagnostic.

## Deliberate exclusions

- source, tests, scripts, `node_modules`, docs-app sources, generated workspaces
  and package-artifact directories;
- registry publication, release admission and deployment;
- installation or clean-consumer behavior as a P01 claim; P02 records that
  evidence separately without changing the package-shape claim;
- product-owner testing, which remains deferred until L4X.

## Open Questions

- P02 records whether the exact archive boundaries install and execute in clean
  TypeScript, Python and Rust consumer flows.
- P03 owns freezing the exact package bytes and complete tested candidate
  manifest after P02; passing installation does not freeze a release.
