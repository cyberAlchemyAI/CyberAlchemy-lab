# Exact UInt64 TypeScript realization v1

Candidate opt-in realization: `domainspec.typescript-exact-uint64/v1`.
The package remains version 1.0.0; a consumer must check the public
EXACT_UINT64_PROFILE capability as well as the package/API version. Existing
builds without the explicit option retain their generator selection and behavior.

```bash
domainspec-v2 build /absolute/project --language typescript --target-root /absolute/new-output --realization-profile domainspec.typescript-exact-uint64/v1
domainspec-v2 verify /absolute/project --language typescript --target-root /absolute/new-output --realization-profile domainspec.typescript-exact-uint64/v1
```

The project-build receipt records the profile and binds exact artifact hashes.
Verification using a different profile fails. The profile rejects other languages.
Single-node instantiation receipts and observe-target conformance do not support
this profile; use whole-project build/verify and separate application parity tests.
A compiled graph certificate alone does not select a numeric realization.

## Realization contract

Typed Calculation v1 produces bigint over [0, 18446744073709551615]. Inputs accept
bigint, safe integer Numbers or canonical unsigned decimal strings. Unsafe Numbers,
noncanonical strings and out-of-range values reject. Arithmetic checks overflow,
underflow, division by zero and inexact division. Floor/ceil use integer arithmetic.
Every declared calculation input is checked. Typed contract JSON still uses safe
numeric literals. Full UInt64 constants may be authored as exact arithmetic over
safe leaves; no unsafe JSON Number is accepted.

Typed Query v1 evaluates supplied rows, requires declared parameters and filter
fields, preserves tie order, limits after filtering and sorting, and requires
projected values. The existing contract supports one sort key. Typed Mapping
preserves copied values and authored defaults, enforcing totality at evaluation.
Typed Policy preserves ordered cases and fallback without invoking a target.
Predicates retain strict equality and native scalar ordering; callers must satisfy
their declared scalar input contract. Query/Mapping numeric values are not coerced.
Generated scalar UInt64 record properties accept bigint or number at the TypeScript
level; callers must reject unsafe/out-of-range Numbers at their input boundary.

The renderer handles scalar typed records and thin Query/Calculation/Mapping/Policy
contracts. Other structural nodes retain existing generation. It does not claim
new effect execution, generic operation conformance, invariant enforcement, or
support for arbitrary nested record contracts. Generated entry function names use
an evaluate_ prefix; consumers should bind through the artifact's exported function.

## Declarative project compositions

Opt-in `domainspec.project/v2` adds exactly one composition ID in `compositions`.
Its source is `compositions/<id>.json` with schema
`domainspec.project-composition/v1`. It carries `id`, `source_text`, `contract`,
`core_bindings`, `model`, `bindings`, and `ontology`. The current boundary profile
is Node HTTP with the Alch derived-ontology scaffold v1.

The loader includes composition bytes in the source manifest. Compilation checks
core selectors, property identities/types, calculation signatures, behavior,
schemas, boundary references and ontology dependency closure. The graph includes
compiled compositions; its certificate reports their validation independently of
the existing core meta-type obligations. Standard `build` and `verify` emit and
check the seven composition artifacts under `compositions/<id>/`.

Node HTTP requires TypeScript and the exact UInt64 realization profile. The opt-in rust-http/rust>=1.94 boundary instead selects native Rust with no realization-profile argument; its Cargo package calls the existing checked-u64 Rust calculation modules. Legacy project
instantiation and checked assurance interchange reject compositions explicitly.
The original source is digest-bound provenance, not an independent source-language
proof. This extension does not add an admitted meta-type or formal Lean proof.

## Open questions

Product approval, broader record shapes, multi-key query ordering and standalone
conformance receipts are outside this candidate. No release or deployment decision
is represented by the profile option or its receipt.
