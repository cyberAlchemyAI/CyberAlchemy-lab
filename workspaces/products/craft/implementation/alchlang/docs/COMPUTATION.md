# Pure computation with Craft and AlchLang

AlchLang is the readable source language. Craft checks its types and declared
bindings, then generates native code. A **Calculation** describes a value you
want to compute. A **Rule** answers a Boolean question; a **Mapping** projects a
value into another declared shape. Together they can describe collection
processing without embedding a JavaScript callback in your model.

This chapter covers the additive pure computation candidate. It keeps
`profile application-v1`, explicitly selects
`alchlang.computation/v1-candidate`, and uses
`domainspec.iteration-expression/v1-candidate` with revision
`ordered-metered-v1-candidate`. It generates standalone **TypeScript**. Select
it through `alchlang computation`; existing application/scalar commands retain
their own contracts. General application graph linking of these expressions is
a separate integration scope.

## Start with an order summary

The complete [summary source](../examples/computation/summary.alch) declares:

- `order`: accepted flag and exact amount.
- `summary`: count and total.
- Rule `eligible`: the accepted flag must be true.
- Mapping `amount`: take the amount from an order.
- Calculation `summary_step`: add one to count and add the amount to total.
- Calculation `main`: filter, map, then fold from a declared zero summary.

Its actual expression is:

```alchlang
fold(map(filter(orders,order:order=>eligible(order)),order:order=>amount(order)),
     summary{count:0,total:0},state:summary,item:UInt64=>summary_step(state,item))
```

The order matters. Filtering preserves accepted items in source order. Mapping
produces one amount per accepted item, keeping duplicates. Folding starts with
`summary{count:0,total:0}` and visits each amount in order. It returns a new
summary at each step. It does not mutate the input or combine partial reductions.

The shipped input produces:

```json
{"count":"2","total":"1250"}
```

UInt64 is an exact unsigned integer from 0 through 18446744073709551615. Source
literals use decimal integers. JSON values use **decimal strings**, including
zero. Native semantic arithmetic uses bigint. JavaScript Numbers are not a wire
substitute; an integer beyond the safe Number range can lose information before
validation.

## Check, generate, verify and run

Install the selected two archives using the repository's quickstart, with
TypeScript 6.0.3 and Node types 26.4.0 in your consumer project. Copy the complete
`examples/computation` directory from the AlchLang package into that project.
Keep each `.alch` file and its `.alch.computation.json` companion together.

These commands run from the consumer root; `$PWD` supplies absolute paths:

```sh
./node_modules/.bin/alchlang computation check "$PWD/computation/summary.alch"
./node_modules/.bin/alchlang computation build "$PWD/computation/summary.alch" \
  --out "$PWD/generated-summary"
./node_modules/.bin/alchlang computation verify "$PWD/computation/summary.alch" \
  --out "$PWD/generated-summary"
./node_modules/.bin/alchlang computation run "$PWD/computation/summary.alch" \
  --input "$PWD/computation/summary.input.json"
```

The build output directory must not exist, even as an empty directory. `check`
validates source and bindings. `build` writes `computation.ts`, normalized
`source-contract.json`, `package.json`, and a manifest with exact source,
companion, ownership and artifact identities. `verify` regenerates the expected
bytes and rejects changed source, modified outputs or extra files. `run` executes
the independent reference evaluator; it is useful for diagnosing a model.

To execute the generated native program:

Compile into a separate directory so native outputs do not change the artifact
root checked by `verify`. The compiler command explicitly ignores any consumer
`tsconfig.json` for this standalone generated module.

```sh
mkdir native-summary
printf '{"type":"module"}\n' > native-summary/package.json
./node_modules/.bin/tsc --ignoreConfig generated-summary/computation.ts --target ES2022 \
  --module NodeNext --moduleResolution NodeNext --strict --skipLibCheck \
  --lib ES2022,DOM --outDir native-summary
node --input-type=module <<'JS'
import {readFileSync} from 'node:fs';
import {runComputationJson} from './native-summary/computation.js';
console.log(runComputationJson(readFileSync('./computation/summary.input.json','utf8')));
JS
```

