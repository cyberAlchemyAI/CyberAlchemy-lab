# Installed AlchLang starter preview

This runner copies the installed delivery example and companion into a new caller-owned directory, checks and builds with `domainspec-1.0.0`, verifies the generated inner Craft project, compiles emitted TypeScript, and calls the actual generated exports. Run it from a consumer with both exact candidate archives already installed, plus Node 26.8.1/npm 11.19.0/TypeScript 6.0.3/Node types 26.4.0:

```bash
node node_modules/@cyberalchemy/alchlang/examples/cli-preview/run.mjs --out "$run_root/alch-preview"
```

`$run_root` is an existing absolute caller-owned directory; `alch-preview` must be absent. Use a new output for every run. The packaged `package.json` and `package-lock.json` pin native consumer development dependencies; installation of the two candidate archives is explicit and separate. No registry publication or public acquisition is implied here. The candidate uses [Apache License 2.0](../../LICENSE) (SPDX: `Apache-2.0`); support contact: [hello@cyberalchemize.com](mailto:hello@cyberalchemize.com).

The consumer uses wrapper `evaluateMapping` and `selectPolicy`, plus generated `urgentRequired`, `expressFee`, `priorityFee`, and `standardFee` functions. It observes a total mapping to `{messageId:"order-42",currency:"GBP"}`, an empty partial mapping, Rule true/false, and selected targets ExpressFee/PriorityFee/StandardFee with fees 1000/750/500. Policy selects an ID; the consumer explicitly wires that ID to its generated function.

The runner then edits only the copied StandardFee expression from 500 to 600. The stale companion rejects check and build with `DS_SOURCE_DRIFT`. Its synthetic meaning review updates StandardFee's meaning and the exact final source SHA, asserts that every unrelated binding is preserved, and builds a second output that produces 600. This example review has no authority effect; a digest establishes byte currentness.

The CommonJS compiler configuration and `{ "type": "commonjs" }` in each JavaScript output are explicit module-envelope glue. All generated TypeScript files are compiled with the consumer's actual pinned `tsc` bin. The runner clears the explicit Craft override and records the resolved compiler binding in the consumer's own node_modules. Package bytes are checked unchanged before and after the journey.

`journey.json` retains exact commands, outputs, tools, roots, source identities, native observations, and controls. Negative commands must leave the run directory byte inventory unchanged: incompatible Mapping input, missing/wrong Policy Bool input, missing companion (`ENOENT`), unsupported profile or language (`DS_PROFILE_UNSUPPORTED`), and existing build destination (`DS_OUTPUT_EXISTS`). Tamper verification changes a separate copied generated target and expects exactly its StandardFee artifact check to fail. Both successful generated targets are retained for inspection.

## Open Questions

Public destination, publication authorization, and anonymous reacquisition remain owner decisions outside this installed local preview.
