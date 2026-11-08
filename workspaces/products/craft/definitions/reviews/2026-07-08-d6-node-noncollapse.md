# Residue — D6 gains a third challenge (node non-collapse)

Date: 2026-07-08
Card: `domainspec-v2-D6` (meta-type) — status **candidate** (unchanged by this edit)
Owner route: definitions-governance · gate: owner decision
Staged by: node-noncollapse-gate-redteam follow-up

Historical-status note (2026-07-16): this residue predates the accepted FPR-01 baseline. Its 25-type/14-type
and live-collapse statements are superseded by the 24-label, 13-active-backend registry with
`DS-D1.10` retained as a non-reusable superseded ID. The node non-collapse challenge remains relevant,
but counts and live-status claims below are historical evidence only.

## What changed

D6's challenge contract carried **two** coverage challenges — *"a concept that fits no meta-type,
or needs two"* (coverage-under / coverage-over). This edit adds a **third** challenge, **non-collapse**:

> *"two meta-types that reduce to one — neither composes into different code from the other"* →
> challenges the 25-type **irredundancy** (distinct from closure). Blocking question (2): *"does each
> of the 25 compose into different code, or do two collapse into one node?"*

It is the **node-side mirror of the D3 edge-law** (`domainspec-v2-D3`, "an edge type is admissible
IFF it composes into different code"). Only D6's challenge contract changed; **no change to D18** or
its D20–D25 relationship-non-collapse property cards, and the three definition voices (formal /
plain / domain) of D6 are untouched.

## Why it is seated on D6, not D18

Node/meta-type formation is owned by **D6/DS-D1**. D18 explicitly disclaims *"DS-D1 meta-type
formation."* The original design (v1) wrongly amended D18; the 2026-07-07 red-team (finding **b1**,
CRITICAL) required re-seating on D6. Full trail:
`development/meta-type-formalization/research/2026-07-07-node-noncollapse-gate-redteam/` (findings.md,
DESIGN-SPEC-v2.md).

## The check behind the challenge

`impl/tools/validate-meta-types-noncollapse.ts` (+ `tools/lib/meta-type-noncollapse.ts`, tests in
`tools/tests/`). A pair collapses iff it has **no separating structural witness**, **no
authority-resolved separating edge witness** (resolved through the DS-D8 relationship authority,
never raw schema slices), and **neither type is on the owner-enumerated exception lane**. On today's
14-type registry it fires exactly once — **Saga ~ Workflow** — and routes the shape-uncheckable
`formal_return_type` trio (Rule/Policy/Calculation) to the exception lane. All acceptance checks and
the anti-tautology / fresh-duplicate / exception-lane tests pass.

## Open items (not blocking this staging)

- **Promotion.** The third challenge is staged on a **candidate** card; promotion to active still
  requires the D6 confirm contract (owner approves + exercised on ≥1 real aspect + no open
  contradiction). The one live collapse (Saga ~ Workflow) is an **open contradiction** until the owner
  rules on the merge (`DEC-DSV2-SAGA-MERGE`, default: merge).
- **Laundering (documented limit).** The checker does not mechanically detect a laundered edge
  witness (an edge difference derived from the attestation under test). The owner-enumerated exception
  lane handles the one known case (the trio); general detection is deferred. See DESIGN-SPEC-v2 §8.
- **"Exercised instance" vs "authority-resolved."** The checker resolves edge witnesses through the
  DS-D8 authority signatures (works on today's registry); the design's stricter "edge exercised in a
  real aspect file" reading would over-reject until aspect instances exist. Revisit when instances land.
