# Standalone pure computation examples

These direct Craft source envelopes use `domainspec.computation-source/v1-candidate`,
with explicit Calculation ownership, root meaning, declaration meanings and
current body fingerprints. Their normalized contracts use the additive candidate profile
`domainspec.iteration-expression/v1-candidate` with
`ordered-metered-v1-candidate`. They do not change frozen scalar profiles or
private catalog authority. [cases.json](cases.json) contains independent expected
values; each `*.input.json` supplies canonical decimal-string UInt64 values.
The example author supplies every meaning explicitly. `bindComputationSource`
checks declaration closure and current body identities; meaning review remains a
separate responsibility.

After installing the Craft package and normal TypeScript 6.0.3 in a consumer,
run the packaged example:

```bash
node node_modules/@domainspec-v2/cli/examples/computation/run-example.mjs \
  --tsc "$PWD/node_modules/typescript/bin/tsc" \
  --out "$PWD/computation-example-run"
```

The output directory must be new. The runner invokes the actual Craft CLI,
compiles standalone generated TypeScript with the consumer compiler, invokes
`runComputation` and `runComputationJson`, checks the fixed values and reference
parity, then changes the authored count increment from 1 to 2 and regenerates.
The edit first fails as a stale declaration fingerprint, then uses the public
`bindComputationSource` helper with explicit updated meanings. The runner also
checks rejection of bare full-stage IR, changed-source no-overwrite and generated-source tamper rejection.
Generated programs have no npm runtime dependency, evaluator import, authored
native callback, external effect, or runtime AST dispatch.

For one contract, the individual commands are:

```bash
node node_modules/@domainspec-v2/cli/dist/cli/main.js computation check "$PWD/node_modules/@domainspec-v2/cli/examples/computation/record-reducer.craft.json"
node node_modules/@domainspec-v2/cli/dist/cli/main.js computation build "$PWD/node_modules/@domainspec-v2/cli/examples/computation/record-reducer.craft.json" --out "$PWD/generated-summary"
node node_modules/@domainspec-v2/cli/dist/cli/main.js computation verify "$PWD/node_modules/@domainspec-v2/cli/examples/computation/record-reducer.craft.json" --out "$PWD/generated-summary"
node node_modules/@domainspec-v2/cli/dist/cli/main.js computation run "$PWD/node_modules/@domainspec-v2/cli/examples/computation/record-reducer.craft.json" --input "$PWD/node_modules/@domainspec-v2/cli/examples/computation/record-reducer.input.json"
```

`run` invokes the reference evaluator. Native execution requires compiling
`generated-summary/computation.ts` and importing its exports. Its result is
`{ok:true,value,fuel_used}` or `{ok:false,error,fuel_used}`; failures expose stable
`code`, normalized `expression_path`, logical `index_path`, and `call_path`.
For evidence of the chosen pure Policy branch, use `runComputationObserved` or
`runComputationJsonObserved`. Their wrapper contains the unchanged `result`, a
bounded `policy_decisions` array and `observation_status`. Each decision identifies
the Policy, branch, Calculation, logical paths and whether callee invocation was
entered after argument evaluation. The engine retains at most 100 decisions and
65536 UTF-8 JSON bytes; truncation changes the observation status while preserving
the normal computation value/error and logical fuel. The packaged runner compares
these observed APIs against the independent reference and checks the named
Policy's fixed selected branch and invoked Calculation.

UInt64 inputs and successful values use decimal strings. Internal arithmetic is
checked bigint, and repeated/condition computations share one logical fuel
account.

| Contract | Expected native behavior |
| --- | --- |
| `record-reducer` | Filter completes, map extracts amounts, ordered fold calls a named Calculation; `{count:"2",total:"1250"}` |
| `indexed-fold` | Original ordinals 0, 1, 2 sum to `"3"` |
| `repeat` | Three explicit steps return `"6"` |
| `range` | Half-open start/end/step produces `["2","4","6"]` |
| `while`, `until` | Final guard test establishes `"3"` within the explicit cap |
| `named-policy` | First matching named Rule selects a pure Calculation using a named Mapping; `"7"` |
| `sort-natural`, `sort-lexical` | Numeric first key, qualified string second key, stable duplicate order |
| `state-machine` | Pure named StateMachine returns a tagged transition and explicit intents |
| `matching` | First matching data branch returns `"9"` and skips an unused division failure |

Policy and StateMachine descriptors belong to matching named pure declarations.
Closed named calls require exact declared parameter/result types and an acyclic
body graph. Sorting explicitly supports numeric, Unicode scalar lexical, and
ASCII digit-run natural comparators; locale mode rejects as unsupported. Natural
numeric runs compare exact significant digits and then original run length;
there is no host locale default. The StateMachine result also carries `machine`, `branch` and `reason`: matched
transitions report `transition:<ordinal>` and `matched`; unmatched branches report
`otherwise` with `no-match-stay` or `no-match-reject`. No operation executes an intent.

## Open Questions

These remain candidate implementation surfaces. Broader target languages,
locale-qualified comparators, optimization equivalence, and machine-checked
proofs require separate qualification. Repository-authority promotion and
runtime hosting remain outside this example. User-facing candidate boundaries and ongoing questions are documented in the
[shipped user guide](../../USER-GUIDE.md). The retained repository research source
is `research/craft-alchlang-formal-iteration-2026-10-13/DESIGN.md`; it is not a
packaged dependency or a shipped documentation link.
