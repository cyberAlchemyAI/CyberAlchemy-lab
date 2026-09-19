# `@domainspec-v2/cli`

This directory contains the DomainSpec v2 Stable 1.0 compiler product. Its
stable boundary is source validation, compiled-graph construction,
deterministic generation, verification, and bounded Lean certification.
Direct JSON and AlchLang compositions share the
[composition ontology input](COMPILATION-ONTOLOGY.md). Project generation consumes
one validated graph snapshot; source provenance remains frontend-specific.
It embeds the immutable `domainspec-meta-types-current-implemented@10` catalog,
selects exactly one of
its 39 realization rows, and exposes the following command forms:

```text
domainspec-v2 add operation <source-project-root> --feature <feature> --name <operation> --description <text> --guard <guard> --failure-continuation <continuation> [--reads <csv>] [--writes <csv>] [--effects <csv>]
domainspec-v2 add query <source-project-root> --feature <feature> --name <query> --description <text> --reads <csv> --typed-contract-json <json>
domainspec-v2 add calculation <source-project-root> --feature <feature> --name <calculation> --description <text> --inputs <csv> --semantics-json <json> --calculates <operation-csv>
domainspec-v2 add rule <source-project-root> --feature <feature> --name <rule> --description <text> --ontology-rule <selector> --parameters-json <json> --expression-json <json>
domainspec-v2 add policy <source-project-root> --feature <feature> --name <policy> --description <text> --strategies <csv> --decisions-json <json> --default-strategy <strategy> --applies <operation-or-calculation-csv>
domainspec-v2 add mapping <source-project-root> --feature <feature> --name <mapping> --description <text> --source <entity-or-interface> --target <entity-or-interface> --direction <inbound|outbound|bidirectional> --totality <total|partial> --fields-json <json>
domainspec-v2 instantiate <source-project-root> --node <feature>:<node> --language <typescript|python|rust> --target-root <absolute-new-root>
domainspec-v2 instantiate <source-project-root> --node <feature>:<node> --language <typescript|python|rust> --target-root <absolute-new-root> --integration-profile provider-neutral-v1 --integration-binding-set <binding-set-id>
domainspec-v2 instantiate-project <source-project-root> --languages typescript,python,rust --target-root <absolute-new-root>
domainspec-v2 instantiate-project <source-project-root> --languages typescript --target-root <absolute-new-root>
domainspec-v2 compile <source-project-root> --target <absolute-new-file>
domainspec-v2 build <source-project-root> --language <typescript|python|rust> --target-root <absolute-new-root>
domainspec-v2 verify <source-project-root> --language <typescript|python|rust> --target-root <absolute-root>
domainspec-v2 verify-project <source-project-root> --target-root <absolute-new-root>
domainspec-v2 formalize <source-project-root> --target <absolute-new-lean-file>
domainspec-v2 formalize-check <source-project-root> --target <absolute-lean-file>
domainspec-v2 certify <source-project-root> --target <absolute-new-directory>
domainspec-v2 certify-check <source-project-root> --target <absolute-certificate-directory>
domainspec-v2 lint <source-or-instantiated-target-root>
domainspec-v2 receipt <source-or-instantiated-target-root>
domainspec-v2 capabilities
domainspec-v2 doctor
domainspec-v2 recipe-plan <source-project-root> --request <absolute-request-file> --consumer-root <absolute-consumer-root>
domainspec-v2 recipe-generate <source-project-root> --request <absolute-request-file> --consumer-root <absolute-consumer-root> --target-root <absolute-new-root>
domainspec-v2 recipe-verify <source-project-root> --request <absolute-request-file> --consumer-root <absolute-consumer-root> --target-root <absolute-root>
domainspec-v2 recipe-qualification-plan <source-project-root> --request <absolute-request-file> --consumer-root <absolute-consumer-root> --target-root <absolute-recipe-root> --profile <absolute-profile-file>
domainspec-v2 recipe-qualify <source-project-root> --request <absolute-request-file> --consumer-root <absolute-consumer-root> --target-root <absolute-recipe-root> --profile <absolute-profile-file> --qualification-root <absolute-new-directory>
domainspec-v2 recipe-qualification-verify <source-project-root> --request <absolute-request-file> --consumer-root <absolute-consumer-root> --target-root <absolute-recipe-root> --profile <absolute-profile-file> --qualification-root <absolute-directory>
domainspec-v2 --help
domainspec-v2 --version
```

