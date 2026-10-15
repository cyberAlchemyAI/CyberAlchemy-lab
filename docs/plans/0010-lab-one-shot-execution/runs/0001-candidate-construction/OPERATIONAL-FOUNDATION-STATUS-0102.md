# Current Lab candidate progress

**36/46 tasks closed; R03/R06 remain in progress.** The current frozen host is
API59, with twenty authored handlers and fourteen missing public operations.
Construction and isolated verification remain authorized. All-member S02
verification precedes the sole actual R08 owner checkpoint; admission and
activation remain pending.

## Implemented and verified

The full API58 export run completed twelve cases: ten PASS and two FAIL, with no
errors. Both failures found an empty lock file created during lookup before a
rejected request reached its claim. The actual failures and predecessor bytes are
preserved. The run is not qualified as passing.

API59 repairs this read operation. Empty-journal lookup writes nothing. Existing
journal lookup opens the lock without creating it. A durable journal whose lock
is missing is refused without recreation. An authorized claim still creates the
original exclusive writer lock and rechecks its exact fingerprint before dispatch.
Native source guards, authentication, permissions and real clocks are unchanged.

Four focused cases/five authenticated public calls passed with source exit and
owned fixture cleanup: the two unchanged original refusal cases, unknown-operation
inspection of an empty journal, and retry after removing a published operation's
lock. File bytes remain unchanged on each rejected or read-only request. All 305
inherited test methods and all twelve original export test bodies are unchanged.
The full fourteen-case suite on API59 is running; its result is not yet established.

Historical API58 candidate/current-source export and exact-retry proof and API57's
17 classification cases/24 calls remain exact predecessor evidence. They do not
qualify all inherited behavior on API59.

## Remaining work

The original API50 export selection completed all 134 cases, PASS/exit 0. Across
its closed selected scopes, 346 selections have completed: 342 PASS, three FAIL
and one ERROR. These are overlapping suite selections, not unique tests. The same
scheduler continues metadata86, Machine14 and termination6. Original failure
evidence and clocks remain.

Complete all current export and inherited journeys; implement all fourteen
missing operations; finish general foreign/admitted-source import, carrier,
reference and authority adapters, non-JSON privacy/encoding, nonempty
Lesson/Context/Ontology sources and actual Machine write authority. Genuine R05
participant evidence, R06/R07 and final S02/R08 remain. A01-A04 require their
separate authorization.

Currentness165 passed with 38 active receipts, 77 preserved preparation files and
887 original bound sources; no changes were detected. No complete API, genuine
pilot, actual owner outcome, canonical admission, activation or completed plan is
claimed.
