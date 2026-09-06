# DCB Correctness Research Strategy

Status: research strategy
Date: 2026-06-11
Target: `/home/vrondelli/projects/domainspec-core/projects/domainspec-v2`
Evidence source: `/home/vrondelli/projects/domainspec-core/implementation/domainspec`

## Project context & discipline note

This tower is part of the [DomainSpec v2](../../README.md) research program. It
predates the [Two-Lane Discipline](../TWO-LANE-DISCIPLINE.md) and was built with
four **concern** lanes (DCB architecture, DomainSpec discipline, correctness
validation, spec authoring), not the advocate/alternative two-lane shape. The
concern decomposition is kept as-is; it is a legitimate different lane shape and
its findings stand.

The discipline gap is now **closed**: a retroactive **Lane A (alternatives)** was
run (2026-06-11) — see [LANE-A-ALTERNATIVES.md](LANE-A-ALTERNATIVES.md). It held
the underlying problem fixed and proposed four non-DCB solutions (content/input-
hash invalidation, rerun-before-use validator policy, snapshot-diff freshness
gate, certificate/version-binding).

**Lane A changed the verdict.** It found the DCB pilot is over-built for its own
toy: content-hash invalidation and rerun-before-use each fully solve the problem
for the large, cheap class of *deterministic* facts with far less machinery, and
the content-hash pattern is already specced in-repo (GitOps bot manifest). DCB
earns its keep only on the residual hard class — **non-rerunnable facts that need
concurrency/causality** (human approvals, agent/LLM verdicts, external evidence,
concurrent promotions). Integrated decision: **proceed-and-borrow** — adopt
content-hash as the freshness primitive (promotion-candidate), rerun as the
policy for deterministic facts, reserve the DCB event/append-condition for the
non-rerunnable+concurrent case, and narrow the first pilot to projection-freshness
(snapshot-diff). The [HANDOFF.md](HANDOFF.md) decision state reflects this.

## Central Question

Can Dynamic Consistency Boundaries help DomainSpec ensure spec-to-code
correctness by preventing stale correctness claims, while also improving how
specs name the facts, evidence, and boundaries their rules depend on?

## Working Thesis

DCB is viable for DomainSpec only if it is introduced first as a lightweight
correctness-boundary discipline, not as a full event-store infrastructure
commitment.

The useful DCB question is:

> Which spec, code, test, evidence, waiver, registry, and promotion facts did
> this correctness claim rely on, and have any relevant facts changed since the
> claim was assembled?

That complements DomainSpec's existing validators. It does not replace them.

## Why This Matters

DomainSpec already treats behavior as multi-artifact truth:

- feature behavior is a pack, not a single file;
- specs declare concepts, edges, operations, rules, events, tests, mappings, and
  workflows;
- code tags connect implementation symbols to DomainSpec concepts and edges;
- validators and drift tools compare documentation facts against code facts;
- governance signals and work-packs record readiness, gaps, and promotion state.

The gap is temporal correctness. Existing checks can say a snapshot is valid.
They do not always say whether a later promotion or verification claim was made
against a still-current fact set.

## Research Shape

The strategy uses four concern lanes:

| Lane | Question | Output |
| --- | --- | --- |
| DCB architecture | What minimal event/tag/read-set model fits DomainSpec correctness? | Candidate fact vocabulary and append-condition model |
| DomainSpec discipline | What existing validators, registry, authority, and traceability mechanics must DCB complement? | Overlap ledger and non-duplication guardrails |
| Correctness validation | What toy stale-evidence scenario proves DCB catches something static checks can miss? | Toy scenario and validator-vs-DCB comparison |
| Spec authoring | Would boundary thinking improve specs or make them too heavy? | Authoring primitive recommendation |

The lanes have already produced enough evidence for a first synthesis. Their
joined receipts are captured in [LANE-RECEIPTS.md](LANE-RECEIPTS.md).

## Candidate Model

### Minimal Fact Types

- `SpecConceptDeclared`
- `SpecRuleDeclared`
- `SpecEdgeDeclared`
- `CodeTagObserved`
- `ValidatorVerdictIssued`
- `EvidenceReceiptRecorded`
- `WaiverApplied`
- `RegistrySnapshotGenerated`
- `ProjectionSnapshotGenerated`
- `PromotionClaimProposed`
- `PromotionClaimAccepted`
- `CorrectnessDriftDetected`

### Minimal Tags

- `feature:<id>`
- `concept:<id>`
- `edge:<from|rel|to>`
- `rule:<id>`
- `operation:<id>`
- `artifact:<path>`
- `code:<path-or-symbol>`
- `test:<path-or-id>`
- `validator:<id>`
- `evidence:<receipt-id>`
- `owner:<authority>`

### First Command Candidate

```text
AcceptSpecCodeCorrectnessClaim(feature, claim_scope, evidence_set, validator_verdicts)
```

The command records which facts it read, including spec rows, code tags,
validator verdicts, registry snapshots, tests, waivers, and evidence receipts.
It accepts the claim only if no relevant facts with matching tags changed after
the read position.

## DCB-Specific Value

DCB adds value where correctness decisions are staged, concurrent, or
promotion-like:

- accepting a verification PASS;
- promoting a feature as implementation-ready;
- syncing generated registry state;
- accepting a waiver;
- approving a work-pack mutation;
- recording a cross-feature correctness claim.

DCB is less valuable for one-shot schema validation, markdown shape checks,
simple link checks, or deterministic validators that are immediately rerun
before use.

## Authoring Discipline

The smallest useful authoring primitive is not "event stream." It is a
Correctness Boundary.

For high-risk rules, operations, generated-code contracts, cross-feature
dependencies, and promotion gates, specs should be able to name:

- Depends on: source facts that must be current.
- Invalidated by: changes that make prior evidence stale.
- Evidence required: tests, validator verdicts, receipts, or reviews.
- Authority source: owner that can accept the claim.
- Boundary tags: feature/concept/rule/artifact/code/test tags.

This should be selective. Applying it to every simple field or rule would add
too much ceremony.

## Viability Verdict

Current verdict: viable as a pilot, with constraints.

DCB should enter DomainSpec v2 as a correctness-boundary pattern over existing
checksums, source refs, code tags, validator reports, and evidence receipts.
Do not start with production event-store infrastructure. Start with an
append-only JSONL or generated evidence ledger plus a toy stale-evidence check.

## Blockers

- The earlier `domainspec-arcanum-superset` feature pack was deleted in the
  `implementation/domainspec` worktree. Treat that as a path-state blocker for
  any handoff that assumes the old feature folder exists.
- DomainSpec v2 currently needs its own research home and later its own feature
  pack before mutating templates, validators, or registry behavior.
- A canonical read-position model is undecided. Candidates: git commit, file
  hash set, registry generation id, JSONL offset, validator run id, or a
  composite read marker.

## Next Move

Run the handoff in [HANDOFF.md](HANDOFF.md):

1. Preserve this research packet in DomainSpec v2.
2. Create a toy correctness ledger for the Knowledge Graph stale-anchor case.
3. Decide whether the pilot command is `AcceptSpecCodeCorrectnessClaim` or a
   narrower `AcceptProjectionFreshnessClaim`.
4. Only after the toy passes, propose template additions for selective
   Correctness Boundary fields.