`runComputationJson` returns an explicit success or error result, including
`fuel_used`. A successful value is encoded using the exact wire format. A
failure contains a code, expression path, iteration index path and declared call
path. The manifest's source map connects Alch expression paths to source
locations. Generated code has no evaluator import or runtime npm dependency.

The complete direct Craft runner exercises generation, native execution,
reference comparison, a model edit and artifact tampering:

```sh
node node_modules/@domainspec-v2/cli/examples/computation/run-example.mjs \
  --out "$PWD/direct-computation-witness" \
  --tsc "$PWD/node_modules/typescript/bin/tsc"
```

## What you can express

| Form | Meaning and boundary |
| --- | --- |
| `map(items,item:Type=>expression)` | One output per input, preserving order and duplicates |
| `filter(items,item:Type=>predicate)` | Keep items whose predicate is true, preserving order |
| `fold(items,seed,state:State,item:Type=>next)` | Ordered reduction with an explicit seed; empty input returns the seed |
| `indexed-fold(...)` / `for(...)` | Ordered reduction with a UInt64 index starting at zero; `for` normalizes to the same form |
| `range(start,end,step,maxItems)` | Positive-step, end-exclusive UInt64 range, with an explicit item cap |
| `repeat(count,cap,seed,state:State,index:UInt64=>next)` | Exactly count steps, subject to the declared cap; zero returns seed |
| `while-bounded(cap,seed,state:State=>guard=>next)` | Check guard before each step; stop when false |
| `until-bounded(cap,seed,state:State=>guard=>next)` | Check guard before each step; stop when true |
| `sort(items,item:Type=>key(...),...)` | Stable, explicitly ordered keys, directions and comparison modes |
| `if`, typed `let`, `match`, record construction, field access | Closed typed value composition with lexical scopes |
| Declared pure calls | Bound Rule, Mapping, Calculation, Policy and StateMachine calls; no arbitrary callback |

Every String declares a UTF-8 byte bound, for example `String[32]`; every List
declares an item bound, for example `List<order,100>`. The selected collection
record fields are bounded scalars. Inputs, intermediate values and output have
explicit byte limits. Types and caller/callee signatures must agree.

Both conditional loops check the guard at the boundary: with cap zero an
already-satisfied exit returns the seed; a requested step fails with
`IterationLimit`. A cap bounds execution; it does not prove convergence. Ranges
reject zero steps. Checked arithmetic rejects overflow and underflow. Division
requires a selected `reject`, `floor` or `ceil` rounding policy and rejects zero
divisors. Boolean `and`/`or`, conditionals and ordered choices short-circuit.

## Sorting means an explicit comparison contract

The [sorting source](../examples/computation/sort.alch) uses:

```alchlang
sort(entries,item:entry=>key(item.priority,desc,numeric),key(item.label,asc,natural))
```

Priority is the first key, label the second. Equal keys preserve original order.
`numeric` compares exact UInt64. `lexical` compares Unicode scalar values.
`natural` compares ASCII digit runs by numeric magnitude inside strings, with
explicit deterministic leading-zero behavior. It is not locale collation.

The shipped natural example yields `item2,item10,item1`; changing only the label
mode to lexical yields `item10,item2,item1` on the same priorities and inputs.
Locale-specific collation and injected JavaScript comparators are rejected.
Missing or malformed fields reject rather than acquiring a default position.

## Reuse the existing meta-types

A named Rule supplies a Boolean predicate; a Mapping supplies an explicit
projection; a Calculation supplies a value or reducer step. All selected calls
are transitively pure and acyclic. An Operation or an unresolved symbol cannot
be called as a pure computation. Declaring an unused invalid function does not
hide it from validation.

