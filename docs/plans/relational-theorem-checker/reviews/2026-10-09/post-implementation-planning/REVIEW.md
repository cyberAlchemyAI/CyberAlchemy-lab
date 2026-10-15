# Review of the successor implementation plan

The plan is ready for bounded execution starting with P00. It fixes the main sequencing problem: public evidence/qualification/explanation consistency is addressed before richer semantic profiles. The reviewer here is the author using current implementation sources; this is not an independent review, a new Lean qualification or human assessment.

## Findings and revisions incorporated

| Finding | Priority | Current implementation evidence | Change incorporated |
|---|---|---|---|
| F01 — Public-path consistency | high | S08 compares the first actual source to a combined generated witness; S09 produces four staged modules and S13 supplies a separate guard/explainer. | P02, P03, P04: Consolidate stricter validation and both layouts before widening semantics. |
| F02 — Saved evidence completeness | high | S09 check_layout zips parts with actual evidence without an exact actual length; S13 requires both lengths to be four and correlates bound proof evidence. | P02, P09: Use the S13 strength in the shared path. This is an inspection guard gap; fresh apply requalifies and is not shown falsely accepting. |
| F03 — Resource enforcement | high | S17 bounds work before allocation and compile stages have 60-second timeouts; S11 recorded about 2.3 GiB child peak RSS and no aggregate memory cap. | P06, P10: Supervise the entire expensive pipeline, capability-check aggregate enforcement and measure before choosing defaults. |
| F04 — Provenance round trips | medium | S13 temporarily wraps the S10 reader to normalize verified documentary toolchain copies, preserving resolved authoritative bindings. | P05: Use tagged binding/report schemas; do not weaken missing proof-source failures. |
| F05 — Repeatability and shared state | medium | Bounded qualification replaces process-global compiler functions temporarily; support.sync includes not-needed in remaining and fixed build artifacts can be rewritten by later runs. | P03, P07: Inject context and isolate immutable runs; distinguish optional resolution from required remaining work. |
| F06 — Publication boundary | medium | S09 advisory lock plus final validation/os.replace/postcheck protects cooperating local writers but not an arbitrary external final-check race. | P08: Do not call rename a CAS; retain explicit mediated writer assumptions, add durability/journal recovery and reconciliation states. |
| F07 — Transport and logical claim scope | medium | JSON/normalizer/generator are tested boundaries; fresh replay is the same kernel. Generic models and source-faithful models have distinct meanings. | P00, P09, E05, E06: Preserve exact claim labels; IR proof and independent checker are separate optional targets. |
| F08 — Semantic expansion and feedback scope | medium | Atomic externally supplied conditions, direct delegation and potential/active norms are bounded; all 41 registry structures do not have full meaning proofs. V2 feedback does not close v1 R06/G4. | P01, P11, E00–E04: Formalize each expansion first; require concrete successor feedback only for the changed artifact scope. |

## Review decisions

Four read-only probes reproduced the first two findings using the accepted rich pilot proposal/result. The existing S13 guard accepted the original split evidence; the public S08 explainer rejected it with a combined-source mismatch. With only an in-memory copy’s actual-module list emptied, S09’s layout checker returned success while S13’s guard rejected the incomplete inventory. These are saved-inspection/explanation controls, not fresh qualification or application tests. See [the exact probe outcomes](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/relational-theorem-checker/reviews/2026-10-09/post-implementation-planning/readonly-probe-report.json).

Keep the accepted logical core. MemberConformance, contextual projection, sealed producers, finite closure, root lineage and arbitrary-old-model fresh extension already have accepted scoped evidence. The successor plan strengthens their transport and operational use; it does not replace the every-model theorem with one sampled closure.

Keep formalization first at two levels: P00 fixes shared claim/evidence meanings, and every selected semantic extension fixes its own independent meaning and theorem hypotheses before schema/runtime implementation. Theorems about generated typed values remain distinct from correctness of decoding raw bytes.

Unify current paths before optimization. P02 adopts the existing stronger S13 checks, P03 removes global function replacement, and P04 makes the public explainer accept checked combined and split layouts. Query absence is qualified only for a typed in-profile query and completed closure.

Require measured resource enforcement. The recorded cold/warm runs took 129.659/82.175 seconds with child peaks 2416472/2425228 KiB. These historical local measurements motivate supervision; they are not default memory budgets or general completion promises. P06 covers setup, decoding, evaluation, compilation and replay, not only Lean subprocesses. A required but unavailable cgroup policy is explicit rather than advertised as enforced.

Keep publication assumptions honest. A file rename is atomic replacement but not conditional publication against an unchanged head. P08 stays within a mediated/cooperating writer boundary and adds crash states/durability. Same-privilege arbitrary host writers remain outside that guarantee; expanding the boundary requires another design, not a stronger sentence in the docs.

Preserve provenance strictness. P05 gives documentary fields a schema without letting a producer relabel missing proof evidence as documentary. Existing 24 metadata exceptions remain exact legacy scope; no blanket proof exception is introduced. P07 isolates later benchmark/run evidence from accepted receipts.

Keep optional work optional. The reference evaluator remains selected until P10 measures a new bottleneck. New expressions, evidence collections, chains, fulfillment, lifecycle, IR verification and a second checker are separate branches. There is no promise to implement full semantics for all 41 relations through one rule profile.

Preserve human assessment scope. The actual v2 approval applies to its exact worked packet and bounded local use. A successor packet can be reviewed after real implementation evidence exists. Original R06/G4 need their own artifact-specific assessment; this plan does not ask for blanket approval or transfer earlier feedback.

## What would make the plan unacceptable

- Moving code generation ahead of the independent P00 target definitions.
- Letting callers shrink catalogs, bypass exact saved-evidence inspection or reuse saved currentness for application.
- Calling partial/incomplete search proof of absence, or new domain/fact/lifecycle changes rule-only conservativity.
- Claiming aggregate memory enforcement from a per-process virtual-memory limit, or arbitrary-writer safety from advisory locking.
- Inferring fulfillment/admission/authenticated truth from active norms, relation names, supplied receipts or kernel type checking.
- Calling author review independent, finite tests universal decoder proof, or same-kernel replay an independent checker.

## Verification performed for this planning package

The package validator passed: 12 core units, seven optional branches, all 19 predecessor task dispositions, 17 concepts, 41 relations, 176 exact retained declaration excerpts across 18 modules, 83 current input bindings and all local document links. It checks DAG reachability/acyclicity, first-step formalization, declared output namespaces, required task-card fields and current predecessor acceptance/status bytes. Four read-only probes exercise the saved-evidence/explanation boundaries. No new runtime qualification, predecessor-wide proof replay, performance or human assessment was performed. See [the validation report](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/relational-theorem-checker/reviews/2026-10-09/post-implementation-planning/validation-report.json).

The remaining choices are bounded inside future units: resource defaults/backend availability in P06/P10; selected condition truth tables in E00; assessment-collection policy in E01; lifecycle conflict policy in E04; and second-checker feasibility in E06. None blocks producing or reviewing this concrete plan.
