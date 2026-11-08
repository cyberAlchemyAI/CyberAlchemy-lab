# DomainSpec CLI user guide

DomainSpec turns one validated domain graph into deterministic TypeScript,
Python, or Rust source. The reconciled compiler is explicit: supplying a
compilation-selection file chooses it; omitting that option preserves the
existing 1.0 build and instantiation behavior.

## Install and inspect

The initial installed TypeScript preview uses Linux x64, Node 26.8.1 and npm
11.19.0, with normal `typescript@6.0.3` and `@types/node@26.4.0`. In a new
caller-owned consumer outside the checkout:

```bash
npm init -y
npm install --save-exact /absolute/path/domainspec-v2-cli-1.3.0.tgz \
  typescript@6.0.3 @types/node@26.4.0
./node_modules/.bin/domainspec-v2 --help
./node_modules/.bin/domainspec-v2 --version
./node_modules/.bin/domainspec-v2 capabilities
```

GitHub repository distribution is selected: installable release archives with
bundled Markdown guides. Use the exact GitHub release archive once published;
until then, replace the local path above with the same candidate supplied by
its owner. npm installs the archive and consumer dependencies; it is not the
publication destination. Public repository access and release approval remain
pending. Keep `package-lock.json` to identify the consumer's tools.
This journey needs no sibling repository, Python, Rust, Lean, server, database or
hosting service. Optional `doctor` output inventories broader tool availability;
it does not make every listed tool a prerequisite for this TypeScript journey.

## Run all thirteen types and edit the source

The installed two-feature commerce example contains all thirteen backend
meta-types. Its packaged runner builds and verifies caller-owned source,
compiles generated TypeScript using the consumer's pinned compiler, and invokes
the actual generated exports:

```bash
run_root="$(mktemp -d)"
node node_modules/@domainspec-v2/cli/examples/reconciled-commerce/test-meta-types.mjs \
  --output "$run_root/craft-meta-types"
```

The output must be absent and its parent must exist. It retains source copies,
both generated versions, native compiler configs and observations. The profile
is `domainspec.reconciled-typescript/v1-candidate`; the exact UInt64 value
contract remains explicit. The TypeScript witnesses cover factories, invariant
refusal, Enums, Rules, arithmetic, Mappings, supplied-row Queries, Policy
selection, Interfaces, Events, State Machines, Operations and Workflows.
See [data signatures](examples/reconciled-commerce/meta-types/DATA.md),
[decision signatures](examples/reconciled-commerce/meta-types/DECISIONS.md) and
[behavior bindings](examples/reconciled-commerce/meta-types/BEHAVIOR.md).

Native commerce `calculateTotal` computes 100 minus 7 as `93n`; the separate
billing function computes 2 plus 3 as `5n`. Large exact values, invalid input,
overflow and underflow are checked. The runner edits only its copied commerce
Calculation from subtract to add and updates the description. Verification of
the old artifacts rejects source drift. A fresh build and native invocation
then yield `107n`. This is a meaningful source edit, not a formula recreated in
the consumer. Negative controls also cover compiler rejection, artifact
tampering and output overwrite.

Operation and Workflow witnesses use explicit local mock transactions. Their
results qualify that contract, not remote providers, durable storage or hosting.

## Build and verify directly

From the same consumer directory, copy the complete source and selections to
caller-owned space. Use paths beneath your installed package; the root export
map is import-only, so CommonJS `require.resolve('@domainspec-v2/cli')` is not
the asset-location mechanism.

```bash
package_root="$PWD/node_modules/@domainspec-v2/cli"
mkdir "$run_root/commerce"
cp -R "$package_root/examples/reconciled-commerce/source" "$run_root/commerce/"
cp -R "$package_root/examples/reconciled-commerce/selections" "$run_root/commerce/"
example_root="$run_root/commerce"
./node_modules/.bin/domainspec-v2 build "$example_root/source" \
  --language typescript \
  --target-root "$run_root/typescript" \
  --compilation-selection "$example_root/selections/typescript.json"
./node_modules/.bin/domainspec-v2 verify "$example_root/source" \
  --language typescript \
  --target-root "$run_root/typescript" \
  --compilation-selection "$example_root/selections/typescript.json"
```

