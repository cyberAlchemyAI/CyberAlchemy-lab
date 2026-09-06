# DCB Lane A — Alternatives Receipt

Status: lane receipt (retroactive Lane A under the Two-Lane Discipline)
Date: 2026-06-11
Lane: alternatives (held the underlying problem fixed; proposed non-DCB solutions)
Integration: **integrated** — narrows and re-primitives the pilot (see SYNTHESIS-DELTA below and HANDOFF.md)

## Underlying problem (held fixed)

A spec→code correctness claim should not be accepted if any spec, code, test,
evidence, registry, waiver, or projection fact it relied on changed after the
claim was assembled. Existing validators check a snapshot is valid, not whether a
later claim was made against a still-current fact set.

## Alternatives considered

### Alt 1 — Content/input-hash invalidation (rollup hash of the dependency set)
- **How:** record `claim_id → dependency_hash` over the content of every relied-on
  fact; recompute at acceptance; differ ⇒ stale ⇒ reject.
- **Reuses (primary-source):** existing SHA-256 checksums — `buildChecksum`
  (`implementation/domainspec/.../knowledge-graph/domain/models.ts:234-235`),
  per-doc `checksum` (`models.ts:52,212`), `snapshotId` content digest
  (`models.ts:299-318`); same pattern already specced for the GitOps bot manifest
  (`docs/features/gitops-assessment/specs/phase-4-domainspec-bot.md:255-343,408-418`).
- **Solves vs reframes:** genuinely solves; content-addressed so it catches
  change-and-revert that timestamps miss. Reframes DCB's read-set (still enumerate
  deps to hash them) but drops the append-condition/event log.
- **Beats/loses:** beats DCB on infra (no event store, no read-marker-model
  decision) and content-revert; loses on per-fact granularity, audit narrative,
  and concurrency/causality.

### Alt 2 — Rerun-before-use validator policy
- **How:** don't track staleness; make the verdict cheap+deterministic to
  recompute and recompute it at decision time. Staleness becomes impossible by
  construction.
- **Reuses (primary-source):** registry generator and projection rebuild are
  already deterministic regenerations from source (`tools/generate-registry.ts`,
  `rebuild-mirror-projection.ts`); drift compare recomputes on demand
  (`compare-code-tag-drift.ts`).
- **Solves vs reframes:** solves for any rerunnable fact; reframes temporal
  correctness as non-persistence of verdicts.
- **Beats/loses:** beats DCB wherever facts are deterministic+cheap (zero standing
  state); **loses hard on non-rerunnable facts** — human approvals, LLM/agent
  verdicts (the bot spec's prompt-hash/model-version exist precisely because those
  can't be reproduced), paid CI, external evidence. RESEARCH-STRATEGY.md:130-132
  already concedes DCB is weak exactly where rerun applies.

### Alt 3 — Snapshot-diff freshness gate (over existing projection + `generatedAt`)
- **How:** persist the projection snapshot a claim was made against; diff vs a
  fresh one at acceptance; lift `FreshnessStatus` (`models.ts:36`, today hardcoded
  `"up-to-date"`) from display value to acceptance gate.
- **Solves vs reframes:** mostly reframes DCB (stored snapshot + diff ≈ read-set +
  change-check); directly solves the narrow `AcceptProjectionFreshnessClaim`.
- **Beats/loses:** beats on projection-shaped facts (snapshot already exists);
  loses on facts not in the projection (waivers, approvals, external receipts).

### Alt 4 — Certificate / TTL expiry on verdicts
- **How:** issue each verdict with the fact-version it certifies (+ optional TTL);
  accept only a non-expired certificate whose certified version == current.
- **Solves vs reframes:** version-binding half solves (= Alt 1 on the verdict; the
  bot-spec Traceability block is the analogy). **TTL half does NOT solve it** —
  wall-clock expiry is orthogonal to whether facts changed; unsound proxy.
- **Beats/loses:** beats on locality (freshness travels with the verdict); loses on
  multi-fact claims (re-introduces a read-set) and inherits TTL unsoundness.

## Comparison vs DCB pilot

| Dimension | DCB (read-set + append-condition) | Best alternative |
| --- | --- | --- |
| Solves stated problem | yes | Alt 1 & Alt 2 — yes |
| New infrastructure | event/JSONL ledger + marker model + append-condition | Alt 1: one manifest map; Alt 2: none |
| Dodges read-marker-model residue | no (open) | Alt 1/2: yes |
| Content-revert detection | only if events content-tagged | Alt 1: yes |
| Non-rerunnable facts (human/LLM/paid CI/external) | **yes** | Alt 2: **no**; Alt 1: yes |
| Per-fact granularity + audit | **yes** | Alt 1: no (rollup) |
| Concurrency / optimistic-concurrency | **yes** | Alt 1/3: weaker |

## Verdict

- **Threatens the pilot on cost-justification, no single alternative dominates.**
  Alt 1 and Alt 2 fully solve the problem for the largest, cheapest class of facts
  (deterministic source/spec/code/projection) with strictly less machinery than a
  read-set + append-condition ledger — and Alt 1 is already specced in-repo. DCB
  earns its keep only on the residual hard class: **non-rerunnable facts that need
  concurrency/causality** (human approvals, agent/LLM verdicts, external evidence,
  concurrent promotion races). The pilot as written is over-built for its own toy
  (a deterministic anchor rename, which Alt 1 or Alt 2 catch trivially).
- **Recommendation: proceed-and-borrow.** Content-hash (Alt 1) as the freshness
  primitive; rerun (Alt 2) as the policy for deterministic facts; reserve the DCB
  event/append-condition for non-rerunnable + concurrent facts; narrow the first
  pilot toward `AcceptProjectionFreshnessClaim` (Alt 3, snapshot-diff) since the
  projection snapshot + checksums already exist.
- **Bridge decisions:**
  - Alt 1 content/input-hash — **promotion-candidate** (adopt as marker primitive).
  - Alt 2 rerun-before-use — **borrow-carefully** (default policy for deterministic
    facts; pilot must scope to the *complement* or it duplicates validators).
  - Alt 3 snapshot-diff — **borrow-carefully** (make the first pilot narrower/cheaper).
  - Alt 4 certificate — **analogy-only** (TTL, unsound) / **borrow-carefully**
    (version-binding half).

## Residue

- Require the toy to include at least one **non-rerunnable fact** (waiver or
  human/agent verdict) or accept the pilot validates only the narrow
  projection-freshness case. Owner: DomainSpec v2.
- Coarse rollup hash vs per-dependency hashes (keeps DCB granularity). Owner: pilot
  task-session.
- Semantic-vs-syntactic change: content-hash over-rejects cosmetic edits; the bot
  spec's semantic-hash fallback suggests a needed escape hatch. Owner: pilot
  task-session.

## Evidence boundary

High confidence, primary-source from direct reads: all five tower docs;
`knowledge-graph/domain/models.ts`; `rebuild-mirror-projection.ts`;
`compare-code-tag-drift.ts`; `gitops-assessment/specs/phase-4-domainspec-bot.md`
(a spec doc = intended design, not confirmed running code);
`tools/generate-meta-health.ts` (`git log --since` change oracle);
`tools/generate-registry.ts`. Could NOT verify: that the bot input-hash mechanism
is implemented; any TTL/expiry/generation-id surface (none found — inferred from
absence); dynamic `FreshnessStatus` producers beyond the hardcoded value. The
repo's GitNexus/semantic MCP tools were not run; findings rest on path-cited reads.
