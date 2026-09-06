# WP-SFC-001 — Lane B exact-byte owner review

- Date: 2026-08-19
- Reviewer: Craft scan (read-only)
- Target: `development/first-production-release/stable-foundation-cli/`
- Verdict: **package sound; accept as a plan.** Two findings change sequencing.
- Authority effect: none. This review selects nothing, admits nothing, and mutates no work-pack byte.

## Verified clean

| Check | Method | Result |
| --- | --- | --- |
| Source bindings | SHA-256 recomputed over each live path | **12/12 exact**, zero drift |
| Define validation | read `DEFINE-VALIDATION.json` | `pass`, `blockers: []` |
| Execution-entry validation | read `EXECUTION-ENTRY-VALIDATION.json` | `pass`, 20 routes, digest `dc177fab…` matches `INTEGRATION-VALIDATION.md` |
| SF-01..SF-21 coverage | `work-pack/shared/TRACEABILITY.md` | all 21 mapped; **S1 correctly excluded** from CLI runtime, held only as shared identity with Lane A |
| P2 kind count | counted `definitions/meta-types/meta-types.yml` | **13 active confirmed** (`DS-D1.1..9`, `.11..14`) — matches the claim |
| Endpoint integrity | cross-checked all backend relation endpoints against the 13 kinds | **zero leakage**; `Enum` is the sole kind with no backend edge (expected — leaf type) |
| Write scopes | 88 declared paths | 1 overlap (`impl/cli/package.json`, units 002 + 009); ordering safe via the linear chain — not a defect |
| Collision risk | `impl/cli/` | does not exist — clean greenfield |
| Task Session coupling | grep `transient` across the package | **zero hits** — independent of the WP-RMT-002 v1.3 contract change |

No fabrication, no self-issued authority, no stale binding.

## Finding 1 — `SFC-PR-001` is a missing profile, not a missing signature

SF-02 binds `feature-with-independent-node-and-edge-files@1` (13 kinds / 16 relations).

The live registry `definitions/minted-project/supported-profiles.yml` contains **exactly one** profile:

```
feature-with-independent-node-files@1     <- different id
  status: experimental
  kinds: 4          (Entity, Event, Operation, Rule)
  relationships: 3  (enforces, performs, produces)
  release_admission: not-granted
```

Both registry digest pins verify current against live bytes, so this is a genuine
content gap, not staleness. Ratifying `SFC-PR-001` therefore means creating a
profile row roughly 3x the kinds and 5x the relations of the only existing one,
and promoting it past `experimental`.

## Finding 2 — the membership number is 17, not 16

`SWU-SFC-004` asserts *exact* 13-kind and 16-relation P2 membership. The live
authority has **31 active signatures: 17 backend-scoped, 14 UI-touching.**

Exact backend-scoped set (candidate P2 membership):

| # | id | source | target | scope |
| --- | --- | --- | --- | --- |
| 1 | `performs` | Entity | Operation | same-feature |
| 2 | `produces` | Operation | Event | same-feature |
| 3 | `produces-for` | Operation | Entity | cross-feature |
| 4 | `creates` | Operation | Entity | same-feature |
| 5 | `triggers-cross` | Event | Operation | cross-feature |
| 6 | `enforces` | Rule | Operation | same + cross |
| 7 | `calculates` | Calculation | Operation | same-feature |
| 8 | `transitions` | Event | State Machine | same + cross |
| 9 | `exposes` | Interface | Operation, Query | same + cross |
| 10 | `orchestrates` | Workflow | Operation | same + cross |
| 11 | `applies` | Policy | Operation, Calculation | same-feature |
| 12 | `maps` | Mapping | Entity, Interface | same + cross |
| 13 | `contains` | Entity | Value Object | same-feature |
| 14 | `queries` | Query, Calculation, Operation | Entity | same-feature |
| 15 | `emits` | Entity | Event | same-feature |
| 16 | `owns` | Entity | Entity | same + cross |
| 17 | `belongs-to` | Entity | Entity | same + cross |

All 17 are `status: active` and legitimately distinct. `owns` carries a
`generated_view` inverse `owned-by` (not a separate signature); `belongs-to` is
explicitly defined as distinct from `owns^-1`. Separately tracked and correctly
outside this set: 3 `deferred`, 1 `deprecated` (`enforces-cross`).

The profile owner must either ratify **17** and correct the one number in
`SWU-SFC-004`, or name exactly which signature is excluded and on what grounds.

## Finding 3 — `SWU-SFC-004` fuses blocked and unblocked work

`SWU-SFC-004`'s acceptance boundary is:

> The approved binding passes; missing, extra, stale, self-issued,
> source-mutated, causal-removal, and owner-digest mutants fail.

Seven of the eight cases are negative controls needing only fixtures. Exactly one
— "the approved binding passes" — needs an owner-ratified receipt. The package's
own `CROSS-TASK-GAPS.md` already permits the unblocked half:

> A Task Session may implement fail-closed readers or fixtures before an owner
> receipt exists, but it cannot mark the corresponding acceptance boundary pass
> using a self-issued substitute.

Because `CLOSEOUT-CONTRACT.md` requires the acceptance-critical command to pass
before a unit closes, and closure is what makes the successor eligible, the fused
`004` stops the whole chain at unit 4 of 20.

**Runway as written: 3 units** (001, 002, 003), then a hard stop.

Splitting `004` into `004a` (schemas, fail-closed readers, 7 negative controls —
unblocked) and `004b` (the single approved-binding positive — blocked on
`SFC-PR-001`) yields **6 units of runway** with `005`/`006` re-parented onto
`004a`.

Note: `005`/`006` cannot be re-parented onto `003` directly. `SPEC.md` requires
the structural receipt to be source/**profile**/version-bound, so the receipt
schema genuinely needs the profile-binding shape that `004` authors. The
dependency is on `004`'s *schema artifact*, not on its *approved-binding
verification* — which is precisely why the split works and a re-parent does not.

## Recommendation

1. Accept the package.
2. Split `SWU-SFC-004` before selecting anything — it doubles runway.
3. Open `SFC-PR-001` as real parallel work: create the profile row, settle 16 vs 17,
   promote past `experimental`. It is the critical path.
4. Hold Task Session execution until the concurrent `arcanum/arcana/task-session`
   work settles; admission checks the live Arcanum binding.