Every output path must be absolute and absent, with an existing parent.
`verify` checks exact planned paths, bytes, receipts and source identity. It does
not run a native compiler. Generated TypeScript must be compiled with all its
imports before invocation; the packaged runner creates the NodeNext compiler
config and invokes the real native modules.

Python and Rust selections are included for their separate target workflows.
Presence in the archive does not extend this initial installed TypeScript
qualification to those toolchains or all their runtime combinations.

## Output layouts

Add this option to a whole-project `build`, `verify`, or stronger
`verify-project` call:

```text
--output-layout domainspec.application-layout/v1
```

The selected language remains inside the selection file and must match
`--language`. Application layout changes only the output envelope: domain code
is under `domain/<language>/src`, application composition under `app`, runtime
support under `runtime`, provenance under `provenance`, and receipts/traces under
`evidence`. Omitting `--output-layout` keeps the reconciled flat view. A node-only
instantiation cannot use application layout because the application envelope is
a whole-project contract.

To generate a coherent native project instead, use:

```text
--output-layout domainspec.project-layout/v1
```

This layout has one executable source root rather than a separate `src` folder
inside every feature. TypeScript emits `src/features` and `src/shared/domain`.
Python emits the same feature and shared-domain structure inside
`src/<package>`. Rust emits a Cargo package with `src/features` and complete
module declarations. Within each feature, `domain` contains domain types and
decisions while `application` contains queries, mappings, interfaces,
operations, and workflows according to their generated role.

Use the same layout value for `build`, `verify`, and `verify-project`. The
project layout requires a reconciled compilation selection and whole-project
output. Its `.domainspec/project-build.json` receipt covers the exact paths and
bytes. Omitting the option preserves the current flat output; choosing the
application layout preserves its existing envelope.

## Strong native verification

`verify-project` accepts one explicit selection and language-specific absolute
tool paths. It also requires an already built target root.

TypeScript:

```text
./node_modules/.bin/domainspec-v2 verify-project <source> --target-root <target> \
  --typescript-root <typescript-package-root> \
  --node-type-root <node-types-root> \
  --lean-executable <lean> \
  --compilation-selection <typescript-selection>
```

Python:

```text
./node_modules/.bin/domainspec-v2 verify-project <source> --target-root <target> \
  --python-executable <python3> \
  --temporary-parent <existing-private-temp-parent> \
  --lean-executable <lean> \
  --compilation-selection <python-selection>
```

Rust:

```text
./node_modules/.bin/domainspec-v2 verify-project <source> --target-root <target> \
  --cargo-executable <cargo> \
  --temporary-parent <existing-private-temp-parent> \
  --compilation-selection <rust-selection>
```

Add the exact `--output-layout` value used by `build` when the target was built
with either structured layout.
Verification creates only an owned private workspace under the supplied
temporary parent and removes that workspace on success or failure.

## Source model

A source root contains `project.json`, one `specs/<feature>/feature.json` per
feature, node files under `specs/<feature>/nodes`, feature-edge files under
`specs/<feature>/edges`, and optional project edges under `edges`. A node keeps
its domain role: Entity, Value Object, Enum, Rule, Calculation, Query, Mapping,
Policy, Event, Operation, State Machine, Workflow, or Interface. These roles are
not interchangeable records.

Relationships are explicit graph edges. For example, a Query `reads` an Entity,
a Mapping `maps` to an Entity or Interface, a Rule `enforces` an Operation, an
Operation `produces` an Event, an Event `transitions` a State Machine, and a
Workflow `orchestrates` Operations. The compiler validates endpoint kinds,
scope, multiplicity, inverse distinctions, and generated projections before it
plans output.

