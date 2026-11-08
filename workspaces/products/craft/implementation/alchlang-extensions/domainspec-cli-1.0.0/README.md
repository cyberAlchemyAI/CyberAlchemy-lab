# AlchLang / DomainSpec 1.0.0 integration candidate

Owner: AlchLang / Language Project owner. Status: construction candidate.
Authority effect: none. This change does not refresh historical approvals.

## Prototype definition and navigation scaffold

A compiler binding selects the exact `@domainspec-v2/cli@1.0.0` package and its
public ESM entry, checks the built API and CLI version, and consumes the compiler's
own graph and certificate. The historical `domainspec-v2` path and package name
are not a semantic version. AlchLang's carrier-v2 is a different format version.

Unregistered navigation scaffold: AlchLang compiler adapter -> uses -> DomainSpec
1.0.0 public compiler -> validates -> authored DomainSpec project -> produces ->
compiled graph and certificate. No registered ontology records are newly consumed
by the adapter. The existing authored project under ../../domainspec supplies its
own selected definitions and semantics; the upstream compiler validates that closure.
The dependency set is that exact project tree and the selected public CLI package,
not an ambient ontology epoch.

## Product and construction chain

Product outcome: AlchLang users and its construction scripts can invoke the
selected compiler without importing private loader implementation modules or
mistaking a stale build for version 1.0.0.

Prototype meaning and scaffold above -> existing AlchLang capability and authored
DomainSpec compiler project -> version-checked public adapter -> compiler graph and
certificate -> focused product tests. The CLI delegates supported commands to the
public `runCli` API; model scripts use public `compileProject`, which validates graph
obligations and produces a compiler-bound certificate.

Product-construction frontier: public adapter and current integration tests.
Runnable work: compile the upstream canonical project fixture, deterministic replay,
certificate comparison, stale/missing/wrong-version failures and CLI error propagation.
Causal construction blockers: the adapter is testable with a fresh 1.0.0 build.
The existing 50-node/42-edge AlchLang project cannot yet compile: its untyped
Mapping omits direction/totality/field mappings and targets a Value Object;
its Policy omits a default strategy. DomainSpec 1.0.0 requires more explicit
semantics and limits untyped Mapping endpoints to Entity or Interface.
The real project rejection is tested and remains a BLOCK, not compilation PASS.

Operational support: local upstream build (developer; implementation-test stage)
is required because the preexisting dist was stale. Publication, global install,
activation and deployment (repository/product operators; later operational stages)
are deferred and do not block local compiler tests. Historical acceptance and
conformance receipts remain bound to their original bytes and are not renewed.

## Exact implementation and validation

Implementation files: ../../implementation/src/domainspec-cli.ts, src/cli.ts,
src/index.ts, package.json and README.md; ../../execution/scripts/compile-system-model.ts
and validate-domainspec-source.ts. The compiler's source package is read-only;
its ignored dist output is rebuilt using its existing build checks.

Tests: ../../implementation/test/domainspec-cli.test.ts plus the existing AlchLang
package tests and typecheck. `compile-system-model.ts --determinism` will check replay without overwriting
generated projections or evidence once the source migration blocker is resolved. A passing test is evidence
for this candidate, not product approval or operational authority.

## Validation observed on 2026-09-05

- DomainSpec 1.0.0 build: PASS (catalog, relationships, integration profile and tsc).
- AlchLang typecheck and build: PASS.
- AlchLang package tests: PASS, 76/76, including eight new bridge tests.
- Rebuilt AlchLang `domainspec --version`: `1.0.0`.
- Existing backend-types.alch check: PASS.
- Current authored AlchLang project compilation: BLOCK, `MTCLI_MAPPING_DIRECTION`
  at `/specs/typed-backend/nodes/typed-mapping.json/body/direction`.
- Separate read-only body audit: 50 nodes checked, two failures (Mapping direction
  and `MTCLI_POLICY_STRATEGY` for Policy default_strategy). This diagnostic used
  the current compiler's body decoder; production integration uses only public API.
- Complete graph closure and projection replay: not_evaluable until source migration.
- An accidentally workspace-wide typecheck failed on unrelated missing
  `@opentelemetry/api`; the focused package checks above passed.

No source migration, generated evidence refresh, acceptance or publication was
performed. Package/entry digests in adapter bindings identify those two files;
they are not a complete package inventory or release provenance certificate.

## Open questions

Should a subsequent `.alch` lowering layer replace local TypeScript generation
with DomainSpec 1.0.0 build/verify? This bridge accepts authored DomainSpec projects;
it does not reinterpret a carrier or local AlchLang graph as a DomainSpec project.
Runtime adapters and external effects need their existing explicit bindings.

The source migration decision must establish whether the generic typed-mapping
node describes a compiler contract or a concrete executable transformation.
Its current source/target declarations do not specify field correspondence or
an allowed Stable 1.0 Mapping endpoint. The Policy needs an explicit default
and decision semantics. Supplying placeholder values would change meaning merely
to satisfy validation, so these source bytes remain unchanged.