A **Policy** owns an ordered first-match/default decision. In this successor its
branches explicitly call compatible Calculations. The
[pricing example](../examples/computation/policy.alch) selects a one-unit discount
for eligible nonzero totals and otherwise returns the input. There is no
undeclared `compute FulfillmentScore`: `compute main` selects the actual declared
Calculation named `main`.

To inspect which Calculation a Policy selected, generate and compile
`policy.alch` using the same steps above, with `generated-pricing` and
`native-pricing` as the two separate directories. Its generated module exports
an opt-in observation function:

```js
import {runComputationObserved} from './native-pricing/computation.js';
const observed = runComputationObserved({value: '5'});
console.log(observed.result);
console.log(observed.policy_decisions);
console.log(observed.observation_status);
```

The pricing decision records `policy: "pricing"`, `branch: "case:0"`,
`calculation: "discounted"` and `invocation_entered: true`, with normalized
expression, index and call paths. A default branch records `otherwise`.
Selection is recorded before evaluating the selected Calculation's arguments;
`invocation_entered` becomes true only when its body is entered. It does not
assert that the body succeeded: check the ordinary `result` too.

Observation is bounded to 100 records and 65536 encoded bytes. A `truncated`
status means the retained decisions are a prefix; never treat them as a complete
execution trace. A `complete` status describes the observation collection, not a
successful domain result. Observation leaves the ordinary result and semantic
fuel unchanged. `runComputationJsonObserved(json)` accepts the canonical JSON
input form. The independent Craft reference counterparts are
`evaluateComputationObserved(checked, inputs)` and
`evaluateComputationJsonObserved(checked, json)`.

A **StateMachine** proposes a typed immutable Outcome. It includes `tag`,
`state`, bounded `intents`, and `machine`, `branch`, `reason` provenance. For the
[approval example](../examples/computation/state-machine.alch):

```json
{"tag":"transition","state":"1","intents":["approved"],"machine":"approval","branch":"transition:0","reason":"matched"}
```

The branch ordinal identifies the selected transition in the frozen source
contract. A default stay or reject preserves state, returns no intents, and
records `otherwise` plus `no-match-stay` or `no-match-reject`. An Outcome is an
explicit typed value you can match or project. It does not store the state,
dispatch an Event, send an email, call an API or persist an intent.

This uses existing meta-type roles with an explicitly selected representation.
It introduces operators and a source contract, not a new domain meta-type.

## Create your own calculation

A companion records which source, owner, declaration kinds and authored meanings
belong together. The drafting helper derives those bindings from your actual source.
It creates a **proposal**, without changing your source or replacing a companion.
It checks syntax and binding coverage. After reviewing and adopting that proposal,
`alchlang computation check` performs Craft's type, reference, purity and cycle checks.

Use the helper from its installed package path. Its relative library import stays
inside that package; copying example source/input data does not relocate the helper.
These steps run from your consumer root after installing the two preview archives
and TypeScript 6.0.3 as described in the quickstart. Each version/output directory
is new, preserving earlier sources, companions and generated artifacts.

Write a complete source and input:

```sh
mkdir -p work
mkdir work/v1
cat > work/v1/sum.alch <<'ALCH'
profile application-v1
capability alchlang.computation/v1-candidate
semantics domainspec.iteration-expression/v1-candidate
revision ordered-metered-v1-candidate
stage full-computation
domain totals
owner sum_author
compute main
rounding reject
limits max_input_bytes=262144 max_output_bytes=65536 max_value_bytes=65536 max_items=100 max_iterations=100 max_ast_nodes=4096 max_ast_depth=32 max_call_depth=32 fuel=100000

calculation main:
  meaning "Sum item amounts in source order."
  pure
  input items:List<UInt64,100>
  result UInt64
  expression fold(items,0,state:UInt64,item:UInt64=>checked-add(state,item))
ALCH
printf '{"items":["2","3"]}\n' > work/v1/input.json
```

Draft and inspect the proposed companion:

