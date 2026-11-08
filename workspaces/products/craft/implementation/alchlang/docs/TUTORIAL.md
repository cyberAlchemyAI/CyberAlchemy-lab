# AlchLang installed CLI tutorial

AlchLang authors domain meaning in `.alch` source. Craft checks the lowered
domain graph and generates typed artifacts. This tutorial uses installed local
candidate archives in a consumer directory outside the source checkout.

The first journey is a deliberately bounded delivery-fee starter: total and
partial Mappings, a Boolean Rule, ordered Policy selection, and explicitly
invoked constant Calculations. It retains historical SFOL compatibility source
and selects the `domainspec-1.0.0` backend explicitly. New application authoring
uses canonical `application-v1`; its separate examples appear below.

## Install the selected candidates

Use Linux x64, Node 26.8.1 and npm 11.19.0. Distribution is selected through
a GitHub repository, with installable release archives and bundled Markdown
guides. Use the exact GitHub release archives once published. Until then,
obtain the same candidate archives from their owner and replace the absolute
local paths below with those files. npm installs archives and consumer
dependencies; it is not the publication destination. Public repository access
and release approval remain pending.

```bash
mkdir alch-consumer
cd alch-consumer
npm init -y
npm install --save-exact \
  /absolute/path/cyberalchemy-alchlang-0.7.0-candidate.0.tgz \
  /absolute/path/domainspec-v2-cli-1.3.0.tgz \
  typescript@6.0.3 @types/node@26.4.0
unset ALCHLANG_DOMAINSPEC_PACKAGE_ROOT
./node_modules/.bin/alchlang --help
./node_modules/.bin/alchlang --version
./node_modules/.bin/domainspec-v2 --help
./node_modules/.bin/domainspec-v2 --version
```

Install Craft explicitly alongside AlchLang, even though it is an optional peer
for the core package. The selected native compiler is normal
`typescript@6.0.3`, with `@types/node@26.4.0`, owned by this consumer.
The TypeScript journey needs no Python, Rust, Lean, database or hosting service.
Keep `package-lock.json` to identify the installed dependency graph.

## Run, inspect and edit the starter

Continue from the consumer directory:

```bash
run_root="$(mktemp -d)"
node node_modules/@cyberalchemy/alchlang/examples/cli-preview/run.mjs \
  --out "$run_root/alch-preview"
```

The runner copies the complete source and its companion into caller-owned
output, invokes the installed CLI, compiles all generated TypeScript with your
consumer's compiler, and invokes actual generated functions. It leaves both
builds and observations for inspection. The requested output must be absent;
its parent must exist. Choose a new name for every run.

| Declaration or call | First result |
| --- | --- |
| `evaluateMapping("OrderToMessage", {orderId: "order-42"})` | `{messageId: "order-42", currency: "GBP"}` |
| `evaluateMapping("PartialMessage", {})` | `{}` |
| Native `urgentRequired` | `true` and `false` for the supplied Boolean values |
| `selectPolicy("ChooseDeliveryFee", facts)` | `ExpressFee`, `PriorityFee` or `StandardFee` |
| Explicit native `expressFee`, `priorityFee`, `standardFee` calls | `1000`, `750`, `500` |

`domain.ts` exports `evaluateMapping` and `selectPolicy`. Native Rule and
Calculation modules are under
`generated/src/domainspec/typescript/delivery-example`. The runner imports
`urgentRequired`, `expressFee`, `priorityFee` and `standardFee`, then maps a
selected declaration ID to that imported function. Policy selection does not
invoke a Calculation. No universal `evaluateCalculation` CLI or wrapper export
is promised for this starter.

The runner then changes only StandardFee's expression from 500 to 600 in its
copy. The unchanged companion must reject. After a synthetic review updates
the corresponding meaning and the exact source SHA-256, a new build returns
600 from the same explicitly invoked native function. Owner, declaration
identities and unrelated bindings stay intact. A digest establishes byte
currentness; it does not establish owner approval or business truth.

The journey also checks invalid inputs, source/binding drift, artifact
tampering, unsupported selections and refusal to overwrite existing output.
These finite observations qualify this combination of source, profile and
toolchain. They do not establish durable runtime behavior or a formal proof.

## Use the installed CLI directly

Copy both starter files so your changes never modify the installed package:

```bash
core_root="$PWD/node_modules/@cyberalchemy/alchlang"
mkdir "$run_root/starter"
cp "$core_root/examples/domainspec-order.alch" "$run_root/starter/"
cp "$core_root/examples/domainspec-order.alch.domainspec.json" "$run_root/starter/"
./node_modules/.bin/alchlang check "$run_root/starter/domainspec-order.alch" \
  --profile domainspec-1.0.0
./node_modules/.bin/alchlang build "$run_root/starter/domainspec-order.alch" \
  --backend domainspec --language typescript --profile domainspec-1.0.0 \
  --out "$run_root/manual-build"
./node_modules/.bin/domainspec-v2 verify "$run_root/manual-build/project" \
  --language typescript --target-root "$run_root/manual-build/generated"
```

