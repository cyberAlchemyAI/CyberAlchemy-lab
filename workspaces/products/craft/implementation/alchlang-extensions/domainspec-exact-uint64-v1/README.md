# Exact UInt64 commerce candidate

Implemented and locally tested. The unchanged `implementation/examples/typed-backend.alch`
now compiles under `domainspec-1.0.0-exact-uint64-v1` into a nine-node DomainSpec
project and executable TypeScript. No product approval or publication is recorded.

## What changed

DomainSpec has a separately selected realization contract,
`domainspec.typescript-exact-uint64/v1`, exposed by its public API and accepted by
whole-project build/verify. The receipt binds this selection. Default generation
is unchanged; the old application trial still verifies the old profile's rejection.
Single-node instantiation/conformance receipts explicitly reject the new profile.

AlchLang adds integer records, queries, parameterized UInt64 arithmetic, numeric
mappings and threshold policies under the new sidecar/CLI profile. It lowers the
complete existing commerce source without deleting declarations or narrowing
calculation arithmetic. Full UInt64 literals use exact base-2^32 decomposition
with safe JSON literal leaves; the trace identifies this derivation.

The checked generated entry exports evaluateQuery, evaluateCalculation,
evaluateMapping and selectPolicy. Selection returns a source identifier and never
invokes the target. Query/Mapping values preserve their supplied representation.

The definitions and ontology JSON files are prototype navigation scaffolds. Their
product/business antecedents are ALCH-CD-PRODUCT-VIEW and ALCH-CD-BUSINESS-VIEW;
this implementation does not promote either view or claim measured customer value.
See PLAN.md for the construction stages and operational separation.

## Use

First rebuild the bound DomainSpec CLI from the repository root:

```bash
npm --prefix projects/domainspec-v2/impl/cli run build
```

From the AlchLang implementation directory:

```bash
npm run build
node dist/cli.js check examples/typed-backend.alch --profile domainspec-1.0.0-exact-uint64-v1 --bindings ../extensions/domainspec-exact-uint64-v1/typed-commerce.bindings.json
node dist/cli.js build examples/typed-backend.alch --backend domainspec --language typescript --profile domainspec-1.0.0-exact-uint64-v1 --bindings ../extensions/domainspec-exact-uint64-v1/typed-commerce.bindings.json --out /tmp/commerce-exact
```

The destination must be new. The sidecar must match both source bytes and selected
profile. A 1.0.0 package without the exact-realization capability is rejected.
Compile the generated domain.ts with its generated imports before application use.

## Evidence

- AlchLang: typecheck and build PASS; full suite 89 passed, zero failed.
- DomainSpec: typecheck and build PASS; 60 affected generation/CLI/vertical tests
  passed; 21 final receipt/observation/generation checks passed; 25 contract tests
  passed. These sets overlap and are not a single aggregate test count.
- Documentation frontend: 32 tests and production build PASS. Firefox checks pass
  at 1440px and 390px, with no page errors or horizontal overflow.
- Executable parity covers query filter/order/ties/limit/projection, explicit
  parameters, missing fields, numeric mapping defaults, policy selection, all
  calculation rounding modes and UInt64 boundaries/failures.
- Profile mismatch, missing capability, unsupported language, overwrite attempts
  and unsafe Numbers reject. Repeated exact builds are byte-identical.
- The actual generated receipt validates against its JSON schema; changing its
  language to Python while retaining the profile fails schema validation.

`evidence/smoke-final.json` and `evidence/commerce-build-final/` are the current
built-CLI application result. The earlier `smoke.json` and `commerce-build/` are
intermediate evidence retained outside the final candidate's selected file scope.
`candidate.json` records the exact selected files and compiler dependencies.
`evidence/alchlang-tests.log` and the two DomainSpec test logs preserve the runs.

The former failure now succeeds: amount 9007199254740991 plus five produces
9007199254740996n. This is tested implementation evidence, not universal formal
proof, runtime effect authorization, ontology admission or product approval.

## Limits and open questions

Calculation inputs accept bigint, safe Numbers or canonical unsigned decimal
strings and return bigint. Integer record and policy inputs accept bigint or
nonnegative safe Numbers within UInt64. Predicate equality retains source strict
equality across number/bigint representations. No unsafe Number is rounded.

Queries support one sort key. Multiple keys and overlapping row/parameter names
reject. Numeric predicate/default literals must be safe integers. Numeric general
Rules, decimal arithmetic, effects and remaining backend kinds are not added.
Structural calculation-support Operations do not claim executable application
behavior or invariant enforcement. Full-range values should cross JSON boundaries
through an explicit encoding because JSON.stringify does not accept bigint.

Construction frontier: tested candidate ready for product review. Product approval
is unrecorded. Repository maintainer owns deferred packaging/publication/deployment;
these have no affected construction stage or blocking role in this local result.