`run` is an explicitly experimental command. Runtime library APIs are available
only from `@domainspec-v2/cli/experimental/runtime`; they are not part of the
Stable 1.x root API compatibility promise.

The stable command surface exposes a candidate deployment-recipe capability that compiles the checked project graph, one
closed recipe request, selected provider-neutral integration bindings, and
caller-owned TypeScript application and SQL migration bytes into the
`aws-ecs-fargate-postgres-v1` target. The generated bundle contains OCI
Dockerfiles, an encrypted/private ECS Fargate plus RDS PostgreSQL Terraform
module, transactional-outbox migrations, an encrypted SQS channel and dead-letter
queue, least-privilege publisher/consumer roles, configuration and observability
contracts, rollback guidance, and inert CI checks. The request must name an
immutable Node base-image digest plus concrete API, outbox-worker, and queue-consumer
entrypoints.

The currently required SQS branch keeps the whole recipe capability candidate.
It is generated only from an exact `TransportBinding`, `MessageChannel`,
`DeliveryPolicy`, and `TransportFailurePolicy` joined to compiled `produces` and
`triggers-cross` edges. Provider acceptance, delivery/redelivery, and application
commit remain separate evidence stages; the recipe never claims exactly-once delivery.
The first target admits only the fixed `domainspec-event-json-v1` envelope and
consumer inbox message-id deduplication owner, and carries the selected bounded
publisher retry count into configuration and the outbox migration.

`recipe-plan` is read-only. `recipe-generate` publishes only to a new absolute
directory through atomic staging. `recipe-verify` independently regenerates
the plan and checks exact path and byte membership. None of these commands
runs Docker, Terraform, PostgreSQL, AWS, image publication, infrastructure
apply, or deployment; those remain separately reviewed consumer operations.
The schemas are shipped under `contracts/deployment-recipe-*.schema.json`.

The candidate `domainspec.recipe-qualification` capability closes the next
no-effect boundary. A digest-bound profile selects exactly five adapters:
recipe-byte verification, Terraform format, backendless provider initialization,
Terraform validation, and Docker Buildx bake checking. `recipe-qualification-plan`
is pure. `recipe-qualify` runs only those fixed adapters, copies Terraform into
a temporary directory before initialization, and atomically writes a deterministic
qualification certificate plus a host run receipt and hashed stdout/stderr evidence.
`recipe-qualification-verify` replays the pure recipe plan and checks exact evidence
membership and digest linkage without rerunning external tools.

Every required check is reported as `pass`, `fail`, or `not_evaluable`; dependency
blockers are explicit and there is no skipped state. A passing qualification
certificate denies release, publication, deployment, and runtime-conformance
claims. It does not build or push images, run Terraform plan/apply, access a live
account, publish a package, release, or deploy. The four closed contracts are
shipped under `contracts/recipe-qualification-*.schema.json`.

The L1 candidate ships two closed OCI adapters under
`tools/recipe-qualification/`. Terraform 1.16.0, Docker CLI 28.0.1, Buildx
0.21.3, and their linux/amd64 image manifests are immutable inputs. The
generated Terraform recipe includes the AWS provider 6.63.0 lockfile, and
qualification uses backendless initialization with the lockfile read-only.
Run `npm run recipe-qualification:l1` from this package checkout to execute two
isolated real-tool qualifications and compare their certificate bytes with the
committed baseline. Raw receipts may differ because cache and registry output
is observational; the normalized semantic certificate must not.

## Stable 1.0 release-candidate preparation

