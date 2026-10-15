# Measured performance and selection

Keep the accepted evaluator and fresh proof recipe. The measured report distinguishes actual complete qualification from explicit resource refusal; no speedup or wider-profile guarantee is selected.

| Sample | Actual outcome | Client seconds | Compile tools | General replay | Source/cache guards | Evaluator process | Peak observed RSS MiB |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| rich-cold | qualified-candidate | 429.352 | 200.988 | 34.517 | 160.118 | 0.622 | 2209.8 |
| rich-warm | qualified-candidate | 236.029 | 111.858 | 55.458 | 43.507 | 0.351 | 1909.8 |
| rich-three-variables | unknown-resource | 202.878 | 155.716 | 0.000 | 27.853 | 0.500 | 1346.1 |
| rich-three-variables-repeat | unknown-resource | 195.304 | 143.385 | 0.000 | 25.932 | 0.423 | 1381.4 |

Compilation includes the projection, concrete witness, general submission and any cold local dependencies. General replay and guarded source/import currentness are retained checks. Finite evaluator-only time is separately recorded where a full payload exists; the process interval includes launch and transport. These measurements do not justify changing the evaluator or removing currentness/replay checks.

The primary workload is the richer target/scope cyclic source with sixteen domain values. Cold and warm runs use the same graph, rules and twenty-obligation catalog. The stress proposal adds two reference-variable binders to one fresh rule, producing 4,144 candidate substitutions overall without changing the graph, domain, predicate declarations, rule count or operator policy. It is a different rule meaning; a completed preflight is not a promise that its proof fits the time budget.

Recorded P09 applications took an enclosing wall interval and performed a separate proposal check and successor registration. The report retains those actual timings for their fifteen-value representative workload. Their child times are not summed again with the application total. Saved inspection/explanation timings are new read-only operations and do not create new qualification events.

The selected optimization is **none**. If a later optimization is proposed, it must target a measured cost and preserve independent equivalence targets, full closure/support checks and fresh replay. Raising deadlines or shrinking the catalog would change the operational or proof claim; neither is done here.

Limits: 4 current instrumented workload samples; successful qualification and refusal are reported separately. No general throughput or latency guarantee. Cold means local dependencies are freshly recompiled; warm means their independently anchored bytes are copied/verified. OS page-cache state and other host load were not controlled. Monotonic host clock and source-bound instrumentation remain assumptions. Group exclusive time includes Python/checking/IO overhead; it is not CPU-only time. Advisory aggregate RSS observation is not a hard memory cap. No per-stage peak RSS attribution is available. Parent/supervisor/client durations are inclusive. Unknown overhead is not reassigned to replay. No isolated commit-only duration was measured in the reused P09 records. The variable-count stress case includes the body occurrences needed to bind its extra variables. Other primary dimensions are fixed; semantic agreement is required for cold/warm, not between different rule meanings. Fresh proof replay remains through the same pinned Lean kernel. No evaluator optimization or independent-kernel assurance is selected. A zero category means that stage was not reached/executed in that sample; it does not describe the cost of completing an omitted stage.
