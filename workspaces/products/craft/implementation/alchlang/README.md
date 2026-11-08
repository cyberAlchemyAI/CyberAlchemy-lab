# AlchLang CLI

AlchLang describes business types and executable requirements in `.alch` files.
Craft checks the model and generates code and graph views through selected
implementation profiles. Formal claims are optional in the generic path.

Start with the [installed Rule and calculation examples](docs/GENERIC-APPLICATIONS.md).
The first runs one Boolean Rule. The second combines filtering, mapping, folding,
sorting, a Policy, a State Machine proposal and an Operation. Their business models,
profiles, inputs and exercises ship with the tools.

| Command path | Use it for | Guide |
|---|---|---|
| `alchlang-generic generate` | Business `.alch` source with an explicit capability profile; the cumulative generic implementation. | [Generic applications](docs/GENERIC-APPLICATIONS.md) |
| `alchlang profile` | Declarative application, service and API-layout recipes with their own admitted mechanisms. | [Profile generation](docs/PROFILE-GENERATION.md) |
| `alchlang check` / `build` | Existing explicit `application-v1` carriers and compatibility profiles. | [Installed tutorial](docs/TUTORIAL.md) |

Each path has versioned profiles and its own supported combinations. The
all-thirteen backend model and compatibility examples remain available below.
The complete generic application matrix is still being qualified; the bundled
examples describe their actual scope.

## Install a local candidate and run it

The selected core package is `@cyberalchemy/alchlang@0.7.0-candidate.0` with the
`alchlang` command. Install the exact `@domainspec-v2/cli@1.3.0` companion for
the journeys below; its command is `domainspec-v2`. Package name and compiler
version are separate identities.

From a new caller-owned consumer outside this checkout, using Linux x64,
Node 26.8.1 and npm 11.19.0:

```bash
npm init -y
npm install --ignore-scripts --save-exact \
  /absolute/path/cyberalchemy-alchlang-0.7.0-candidate.0.tgz \
  /absolute/path/domainspec-v2-cli-1.3.0.tgz \
  typescript@6.0.3 @types/node@26.4.0
unset ALCHLANG_DOMAINSPEC_PACKAGE_ROOT
./node_modules/.bin/alchlang --help
./node_modules/.bin/alchlang --version
./node_modules/.bin/domainspec-v2 --help
./node_modules/.bin/domainspec-v2 --version
run_root="$(mktemp -d)"
node node_modules/@cyberalchemy/alchlang/examples/cli-preview/run.mjs \
  --out "$run_root/alch-preview"
```

GitHub repository distribution is selected: installable release archives with
bundled Markdown guides. Use the exact GitHub release archives once published;
for now, replace the local paths above with those same candidate artifacts
supplied by their owner. npm installs the archives and consumer dependencies;
it is not the selected publication destination. Public repository access and
release approval remain pending. Keep the consumer lockfile.
This TypeScript preview needs no source checkout, sibling repository, Python,
Rust, Lean, database or hosting service.

The starter runner checks/builds/verifies the complete copied delivery model,
compiles generated TypeScript, invokes actual Mapping/Rule/Policy/constant
exports, and makes a reviewed example edit from fee 500 to 600. It retains
observations and both versions. Its historical SFOL source selects the narrow
`domainspec-1.0.0` backend explicitly; it is a compatibility starter rather
than the canonical all-thirteen application authoring contract.

Follow the [installed tutorial](docs/TUTORIAL.md) for the complete source,
companion, native invocation and edit workflow. The wrapper exports
`evaluateMapping` and `selectPolicy`; selected Calculations are explicitly
invoked through their generated native functions.

## Canonical source and native examples

Continue from the same installed consumer:

```bash
node node_modules/@cyberalchemy/alchlang/examples/meta-types/formation.mjs
node node_modules/@cyberalchemy/alchlang/examples/meta-types/rule-query/run.mjs \
  --output "$run_root/named-rule-query"
node node_modules/@domainspec-v2/cli/examples/reconciled-commerce/test-meta-types.mjs \
  --output "$run_root/craft-meta-types"
```

