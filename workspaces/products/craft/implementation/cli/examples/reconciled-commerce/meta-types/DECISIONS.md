# Rules, Calculations, Queries and Policies

This example uses the existing `domainspec.reconciled-typescript/v1-candidate`
profile and `domainspec.typescript-exact-uint64/v1` value representation. The
source is the packaged `../source` project, compiled with
`../selections/typescript.json`. These are Craft source contracts; this example
does not invent equivalent AlchLang syntax or promise every AlchLang lowering
path supports the same features.

`runDecisions({generatedRoot, exampleRoot})` in `decisions.mjs` invokes the
actual emitted JavaScript functions. `generatedRoot` is the native TypeScript
compiler output containing `commerce-corpus/features`; `exampleRoot` is this
example's parent directory containing `values.json`. Run it through the
all-meta-type runner so that the source is built, verified and natively compiled
before the witness executes. The witness imports no development compiler.

## Rule

`commerce:allowed` means an explicitly supplied UInt64 value is below 100.
`ruleAllowed({value: "99"})` returns true; value `"100"` returns false.
`commerce:positive` checks the strictly positive boundary. Wrong, missing or
extra arguments reject as `RULE_INPUT`. The Rule contract is
`domainspec.typed-rule/v2`; it is executable behavior, not a formal proof.
An unknown expression operator must be rejected by source compilation; the
integration qualification owns that negative source check.

The separate AlchLang compatibility normalizer now rejects numeric containment,
non-list `in` containers and non-string substring operands rather than silently
returning false. String containment and list membership retain their true/false
behavior. Lists in this older carrier have no declared element type; these
checks establish container shape, not a stronger homogeneous element contract.

## Calculation

`commerce:total` subtracts `adjustment` from `gross`; `billing:total` adds them.
The new `commerce:product` multiplies those parameters. `quotient-reject`,
`quotient-floor` and `quotient-ceil` divide them with explicitly different
rounding. All use `domainspec.typed-calculation/v2` and return exact `bigint`.
Inputs accept canonical decimal strings, UInt64 `bigint`, or safe integral
JavaScript numbers. Numbers outside the safe integer range are rejected; use
strings or `bigint` for large values.

For example, subtracting `"1"` from `"9007199254740993"` returns
`9007199254740992n`. Dividing seven by two returns three with floor, four with
ceil, or throws `CALCULATION_INEXACT` with reject. Overflow, underflow and a
zero divisor throw explicit errors. The witness also checks full-width UInt64
values, malformed inputs and unchanged input objects. Maps, filters, folds and
loops inside Calculations remain the separately designed computation successor.

## Query

`commerce:find` projects order and billing-customer identities from supplied
rows and returns a list. `find-optional` filters by `id >= min_id` and returns
null or one projected row; several matching rows throw `QUERY_CARDINALITY`.
It has no limit: optional cardinality must not hide extra matches.

`find-ranked-asc` and `find-ranked-desc` use the same inline filter, order by the
single UInt64 `billing_customer_id` field, then return at most two rows.
On this TypeScript profile equal sort keys preserve the supplied row order;
the witness checks ties before truncation. Projected identities are `bigint`.
The caller's original rows remain unchanged. No database or persistence provider
is accessed. The v2 Query contract supports inline predicates, not named Rule
calls in the filter. Multi-key/custom comparator sorting remains separate work.

## Policy

`commerce:choose-calculation` takes `gate` and `amount`. Its first case calls the
named `allowed` Rule with `gate` and selects `commerce:total`; its second case
calls `positive` with `amount` and selects `commerce:product`. The fallback is
`commerce:quotient-floor`. With both cases true the first wins.

`policyChooseCalculation({gate: "1", amount: "1"})` returns the string
`"commerce:total"`. It does not execute the Calculation. A caller explicitly
dispatches that selector to `calculateTotal({gross: "100", adjustment: "7"})`
to obtain `93n`. The witness checks that arithmetic errors arise only during
that separate invocation. No calculation-to-policy dispatch syntax or implicit
effects are introduced.

## Evidence boundary

The compatibility membership tests are development tests. The runtime witness
must pass against the exact packaged and installed successor before installed
qualification can be claimed. Its finite cases are evidence for the selected
TypeScript profile, not every target, every expression or a proof of purity.
Publication is a separate decision. Local hosting, TDE and EVF remain deferred.

## Open Questions

Current integrated development, installed-package and source-negative results
are owned by the execution record and the all-meta-type qualification receipt.
Named Rule filters, richer sorting and collection computation are owned by the
separate successor tasks; this example does not redefine those contracts.