From a clean checkout with pinned dependencies installed and an absolute L1
qualification evidence root, prepare and then independently verify the
unsigned candidate bundle. The builder compiles from a fresh archive of the
selected commit, so ambient ignored `dist/` bytes cannot enter the package:

```bash
npm run release-candidate:prepare -- \
  --qualification-evidence-root /absolute/qualification \
  --output-root /absolute/release-candidate \
  --source-commit "$(git rev-parse HEAD)"

npm run release-candidate:verify -- \
  --bundle-root /absolute/release-candidate \
  --expected-source-commit "$(git rev-parse HEAD)"
```

The bundle contains the exact npm tarball, packed-file inventory, SPDX 2.3
SBOM, unsigned in-toto/SLSA provenance candidate, normalized qualification
evidence, complete checksums, and a standalone offline verifier. Preparation
rejects dirty or mismatched Git source and binds the workspace lock. It does
not publish, tag, sign, release,
plan/apply infrastructure, access credentials, or deploy. The unsigned bundle
does not prove publisher identity or release authorization.

`add operation` authors one closed `domainspec.node/v1` Operation in an
existing validated source project. The feature and name are lowercase
kebab-case identities; the language profiles derive their filenames and
function symbols from that single node identity. Descriptions, guards, and
failure continuations are required rather than inferred. Omitted read, write,
or effect options become explicit empty sets. The command stages and validates
the complete prospective project, rejects existing nodes and concurrent
authoring, writes the new node while it is still unreferenced, and atomically
replaces the feature index as the visibility boundary. Its result includes the
recomputed source-manifest digest. This slice does not create projects,
relationships, generated implementations, or runtime providers.

`add rule` uses the same staged, locked, atomic authoring boundary. It requires
an exact ontology Rule selector, typed parameters, and a Boolean expression in
the `domainspec.typed-rule/v1` grammar. The prospective project must resolve
every referenced node, property, variant, and Rule before publication. The
three generators consume that typed closure; an untyped Rule fails explicitly
instead of receiving a truthiness default.

`add calculation`, `add policy`, and `add mapping` author closed static
semantics rather than descriptive placeholders. Calculations bind named numeric
inputs, an expression tree, explicit rounding, and finite/error behavior.
Policies bind ordered Rule conditions, a closed strategy set, and an explicit
default while rejecting ambiguous simultaneous matches. Mappings bind exact
source and target fields, conversions, defaults, requiredness, direction, and
totality; incompatible identity conversions fail during project compilation.

`instantiate` decodes one of the 13 closed backend meta types, plans one
deterministic language artifact, and publishes the artifact plus a
baseline-bound receipt through a single atomic directory rename. It never
updates an existing target. `lint` and `receipt` independently re-read an
instantiated target, reproduce the expected generator output for the selected
frozen row, and reject undeclared files or semantic drift.

`instantiate-project` plans every compiled node for one or more explicitly
selected languages from one immutable source identity. It stages all artifacts privately, claims
the target with an exclusive directory create, installs artifacts without
replacement, and links a digest-bound receipt last. A private claim token
prevents rollback from deleting a hostile replacement. `verify-project` runs
the complete source, compiled-graph, DS-D8 obligation, artifact, receipt,
formalization-currentness, and isolated exact-source replay checks in one
command. Generated TypeScript, Python, and Rust files are passed to `tsc`,
`python3 -m py_compile`, and `rustc` respectively, and every generated Cargo
manifest is parsed by `cargo metadata`; a missing or rejecting
toolchain fails the command. `DOMAINSPEC_TSC`, `DOMAINSPEC_PYTHON`,
`DOMAINSPEC_RUSTC`, and `DOMAINSPEC_CARGO` may bind exact absolute executables;
otherwise the four
commands must resolve on `PATH`. Its receipt exposes eight explicit passing checks
and zero skipped or inferred checks; it remains evidence-only.

