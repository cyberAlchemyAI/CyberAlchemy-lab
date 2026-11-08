# Measured Session-open repair

The original API64 first Session class ran 34 inherited methods: 33 passed,
while the unchanged 70-second expiry-timer method failed; 311 methods were not
run afterward. The original ledger is retained unchanged.

| Cut | Actual Session-open observation | Qualification scope |
| --- | --- | --- |
| API66 prepared metadata once | 77.784 seconds, `indeterminate` | The 70-second inherited case failed; underlying exception was not captured. |
| API68 complete physical/captured freshness | 83.493 seconds, deadline expired after claim/evidence | Same 70-second case failed; actual physical/policy/captured-memory mutation checks passed. |
| API68 ordinary open with cProfile | 106.501 seconds, result | One ordinary memory-erasure method passed; profiling adds overhead and this timing is not directly comparable to unprofiled runs. |
| API69 per-call verified-source scope | 43.461 seconds, result | Unchanged 70-second timer method passed, including actual expiry disposal, zeroed held RAM and expired inspection. |

The API68 profile identifies the redundant work: 15 Reader channel guards
accumulated 68.772 seconds; 11 repeated current Context-producer selections
accumulated 49.380 seconds; 163 input-verification calls accumulated 82.090
seconds. These are nested totals and must not be added. The schema guard alone
measured roughly one second per pass. The exact profile and logs remain in
this directory.

API69 keeps the original complete Reader proof at each Session-open call
entry. During that call it rechecks every independently pinned physical source
member, captured-memory basis, private policy/revocation/period and clock at
each guard boundary. Actor and opaque-context checks remain in the original
Service. The private scope is thread-local, cannot nest and is erased in
`finally`; Machine, metadata and Session-close paths keep their original
selection. No deadline, source period or existing Session is extended.

Twelve normal and optimized pure call-scope tests pass. A real API69 fixture
also refused physical signed-artifact changes, private-policy changes,
per-process baseline retargeting with a matching owned file, and authenticated
opaque-context substitution; all bytes were restored and its scope erased.
The first supplemental driver had a missing `copy` import, which is preserved
as a harness error; the separate corrected retry passed on identical API69
source bytes. See `API69-TIMER-PASS-0001.json` and
`API69-FOCUSED-REPAIR-RECEIPT-0001.json` for exact bindings and limits.

Four other inherited Session cases affected by the repair pass (4/4 in
948.339 seconds): same-key retry, captured-source corruption disposal, close
after current Project State drift, and private-policy revocation disposal. This
is a bounded repair proof. The combined Lesson/Agent-contest family and a
complete same-cut 345-method terminal ledger remain required for T15/T16.
