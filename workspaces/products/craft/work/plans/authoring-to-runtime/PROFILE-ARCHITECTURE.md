# Shared Alch source-profile architecture

Date: 2026-09-20. Status: C01 bounded construction evidence.
Authority effect: none.

## Product grammar boundary

`application-v1` is the sole product-language profile for the
authoring-to-runtime plan. It selects the shared `parseDomainSource` scanner,
the normalized application model and bounded domain, FormalClaim, integration,
realization and runtime-profile capabilities. A profile never adds an alternate
meaning for an existing declaration.

`legacy-sfol-v1` is an explicit compatibility selection on the same scanner.
The historical no-profile default selects that compatibility record. It is not
the product grammar and cannot receive `application-v1` declarations.

The remaining shipped roots are registered as bounded capability adapters or
optional packages. They retain their existing package-local decoders and
outputs, but `product_language: false` prevents them from being treated as
alternate definitions of the coherent application language. Moving one into
the product denominator would require lowering its capability through the
shared normalized model and a separately reviewed compatibility change.

## Executable registry

`src/profile-architecture.ts` is the closed dispatch registry. The CLI invokes
`selectAlchSourceProfile` once per source and routes by the returned identity;
it no longer independently searches the file with one regular expression per
profile. The shared parser calls the same selector. Duplicate, malformed and
unregistered root profiles reject before semantic parsing, and each descriptor
limits its supported commands.

| Role | Profiles | Parser/model ownership | Product-language status |
| --- | --- | --- | --- |
| canonical product | `application-v1` | shared domain parser; normalized `application-v1` model | sole product grammar |
| compatibility | `legacy-sfol-v1`, including historical no-profile selection | shared domain parser; legacy carrier | compatibility only |
| capability adapters | `bound-application-v1`, `declarative-function-v1`, `event-function-v1`, `function-v1`, `module-configuration-v1`, `outbound-invocation-v1`, `query-iteration-v1`, `request-custody-v1`, `response-stream-v1`, `semantic-contract-v1`, `service-v1` | package-local adapter | excluded from the product-language denominator |
| extension-owned formats | `http-contract-v1`, `outbound-invocation-v2` | package-local extension adapter; no core CLI commands | excluded and rejected by the core CLI command boundary |
| Rust optional package | `event-execution-v1`, `semantic-host-v1` | package-local adapter; requires the Rust package | excluded; preserved optional capability |
| local-host optional package | `local-host-migration-v1`, `local-host-v1`, `ontology-host-v1` | package-local adapter; requires the local-host package | excluded; preserved optional capability |

Imported HTTP contracts and the inference-router v2 invocation format remain
owned by their extension adapters. They are registered so their identity is
not unknown, but expose no core CLI commands and cannot be selected as the
product grammar by the root CLI.

## Compatibility and hostile cases

The registry and shared-parser tests establish:

- exactly one `product_language` descriptor, `application-v1`;
- exact agreement between CLI selection and parser selection for application,
  explicit compatibility and historical-default sources;
- no duplicate profile identity or mutable descriptor/capability array;
- causal rejection of duplicate, malformed and unknown root profile claims;
- bounded Rust and local-host package identities without ambient fallback; and
- package-local adapters cannot enter `parseDomainSource` as a second product
  grammar.

Existing focused adapter tests remain regression evidence. The selector,
shared-parser, source-container and CLI command-boundary suite passed 18 of 18.
The selected adapter run passed 35 of 35 applicable tests; three
module-configuration tests were not evaluable because their pre-existing external
`implementation/agent-reasoning-engine/packages/module-port/alch-semantic-adapter.mjs`
dependency is absent in this checkout. That missing adapter is not caused or
repaired by C01 and does not authorize a checkout fallback.

The optional-package boundary, Rust event execution, ontology projection, state
migration and related semantic suites passed 48 of 48. A broader local-host
runtime run reached the existing provisioning currentness guard and rejected
with `SOURCE_DRIFT` for
`work-orchestration-implementation/runtime/Cargo.toml`; its dependent listener
cases were therefore not used as C01 evidence. C01 changes neither that runtime
source nor its manifest.

## Claim ceiling

This closes profile selection and ownership architecture, not C02–C06. It does
not prove thirteen-meta-type breadth, all FormalClaim consumers, generalized
modules/multiple entries, three-language parity or installed-package behavior.
It grants no publication, release, deployment or runtime authority.

## Open Questions

C02–C04 decide which currently package-local capabilities are re-expressed in
the shared application model. Promotion cannot occur by changing registry
metadata alone; it requires source grammar, normalized-model, lowering and
compatibility evidence.