`formalize` decodes and validates the entire authored project before it creates
one generated Lean module plus three reusable checked-refinement modules. The
output binds the source-manifest, aggregate source-bytes, compiled-graph, and
complete semantic-render-payload digests,
the ordered filename-and-byte digest of the three reusable Lean modules, and
the ordered four-file proof-unit digest,
the immutable `@10` predecessor, all 31 DS-D8 signatures, all 45 obligation
identifiers, executable predicates for the six obligation families, and one
witness for every obligation applicable to an authored edge. State Machine
sources also project their declared states, initial state, structured
transitions, Rule guard references, and Event-intent relationships into an
executable `allProjectStateMachinesHold` theorem. The same projection carries
L1 typed-field identities, Entity identity,
Value Object structural equality, Enum closure, Event occurrence/version, and
Interface boundary/compatibility facts into `allProjectL1RolesHold`.
The containing output directory must not already exist. `formalize` writes the
complete proof unit in a private sibling staging directory, claims the public
directory with an atomic exclusive create, and installs each complete staged
file with an atomic no-replace hard link. A digest-bound completion record is
linked last, retained as positive completion evidence, and never deleted by the
publisher. Failed publication removes only private staging bytes and never
deletes a claimed or competing public path. `formalize-check` rebuilds all four
proof files and the completion record, requires the exact directory inventory,
and rejects incomplete publication, source, module, or target drift.
The reusable kernel reflects graph-digest binding, source-identity binding, and
static conformance into a checked certificate. The generated current module
proves the TypeScript projection lowers to the Lean `CheckedProjectionInput`
shape and proves that successful checked compilation returns all three facts;
actual SHA-256 computation and source admission remain TypeScript/compiler
responsibilities. These finite Lean proofs do not establish runtime
conformance, business acceptance, publication, or external authority.

The graph-bound certificate also records node and edge denominators, the frozen
13-type and 17-relationship denominators, every applicable backend obligation
ID, every passing executable witness outcome, compiler/tool versions, baseline
identity, relationship-authority digest, and an explicit no-authority ceiling.
The compiler classifies all 28 backend DS-D8 obligation IDs as applicable or
inapplicable with a source selector and reason; endpoint, scope, multiplicity,
generated-projection, inverse-collapse, and deprecation witnesses are
reevaluated before the graph is accepted.

The optional system-integration pair is explicit and closed: both options must
be present or both absent. The CLI reads
`integrations/<binding-set-id>.json` from the source project, validates the
provider-neutral D45-D49 contract family, binds its source/profile/language and
architecture digests into the receipt, and emits one additional contract at
`src/domainspec/system-integration/<language>/<binding-set-id>.<extension>`.
DomainSpec accepts the target project's opaque adapter and resource references;
it does not select SQLite, another database, a framework, or a dependency
container. Generated contracts preserve
`runtime_guarantees_observed: false`: provider runtime behavior requires a
separate observation layer and is outside the stable compiler-product boundary.

Relationship inputs are validated project-wide against a digest-bound generated
projection of all 31 canonical signatures and all 45 declared validation
obligations. Source `lint`, source `receipt`, authoring, and instantiation use the
same fail-closed project validator. The decoder rejects invalid endpoint types
and placement, deprecated aliases, authored generated views, selected duplicate
propositions, inverse `owns`/`belongs-to` collapse, and the explicit `creates`
one-to-one obligations before it plans any target. `creates` also derives the
sorted `creation_targets` semantic projection without permitting source
authorship. Operation generators keep instrumentation in an injected
outer wrapper around the pure state/outbox core; Workflow generators require an
explicit composition-root compensation callable, emit a five-state forward-recovery
plan, and preserve the selected realization's `compensation_execution: false` ceiling.
Every forward and recovery step must be connected through the canonical
`Workflow --[orchestrates]--> Operation` relationship. Explicit compensation
dependencies use `operation:depends-on:operation`; absent dependencies fall back
to reverse completed-step order. A separately owned executor preflights every
Operation binding and deterministic idempotency key before the first invocation.