```sh
node node_modules/@cyberalchemy/alchlang/examples/computation/draft-companion.mjs \
  --source "$PWD/work/v1/sum.alch" \
  --out "$PWD/work/v1/sum.alch.computation.candidate.json"
cat work/v1/sum.alch
cat work/v1/sum.alch.computation.candidate.json
```

Review the input type, fold seed/body, meaning and owner. The helper preserves your
meaning text; a hash cannot establish that the explanation is correct or that a
person reviewed it. When these are the bytes you want to use, copy the proposal to
the companion filename expected by the CLI, then perform the full check:

```sh
cp -n work/v1/sum.alch.computation.candidate.json work/v1/sum.alch.computation.json
./node_modules/.bin/alchlang computation check "$PWD/work/v1/sum.alch"
./node_modules/.bin/alchlang computation build "$PWD/work/v1/sum.alch" \
  --out "$PWD/generated-sum-v1"
./node_modules/.bin/alchlang computation verify "$PWD/work/v1/sum.alch" \
  --out "$PWD/generated-sum-v1"
./node_modules/.bin/alchlang computation run "$PWD/work/v1/sum.alch" \
  --input "$PWD/work/v1/input.json"
```

The reference result has `ok: true` and `value: "5"`. Compile and run the native
program in a sibling directory, then verify the original artifacts again:

```sh
mkdir native-sum-v1
printf '{"type":"module"}\n' > native-sum-v1/package.json
./node_modules/.bin/tsc --ignoreConfig generated-sum-v1/computation.ts --target ES2022 \
  --module NodeNext --moduleResolution NodeNext --strict --skipLibCheck \
  --lib ES2022,DOM --outDir native-sum-v1
node --input-type=module <<'JS'
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runComputationJson} from './native-sum-v1/computation.js';
const result = runComputationJson(readFileSync('./work/v1/input.json','utf8'));
assert.equal(result.ok, true);
assert.equal(result.value, '5');
console.log(result);
JS
./node_modules/.bin/alchlang computation verify "$PWD/work/v1/sum.alch" \
  --out "$PWD/generated-sum-v1"
```

## Make a meaningful edit

Keep version 1 intact. Version 2 changes both the body and its authored meaning:

```sh
mkdir work/v2
cp -n work/v1/input.json work/v2/input.json
cat > work/v2/sum.alch <<'ALCH'
profile application-v1
capability alchlang.computation/v1-candidate
semantics domainspec.iteration-expression/v1-candidate
revision ordered-metered-v1-candidate
stage full-computation
domain totals
owner sum_author
compute main
rounding reject
limits max_input_bytes=262144 max_output_bytes=65536 max_value_bytes=65536 max_items=100 max_iterations=100 max_ast_nodes=4096 max_ast_depth=32 max_call_depth=32 fuel=100000

calculation main:
  meaning "Sum twice each item amount in source order."
  pure
  input items:List<UInt64,100>
  result UInt64
  expression fold(items,0,state:UInt64,item:UInt64=>checked-add(state,checked-multiply(item,2)))
ALCH
cp -n work/v1/sum.alch.computation.json work/v2/sum.alch.computation.json
! ./node_modules/.bin/alchlang computation check "$PWD/work/v2/sum.alch"
mv -n work/v2/sum.alch.computation.json work/v2/sum.alch.computation.stale.json
```

The deliberately stale check reports `COMPUTATION_BINDING_SOURCE`. Updating only
its global source hash would still leave the declaration meaning/text hash stale
and reject. Preserve the rejected bytes and draft a new proposal from version 2:

```sh
node node_modules/@cyberalchemy/alchlang/examples/computation/draft-companion.mjs \
  --source "$PWD/work/v2/sum.alch" \
  --out "$PWD/work/v2/sum.alch.computation.candidate.json"
cat work/v2/sum.alch
cat work/v2/sum.alch.computation.candidate.json
```

Review the changed meaning and reducer together, then adopt the selected proposal.
The old generated artifacts also reject against the new source. Generate new ones:

