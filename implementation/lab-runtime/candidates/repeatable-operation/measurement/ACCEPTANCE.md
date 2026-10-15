# C03 measurement acceptance assessment

Status: bounded evidence collection complete; performance thresholds flagged.

All 14 declared operation/case combinations are accounted for. Nine combinations produced three repeatable successful samples with variance and identical output digests. Three session samples at one transaction exceeded 30 seconds; five-transaction setup exceeded its 45-second limit, leaving four downstream combinations explicitly unmeasured. There are 27 successful samples, 3 failed sample attempts and 4 setup-blocked combinations. The runner printed 42 nominal samples by multiplying every combination by three; that summary count includes unattempted cases and must not be used as actual evidence. Per-result sample arrays are the source for actual counts.

| Operation | Transactions | Mean seconds | Outcome |
| --- | --- | --- | --- |
| independent_source_capture | None | 1.240774 | measured |
| source_byte_hashing_in_memory | None | 0.004086 | measured |
| full_replay | 0 | 0.466124 | measured |
| one_work_schema_validation | 0 | 0.009201 | measured |
| graph_build | 0 | 0.123936 | measured |
| session_context_and_close | 0 | 3.593027 | measured |
| full_replay | 1 | 7.877645 | measured |
| one_work_schema_validation | 1 | 0.016554 | measured |
| graph_build | 1 | 0.415886 | measured |
| session_context_and_close | 1 | unmeasured | bounded-failure |
| full_replay | 5 | unmeasured | blocked-by-setup-budget |
| one_work_schema_validation | 5 | unmeasured | blocked-by-setup-budget |
| graph_build | 5 | unmeasured | blocked-by-setup-budget |
| session_context_and_close | 5 | unmeasured | blocked-by-setup-budget |

The observed repeated schema meta-validation and reconstruction supports examining compiler reuse. C06 permits a measured no-op: retain the complete verifier until a coherent runtime can bind compiler reuse to exact inputs and demonstrate parity. These measurements establish neither a Product SLA nor performance at five transactions. The original two failed attempts remain immutable. Resource limits bound the experiment and report failures; they are not silently weakened to claim runtime acceptance.

Receipt PASS describes the C03 reporting criterion only. C09/C13 still require integrated runtime and acceptance evidence. No genuine work episode, human pilot, canonical admission or live operation occurred.