State Machine bodies are closed transition tables. Each transition has a stable
identity, a declared source and target state, an optional Rule selector, and an
optional Event selector. Event intents must be backed by an incoming canonical
`Event --[transitions]--> State Machine` relationship. Generated TypeScript,
Python, and Rust runtimes apply the same fail-closed causal outcomes:
`invalid-current-state`, `undeclared-transition`, `source-mismatch`, and
`guard-rejected`. The Rule-reference evaluator is required at every call site;
there is no allow-by-default guard callback. A successful transition returns only the declared next state
and Event intent; effect execution remains outside this package.

L1 domain and boundary bodies share one closed `FieldSpec`/`TypeRef`
vocabulary. Primitive references are limited to `string`, `boolean`,
`integer`, `decimal`, `timestamp`, and `uuid`; named references must resolve to
an Entity, Value Object, Enum, or Event in the compiled project graph. Entities
designate one required identity field and compare identity independently of
mutable state. Value Objects require a complete field set, no Entity-style
runtime object identity semantics, recursive structural equality, defensive
deep copies at construction and snapshot boundaries, zero identity-marked
typed properties, and at least one exact Rule invariant reference. A closed
exact-source-digest bridge preserves immutable pre-L1 typed Value Object
predecessors only; any byte change removes that compatibility. Typed-record
property metadata is otherwise preserved without changing equality into Entity
identity. Events declare their
event type, positive integer version, required occurrence identity,
occurred-at policy, and typed payload. Interfaces declare external/internal
boundary kind, version, exact/backward compatibility direction, and typed
request/result signatures whose Operation or Query references close exactly
against authored `exposes` relationships. Generated TypeScript, Python, and
Rust artifacts preserve these roles and expose deterministic identity,
equality, Event compatibility, and Interface version checks.

The implementation and compatibility boundary are stable at package version
`1.0.0`. This repository state is not itself evidence that the package was
published, registered, deployed, adopted by an owner, or used in production.
The root export is the curated compiler/generation/conformance API; the
experimental runtime uses its explicit subpath. The architecture-conformance
proof runner remains internal to `@domainspec-v2/impl` and is not used as a
code generator.

The supported target environment is Linux x64 in the repository Node toolchain
container with Node.js `v26.8.1` and npm `11.19.0`. The package has its own npm
`11.19.0` lock and a restricted registry publication configuration. Clean-package validation packs the
compiled output into isolated temporary consumers, exercises both whole-project
commands, and compares their plans and generated targets byte for byte. These checks are implementation evidence only; they do
not publish, release, deploy, or claim production operation.

## Closed Governance-kernel instantiation

`tools/governance-kernel.mjs` is a bounded, dependency-free candidate extension.
It validates the six-node DomainSpec source for the smallest Governance
evaluation kernel, binds every node to the accepted Rust realization protocol,
and deterministically emits one no-effect Rust crate. It is intentionally not a
generic generator and does not widen the supported public CLI command surface.

The generated receipt uses SHA-256 only for static source/artifact conformance.
The generated evaluator invokes no hash operation and does not use a repository
digest as identity, authority, or a lifecycle clock. Generated Rust types still
implement the standard `Hash` trait where the admitted DomainSpec realization
protocol requires equality-compatible type behavior.

Each source project pins its own admitted implementation baseline. Generation
does not follow the mutable repository-wide current pointer, so unrelated
baseline advancement cannot trigger an implicit kernel refresh.

## Property-closed Rust Operations

The standard `instantiate` command accepts a typed Operation whose referenced
records, sums, Rules, and legal relationships form one deterministic closure.
The bounded type algebra currently includes `String`, `Bool`, `UInt64`, named
types, sets, multiplicity-preserving lists, optionals, and sums. The Rule
algebra is structured data; executable Rust snippets are not accepted. List
projection preserves multiplicity unless the source explicitly applies
`to_set`, and `rule_ref` binds every target parameter by name and typed value.