```sh
cp -n work/v2/sum.alch.computation.candidate.json work/v2/sum.alch.computation.json
./node_modules/.bin/alchlang computation check "$PWD/work/v2/sum.alch"
! ./node_modules/.bin/alchlang computation verify "$PWD/work/v2/sum.alch" \
  --out "$PWD/generated-sum-v1"
./node_modules/.bin/alchlang computation build "$PWD/work/v2/sum.alch" \
  --out "$PWD/generated-sum-v2"
./node_modules/.bin/alchlang computation verify "$PWD/work/v2/sum.alch" \
  --out "$PWD/generated-sum-v2"
./node_modules/.bin/alchlang computation run "$PWD/work/v2/sum.alch" \
  --input "$PWD/work/v2/input.json"
mkdir native-sum-v2
printf '{"type":"module"}\n' > native-sum-v2/package.json
./node_modules/.bin/tsc --ignoreConfig generated-sum-v2/computation.ts --target ES2022 \
  --module NodeNext --moduleResolution NodeNext --strict --skipLibCheck \
  --lib ES2022,DOM --outDir native-sum-v2
node --input-type=module <<'JS'
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runComputationJson} from './native-sum-v2/computation.js';
const result = runComputationJson(readFileSync('./work/v2/input.json','utf8'));
assert.equal(result.ok, true);
assert.equal(result.value, '10');
console.log(result);
JS
./node_modules/.bin/alchlang computation verify "$PWD/work/v2/sum.alch" \
  --out "$PWD/generated-sum-v2"
```

The same input now gives `"10"`. Version 1 still gives `"5"`; neither source nor
artifact directory was overwritten. The shipped
[count-two source](../examples/computation/summary-count-two.alch) similarly changes
`checked-add(state.count,1)` to `checked-add(state.count,2)` and “Add one” to “Add two”,
producing `{count:"4",total:"1250"}` with the original summary input. For your own
summary edit, use the same helper/review/adopt process rather than guessing hashes.

### Companion identities in the library

`lowerComputationSource(source, companion, options)` returns `companion_text`,
`companion_identity_kind` and `companion_sha256`. Text entry preserves the exact
original UTF-8 text as `raw-utf8`; object entry returns compact sorted JSON as
`canonical-json`, with no trailing newline. The digest always describes the
returned text. Save those exact bytes when materializing an object companion.
`serializeComputationCompanion(value)` exposes the same safe object serialization
with standalone format checks; full source/declaration agreement remains lowering's
job. Formatting changes create a different file identity even when meaning is
unchanged. Outputs built with the predecessor normalized library hash require
regeneration into a new directory; verification has no alternate-hash fallback.

Direct Craft uses a `domainspec.computation-source/v1-candidate` JSON envelope.
It contains `profile application-v1`, explicit
`domainspec.computation/v1-candidate` capability, a Calculation owner,
owner reference and meaning, exact declaration meanings/body hashes, and the
normalized contract. The public `bindComputationSource(contract, options)` helper
constructs that envelope from explicitly supplied meanings; it does not approve
them. `unwrapComputationSource` validates it. Bare full-computation IR is rejected
by the artifact CLI. Earlier collection-only IR stages remain explicit legacy
reference inputs. See the shipped direct examples for exact envelope bytes.

## Effects and practical application work

Keep computations pure. To expose an API, declare the public Interface and bind
an inbound transport adapter to your supplied implementation. To call another
API, bind an outbound adapter and explicit request/response mappings. See
[API connections](API-CONNECTIONS.md) for both tested examples and
[the working workflow](WORKFLOW.md) for the application journey.

## Open Questions

This candidate covers the selected standalone TypeScript computation path.
Whole-application graph integration of the new expression contract, broader
record/container shapes, other generated languages, locale collation and
universal proof claims require separate successors and evidence. Local hosting,
TDE, EVF and durable recovery expansion remain deferred. Public publication
remains an owner decision; local tests do not establish a deployed service.