Every output must be absent with an existing parent. The first command checks
all-thirteen `application-v1` source formation. The second qualifies named Rules
in list/optional Queries and a read-bound Operation with explicit in-memory
transaction bindings. Direct Craft separately exercises all thirteen generated
TypeScript types under `domainspec.reconciled-typescript/v1-candidate`, with
exact UInt64 controls and an authored arithmetic edit from 93 to 107.
These examples do not imply every profile/target combination supports the same
runtime behavior.

Read the [FormalClaim reference](docs/FORMAL-CLAIMS.md),
[source formation](examples/meta-types/README.md), and
[named-Rule Query/Operation guide](examples/meta-types/rule-query/README.md).
The [language reference](docs/LANGUAGE.md) preserves the explicitly bounded
legacy grammar. [Compilation reconciliation](docs/COMPILATION-RECONCILIATION.md)
explains backend selection and rejection. [Behavioral qualification](docs/BEHAVIORAL-QUALIFICATION.md)
separates source closure from observed runtime behavior.

## Package boundaries

This source directory is a private development workspace named
`@cyberalchemy/domainspec-cli-candidate`; that monolithic package is not the
selected installed core release. Its builds produce separate candidate archives:

| Package | Command | Boundary |
| --- | --- | --- |
| `@cyberalchemy/alchlang` | `alchlang` | Node/TypeScript core; no Cargo templates or local-host modules |
| `@cyberalchemy/alchlang-rust` | `alchlang-rust` | Optional native Rust generation/conformance; its native work requires Cargo |
| `@cyberalchemy/alchlang-local-host` | `alchlang-local-host` | Experimental repository-bound hosting/provisioning; separate operational prerequisites |

See [PACKAGE-BOUNDARIES.md](PACKAGE-BOUNDARIES.md) for the source packaging
contract. Core rejects optional Rust/host targets with a diagnostic identifying
the required optional command. Building candidate archives does not publish them.

## Meaning, generation and execution

Policies select target identities; callers invoke the selected function.
Mappings construct fields and do not automatically invoke factories or enforce
Value Object invariants. Events describe occurrences; delivery requires an
explicit provider. State Machine and Workflow recovery outputs remain intent
until explicitly executed. Operations require explicit runtime bindings.

Compiler verification binds generated bytes to source and selections. Native
examples add finite behavioral observations. Neither establishes universal
formal proof, durable recovery, public distribution or production readiness.
Source-linked companion meanings and synthetic accepted-shaped fixtures carry
no authority effect.

## License and support

Licensed under [Apache License 2.0](LICENSE) (SPDX: `Apache-2.0`).
For support, contact [hello@cyberalchemize.com](mailto:hello@cyberalchemize.com).

## Open Questions

The exact public repository/access arrangement and release approval remain
owner decisions. Anonymous acquisition of exact qualified
artifacts must be verified after publication. Other platforms and additional
runtime/provider combinations need their own evidence. Local hosting, TDE and
EVF remain deferred.

## Profile generation

[Generate APIs from business sources and profiles](docs/PROFILE-GENERATION.md). The CLI exposes selection, checking, planning, generation, views and verification. Formal claims remain unproved unless separately established; local hosting, TDE, EVF and publication remain deferred.

## Business authoring from one source

Use `alchlang business --help` for the candidate workflow: initialize a project with a v3 profile, check and inspect the business review, explicitly record the exact owner decision, then generate the API and its business/system/bridge views. Users author business requirements and formal claims; the finite recipe generates semantic bindings and request wiring.

See the complete [business authoring guide](docs/BUSINESS-AUTHORING.md) and [source examples](/home/vlad_/projects/cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/implementation/examples/profile-engine/business-authoring). The candidate supports the documented Entity Bool-field, whole-input, empty-effects slice; claims remain unproved. Local hosting, TDE and EVF remain deferred. Package preparation grants no publication or product approval.

## Contributing integration/profile changes

Start with the repository [contributor guide](/home/vlad_/projects/cyberAlchemy-v2/CONTRIBUTING.md). Reuse source-backed capabilities across generation paths; record selected contracts, lifecycle and failure behavior using the shared integration process. Keep source formation and actual provider/runtime qualification separate. Open development questions are owned by that process and the current implementation plan.
