# DCB Correctness Lane Receipts

Status: joined research receipts
Date: 2026-06-11

## DCB Architecture Lane

Key findings:

- Existing code-tag schema can provide a fact/tag substrate for DomainSpec
  correctness facts: implementation symbols already connect to concept IDs,
  concept types, spec refs, and relationships.
- Existing drift comparison is projection-like, but batch-oriented. It can
  detect docs/code mismatch, but does not guard stale decision acceptance.
- Governance signals are already event-shaped enough to become correctness
  facts.
- Lean code validation is a write-model projection, not DCB. DCB should wrap
  readiness verdicts with freshness guards.

Gaps:

- no current read position for correctness decisions;
- no append condition for accepting correctness claims;
- no minimal correctness event vocabulary yet.

Synthesis question:

- Should the first command be `AcceptSpecCodeCorrectnessClaim`,
  `AcceptWaiver`, `SyncRegistry`, or a narrower projection-freshness command?

## DomainSpec Discipline Lane

Key findings:

- DomainSpec already has an explicit authority hierarchy. DCB should bind
  claims to authority facts, not replace the authority map.
- The pipeline already makes spec -> test -> implementation -> registry ->
  observability -> verification explicit.
- Code tags and drift comparison already provide strong static validation.
- Missing or stale feature-pack paths are a real correctness problem; direct
  path/link validators should catch path absence, while DCB can invalidate
  dependent claims.

Gaps:

- generated registry snapshots do not appear to encode durable read sets;
- work-pack coverage relies on rerunning validators, not preserving freshness
  conditions.

Synthesis question:

- Which decisions deserve DCB freshness checks: registry sync, verification
  PASS, promotion, work-pack mutation approval, or only cross-feature claims?

## Correctness Validation Lane

Key findings:

- DomainSpec feature truth is multi-file pack truth, which maps well to DCB
  tags.
- Traceability and coverage audits catch source links, but do not naturally
  express "no relevant source changed since this decision."
- The Knowledge Graph feature already has source checksums, projection
  snapshots, stale projection behavior, and command-time mismatch handling.
- The Knowledge Graph stale-anchor case is the best local toy scenario.

Gaps:

- no generalized append-condition artifact exists for correctness claims;
- GitOps bot specs rediscover input-hash freshness ideas, suggesting this is a
  real recurring need.

Synthesis question:

- Can existing `snapshotId`, source checksum, `@source`, and work-pack coverage
  mechanisms become a minimum viable DCB simulation?

## Spec Authoring Lane

Key findings:

- DomainSpec docs already function as canonical correctness inputs.
- `templates/SPEC.md` already has concept registry and concept graph surfaces;
  DCB thinking can sharpen them with stale-if-changed facts.
- Operation specs expose rules, postconditions, and errors, but not the
  boundary of facts each rule reads.
- Advanced features already use DCB-like boundary concepts such as source refs,
  interpretation limits, projection receipts, approval guardrails, handoff
  refs, decision snapshots, telemetry, and deterministic hashes.

Gaps:

- base templates do not ask rules to name dependency sets or invalidation facts;
- event docs do not ask for semantic tags, authority level, or invalidation
  effects;
- traceability discipline is uneven across features.

Synthesis question:

- What is the smallest authoring primitive: `Depends On`, `Invalidated By`,
  `Authority Source`, `Evidence Required`, or a single `Correctness Boundary`
  block?
