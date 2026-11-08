# Decide whether publication may proceed

This small pure example shows a reusable eligibility decision without introducing another Policy language. The business author declares the reason, typed result, Rule, Calculations, Policy and Operation in [publication.alch](publication.alch). Craft generates the Operation's control flow from that model.

The decision is inspectable as an ordinary Policy result. `enforce` is the explicit point where an Operation consumes it: `Allow` continues, while `Reject` propagates the declared `approval-needed` code. The first matching rejection wins.

## Files and use

- [publication.alch](publication.alch): complete small business module.
- [profile.json](profile.json): existing Node bounded-value profile with the explicit `operation-policy-enforcement` capability appended.
- [contracts/bounds.json](contracts/bounds.json): finite existing computation limits.
- [Authoring guide](../../docs/POLICY-ENFORCEMENT.md): why the pattern exists, how its parts relate and what its limits mean.

Using a paired working CLI that supports the capability, run from this directory with a new output directory:

```sh
alchlang-generic generate \
  --source publication.alch \
  --profile profile.json \
  --operation Publications.Publish \
  --out /absolute/path/to/new-publication-output \
  --accept-local-review example-owner
```

Generation creates code; it does not start a listener or publish a document. The frozen public release is unchanged and is not asserted to support the new capability.

The generated `operation.mjs` exports `evaluate`. It receives UTF-8 JSON bytes:

```js
const result = evaluate(new TextEncoder().encode(JSON.stringify({approved: false})));
if (result.ok) console.log(new TextDecoder().decode(result.wire));
```

The decoded value is:

```json
{"tag":"Rejected","fields":{"code":"approval-needed"}}
```

With `approved: true`, it returns `{"tag":"Returned","fields":{"value":true}}`. Evaluation faults have the existing error channel; they are not converted to business rejection.

## Meaning and verification scope

This example deliberately accepts a Boolean input to demonstrate a pure language mechanism. It is not a protected approval system. A real publication application must obtain trustworthy facts and authorization through its original owners; `Allow` does not grant permission.

The focused `test/generic/policy-enforcement-example.test.ts` generates this actual sample through the original public owner and compares both generated outcomes and fuel accounting against the original reference evaluator. Installed CLI qualification and the complete selected result belong to the final implementation proof, separately from this local example check.

## Open Questions

Supported scope and deferred extensions are owned by [the guide](../../docs/POLICY-ENFORCEMENT.md#open-questions). Local hosting, TDE, EVF, deployment and publication remain deferred. No real provider/model qualification is implied.
