# Existing-application trial and product review

The tutorial, language reference and documentation frontend now explain the
DomainSpec 1.0.0 target, its sidecar, commands, output contract and limits.
The maintained typed-commerce application was tested unchanged. Its local
generated application passes; migration to the current target is blocked.
This is a repository application model, not a deployed customer application.

## Reproduce

From `implementation/`, using the repository Node environment:

```bash
../../../../../../../projects/domainspec-v2/impl/node_modules/.bin/tsx ../extensions/domainspec-application-trial-v1/trial.ts
```

An optional `--out /absolute/new-result.json` writes a new receipt without
replacing an existing one. `result.json` records this run. The regression is
included in `npm test` as `test/domainspec-application-trial.test.ts`.

The trial executes the existing local generated TypeScript for queries,
calculations, mappings and policy selection and compares it with the existing
AlchLang evaluator. It covers equal-sort-key stability, filtering, projection,
limit, policy threshold/fallback, numeric boundaries and source preservation.

The explicit candidate sidecar covers the unchanged application's declarations.
DomainSpec-profile checking rejects `queries` with `DS_UNSUPPORTED` before
producing application output. Additional source-visible gaps are integer record
fields, input arithmetic and ordered numeric predicates. The regression expects
rejection today; it must be deliberately revised when migration becomes supported.
A passing regression is not a passing application migration.

## Current checks

- AlchLang typecheck: PASS; package tests: 85 passed, zero failed.
- Documentation frontend: 32 tests passed; TypeScript and Vite build passed.
- Firefox smoke: target guide visible, command and limit text present, no page
  errors or horizontal overflow at 1440px and 390px; see `frontend-smoke.json`.
- Complete commerce migration: BLOCKED, as recorded in `result.json`.

## Numeric incompatibility

A separate, explicitly authored DomainSpec probe models `amount + 5`. It is
compiled by the public 1.0.0 API, built by the public CLI and typechecked before
its generated function is executed. This probe is not claimed as application
lowering and has no application output or acceptance status.

| Input amount | AlchLang calculation | DomainSpec TypeScript probe |
| --- | --- | --- |
| 140 | 145n | 145 |
| 9007199254740991 | 9007199254740996n | Calculation overflow |

AlchLang permits full UInt64 values using bigint, safe numbers or decimal strings.
The bound TypeScript calculation generator uses Number.isSafeInteger on inputs
and arithmetic results. Merely translating its expression would change behavior.
The original application and the first lowering profile have not been weakened.

## Product-definition review

Exact dependencies: `ALCH-CD-PRODUCT-VIEW` and `ALCH-CD-BUSINESS-VIEW`, all nodes
and relations in their two JSON files under
`definitions/compiler-domain-separation/v1/`. `review.json` maps every selected
node to an assessment and pins both source files. This is an implementation
assessment, not ontology admission or a human product approval.

The bounded compiler capability has passing determinism, traceability and target
parity evidence from the first candidate. The existing-application trial shows
that the broader modeling promise is only partially realized in this target.
Unsupported meaning remains visible. Ownership and business outcomes are not
established by tests. No customer-value, adoption or operational-authority claim
is made. The original candidate evidence remains historical; `candidate.json`
identifies this documentation and trial increment without rewriting it.

## Construction and operational lanes

Product construction frontier: documentation complete; unchanged-application
baseline tested; migration blocked at target compatibility. Runnable next work is
the numeric and query contract prototype in `NEXT-PROFILE.md`. Integer record
representation, arithmetic and numeric policy predicates share the numeric
contract prerequisite. Query semantics can be specified and tested independently.

The exact blocker for complete commerce migration is target semantic coverage,
including a demonstrated numeric mismatch. It is not packaging, repository
bookkeeping or ambient ontology drift. Product approval remains unrecorded.

Operational support owner: repository maintainer. The bound compiler and local
documentation build are available. Publication, registry packaging and deployment
have no affected construction stage here and remain deferred. No external effects
were performed. The temporary browser server and probe directories are closed.
