# SFC-PR-001 — P2 profile ratification proposal

- Date: 2026-08-19
- Author: Craft scan (read-only). **Proposal only.**
- Blocker: `BLK-DSV2-SFC-PR001-PROFILE-ABSENT`
- Target owner: profile owner (`definitions/minted-project`) + definitions-governance
- Authority effect: none. Nothing here mutates `supported-profiles.yml`, ratifies a profile, or admits a release.

## Headline: do not author this from scratch — it already exists

A precedent sweep found the P2 material already authored as owned candidates inside
the `WP-SMO-001` refinement run:

| Material | Owned candidate |
| --- | --- |
| Profile row | `development/refinement-runs/20260814T103237-0300-shared-meta-obligation-product-readiness/proposals/formation/supported-profiles.candidate.json` |
| Formation contract | `.../proposals/formation/formation-projection-contract.candidate.json` |
| Golden corpus | `.../proposals/formation/formation-golden-corpus.candidate.json` |
| Staged live postimages | `.../governance-sidecar/g1-material-apply-repair-005/payload/packages/wp-smo-001-g1-v5-private-private/outputs/projects/domainspec-v2/definitions/minted-project/` |

The candidate profile is `complete-backend-criteria@2`:

- `status: candidate`, `release_admission: not-granted`
- **13 kinds** — exactly the 13 active meta-types
- **17 `relationship_ids`** — exactly the 17 backend-scoped active signatures
- `non_admitted_relationship_count: 14` — exactly the 14 UI-touching signatures (17 + 14 = 31 total)
- `formation_contract` — one `criterion-projection` validator at
  `definitions/minted-project/formation-projection.v1.json` (8126 bytes, staged)
- `golden_corpus` — 26 cases

Its `effective_when` states the membership explicitly:

> all 13 active kinds and **17 active backend relationship signatures** are denominator-complete

## Consequence 1 — the number is 17, and SF-02 is wrong by one

Two independent derivations agree on 17:

1. My enumeration of live `definitions/relationships/relationships.yml` — 31 active,
   17 backend-scoped, 14 UI-touching, zero endpoints outside the 13 kinds.
2. The 2026-08-14 owned candidate, authored independently for a different purpose.

`SF-02` and `SWU-SFC-004` both assert **16**. That is a one-number defect in the
decision text and in the unit's acceptance boundary, not a membership dispute.
`Enum` is the only kind with no backend edge — expected, it is a leaf type.

**Recommended resolution:** correct both to 17. This does not reopen `SF-02`'s
selected branch; the breadth intent is unchanged and the corpus is unchanged.

## Consequence 2 — the candidate is not a drop-in

Three discrepancies remain between the owned candidate and what `SWU-SFC-004` consumes.

| # | Field | Owned candidate | SF-02 / `SPEC.md` needs | Owner call |
| --- | --- | --- | --- | --- |
| D1 | `id` / `version` | `complete-backend-criteria@2` | `feature-with-independent-node-and-edge-files@1` | rename the candidate, or amend the SF-02 binding to the owned id |
| D2 | `source_layout` | `per-node-connections` | independent edge files — `specs/<f>/nodes/`, `specs/<f>/edges/`, project-level `edges/` | **substantive.** The candidate was authored for SMO obligation coverage, not for the CLI source topology |
| D3 | `status` | `candidate`, `release_admission: not-granted` | an owner-ratified receipt `SWU-SFC-004` can consume | promote, with the exact effective_when evidence |

D2 is the real one. `per-node-connections` means connections are declared inside node
files — which is precisely what the existing experimental profile lists under
`non_goals` as "independent edge lifecycle". The new profile's own *name* encodes the
difference. **The candidate's membership set is reusable; its layout is not.**

## Consequence 3 — the corrected dependency chain

`SFC-PR-001` is not net-new authoring blocked on the profile owner alone. The material
is staged inside the `WP-SMO-001` G1 package, which is itself blocked:

```
BLK-DSV2-SMO-ARCANUM-BINDING   (stale live Arcanum binding; 8 residual G-gates)
        |
        v  G1 apply lands supported-profiles.yml + formation-projection.v1.json
BLK-DSV2-SFC-PR001-PROFILE-ABSENT
        |
        v  owner-ratified P2 receipt
SWU-SFC-004  ->  SFC units 4..20
```

`WP-SMO-001`'s stated next owner is `refine:evidence-refresh` **after Arcanum
stabilizes** — and Arcanum is currently being changed by the concurrent
`arcanum/arcana/task-session` work. Three of the seven active blockers are one chain,
rooted in Arcanum stability.

## Recommended route

1. **Correct the count to 17** in the `SF-02` record and `SWU-SFC-004`. Cheapest item;
   removes a false exactness assertion from an acceptance boundary.
2. **Decide D1 and D2** — profile id, and whether the ratified profile carries the
   independent-edge-file layout the CLI needs. D2 may require amending the owned
   candidate rather than reusing it verbatim.
3. **Do not fork the material.** Route through the owning `WP-SMO-001` G1 apply rather
   than authoring a second profile row; a competing row would create exactly the
   dual-authority problem the two-lane integration check exists to prevent.
4. **Sequence honestly:** SFC units 4-20 cannot start before this closes. Units 1-3
   (or 1-3 plus `004a` if `GAP-DSV2-SFC-004-FUSED` is taken) are the available runway.
