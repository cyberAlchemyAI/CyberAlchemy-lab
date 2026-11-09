# Current Meta-Type Implementation State

Status: owner-admitted, frozen, project-local

The current canonical implementation baseline is
`domainspec-meta-types-current-implemented@10`, with baseline digest
`bfbc335d151ab8b29150dc95f246c2bc0954cff179ece5ce51222b2d1455abda`.
Its immutable manifest is
[`CANONICAL-IMPLEMENTED-BASELINE.v10.json`](../../development/meta-type-instantiation-cli/CANONICAL-IMPLEMENTED-BASELINE.v10.json).

This is the canonical answer to “what DomainSpec meta-type implementation exists now?”:

- all 13 active backend meta-types have one admitted realization in TypeScript, Python, and Rust;
- the baseline therefore contains 39 exact realization rows;
- every row binds a source, provider, and binding path and digest;
- the 11 UI meta-type rows remain frozen supporting context at their existing maturity and are outside the
  first CLI instantiation surface;
- the 31 canonical relationship signatures remain governed by DS-D8;
- the private CLI implements deterministic instantiation and static target conformance for the
  TypeScript, Python, and Rust profiles;
- the complete Workflow Compensation model is admitted as D36-D44, with semantic, dispatch, attempt, replay,
  Claim, Lease, Retry, and Terminal Disposition axes kept distinct;
- D45-D49 have closed provider-neutral schemas, compiler validation, deterministic TypeScript/Python/Rust
  contract profiles, CLI binding formation, receipt binding, and exact static observation; no universal `Port`
  or provider is selected;
- prior form-queue and provider/profile gate findings remain provenance only and do not control this baseline.

Semantic maturity, implementation admission, and target conformance are separate axes. DS-D1 defines what the
meta-types mean. This state records which implementation bytes are selected. Today, target instantiation and
static conformance and provider-neutral system-integration formation are implemented for the private
three-profile CLI. The durable compensation model is admitted, while its provider runtime remains the next
product unit.

For Operation (`DS-D1.4`), the selected implementation contract includes declared read, write, and effect
sets; guard execution before state mutation; atomic state-and-outbox behavior; explicit failure continuation;
no undeclared reads, writes, or effects; and typed relationships to Rule, Event, and Workflow.

For Workflow Compensation (`domainspec-v2-D36..D44`), Workflow evaluation distinguishes `not-required` from
`recovery-required`; the D37 Recovery Intent is `required`, `satisfied`, or `unresolved`; durable dispatch uses
`ready`, `leased`, `executing`, `retry-scheduled`, and `terminal`; one attempt is `succeeded`, `failed`, or
`unknown`; and the terminal disposition is `completed`, `exhausted`, or `escalated`. Replay Identity, Claim,
and Lease are separate contracts. The current runtime implements Recovery Intent planning, exact-binding preflight,
external invocation, and deterministic replay keys. Durable storage, fenced claiming, lease renewal, persisted
retry scheduling, terminal recording, and restart recovery are not implemented.

For infrastructure binding (`domainspec-v2-D45..D49`), the current implementation validates one closed
binding set, compiles a digest-bound manifest, emits a responsibility-named contract in TypeScript, Python,
or Rust, records that selection in the instantiation receipt, and reproduces it during target observation.
This is formation and generated-source evidence only: adapter/resource references are target supplied,
`runtime_guarantees_observed` remains false, and no database, ORM, broker, or provider runtime is selected.

Baselines `@1` through `@9` remain immutable historical evidence. Baseline `@5` is retained as the failed
validator-self-match attempt. Baseline `@7` preserves the validated Recovery Intent and canonical
infrastructure-binding vocabulary epoch. Baseline `@8` freezes the completed recovery corrections and
provider-neutral system-integration formation implementation. Baseline `@9` separates current Node 26/baseline
projections from immutable baseline digest membership. Baseline `@10` additionally makes the recovery semantic
contract baseline-independent and refreshes exact three-language Workflow binding closure. The
private CLI and its static generated-target observer consume `@10` as the current selection surface, but that selection does not turn the
open durable-recovery runtime into implemented behavior.

Claim ceiling: this state admits a canonical project-local implementation baseline, bounded static
generated-target conformance, the complete durable compensation semantic model, and durable-recovery
architecture @2. It does not prove the
durable compensation dispatcher is implemented, publish or release a package, deploy anything, or establish
production readiness.
