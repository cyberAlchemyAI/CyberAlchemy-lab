---
node_type: skeptic-memo
gate: definitional-soundness
skeptic: Rittel, Horst
target: findings.md (Jacobs synthesis, 2026-06-30)
date: 2026-06-30
verdict: PARTIAL-COLLAPSE — net-new content is real but narrow; one claim collapses; one is a re-label
---

# Skeptic Gate — Definitional Soundness

## Collapse test: does the model reduce to D30 alone?

**D30's schema requires:** artifact · altitude · owner · gate · residue · recomposition · stopping-condition.
The synthesis adds: (a) the μF/νF spine-vs-drift split, (b) a typed decidable atomic-leaf base case, (c) Model A vs B.

**μF/νF split — net-new, does NOT collapse to D30.**
D30 says "stopping condition" but gives no typed criterion for what constitutes one. The synthesis asserts that only a `classifyFormal`-style one-step decidable verdict qualifies as a stopping condition in this domain, and that drift/trend fails this criterion and is therefore coinductive (νF). That is a substantive, checkable claim D30 does not entail: you could satisfy D30 with a viability-rooted stopping condition (e.g. VSM operational closure) and be definitionally compliant with D30 while the synthesis would reject it. The split adds real, decidable content — specifically the **exclusion criterion**: a stopping condition that is not a one-step finite verdict is not a valid μF leaf here, regardless of D30 compliance.

**Decidable atomic-leaf base case — net-new and checkable.**
D30 requires a stopping condition but is silent on its computational character (decidable vs. semi-decidable vs. viability-based). The synthesis pins "stopping condition" to `classifyFormal`-style totality over finite `G` in one engine step. This is falsifiable: produce a level-2 governed node whose `check` arm has no such leaf → the model fails even if D30 is satisfied. D30 alone cannot make that judgment.

**Model A vs B — COLLAPSES to write-authority proviso already in D30.**
D30 states "authority boundaries must be preserved; owner route must remain distinct unless an explicit promotion or coupling records otherwise." Model A (each governance owns its own norm) versus Model B (one central law-node) is precisely the question of whether a single owner route is collapsed across governed nodes without a recorded coupling — which D30's authority-boundary clause already answers negatively. The synthesis's functional argument (B breaks the functor's recursive position) is a useful restatement, but the normative verdict — distributed ownership is required — is already entailed by D30. This is a re-label, not net-new content.

**VSM / reflection-tower collapse test — does not collapse.**
D17 (reflection tower) requires unresolved residue to seed a higher layer. The synthesis's νF/coinductive drift factor is not a residue-climb: it runs in parallel with the μF spine, not above it, and its bound is guardedness/productivity rather than a new schema + recomposition path. The two are structurally distinct; the synthesis does not re-skin D17.

## Typed verdict

| Claim | Status |
|---|---|
| μF/νF split (spine vs drift) | NET-NEW — decidable, falsifiable exclusion criterion not entailed by D30 |
| Decidable atomic-leaf base case | NET-NEW — pins D30's "stopping condition" to a checkable computational class |
| Model A vs B | COLLAPSES — re-label of D30's write-authority / owner-route proviso |
| VSM / D17 re-skin | DOES NOT COLLAPSE — structurally distinct from both |

**Overall:** not a tautology; not a re-skin of D30 or D17. Two claims survive the gate with real content. One claim (Model A/B) is derivable from D30 and should be demoted to a corollary, not a top-level decision. The synthesis's load-bearing residue (R-leaf-inhabitation, R-trend-type) correctly locates where the net-new claims are unwitnessed — those residues are the only honest anchors for the gate.
