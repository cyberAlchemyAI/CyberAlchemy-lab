---
node_type: implementation-layering
is_session: false
status: candidate
created: 2026-07-01
authored_by: invoke (mode: plan)
work_pack: ./WORK-PACK.md
define: ../DEFINE.md
design: ../DESIGN.md
---

# Spec–Ontology Toy — Implementation Layering

**Layer-boundary heuristic:** each layer produces one artifact the next strictly needs; the criterion
is only *measured* at L2 (after it is frozen), so no layer can "pass by preference". Promotion requires
the previous layer's artifact to exist and be reviewable.

| Layer | Slice | Minimum working unit | Promotion evidence |
| --- | --- | --- | --- |
| **L0 — extract** | T1 | The spec-graph for financial-settlement: a typed node list + typed edge list. | Node/edge inventory exists; every item carries a TAXONOMY/RELATIONSHIPS type (or is flagged unclassifiable = an M1 signal). |
| **L1 — map** | T2, **T2b** | T2: node→pattern + edge→composition for the *corpus's* types. **T2b (added 2026-07-01): the feature-independent catalog check — all 25 types + all 29 edges (author the 19 missing rules) + M0.** | Both corpus tables filled (T2); catalog coverage recorded + the 19 edge rules written or gap-flagged → R3 (T2b). |
| **L2 — run + attack** | T3 | The paper pattern-skeleton + M1–M4 computed + the attack break-list. | Criterion FROZEN first; M1–M4 reported with the exception lists; determinism re-run matches; attack lenses all exercised. |
| **L3 — compare + verdict** | T4 | Lane A sketch + SURVIVED/FALSIFIED/INVALID verdict + promotion recommendation. | Verdict cites M1–M4 against the frozen bars; Lane A weighed; recommendation respects the promotion boundary. |

**Dependency order:** T1 → T2 → **T2b** → T3 → T4 (T2b consumes T1+T2; T3 consumes M0 from T2b).

**Recomposition:** L0–L3 produce the evidence the SEED tower needs to close Lane Z-vs-A — the decision
the 2026-07-01 research explicitly deferred here.

**Boundary carried down every layer:** local research only (no spec/code mutation); engine black-box;
authority flows spec → toy, never back.
