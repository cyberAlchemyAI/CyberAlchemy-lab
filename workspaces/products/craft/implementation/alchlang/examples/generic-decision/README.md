# A generated decision with collections and a state proposal

The business model combines a Rule, Operation, Mapping, Calculations, Policy,
validated values and a State Machine. All business behavior is in `business.alch`.
The example driver only invokes the generated module and checks its results.
Use the tested Linux x64 / Node 26.8.1 tool pair.

After installing both downloaded CLI archives into a new npm project:

```sh
cp -R node_modules/@cyberalchemy/alchlang/examples/generic-decision/. .
npx --no-install alchlang-generic generate --source business.alch --profile profile.json --operation ReviewDesk.ApproveRequest --out generated --accept-local-review my-decision > generation.json
node exercise.mjs
```

| Declared concept | What it contributes |
|---|---|
| `IsVerified` Rule | Checks `request.verified`; the Operation rejects an unverified request. |
| `EligibleItems` Calculation | Filters the original list using `item.eligible`. |
| `Scores` Calculation | Maps each eligible item to its declared doubled amount. |
| `Total` Calculation | Folds those scores from an explicit zero accumulator. |
| `SelectTotal` Policy | Chooses the priority Calculation or the ordinary total. |
| `Presentation` Calculation | Sorts amount descending, then label ascending in natural order, preserving equal-key occurrences. |
| `Approval` State Machine | Proposes a next state using the first matching transition and explicit fallback. |
| `ToDecision` Mapping | Assembles the typed output from those declared results. |
| `ApproveRequest` Operation | Applies the Rule and returns the Mapping. |

The supplied input produces scores `["4","8","8"]`, total `"20"`, and
presentation item IDs `["2","4","3"]`. Scores retain source occurrence order;
presentation has its own explicit sort. The repeated scores and labels remain
separate occurrences. The priority example changes the total to `"30"`.
UInt64 values use exact decimal strings in JSON.

The supplied Draft/Submit state proposes Approved with zero intents. Review/Cancel
keeps Review; `initial Draft` does not reset existing state. A proposal is returned
data. This pure profile performs no state storage or external effects.

`Label` has explicit text bounds and a finite pattern. `Item` requires a positive
amount. The exercise distinguishes validation errors, calculation overflow and
the Operation's declared business rejection. Formal claims are optional; this
project has none.

The profile supplies the selected capabilities and execution limits; the matching
bounds are already included. Generation also emits `business-graph.json`,
`system-graph.json` and `business-system-bridge.json` for inspection.

Edit the business model or input to explore different requirements. Regeneration
needs a new output directory; keep earlier outputs available:

```sh
npx --no-install alchlang-generic generate --source business.alch --profile profile.json --operation ReviewDesk.ApproveRequest --out generated-v2 --accept-local-review my-decision > generation-v2.json
node exercise.mjs generated-v2
```

The supplied exercise checks the original requirements, so update its expectations
when deliberately changing the business requirements. For protected APIs and
persistent applications, follow the installed generic application guide and
select a profile that admits those capabilities.

## Open Questions

Complete cumulative application qualification and general performance remain open.
Local hosting, TDE, EVF and publication remain deferred.
