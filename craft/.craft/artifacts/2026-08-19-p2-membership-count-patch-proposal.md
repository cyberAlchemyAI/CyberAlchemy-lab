# P2 membership count 16 -> 17 — patch proposal

- Date: 2026-08-19
- Author: Craft scan (read-only). **Proposal only — no byte changed.**
- Related: `BLK-DSV2-SFC-PR001-PROFILE-ABSENT`, `ART-DSV2-P2-RATIFICATION-PROPOSAL`
- Authority effect: none.

## This is not a typo. It is uncaught authority drift.

I initially reported the `16` as a one-number defect. It is not. `16/16` is a
**decided quantity** in the accepted 2026-07-17 FPR-02 supported-profile decision:

> ### Selected option — All 16 backend signatures admitted and exercised
> `Backend_signatures_admitted = Backend_signatures_exercised = 16`

Git history shows that decision was **correct when made**. At the commit current on
2026-07-17, `relationships.yml` held 30 signatures, exactly 16 backend-scoped.

## Timeline

| Date | Event |
| --- | --- |
| 2026-07-17 | FPR-02 decision selects `16/16`. **Correct** — authority had 16 backend signatures |
| 2026-07-23 | commit `82edd13e4` *"formalize creation and edge authority"* adds `creates` (Operation → Entity, same-feature). Authority becomes **17**. Invalidation trigger fires |
| 2026-08-14 | `WP-SMO-001` authors its profile candidate — correctly records **17** |
| 2026-08-16 | `SF-02` restates **16**, inheriting the stale quantity |
| 2026-08-16 | `WP-SFC-001` propagates **16** into nine artifacts, including an acceptance boundary |
| 2026-08-19 | caught here |

The single added signature is `creates`. Nothing else changed in the backend set.

## Two things this exposes

**1. A designed invalidation trigger did not fire for 27 days.** `SPEC.md` line 57
declares the CLI must reject "stale acceptance when profile, meta-type, **relationship**,
runtime, dependency, schema, rule, or source binding changes". That is exactly what
happened on 2026-07-23, and nothing caught it. The mechanism is specified but not yet
realized — which is the same shape as `BLK-DSV2-DRIFT-ENGINE`.

**2. The two-lane integration check has a hole.** On 2026-08-16 Lane A and Lane B were
validated as sharing one decision digest with zero write-scope overlap — and passed.
But `WP-SMO-001` said 17 and `WP-SFC-001` said 16 on the same day. The check verified
that both lanes bind the same decision *bytes*; it did not verify that they agree on
what the decision's *quantities* denote. Denominator agreement is the stated purpose of
that gate.

## Cost of the correction

Going to 17 is not free. The July decision selected signatures "admitted **and
exercised**". One more signature must therefore be exercised in the conformance corpus,
not merely listed. `creates` needs positive coverage and negative controls before any
`16/16`-style completeness claim can be restated at `17/17`.

## Exact edit set (9 sites, none applied)

| # | File | Line | Current | Proposed |
| --- | --- | --- | --- | --- |
| 1 | `decisions/2026-08-16-first-stable-foundation-candidate.md` | 58 | `all 16 backend relationship signatures` | `all 17 backend relationship signatures` |
| 2 | `stable-foundation-cli/SPEC.md` | 30 | `16-backend-relation source denominator` | `17-backend-relation source denominator` |
| 3 | `stable-foundation-cli/SPEC.md` | 41 | `16 backend relationship signatures` | `17 backend relationship signatures` |
| 4 | `stable-foundation-cli/REQUIREMENTS.md` | 12 | `16 backend signatures` (SFC-F-004) | `17 backend signatures` |
| 5 | `stable-foundation-cli/GLOSSARY.md` | 18 | `16 backend signatures` | `17 backend signatures` |
| 6 | `stable-foundation-cli/DEFINE-CONTEXT.md` | 33 | `16 backend signature rows` | `17 backend signature rows` |
| 7 | `stable-foundation-cli/DESIGN-PLANNED-WITNESSES.json` | 5 | `13-kind and 16-signature profile identity` | `13-kind and 17-signature profile identity` |
| 8 | `stable-foundation-cli/work-pack/shared/SWU-MANIFEST.json` | 115 | `13-kind and 16-relation P2 membership` | `13-kind and 17-relation P2 membership` |
| 9 | `stable-foundation-cli/work-pack/waves/W0-CONTRACT.md` | 14 | `bind exactly 13 backend kinds and 16` | `bind exactly 13 backend kinds and 17` |

Deliberately **excluded** from this set:

- `INTEGRATION-VALIDATION.md:24` — `16/16 hostile controls` is an unrelated quantity.
- `TASK-SFC-INPUT.md:14` — `decisions 2, 3, 7, 8, 9, 10, and 16` are decision indices.
- `INTEGRATION-VALIDATION.md:25` — states `16 backend relations`, but this file is a
  *validation record* of a check that ran on 2026-08-16. Records of past checks should
  not be retroactively edited; it should be superseded by a re-run, not patched.
- The 2026-07-17 decision itself — see routing below.

## Routing — this cannot be applied as a text edit

1. **The July `16/16` selection needs owner re-ratification at `17/17`.** It is an
   accepted decided quantity with an evidence obligation. A downstream document cannot
   silently restate it. This is the governing act; the nine edits are its projection.
2. **Then an Invoke Refresh over the Lane B package** for sites 2-9. `SWU-MANIFEST.json`
   is one of the six closeout-inventory targets, so it moves only through a refresh with
   exact owner approval and pre/post baseline validation.
3. **Site 1 requires fresh owner acceptance of the changed bytes** under the August
   record's own rule: changed acceptance-bound bytes do not reopen an unchanged
   decision, but they always require fresh inventory, validation, independent review,
   and owner acceptance.
4. **Re-run the two-lane integration check** with a denominator-agreement assertion
   added, so this class of divergence fails closed next time.
5. **`creates` needs corpus coverage** before any `17/17` admitted-and-exercised claim.

None of this needs Arcanum, Task Session, or a SWU selection. It is the one part of the
`SFC-PR-001` chain that can move while the Arcanum work settles.
