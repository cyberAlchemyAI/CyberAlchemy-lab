# Compatibility

DomainSpec v2 CLI 1.x preserves the documented root exports, stable commands, JSON schema identifiers, and exit behavior within the major version.

- Exit `0`: requested check or deterministic materialization succeeded.
- Exit `1`: a check ran and reported a negative result, or an unexpected/toolchain failure occurred.
- Exit `22`: invalid input, unsupported arguments, source drift, or another fail-closed contract violation.
- Structured failures include `result`, `code`, `pointer`, `message`, and `authority_effect`.

The `run` command and the `@domainspec-v2/cli/experimental/runtime` subpath are outside the 1.x compatibility promise. Generated TypeScript, Python, and Rust are stable only for the exact source, compiler version, language, and receipt digest that produced them.

## Explicit reconciled compiler

Supplying `--compilation-selection <absolute-json-file>` selects the reconciled
TypeScript, Python, or Rust compiler for `build`, `verify`, `verify-project`,
`instantiate`, or `instantiate-project`. Omitting that option keeps the existing
1.0 route and receipts. An invalid explicit selection never falls back to the
legacy route.

The command language must equal the language in the selection. Selected project
instantiation accepts one language because a selection describes one native
target. Whole-project build, verify, and stronger verification optionally accept
`--output-layout domainspec.application-layout/v1`; omission keeps the
reconciled flat view. Node instantiation cannot use the application envelope or
a system-integration overlay.

Artifact-currentness `verify` does not run a compiler or theorem checker.
Selected `verify-project` does, and therefore requires the language-specific
absolute tool paths shown in `USER-GUIDE.md`. Both forms reject source, selection,
receipt, artifact, path, or layout drift without repairing output.

## Optional Node permission mode

Normal CLI invocation requires no additional flag or compiler installation for
atomic output writing. On the supported Linux x64 platform, the CLI bundles the
native no-replace operation used by `build`, single-node `instantiate`, and
reconciled project publication. Existing destinations are never replaced.

When the caller explicitly enables Node's `--permission` mode, these atomic
writers return exit `22` before creating output, with code
`DS_RECONCILED_OUTPUT_UNAVAILABLE`, `MTCLI_PUBLISH_UNAVAILABLE`, or
`MTCLI_PROJECT_BUILD_UNAVAILABLE`. Planning and artifact-currentness inspection
remain available within the caller's filesystem grants. Adding `--allow-addons`
does not enable this output path: the CLI does not bypass scoped permissions,
grant permissions automatically, or fall back to an overwrite-capable rename.
Use a normal CLI process for output writing. Operating-system permissions still
apply. This handling does not extend to commands that need their own external
tools or to the separate legacy per-file project publisher.

`recipe-plan`, `recipe-generate`, and `recipe-verify`, the
`domainspec.deployment-recipe-{request,manifest,receipt}/v1` schemas, and target
ID `aws-ecs-fargate-postgres-v1` are part of the stable 1.x surface. Generated
recipe bytes are reproducible only for the exact source graph, recipe request,
consumer application and migration inventories, integration binding digests,
compiler version, and target implementation digest recorded by the receipt.
A changed target implementation changes that digest and must be reviewed as a
new recipe output. The 1.x promise does not cover cloud-provider behavior,
consumer entrypoint semantics, image registries, Terraform state backends, or
deployment environments.
