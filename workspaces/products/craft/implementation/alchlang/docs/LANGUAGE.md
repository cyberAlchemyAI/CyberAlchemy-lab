# AlchLang source reference

Canonical product source uses `profile application-v1`. Begin with the
[installed application examples](../examples/application-v1/README.md),
[FormalClaim and sorted first-order logic reference](FORMAL-CLAIMS.md),
[all-thirteen source formation example](../examples/meta-types/README.md), and
[executable named-Rule Query/Operation example](../examples/meta-types/rule-query/README.md).
The [installed tutorial](TUTORIAL.md) gives complete candidate installation,
copy/check/build/native invocation and edit journeys.

## Select the source and backend contracts

`application-v1` has typed field productions such as `amount UInt64`,
`note optional<String>`, `labels list<String>`, `tags set<String>`,
`status sum<Status>` and `parent -> Order.id`. A Rule references its declared
FormalClaim; a Query names the Rule and explicitly binds its row. The packaged
`examples/meta-types/model.alch` is a complete source formation reference.
Its formation witness is separate from the executable named-Rule Query/read-bound
Operation witness and from direct Craft's all-thirteen TypeScript witness.

The compatibility grammar below describes the implemented `sfol-v1` branch,
selected with `profile legacy-sfol-v1`; historical files may retain `logic
sfol-v1` and the compatibility default. This branch uses lowercase scalar
fields, inline predicates and its own clause shapes. It does not redefine
canonical application authoring. In canonical `application-v1`, Policies,
State Machine guards, Invariants, Operations, Queries and Workflow guard
bindings reference declared Rules or FormalClaims.

The backend `domainspec-1.0.0` is a separate selection. Its narrow delivery
starter supports Mapping/Boolean Rule/Policy/constants; parser acceptance of
another backend kind is not a runtime-support claim. `--backend local-compat`
selects the historical local generator explicitly. Unsupported DomainSpec
source never silently switches backend.

## Compatibility reference map

- **Source and lexical rules:** file containers, identifiers, comments,
  indentation, literals, lists, and scalar field types.
- **Declaration reference:** the 13 DomainSpec backend types and the supporting
  AlchLang declarations used around them.
- **SFOL reference:** formula operators, precedence, and the bounded arithmetic
  term language.
- **Execution model:** the boundary between declared meaning, integration
  bindings, runtime providers, and operational evidence.
- **Implementation limits:** accepted syntax whose semantic checks are not yet
  complete.

## File contract

Canonical AlchLang source uses the `.alch` suffix. A file is plain UTF-8
without a byte-order mark and does not use a Markdown code fence.

```text
orders.alch
```

The CLI still accepts `.md` as a legacy container only when the document has
exactly one fenced `alchlang` block. New source should use `.alch`. Other file
extensions fail with `SOURCE_EXTENSION`; fences inside `.alch` fail with
`SOURCE_CONTAINER`.

Validate before generating anything:

```bash
./node_modules/.bin/alchlang check \
  node_modules/@cyberalchemy/alchlang/examples/typed-backend.alch \
  --backend local-compat
```

Compile after validation:

```bash
run_root="$(mktemp -d)"
./node_modules/.bin/alchlang build \
  node_modules/@cyberalchemy/alchlang/examples/typed-backend.alch \
  --backend local-compat --out "$run_root/legacy-generated"
```

These commands run from the installed consumer created in the tutorial.
They exercise the historical compatibility generator. For that generator,
`check` is read-only. `build` refuses to replace a non-empty output directory
unless `--force` is explicit.

## Target-profile reference

The declaration grammar below describes the local language. Selecting
`--profile domainspec-1.0.0` or `build --backend domainspec` adds a narrower
compatibility check; parser acceptance alone does not prove target support.

| Surface | Local generator | DomainSpec 1.0.0 target |
| --- | --- | --- |
| Records | Existing scalar types | String, Bool, identifier only |
| Entity identity | Local declaration rules | Explicit required String identity binding |
| Value Object | Equality fields | Required equality fields plus explicit Rule invariant references |
| Rule | Bounded SFOL | Equality, inequality, Boolean composition |
| Calculation | UInt64 inputs and arithmetic | Input-free exactly representable UInt64 constants only |
| Mapping | Authored field clauses | Explicit endpoints, compatible types, all target fields for total mappings |
| Policy | Ordered cases and default | Boolean equality cases selecting constant Calculations |
| Query and other backend kinds | Local declaration support | Rejected by the first target profile |
| Existing output | Local `--force` behavior | Any existing directory rejected; no `--force` |

