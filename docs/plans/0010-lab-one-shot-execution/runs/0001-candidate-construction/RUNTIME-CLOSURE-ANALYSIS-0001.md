# Runtime source closure and qualification evidence

Status: candidate implementation analysis, not a guard change.
Authority effect: none. Current frozen source: `interface/api-v71`.

## Inspected behavior

`Schemas.guard` reads every original schema input and every file in the selected
contract profile on each invocation. It also checks the original operation
catalog, captured authentication schema and protocol profile. The freeze producer
carries preceding profile rows forward, so current profiles include accumulated
historical implementation and qualification material.

`guard.verify` additionally verifies every source-manifest row with anchored
filesystem reads and exact bytes. Candidate selection/calculation use complete
entry and exit guards; each actual policy check still uses the real file and
clock. These checks remain unchanged in this increment.

The selected suite's actual process terminals retain wall time. That timing
qualifies only its own fixture and selected work, not production throughput or an
established cause for the historical Machine failure. The process was active when inspected; no
runtime profiling instrumentation or callback replacement was introduced.

## Bounded observations

API68 has 1,865 contract-profile file rows and 16,122 source-manifest rows.
API71 has 2,250 contract-profile rows and 16,513 source-manifest rows. These are
inspected manifest counts, not a map of executed runtime dependencies.

The API71 generated-output full selection passed five cases and eleven public
calls; its native test log reports 1,590.477 seconds. No equivalent earlier full
selection exists for a throughput comparison. This measurement does not establish
which guard or operation consumed that time.

## Recommended investigation

Before optimizing, map all actual runtime reads/imports, schema resources,
producer dependencies, source/project heads, original representation adapters
and independently selected evidence. Separate these dependencies from immutable
historical tests and qualification reports that are retained for final review.

A future candidate may declare two independently bound manifests:

- Execution closure: exact code, schemas, profile, provenance and source material
  required by the selected runtime. All relevant changes must still be detected
  at their required effect boundaries.
- Qualification closure: exact historical/current proofs, test producers, failed
  outcomes and review material supporting the package's readiness claims.

Keep every frozen predecessor. This proposal does not authorize deleting files,
shortening grants, extending clocks, replacing callbacks or skipping required
original checks. Material actively used as evidence by an operation belongs in
that operation's selected dependency closure even when it is a historical receipt.

Declare and test the new closure in a successor. Inject changes independently in
runtime code, schema resources, selected source, private policy, receipt evidence
and historical-only proof material; verify the corresponding operation refusal
or readiness invalidation without creating authority. Re-run original dispatch,
source drift, idempotency and recovery tests. A new source profile must preserve
its explicit fingerprint/invalidation behavior rather than silently reusing an
old completed operation under a changed profile.

The optimization goal is to verify the complete required live dependency set and
preserve complete review evidence. No performance or guard-equivalence outcome
is claimed by this analysis.
