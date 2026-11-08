# Handoff: DCB Correctness Boundary Pilot

Status: ready for next research execution
Date: 2026-06-11
Owner surface: DomainSpec v2

## Objective

Turn the DCB correctness research into a small DomainSpec v2 pilot that proves
or rejects this claim:

> A correctness claim should not be accepted if any spec, code, test, evidence,
> registry, waiver, or projection fact it relied on changed after the claim was
> assembled.

## Starting Context

Research strategy:

- [RESEARCH-STRATEGY.md](RESEARCH-STRATEGY.md)
- [SYNTHESIS.md](SYNTHESIS.md)
- [TOY-SCENARIO.md](TOY-SCENARIO.md)
- [LANE-RECEIPTS.md](LANE-RECEIPTS.md)

Original evidence was gathered from:

- `/home/vrondelli/projects/domainspec-core/implementation/domainspec`

Current artifact home:

- `/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/research/dcb-correctness`

## Decision State

Decision: proceed with a lightweight DCB-inspired pilot, **revised by Lane A**
(see [LANE-A-ALTERNATIVES.md](LANE-A-ALTERNATIVES.md)) to proceed-and-borrow.

Do:

- record read sets for correctness claims, but make the **read-marker a content
  rollup hash of the read-set** (borrowed: Alt 1 content-hash) — this kills the
  unresolved "git commit vs JSONL offset vs registry-gen-id" marker residue;
- for any dependency that is cheaply, deterministically re-derivable, **rerun
  before use instead of tracking it** (borrowed: Alt 2);
- **scope the first pilot to `AcceptProjectionFreshnessClaim`** via a snapshot-diff
  over the existing projection snapshot + checksums (borrowed: Alt 3), before the
  general `AcceptSpecCodeCorrectnessClaim`;
- reserve the DCB event/append-condition model for the residual hard class:
  **non-rerunnable facts that need concurrency/causality** (human approvals,
  agent/LLM verdicts, external evidence, concurrent promotions);
- use existing DomainSpec concepts such as code tags, registry snapshots,
  source checksums, validator verdicts, and evidence receipts.

Do not:

- introduce a production event store yet;
- mutate DomainSpec templates yet;
- replace existing validators;
- build the full append-condition ledger for facts that rerun cheaply (Lane A:
  that duplicates existing validators — the pilot's own stop condition);
- treat research evidence as promotion authority.

## Proposed Pilot

Pilot name:

```text
Correctness Boundary Ledger
```

First command:

```text
AcceptSpecCodeCorrectnessClaim
```

Minimum inputs:

- `claim_id`
- `feature_id`
- `read_marker`
- `read_tags`
- `evidence_refs`
- `validator_verdict_refs`
- `authority_owner`

Minimum behavior:

1. Resolve all facts matching `read_tags`.
2. Record the read marker.
3. Before accepting the claim, check whether any matching fact changed after the
   read marker.
4. Accept if unchanged.
5. Reject or flag if stale.

## Toy Scenario

Use the Knowledge Graph stale-anchor case described in
[TOY-SCENARIO.md](TOY-SCENARIO.md).

It is a good first scenario because the existing DomainSpec implementation
already has:

- source checksums;
- projection snapshots;
- UI/test source references;
- stale projection behavior;
- command-time mismatch handling.

## Expected Files For Next Task

The next task-session should create one of these, depending on scope:

```text
projects/domainspec-v2/research/dcb-correctness/correctness-ledger.example.jsonl
projects/domainspec-v2/research/dcb-correctness/correctness-boundary.schema.json
projects/domainspec-v2/research/dcb-correctness/toy-run-result.md
```

Optional later files:

```text
projects/domainspec-v2/docs/features/correctness-boundary/SPEC.md
projects/domainspec-v2/docs/features/correctness-boundary/domain.md
projects/domainspec-v2/docs/features/correctness-boundary/operations.md
projects/domainspec-v2/docs/features/correctness-boundary/events.md
projects/domainspec-v2/docs/features/correctness-boundary/TEST-SPEC.md
```

## Acceptance Criteria

The pilot is successful if:

- it demonstrates one stale correctness claim that static validation could miss
  or catch only after the fact;
- the DCB-style check rejects the stale claim using tags and a read marker;
- the mechanism uses existing DomainSpec evidence shapes where possible;
- the output clarifies which parts belong to validators and which belong to
  correctness-boundary freshness checks.

The pilot should be stopped or downgraded if:

- it duplicates existing validators without adding freshness protection;
- it requires production event-store infrastructure before a toy proof;
- it makes simple spec authoring materially heavier;
- it cannot identify a stable read-marker model.

## Recommended Next Command

Run a bounded task-session:

```text
Create a toy Correctness Boundary Ledger under projects/domainspec-v2/research/dcb-correctness that simulates AcceptProjectionFreshnessClaim for the Knowledge Graph stale-anchor scenario, using a content rollup hash of the read-set as the read-marker. Include at least one NON-rerunnable fact (a waiver or human/agent verdict) so the toy proves something a rerun-before-use policy cannot. Do not mutate templates or validators.
```

Lane A constraint: if every fact in the toy is cheaply rerunnable, the pilot
duplicates existing validators and should be downgraded to a rerun policy rather
than a ledger.

## Residue

- ~~Decide whether read markers should be git commits, file hashes, JSONL offsets,
  registry generation ids, or a composite marker.~~ **Resolved by Lane A:** use a
  content rollup hash of the read-set. Open sub-question: coarse single hash vs
  per-dependency hashes (the latter keeps DCB's per-fact granularity).
- ~~Decide whether the first pilot command should be general
  `AcceptSpecCodeCorrectnessClaim` or narrower `AcceptProjectionFreshnessClaim`.~~
  **Resolved by Lane A:** start narrow with `AcceptProjectionFreshnessClaim`.
- Semantic-vs-syntactic change: content-hash over-rejects cosmetic edits; decide
  whether the ledger needs a semantic-hash escape hatch (Lane A, pilot owner).
- Recreate or intentionally replace the deleted `domainspec-arcanum-superset`
  feature pack before any work depends on that path.