The default companion is `<source>.domainspec.json`; `--bindings` selects an
explicit alternative. Keep source and companion together. Its declarations
bind meanings, ontology selectors, record properties, Entity identity and
Value Object Rule references to exact source bytes.

Build output contains `project/`, `generated/`, `domain.ts`, source/binding
snapshots, trace, certificate, compiler inventory and final `manifest.json`.
Compile the wrapper together with every generated TypeScript import before
invocation. The packaged runner creates a TypeScript config and the explicit
CommonJS output envelope for that step; emitted `.ts` files are source.
`verify` checks artifact bytes and source identity; it does not run native code.
Existing output directories reject, including empty ones. Use a fresh output;
this backend has no overwrite mode.

## Author canonical application source

Canonical `application-v1` declares named Rules and FormalClaims, typed fields,
explicit relationships and portable companion inputs. Start with the installed
[installed application examples](../examples/application-v1/README.md), [FormalClaim reference](FORMAL-CLAIMS.md),
and [all-thirteen source example](../examples/meta-types/README.md).

From the same consumer directory:

```bash
node node_modules/@cyberalchemy/alchlang/examples/meta-types/formation.mjs
node node_modules/@cyberalchemy/alchlang/examples/meta-types/rule-query/run.mjs \
  --output "$run_root/named-rule-query"
```

Formation checks that all thirteen meta-types retain their roles in a Craft
graph. The second example executes normal `check`, `build` and `verify`,
compiles generated TypeScript and invokes a named Rule in list and optional
Queries over supplied rows. The optional Query rejects several matches rather
than hiding ambiguity with a limit. It also exercises a read-bound Operation
with explicit in-memory transactions, including refusal and uncertain commit.
See its [exact scope](../examples/meta-types/rule-query/README.md).

For native behavior across all thirteen types, use the separately installed
Craft example:

```bash
node node_modules/@domainspec-v2/cli/examples/reconciled-commerce/test-meta-types.mjs \
  --output "$run_root/craft-meta-types"
```

That journey uses `domainspec.reconciled-typescript/v1-candidate`, invokes
real generated exports, and edits commerce subtraction to addition so 93 becomes
107. Its profile and authored JSON contracts are distinct from the narrow
AlchLang delivery starter. See the installed Craft `USER-GUIDE.md` and the
commerce example's `meta-types/DATA.md`, `DECISIONS.md` and `BEHAVIOR.md`.

## Profiles and semantic boundaries

| Profile | Supported journey |
| --- | --- |
| Historical SFOL source + `domainspec-1.0.0` backend | Delivery starter: String/Bool records, identifier fields, Boolean equality Rules, safe input-free UInt64 constants, concrete Mappings and ordered Policies |
| `application-v1` | Canonical all-thirteen source formation; the separate named-Rule Query/read-bound Operation example qualifies its explicit runtime subset |
| Direct Craft `domainspec.reconciled-typescript/v1-candidate` | All-thirteen local TypeScript witnesses, including factories, exact arithmetic and explicit mock transaction bindings |
| `legacy-sfol-v1` with `--backend local-compat` | Historical parser/generator compatibility; see [language reference](LANGUAGE.md) |

A Mapping constructs fields; factory construction and invariant enforcement
require their own contract. Declared Entity/Value Object types in the narrow
starter do not imply invariant-enforced constructors. Event construction is
separate from delivery. State Machine outputs and Workflow recovery outputs
are intents until an explicit provider performs them.

Optional Rust, local-host, provider and operational-evidence profiles have
separate dependencies and qualification. They are outside this tutorial's
installed TypeScript preview. The [language reference](LANGUAGE.md) retains
compatibility syntax and clearly bounded historical extension links.

## Troubleshooting

A missing companion requires the complete copied example, including fixtures
for application source. A stale source digest requires review of the source
and affected meaning before updating exact hashes. Unsupported profile/target
combinations fail explicitly; selecting another profile changes the contract.
Do not use `--backend local-compat` to conceal a rejected DomainSpec build.

If Craft is missing or has a different version, install the exact companion
archive in this consumer. Clear `ALCHLANG_DOMAINSPEC_PACKAGE_ROOT` to use the
consumer's peer. Wrong native compiler/type versions require the pinned consumer
dependencies above. An existing output requires a new destination.

## License and support

Licensed under [Apache License 2.0](../LICENSE) (SPDX: `Apache-2.0`).
For support, contact [hello@cyberalchemize.com](mailto:hello@cyberalchemize.com).

## Open Questions

The exact public repository/access arrangement, release approval and anonymous
public acquisition remain owner decisions. Other platforms, additional source
and runtime combinations, and durable providers need separate qualification.
Local hosting, TDE and EVF remain deferred.