The binding sidecar schema version is `alchlang.domainspec-bindings/v1`.
Required top-level members: `schema_version`, `profile`, `source_sha256`, `owner`,
`declarations`. Declaration keys must exactly cover the model. Each has a unique
ontology selector and non-empty meaning. Record bindings additionally map every
property to its selector and meaning; Entity `identity` names an actual required
String field and Value Object `invariants` names actual Rule declarations.
Selectors are explicit prototype meaning, not proof of ontology admission.

The binding digest covers exact source text. Identifiers normalize to DomainSpec
symbols; collisions reject. The compiler package, public API and executable must
all report version 1.0.0. Generated bundles carry input snapshots, traces, compiler
inventory, certificate and file hashes. Read the manifest only after completion.

See [the installed target tutorial](TUTORIAL.md#use-the-installed-cli-directly) for commands,
the complete example sidecar, output usage and existing-application migration.
`ALCHLANG_DOMAINSPEC_PACKAGE_ROOT` selects an external built 1.0.0 package.

### Exact UInt64 profile

Select `domainspec-1.0.0-exact-uint64-v1` in both the CLI and sidecar. It binds
the opt-in DomainSpec realization `domainspec.typescript-exact-uint64/v1`.
The original `domainspec-1.0.0` profile remains available with its previous limits.

| Added surface | Exact-profile contract |
| --- | --- |
| Integer records | bigint or nonnegative safe Number, within UInt64 |
| Calculation | Parameterized add/subtract/multiply/divide; exact bigint result |
| Calculation input | bigint, safe Number or canonical unsigned decimal string |
| Calculation literal | Full UInt64 via exact safe-literal arithmetic decomposition |
| Rounding | floor, ceil or reject; zero division, underflow and overflow reject |
| Query | Explicit inputs/source, filter, one stable sort key, limit, projection |
| Mapping | Numeric copies retain their input representation; defaults are explicit |
| Policy | Ordered numeric comparisons, first match and explicit fallback |

The checked entry rejects unsafe Numbers, out-of-range integers, inherited input
records and accessors on used fields. Query/Mapping outputs preserve supplied
values; equality and ordering preserve the source evaluator's semantics, including
strict equality across number/bigint representations. Calculation results use
bigint. Policy selection returns a source identifier without executing it.

Overlapping Query row/parameter names and multiple sort keys reject. Numeric
predicate and Mapping-default literals must be safe integers. Numeric general
Rules, decimal arithmetic, effects and other backend kinds are not added here.
A graph certificate establishes compilation, while the generated build receipt
also records the selected realization; verification must select that same profile.

## Document shape

Author each file with one domain and one owner; repeated headers reject. Identifiers start with a
letter or underscore and may then contain letters, digits, underscore, dot, or
hyphen. Full-line comments start with `#`. Section bodies are indented.

```alchlang
domain inventory "Inventory"
profile legacy-sfol-v1
owner inventory-domain-owner
logic sfol-v1

entity Item:
  item_id: identifier required
  quantity: integer required
```

`logic sfol-v1` selects the compatibility branch's bounded Specified First-Order
Logic vocabulary. `profile legacy-sfol-v1` makes that compatibility selection
explicit; historical carrier-v2 input defaults to this branch. Canonical new
application source uses `profile application-v1` and does not also declare
`logic sfol-v1`.

Supported scalar field types are `string`, `integer`, `decimal`, `boolean`,
`identifier`, `timestamp`, `duration`, `enum`, `reference`, `list`, and
`record`. A field is `required` unless declared `optional`.

Scalar field types are not DomainSpec backend meta-types. The complete backend
alphabet contains 13 distinct concepts: Entity, Value Object, Enum, Operation,
Query, Calculation, Rule, Policy, Workflow, Interface, Event, Mapping, and
State Machine. `DS-D1.10` was Saga and is intentionally not reused.

## Lexical reference

| Subject | Syntax | Rule | Typical diagnostic |
| --- | --- | --- | --- |
| Canonical file | `*.alch` | Lowercase extension, plain UTF-8, no byte-order mark, no Markdown fence | `SOURCE_EXTENSION`, `SOURCE_ENCODING`, `SOURCE_CONTAINER` |
| Legacy container | `*.md` | Exactly one fenced `alchlang` block | `SOURCE_BLOCK_COUNT`, `SOURCE_CONTAINER` |
| Identifier | `[A-Za-z_][A-Za-z0-9_.-]*` | Begins with a letter or underscore | `TEXT_SYNTAX` |
| Comment | `# text` | A full line whose first non-whitespace character is `#` is ignored | none |
| Body row | one or more leading whitespace characters | Belongs to the preceding top-level declaration; canonical examples use two spaces | `TEXT_SYNTAX` |
| Identifier list | `first, second` | Comma-separated; uniqueness and reference rules depend on the clause | `UNRESOLVED_REFERENCE` or a declaration-specific diagnostic |
| String | `"text"` or `'text'` in compatibility SFOL | Quote operands; titles and Enum descriptions use double quotes | `PREDICATE_SYNTAX`, `TEXT_SYNTAX` |
| Number | `42` or `4.2` | Compatibility SFOL accepts signed integer/decimal tokens (without exponent notation); Calculation terms use unsigned integer literals | `PREDICATE_SYNTAX`, `CALCULATION_SYNTAX` |

Parsing establishes that tokens and productions are recognized. Validation is
a separate stage: it checks required clauses, uniqueness, reference targets,
operand compatibility, and declaration invariants. Neither stage establishes
that generated code ran or that an external effect was authorized.

## Choosing a declaration

| Question | Choose | Distinction |
| --- | --- | --- |
| Does the concept retain identity while facts change? | Entity | A Value Object is equal by its contained values. |
| Is it a finite vocabulary without transitions? | Enum | A State Machine defines legal changes between states. |
| Does it mutate state with explicit reads, writes, and effects? | Operation | `action` is the smaller compatibility form. |
| Does it read caller-supplied rows? | Query | An Interface exposes Queries or Operations across a boundary. |
| Does it produce one checked numeric result? | Calculation | A Mapping constructs a target object field by field. |
| Does it state reusable truth? | Rule | A Policy uses ordered conditions to select a target. |
| Is it an observable outcome? | Event | An Effect declares the responsibility that performs writes or emits events. |
| Does it coordinate two or more ordered operations? | Workflow | One atomic mutation remains a single Operation. |

## Grammar notation and top-level productions

The compact grammar uses `literal` for source text written exactly as shown,
`<name>` for a supplied value or named production, `[item]` for an optional
item, `item*` for zero or more occurrences, `item+` for one or more occurrences,
`a | b` for alternatives, and parentheses for grouping.

```text
document       := domain-header [profile-header] owner-header [logic-header] declaration*
domain-header  := "domain" <id> [<double-quoted-title>]
profile-header := "profile" "legacy-sfol-v1"
owner-header   := "owner" <id>
logic-header   := "logic" "sfol-v1"

declaration := entity | value-object | enum | operation | query
             | calculation | rule | policy | workflow | interface
             | event | mapping | state-machine
             | actor | boundary | permission | action | effect | example
```

This production is an index, not a replacement for the parser. Each
declaration section below supplies its clause requirements, and the validator
enforces constraints the grammar cannot express.

## Declaration clause index

The web reference assigns stable anchors in the forms `type-<keyword>` and
`declaration-<keyword>`. Search results resolve to those entries rather than to
the top of the reference. Cardinality describes this compatibility branch:
`0..1` is optional and singular, `0..n` is optional and repeatable, `1` is
required and singular, and `1..n` or `2..n` requires at least that many values.

| Declaration | Clause cardinalities |
| --- | --- |
| `entity` | field `0..n` |
| `value-object` | field `1..n`; `equality` `1` |
| `enum` | `value` `1..n` |
| `operation` | `state-change yes` `1`; `actor`, `subject`, `input`, `reads`, `effects`, `requires`, `permission`, `emits`, and `performs` `0..n`; `writes` `1..n`; `boundary` `1`; inline guard and human-confirmation compatibility clauses `0..n` |
| `query` | `source` `1`; `inputs`, `where`, and `limit` `0..1`; `order` `0..n`; `project` `1` with a nonempty list |
| `calculation` | `inputs` `0..1`; `expression` `1`; `rounding` `0..1`, default `reject` |
| `rule` | Boolean SFOL formula `1` |
| `policy` | `inputs` `0..1`; `case` `1..n`; `default` `1` |
| `workflow` | `scope` `1`; ordered `steps` `2..n` |
| `interface` | `kind` `1`; `exposes` `1..n` |
| `event` | `subject`, `payload`, and `boundary` `0..1` |
| `mapping` | `source` and `target` `1`; `total` `0..1`, default `true`; copied or defaulted `field` clauses collectively `1..n` |
| `states` | `initial` `0..1`; transition `0..n` |
| `actor` | no body clauses |
| `boundary` | `owner` `1` |
| `permission` | `actor`, `action`, `when`, and `boundary` `1` each |
| `action` | `state-change` `0..1`; `actor`, `subject`, `input`, `reads`, `writes`, `effects`, `requires`, `permission`, `emits`, `performs`, inline guard, and human-confirmation compatibility clauses `0..n`; `boundary` `1` |
| `effect` | `pattern`, `binding`, `writes`, `emits`, `guarantee`, `on-failure`, and `boundary` `1` each |
| `example` | `kind`, `expected`, and `rules` `0..1` |

The detailed web entries also state each clause's value shape, reference target,
meaning, and declaration-level validation rules. Repetition in this table may
represent either repeated rows or one comma-separated list, depending on the
clause form shown in that entry.

## Extending the meta-type system

An `.alch` file instantiates the supported meta-types; it does not define new
meta-type categories. The textual parser has a closed declaration grammar for
`entity`, `value-object`, `enum`, `operation`, `query`, `calculation`, `rule`,
`policy`, `workflow`, `interface`, `event`, `mapping`, and `states`, plus the
supporting `actor`, `boundary`, `permission`, `action`, `effect`, and `example`
forms. An unknown top-level declaration fails with `TEXT_SYNTAX`.

Adding a new category requires a coordinated DomainSpec and compiler change:

1. define a distinct semantic category, canonical identity, invariants,
   relationships, failure behavior, and authority ceiling;
2. add a typed carrier and normalized-model representation;
3. implement parser grammar, causal validation, lowering, traceability, and
   deterministic output;
4. implement and test every claimed target-language realization and runtime
   boundary;
5. bind the exact candidate bytes and obtain the separate owner decisions
   required for admission.

A parser branch or metadata field alone does not establish a DomainSpec
meta-type, generator, runtime, or admission decision.

## Structural backend types

A Value Object has typed fields, no identity declaration, and an explicit
equality field set:

```alchlang
value-object Money:
  value: decimal required
  currency: string required
  equality value, currency
```

An Enum is a finite set. Every value carries a description; it is not a State
Machine and cannot declare transitions:

```alchlang
enum OrderStatus:
  value pending "Accepted but not committed"
  value committed "State and event committed"
```

## Operation, Workflow, and Interface

`operation` is the explicit DomainSpec write-side form. It requires
`state-change yes`, a nonempty `writes` set, and an `effects` set that exactly
matches its `performs` clauses. Effect writes must be declared by the Operation.

```alchlang
operation CommitOrder:
  state-change yes
  actor OrderService
  subject Order
  reads Order
  writes Order, OutboxMessage
  effects PersistOrderWithOutbox
  requires PositiveAmount
  boundary order-transaction-authority
  emits order-committed
  performs PersistOrderWithOutbox using sqlite-transactional-outbox
```

Legacy `action` remains supported for existing sources. It does not claim the
complete Operation contract unless authored as `operation`.

A Workflow coordinates at least two ordered Operation identifiers and declares
exactly one admitted scope:

```alchlang
workflow FulfilOrder:
  scope intra-feature
  steps CommitOrder, ConfirmOrder
```

An Interface is an internal or external boundary exposing declared Operations
or Queries:

```alchlang
interface OrdersApi:
  kind external
  exposes CommitOrder, OpenOrders
```

State Machine syntax remains `states <entity>` with an initial state and one or
more transitions. A State Machine has transitions; an Enum is only a flat value
set.

## Typed backend constructs

### Query

A Query operates only on rows supplied by its caller. Declaring a source does
not fetch it or grant access.

```alchlang
query AvailableItems:
  source Item
  where quantity > 0
  order quantity desc
  limit 20
  project item_id, quantity
```

`where`, `order`, and `limit` are optional. `project` is required and must list
unique declared fields. Without `order`, input order is preserved.

### Calculation

A Calculation evaluates checked unsigned 64-bit integer arithmetic. Declare
`inputs` before `expression`.

```alchlang
calculation AddStock:
  inputs quantity, incoming
  expression add(quantity, incoming)
  rounding reject
```

Expressions use inputs, unsigned integer literals, and nested `add`,
`subtract`, `multiply`, or `divide` calls. Rounding is `floor`, `ceil`, or
`reject`. Negative values, overflow, underflow, division by zero, missing
inputs, and rejected inexact division fail causally.

### Mapping

A Mapping constructs only its declared target fields.

```alchlang
mapping ToSummary:
  source Item
  target ItemSummary
  total true
  field summary_id <- item_id
  field label default string "unlabelled"
```

`total true` rejects when a clause cannot provide a value. A default uses a
declared scalar type followed by a JSON value.

### Policy

A Policy selects one declared Calculation or Action identifier. Selection does
not execute or authorize that target.

```alchlang
policy ReorderPolicy:
  inputs quantity
  case quantity == 0 -> ReorderNow
  default KeepStock
```

Cases are evaluated in authored order. A nonempty case list and an explicit
default are required.

## Compatibility SFOL semantic kernel

The compatibility branch uses one bounded SFOL kernel for declarative logic. A Rule is a named
SFOL formula. Query `where` clauses, Permission `when` clauses, transition
guards, inline Action conditions, and Policy cases consume the same formula
representation. Calculations are typed SFOL terms over the deliberately small
UInt64 arithmetic domain.

SFOL formulas support `==`, `!=`, `<`, `<=`, `>`, `>=`, `in`, `contains`,
`and`, `or`, `not`, `exists(...)`, and `absent(...)`. Quote string literals in
compatibility source. Declared fact names resolve as fact references; the current
parser may accept a bare undeclared right-hand word as a string literal.
Equality and ordering operands must have compatible declared types, and Boolean
operators require Boolean formulas. The normalized carrier records formulas as
`SfolFormula` and calculation terms as `SfolUInt64Term`.

`sfol-v1` evaluates quantifier-free formulas over declared, bounded values. It
excludes quantifiers, proof scripts, reflection, provider reads, and embedded
host-language expressions.

## Execution model

SFOL defines conditions over supplied values. Effectful execution uses the
following downstream components:

1. An Action or Effect contract declares what may happen, its boundary, its
   events, and its failure continuation.
2. A system Integration Binding maps the Effect to explicit persistence,
   transaction-guarantee, failure-outcome, durable-workflow, and provider
   responsibilities.
3. A registered architecture pattern and runtime provider supply concrete
   behavior. A binding alone never executes.
4. ORODI (Operational Resilience, Observability, Deployment, and Integration)
   evaluates operational evidence from bound runtime observations.

```text
AlchLang declaration -> SFOL meaning -> Action/Effect contract
  -> Integration Binding -> pattern/runtime provider
  -> runtime observation -> ORODI evidence evaluation
```

## Action-centered declarations

The same file may declare the existing constructs:

- `actor <id>`
- `states <entity>` with `initial` and `<from> -> <to>` transitions
- `rule <id>` with one predicate line
- `boundary <id>` with `owner <route>`
- `event <id>` with `subject`, `payload`, and `boundary`
- `permission <id>` with `actor`, `action`, `when`, and `boundary`
- `effect <id>` with explicit pattern, binding, writes, events, guarantee,
  failure continuation, and boundary
- `action <id>` with explicit actor, subject, inputs, rules, permissions,
  boundary, events, and optional `performs <effect> using <binding>`
- `operation <id>` with explicit state change, reads, writes, effects, guards,
  events, and exact performed effects
- `value-object <id>` with typed fields and explicit equality fields
- `enum <id>` with described finite values
- `workflow <id>` with admitted scope and ordered Operation steps
- `interface <id>` with boundary kind and exposed Operations or Queries
- `example <id>` with kind, expected result, and affected rules

See `examples/typed-backend.alch` for the typed-backend example,
`examples/backend-types.alch` for the complete 13-type profile,
`examples/customer-approval.alch` for an action, and
`examples/outbox-operation.alch` for an action with a bound Effect. The latter
two action examples are checkout reference assets omitted from the installed
core archive; they are not steps in the installed preview journey.

## Compatibility checks and remaining limits

- Repeated `domain` and `owner` headers reject; each source has one identity
  and one owner.
- Membership operands are checked: `contains` requires a list or string
  receiver, string membership requires a string member, and `in` requires a
  list as its second operand. Incompatible known types and malformed literal
  containers reject with `TYPE_MISMATCH`.
- Runtime permission checking requires the requested action to appear in that
  permission's `action_refs`. A mismatch rejects with
  `PERMISSION_ACTION_DENIED` before adapter invocation or effects.
- In the historical local-compat generator, `total true` validates authored
  Mapping clauses; complete target-field coverage needs separate review. The
  explicit `domainspec-1.0.0` backend checks coverage for its total Mappings.

## What compilation produces

`check` parses, normalizes, validates, and lowers the source in memory. `build`
writes deterministic domain artifacts and a manifest. Provider access and
effect execution occur only through an explicit runtime command with the
required adapter or binding inputs.

The generated backend-type contract files include `domain.operations.ts`,
`domain.workflows.ts`, and `domain.interfaces.ts`. This compiler renders
TypeScript for this compatibility generator. Separate Python and Rust
realizations belong to `@domainspec-v2/cli@1.0.0`, whose command retains the
`domainspec-v2` name; those targets require their own selected contracts and
qualification.

## Separate profile reference material

The following profiles have separate contracts and dependencies. Links to
checkout extension directories and omitted guides are historical/source
references; they are not installed continuation steps. Use the complete packaged meta-type examples for the supported application
journey. `APPLICATION.md` documents the separate `bound-application-v1`
compatibility adapter, not canonical `application-v1`.

## Complete function compilation units

profile function-v1 (checkout-only path `FUNCTIONS.md`) adds inline ontology bindings, boundary
schemas, integration declarations, flow expressions and an HTTP endpoint to a
single `.alch` source. This profile packages a Node HTTP function through the
DomainSpec exact UInt64 realization. The checkout reference owns its grammar,
runtime limits and open questions.

## Portable Node/Rust conformance

`portability node-rust-v1` selects the common value, ordering, date, pattern and integration semantics. `check --target rust-http` catches unsupported source before generation; `conformance` compares both generated targets against fixtures. See Portable conformance (checkout-only path `PORTABLE-CONFORMANCE.md`) and the shipping-options example in `../extensions/portable-conformance-v1`.

## Typed module composition

Portable functions can import boundary types and call another generated function with `module-local` or `module-http` bindings. See Module composition (checkout-only path `MODULE-COMPOSITION.md`) for the checkout example, import closure, trace scope and limits.

## Multi-file application composition

`alchlang.application-file/v2-candidate` composes two or more named
`application-v1` source partitions into one selected application entry. The
small root `.alch` file declares only the shared domain, profile and owner. Its
companion lists exact source references, stable namespaces and two or more
entries. Every entry names its ordered source namespaces, inbound endpoint,
runtime identity, optional runtime profile and the same exact binding roles used
by the one-file application path.

The CLI entry selection is mandatory. The following is reference-only command
syntax, not a packaged runnable example. Supply a complete composition source,
all source partitions and companions, an entry declared by that companion, and
a separately qualified runtime/profile combination. Choose an absent absolute
build output with an existing parent, then use that same output for verification.

```text
./node_modules/.bin/alchlang check <complete-composition.alch> --entry <selected-entry>
./node_modules/.bin/alchlang build <complete-composition.alch> --entry <selected-entry> --out <new-absolute-output>
./node_modules/.bin/alchlang verify <complete-composition.alch> --entry <selected-entry> --out <same-build-output>
```

There is no first-entry default, including when only one caller-facing choice
would appear convenient. Every selected source repeats the same domain title,
`application-v1` profile and owner; the loader removes only those repeated
identity headers and sends the joined declarations through the existing shared
parser and lowering path. File boundaries therefore do not create another
language or semantic authority.

Source and entry namespaces are lowercase dotted identities. The generated
`.alch/entry-manifest.json` retains every source namespace, exact path/digest,
per-partition declaration inventory, entry namespace, runtime identity,
selected endpoint, derived Operation and HTTP route. Duplicate namespaces,
entry identities, runtime identities, normalized declaration identities or
method/path pairs reject. All source and companion paths remain bounded beneath
the composition directory; symlinks and escaping paths reject before output.

The predecessor `alchlang.application-file/v1-candidate` remains the exact
one-file compatibility contract and rejects `--entry` rather than silently
ignoring it.

## Guarded module bindings

`bind shipping from ShippingPrice when HasPrice` invokes a module only when its
Boolean guard holds. DomainSpec checks output availability and generates both Node
and Rust behavior. See guarded bindings (checkout-only path `GUARDED-BINDINGS.md`) for the complete contract and examples.

## Module input mappings

`input ShippingInput` selects a typed Mapping that constructs an imported module
argument from the request and earlier binding outputs. See module input mappings (checkout-only path `MODULE-INPUT-MAPPINGS.md`)
for typing, guarded availability, runtime validation and open questions.

## Corrected event and state semantics

For the current bounded event-host prototype, use semantic-host-v1 (checkout-only path `../../extensions/semantic-corrections-v1/README.md`) and its complete orders.alch (checkout-only path `../../extensions/semantic-corrections-v1/orders.alch`). The command supplies business inputs; the envelope supplies message identity; transitions read stored state; event payloads and consumer projections have separate types. The guide includes build commands, operator policy, HTTP input and snapshot migration. Earlier event/ontology-host examples are historical prototypes with known semantic defects documented by the review baseline.

## Semantic contracts

The `semantic-contract-v1` profile declares compiler-level premises and
must-hold conditions without creating a new overlapping `law` concept:

```alch
axiom MeaningfulTokensHaveBoundaries:
  ontology "ALCH-AXIOM-MEANINGFUL-TOKEN-BOUNDARIES"
  meaning "Intent vocabulary is matched as complete normalized tokens."
  statement "A substring inside a larger token is not the same language token."
  subject domain
  commitment taken-as-given

invariant TokenMatchingDoesNotCollapseSubstrings:
  ontology "ALCH-INVARIANT-TOKEN-NON-COLLAPSE"
  meaning "A token match must not collapse a substring into a complete token."
  grounded-by MeaningfulTokensHaveBoundaries
  intrinsic ContainsToken
  property token-non-collapse
  violation "ALCH_TOKEN_COLLAPSE_DEFECT"
```

An `axiom` is a declared premise. An `invariant` is a violable condition bound
to an intrinsic and exactly one finite-fixture `validation`. `governed-by`
records an unadopted candidate Constitution reference and is accepted only with
`status candidate`, `adopted false`, and `authority-effect none`. The full
syntax and runnable source are in the
semantic contract extension (checkout-only path `../../extensions/semantic-contract-v1/README.md`).

## Distribution, license and support

Distribution is selected through a GitHub repository, with installable release
archives and bundled Markdown guides. Use exact release archives once published;
the tutorial's current local archive paths install the same candidate artifacts.
npm is the installer for archives and consumer dependencies. Public repository
access and release approval remain pending.

Licensed under [Apache License 2.0](../LICENSE) (SPDX: `Apache-2.0`).
For support, contact [hello@cyberalchemize.com](mailto:hello@cyberalchemize.com).

## Open Questions

The exact public repository/access arrangement, release approval and additional
qualified profile/target combinations remain unresolved. FormalClaim formation and finite
runtime observations do not establish universal proof or authority admission.
Local hosting, TDE and EVF remain deferred for the installed compiler preview.
