# DAG-to-interface traceability

Every DAG task has a declared interface contract. This records interface coverage, not implementation completion.

| Task | Layer | Contract | Status |
|---|---|---|
| P01 — Define the relational semantics and theorem targets | L0 | C-normalizeGraph | interface candidate; task not started |
| P03 — Formalize typed graphs and independent validity predicates | L0 | C-normalizeGraph | interface candidate; task not started |
| P04 — Define the reference checker in Lean | L0 | C-checkAddition | interface candidate; task not started |
| P05 — Prove and review general reference-checker soundness | L0 | C-checkAddition | interface candidate; task not started |
| B00 — Refresh the execution baseline after formalization | L0 | C-captureSnapshot | interface candidate; task not started |
| P02 — Align schemas and implement decoding from the formal model | L0 | C-normalizeGraph | interface candidate; task not started |
| P06 — Produce a bound demonstration and hostile controls | L0 | C-checkAddition | interface candidate; task not started |
| G0 — Review the working proof gate | L0 | C-checkAddition | interface candidate; task not started |
| C01 — Resolve the effective registry snapshot | L1 | C-captureSnapshot | interface candidate; task not started |
| C02 — Reconcile carrier and registry coverage | L1 | C-reviewBundle | interface candidate; task not started |
| C03 — Generalize registry-driven checking | L1 | C-normalizeGraph | interface candidate; task not started |
| C04 — Resolve qualified references | L1 | C-reviewBundle | interface candidate; task not started |
| C05 — Measure semantic coverage and exercise the baseline | L1 | C-reviewBundle | interface candidate; task not started |
| C06 — Make replay deterministic and invalidate stale evidence | L1 | C-replayBundle | interface candidate; task not started |
| G1 — Review the faithful baseline gate | L1 | C-reviewBundle | interface candidate; task not started |
| E01 — Classify relation-change proposals | L2 | C-deriveObligations | interface candidate; task not started |
| E02 — Derive the required obligation set | L2 | C-deriveObligations | interface candidate; task not started |
| E03 — Check compatibility and prove preservation | L2 | C-reviewBundle | interface candidate; task not started |
| E04 — Check inhabited models and conservative expansions | L2 | C-checkModel | interface candidate; task not started |
| E05 — Compose the compatibility and invalidation report | L2 | C-reviewBundle | interface candidate; task not started |
| G2 — Review supported non-rule extension readiness | L2 | C-reviewBundle | interface candidate; task not started |
| I01 — Specify the restricted inference and root profile | L3 | C-checkDerivation | interface candidate; task not started |
| I02 — Check derivation certificates and prove soundness | L3 | C-checkDerivation | interface candidate; task not started |
| I03 — Check the least fixed point and completeness | L3 | C-checkClosure | interface candidate; task not started |
| I04 — Prove protected lineage through indirect chains | L3 | C-reviewBundle | interface candidate; task not started |
| I05 — Check independence and non-entailment witnesses | L3 | C-checkModel | interface candidate; task not started |
| I06 — Discharge rule-change extension obligations | L3 | C-reviewBundle | interface candidate; task not started |
| G3 — Review inference discipline | L3 | C-reviewBundle | interface candidate; task not started |
| R01 — Define CLI and outcome contracts | L4 | C-reviewBundle | interface candidate; task not started |
| R02 — Verify proof submissions and fresh replay | L4 | C-verifyProof | interface candidate; task not started |
| R03 — Verify evidence bundles and aggregate obligations | L4 | C-reviewBundle | interface candidate; task not started |
| R04 — Integrate CLI and CI diagnostics | L4 | C-reviewBundle | interface candidate; task not started |
| R05 — Recheck the application baseline in a candidate adapter | L4 | C-recheckApplication | interface candidate; task not started |
| R06 — Run a representative shadow pilot | L4 | C-reviewBundle | interface candidate; task not started |
| G4 — Review supported use and audit plan alignment | L4 | C-reviewBundle | interface candidate; task not started |
