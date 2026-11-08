# Reconciled commerce example

This installed example contains one two-feature DomainSpec graph using all 13
meta types. `source/` is the authored JSON graph. `selections/` contains exact
TypeScript, Python, and Rust compiler selections. `values.json` and
`scenarios.json` document the original bounded qualification scenarios. Newly added meta-type nodes require the separate current journey below.
`scenarios/` contains the executable installed-package signed-webhook startup
checks used for all three generated languages.

## All thirteen meta-types without hosting

Install the exact consumer dependencies alongside the selected Craft archive:

```bash
npm install --save-exact typescript@6.0.3 @types/node@26.4.0
node node_modules/@domainspec-v2/cli/examples/reconciled-commerce/test-meta-types.mjs \
  --output /tmp/domainspec-meta-types-new
```

The parent must exist and the output must be absent. This command copies the
editable source graph, builds and verifies it, compiles the generated TypeScript,
and invokes all thirteen types through their actual exports. It includes invalid
inputs, compiler rejection, tampering and overwrite controls, and an authored
Calculation edit whose result changes from 93 to 107. It leaves observations and
both generated versions in the output directory. It does not start a server.

See `meta-types/DATA.md`, `DECISIONS.md` and `BEHAVIOR.md` for exact signatures,
profiles and boundaries. Operation and Workflow examples use explicit local mock
transaction bindings; this does not establish remote or durable provider behavior.

## Earlier TypeScript provider smoke test

From this CLI checkout, choose a new output directory and run:

```bash
npm run smoke:reconciled-commerce:typescript -- \
  --output /tmp/domainspec-typescript-smoke
```

The command builds the CLI, generates the TypeScript provider application,
checks exact currentness, installs locked dependencies in a disposable copy,
natively compiles that copy, and exercises the signed loopback webhook. It
leaves the generated application and JSON observations under the requested
output directory for inspection. It refuses to overwrite an existing path.

The smoke receipt proves native compilation, listener startup, invalid
signature rejection (`401`), valid signature acceptance (`202`), one handler
invocation, and an unchanged generated target. PostgreSQL, NATS, outbound HTTP,
transport delivery, consumer completion, and production guarantees remain
explicitly unobserved.

From a consumer project with the package installed, the equivalent packaged
example command is:

```bash
node node_modules/@domainspec-v2/cli/examples/reconciled-commerce/test-typescript.mjs \
  --output /tmp/domainspec-typescript-smoke
```

From a consumer that installed `@domainspec-v2/cli`, resolve this directory:

```bash
package_root="$PWD/node_modules/@domainspec-v2/cli"
example_root="$package_root/examples/reconciled-commerce"
run_root="$(mktemp -d)"
```

Then build one language, for example Rust:

```bash
node "$package_root/dist/cli/main.js" build "$example_root/source" \
  --language rust \
  --target-root "$run_root/rust" \
  --compilation-selection "$example_root/selections/rust.json" \
  --integration-source "$example_root/integrations/application.json" \
  --provider-selection "$example_root/providers/rust.json"
```

The target must not already exist. Use the matching language and selection for
TypeScript or Python. See the installed `USER-GUIDE.md` for currentness checks,
application layout, stronger native verification, diagnostics, and migration.


## Open Questions

Public availability and support terms remain separate from local installed
qualification. Additional computation operators and durable recovery require
successor contracts and evidence. Local hosting, TDE and EVF remain deferred.