The installed TypeScript commerce witness documents its supported contracts for nested fields,
references, exact integers, tagged sums, Rule calls, explicit Calculation values,
Queries, pure Mappings, Policy selection, atomic Operations, Event time,
State Machine transitions, Workflow occurrences/recovery intent, Interfaces,
and cross-feature identity.

## Selection files

A reconciled selection is closed versioned JSON. It names exactly one language,
profile, module root, internal layout version, field/reference bindings, factory
validators, Operation action bindings, and Workflow occurrence bindings. Unknown
fields, versions, profiles, languages, paths, incomplete bindings, duplicates,
and source drift fail. The CLI never retries an invalid explicit selection using
the legacy compiler.

Use the installed example selections as working shapes. Do not copy their
ontology selectors or bindings into a different graph; selections are checked
against the exact source identities they describe.

## Migration

The package root exports three pure helpers:

```js
import {
  migrateTypedPolicyV1,
  migrateLegacyStateMachine,
  planWorkflowOccurrenceMigration,
} from '@domainspec-v2/cli';
```

They require explicit Rule names, transition bindings, or occurrence IDs where
the old source does not contain enough meaning. Their return value is a candidate
for review. They never rewrite files or graph edges. After applying a reviewed
candidate in caller-owned source, run `lint` and the selected build/verification
flow normally. See `MIGRATION.md` for the compatibility boundary.

## Diagnostics and effects

- Exit 0 means the requested materialization or check passed.
- Exit 1 means a check ran and found a negative result, or a tool execution
  failed.
- Exit 22 means invalid arguments, unsupported input, source drift, unsafe paths,
  or another fail-closed contract violation.

Structured errors include `result`, `code`, `pointer`, `message`, and
`authority_effect`. Build and instantiation publish only to a new target. They do
not replace or repair an existing target. Planning and migrations are pure.

## Runtime boundary

For the base build and instantiation path above, generated Operations and
Workflows expose explicit provider contracts; that path does not select a
database, transport, clock, or dependency container. Selected application
profiles have their own bounded generation path in
[profile generation](docs/PROFILE-GENERATION.md).
The `run` command and `@domainspec-v2/cli/experimental/runtime` remain
experimental and are outside the stable root compatibility promise. A Policy
selects a target identity without executing it, a State Machine returns ordered
Event intents without publishing them, and Workflow recovery output is intent,
not automatic compensation execution.

Compilation, verification, and candidate evidence do not by themselves publish
a package, admit a profile, deploy infrastructure, or prove production runtime
behavior.

## License and support

Licensed under [Apache License 2.0](LICENSE) (SPDX: `Apache-2.0`).
For support, contact [hello@cyberalchemize.com](mailto:hello@cyberalchemize.com).

## Open Questions

The exact public repository/access arrangement, release approval and anonymous
public acquisition remain owner decisions. Other platforms and additional
source/runtime combinations need separate qualification. Local hosting, TDE
and EVF remain deferred.

## Profile-generated APIs

Follow [the profile generation guide](docs/PROFILE-GENERATION.md) to write business sources, select an architecture, expose APIs and consume an external read. [Profile package authoring](docs/PROFILE-PACKAGES.md) explains supported extension rules and qualification.

## Business-only application profiles

Follow [business-only application generation](docs/BUSINESS-APPLICATIONS.md) to create a single public Operation with zero functions and no authored technical companions. Supply the Alch source, explicit business-semantic manifest and public intent; a selected v2 profile supplies typed request transport and empty-effects settlement. Both local and shared transport profiles preserve the authored behavior. [Create an API-prefix profile](docs/PROFILE-PACKAGES.md#create-a-v2-api-prefix-profile-without-compiler-changes) without changing compiler code. Formal claims remain unproved; persistence and external API calls in this application slice need separate mechanisms.
