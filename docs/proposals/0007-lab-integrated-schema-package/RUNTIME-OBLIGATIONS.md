# Runtime obligations

Status: proposed. These 31 responsibilities describe what runtime code and observed evidence must establish. A JSON Schema validates message shape; it cannot verify a signature, a hash, a live owner, causal evidence, a path on disk or a committed transaction.

The [machine-readable catalog](obligations.json) is linked from every protocol in [schema-catalog.json](schema-catalog.json). No responsibility is certified implemented by this package. Existing bounded runtime behavior retains its existing evidence and scope.

## O-EXACT: Exact binding

Verify selected bytes, scope, identity, version, schema, selector and predecessor; reject ambiguous or altered references.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-HASH: Stable hashing

Define encoding and digest boundaries; keep Decision cores independent of generated consequences and their receipts; detect all altered reviewed inputs.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-CUT: Source cut

Verify every selected stream head and watermark, compatibility and freshness; reject stale write preconditions and disclose stale reads.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-CARRIER: Domain carrier

Select the exact schema and selector; enforce current-write versus historical-read posture; verify identity and discriminators, body/header agreement and extension rules.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-CANDIDATE-CARRIER: Prospective carrier

Resolve exact candidate descriptor/schema closure before validation; maintain separate candidate dispatch until a complete owner-authorized admission permits the new carrier.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-REFERENCE: Reference closure

Resolve transitive dependencies, selectors, cross-artifact equality, ownership and admissibility; preserve unresolved, ambiguous, excluded and historical states.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-RELATION: Typed connection

Verify declared endpoint pair, explicit carrier/endpoint mappings, qualifier value domains, pair-specific constraints, semantic direction and the canonical writable authority.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-EXTENSION: Typed extension

Require the unique semantic question, orthogonal axis, exact pairs, qualifiers, semantic noncollapse analysis, affected carrier successors and owner review before new connections are writable.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-AUTHORITY: Authority evaluation

Verify real principal/role/delegation/owner authority, action and effect scope, time, revocation, redelegation, all gates and exact authorization provenance; schema validity grants no authority.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-VIEW: Bounded view

Apply selectors, exclusions, depth, privacy and byte budgets; attribute every included result to exact source evidence and expose freshness/gaps; context grants no authority.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-MEMORY: Ephemeral memory

Keep machine Agent identity/session short memory ephemeral, expire it on close/failure/cancellation and prevent exports or persistence; durable continuity comes from governed Project State via Context and Ontology Views.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-PRIVACY: Custody and disclosure

Enforce source and export scope, owner review, exclusions and private custody; keep credentials and session memory out of repository packages and query caches.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-PROFILE: Profile compatibility

Pin source and executable independently; require explicit successor/branch and selective revalidation rather than changing old source cuts or silently rebasing history.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-ACTION: Action dispatch

Evaluate exact inputs and bounds before tools run; observe real outputs and effects, attribution and budget; record success, failure or uncertainty without inferred completion.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-RECOVERY: Recovery and retry

Observe uncertain effects before retry; enforce idempotency, expected heads and recovery contracts; reconcile allowed residue without deleting committed history.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-EVIDENCE: Evidence and claim ceiling

Bind validator, observations, methods, sample/environment and results; distinguish authoring checks, implementation verification, operational success and assessed outcomes.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-COMMIT: Canonical publication

Preflight exact authority, dependency closure and expected head; stage immutable packages/records, serialize competing writers, publish one canonical head and verify crash recovery/idempotency.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-BYTES: Original content

Verify byte count, media type, digest and encoding against original bytes; include the complete dependencies needed for portable replay; JSON normalization is not exact reconstruction.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-PROJECTION: Disposable SQLite generation

Enforce SQL/SQLite compatibility, foreign keys, complete input generation and watermarks; switch the active generation only after checks; rebuild from canonical sources and reject invalid or undisclosed stale results.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-FILE: File generation

Verify the selected output scope and safe paths including symlinks; preserve unmanaged files, stage and publish a complete generation, pin rendering and distinguish exact exports from rendered views.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-WORKFLOW: Workflow transition

Bind carrier lifecycle mappings, actor routes, exact checks and decision profile; validate current state, required inputs, transitions, satisfaction, concurrency and recoverability; assessed outcomes remain separate from tool completion.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-CLASSIFICATION: Classification axes

Verify scheme/value/axis agreement, applicability and independent classification dimensions; classification assignment does not establish causality or authority.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-FAILURE: Failure analysis

Separate occurrence, mode, cause hypothesis, impact, incident threshold and control/recovery assessment; bind evidence and preserve uncertainty.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-CHALLENGE: Contestability

Verify the exact Challenge Contract, challenger eligibility, grounds, response and resolution routes and evidence; retain the challenged subject and distinguish semantic from governance consequences.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-LESSON: Operational learning

Select lessons by evidenced applicability and exclusions; preserve observation/reflection/lesson/application/outcome distinctions; assess applications and counterevidence before broader effectiveness claims.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-ONTOLOGY: Ontology representation

Maintain represented-subject identity, source revisions and independent Lab/ontology stream heads; global relation projections are read-only, local ontology edges obey their own profile and authority.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-MIGRATION: Migration accounting

Account for all selected source items and their dependencies with import/adaptation/reference/defer/exclude/block disposition; preserve source custody and do not infer broad cutover or source retirement.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-ADOPTION: Capability adoption

Verify capability realization binding, implementation conformance, owner-local scope, observation contract and actual authorization; admission and operational adoption have distinct evidence.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-RELEASE: Release acceptance

Verify exact package closure, product/thesis/capability bindings, acceptance contracts, pilot observations, compatibility and release Decision; candidate evidence is not production acceptance.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-INSTALL: Local installation

Verify exact release, target, authority, preimage, private custody and rollback; observe installed postimage and uncertain residue without inferring service activation.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.

## O-TRANSPORT: Service boundary

Resolve exact operation and request/result schemas, authenticate the actual caller, evaluate policy and bounds, verify request/result correspondence and avoid interpreting caller_requirement text as permission.

Failure: block the affected write or effect; disclose gaps and claim limits in eligible reads.