For Rust, the CLI lowers that closure to typed structs, enums, and one predicate
function for every referenced Rule. It evaluates the selected guard inside the
Operation, emits deterministic ontology-to-selector-to-Rust-symbol bindings and
a Cargo manifest, and binds the complete closure into the instantiation receipt.
Missing selectors, argument drift, normalized symbol collisions, read-edge
drift, cycles, incompatible types, receipt tampering, and caller-supplied Boolean
guards fail closed.

The Auth Foundation candidate exercises this standard path:

```text
domainspec-v2 instantiate <absolute-operation-source> \
  --node auth-exact-permission:authorize \
  --language rust \
  --target-root <absolute-new-target>
```

Capability neutrality is exercised independently by the persistent
`test/fixtures/capacity-decision/` source. It selects
`capacity-decision:decide-capacity`, closes three non-Auth properties, two
result variants, one Rule, and two legal relationships, then generates and
executes a Rust capacity decision through the same command, closure compiler,
renderer, receipt, and observer. The fixture also proves that generated crates
do not retain collection imports when their selected closure does not use a
collection type or operator.

## Typed Operation fail-closed diagnostics

The L2 hardening matrix mutates that non-Auth capacity source and requires two
independent runs to return the same code, pointer, message, and exit status.
Malformed schema, missing and untyped dependencies, self-recursion, duplicate
property identity, unsupported Rule operators, and Rust semantic type mismatch
all fail before target creation.

Closure diagnostics retain the `MTCLI_TYPED_CLOSURE_*` family. Rust lowering
uses typed errors rather than generic exceptions:

- `MTCLI_TYPED_RUST_CRATE` and `MTCLI_TYPED_RUST_LITERAL` close output encoding;
- `MTCLI_TYPED_RUST_COLLISION` closes normalized symbol ambiguity;
- `MTCLI_TYPED_RUST_GUARD`, `MTCLI_TYPED_RUST_RULE`, and
  `MTCLI_TYPED_RUST_SCOPE` close dependency and binding drift;
- `MTCLI_TYPED_RUST_TYPE` and `MTCLI_TYPED_RUST_RESULT` close incompatible
  operands and output constructors;
- `MTCLI_TYPED_RUST_UNSUPPORTED` rejects forms outside the bounded Rust
  realization.

Each typed Rust diagnostic carries exit status 22 and survives the CLI failure
envelope with its code and pointer. These diagnostics are implementation
evidence, not source admission or runtime authority.

The former `tools/auth-kernel.mjs` specialization has been retired. Auth now
uses this same `instantiate` surface and typed Operation realization as every
other consumer. Historical parity evidence is owned by the Auth package, not by
an alternate CLI generator.

## Opt-in exact UInt64 TypeScript realization

Whole-project `build` and `verify` accept `--realization-profile domainspec.typescript-exact-uint64/v1`.
This local candidate adds exact bigint calculations and checked thin-query behavior.
Default generation is unchanged. See [the contract and limitations](EXACT-UINT64.md).

## Application output layout

`build` and `verify` accept `--output-layout domainspec.application-layout/v1`.
Supply the same layout and realization profile to both commands. Omitting the
layout preserves the existing low-level output structure.

The application layout emits core implementations at
`domain/<language>/src/<feature>/<node>.<extension>`, composition code at
`app/<composition>/`, runtime support at `runtime/<composition>/`, source and
composition metadata at `provenance/<composition>/`, and traces and the build
receipt under `evidence/`. Rust compositions include their separate runtime
source using generated relative paths. Build receipts bind the selected layout,
exact file paths and contents. Compilation caches belong outside the bundle.

Consumers bind the exported `APPLICATION_LAYOUT`, `APPLICATION_PATHS`,
`applicationArtifactPath` and `outputImport` contract rather than defining a
second output tree. This layout is a new local product candidate; it does not
change the previously accepted release archive. Product decision status is
tracked in `../../development/output-layout/v1/DESIGN.md`.
