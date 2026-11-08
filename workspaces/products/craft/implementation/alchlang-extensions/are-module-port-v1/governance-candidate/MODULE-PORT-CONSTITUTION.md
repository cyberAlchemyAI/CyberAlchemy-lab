# ARE Module Port Constitution

Status: candidate
Constitution ID: `ARE-MODULE-PORT-CONSTITUTION-CANDIDATE`
Version: `1-candidate`
Owner: Agent Reasoning Engine runtime owner
Governance reviewer: CyberAlchemy v2 governance-model owner
Authority level: capability-local candidate Constitution
Selectors: `profile:semantic-contract-v1/domain:are-module-port`
Authority effect: none
Enforcement effect: none

## Scope

This candidate governs static, process-local composition of reviewed no-effect
ARE adapters. It governs exact binding, dependency closure, snapshot identity,
degraded behavior, compatibility, ownership, and evidence posture. It does not
govern module discovery, installation, untrusted execution, remote transport,
consumer policy, route selection, effect authorization, or deployment.

The `.alch` source declares the premises and finite invariants. This document
supplies reviewable rules for its `governed-by` reference. Neither artifact
adopts or activates the other.

## Rules

### ARE-MPC-1. Declared Source And Projection Stay Bound

Validation mode: deterministic

The exact `.alch` source, compiled manifest, Module Port implementation, and
conformance evidence must remain digest-bound. Generated projections cannot
replace or redefine their source.

Example: a source change forces recompilation and evidence refresh.

Non-example: an implementation change retains an earlier source binding.

### ARE-MPC-2. Static Bindings Are Exact And Reviewed

Validation mode: deterministic

Each configured adapter factory binds one exact module identity, version, and
manifest digest. Discovery, semver negotiation, fallback priority, and implicit
replacement are forbidden.

Example: a drifted adapter makes the complete configuration unavailable.

Non-example: composition accepts the nearest compatible installed version.

### ARE-MPC-3. Dependency Graphs Are Closed And Acyclic

Validation mode: deterministic

Every dependency names one configured module and exact version. Missing,
version-mismatched, duplicate, or cyclic graphs reject before a port is exposed.

Example: lexical topological ordering produces one stable inspection snapshot.

Non-example: independent modules remain available from a partially valid graph.

### ARE-MPC-4. Module Epochs Are Immutable

Validation mode: deterministic

One successful composition creates one recursively immutable module-set epoch.
Adding, removing, or replacing a module requires a successor snapshot and
digest; hot mutation is forbidden.

Example: an alpha-only set and alpha-plus-beta set have distinct digests.

Non-example: a factory map is mutated after startup to replace a provider.

### ARE-MPC-5. Consumers Retain Decision Authority

Validation mode: hybrid

The Module Port validates lifecycle and evidence only. Router, request-intent,
Context Basis, Definitions, ontology, and effect boundaries retain their own
policy and owners.

Example: Context Basis declares whether a missing catalog blocks an operation.

Non-example: the Module Port infers that Definitions are optional everywhere.

### ARE-MPC-6. Degraded Operation Fails Closed And Locally

Validation mode: deterministic

The degraded-mode policy distinguishes unavailable from blocked and forbids
silent host reimplementation. A configuration failure exposes no partial port;
a missing capability affects only its declared consumer dependency.

Example: missing context blocks a context-dependent turn but not health checks.

Non-example: missing semantic capability falls back to substring matching.

### ARE-MPC-7. Compatibility And Retirement Are Explicit

Validation mode: hybrid

Any bound-byte change requires a successor candidate and validation. Breaking
protocol, dependency, authority, or degraded-behavior changes require a new
contract version. The in-process design retires if effects, credentials,
untrusted code, process isolation, installation, or remote transport are needed.

Example: an effectful adapter begins a separate isolated-runtime architecture.

Non-example: the v1 port expands into a general plugin loader in place.

### ARE-MPC-8. Evidence Cannot Approve, Adopt, Admit, Or Activate

Validation mode: deterministic

Passing compilation and tests make a product-approval request eligible only.
Product approval, Constitution adoption, runtime admission, and activation are
separate ordered owner decisions over exact bytes. No validator may select them.

Example: all local checks pass while later decision records remain unselected.

Non-example: a passing governance validator sets `runtime_admitted` to true.

## Validation Adapters

| Rule | Adapter |
| --- | --- |
| ARE-MPC-1 | Candidate and dependency digest closure. |
| ARE-MPC-2 | Static composition binding and drift fixtures. |
| ARE-MPC-3 | Missing, version mismatch, duplicate, cycle, and permutation fixtures. |
| ARE-MPC-4 | Recursive freeze and successor digest fixtures. |
| ARE-MPC-5 | Unified wrapper integration plus owner-boundary review. |
| ARE-MPC-6 | Degraded-policy validation and zero-module behavior fixtures. |
| ARE-MPC-7 | Compatibility/retirement policy validation and review. |
| ARE-MPC-8 | Ordered decision-state validator and hostile fabricated-selection tests. |

## Promotion Boundary

This exact candidate may be considered only after an explicit product approval.
Constitution adoption would adopt these rules for this selector only. It would
not admit a runtime configuration, activate enforcement, authorize effects,
publish, release, or deploy anything.

## Retirement Or Split Triggers

- Retire the in-process profile when any adapter requires effects or credentials.
- Split transport and isolation rules into their own Constitution before adding
  cross-process or untrusted modules.
- Issue a successor contract and candidate when a protocol or dependency meaning
  changes.

## Open Questions

- Which exact production adapter configuration should later be proposed for
  runtime admission?
- Which admitted Rust governance binding could enforce this Constitution after
  all prerequisite decisions exist?
