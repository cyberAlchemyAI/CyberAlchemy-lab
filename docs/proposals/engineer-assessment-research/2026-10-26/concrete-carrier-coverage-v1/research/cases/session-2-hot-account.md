# `EA-C2-LEDGER-001`: hot-account transaction limit

Status: **draft, not released**. Family: existing-system evolution with a scale/failure reveal. Intended research construct: technical and product design judgment for an illustrative backend payments role. This is a case fixture, not financial-system guidance. [Role trace](role-business-trace.md) and [common case contract](README.md) apply.

## Participant-visible question protocol

**Context.** A product lets customers set a daily outgoing-transfer limit. An existing service receives transfer requests, checks an account's remaining daily allowance in a relational database, then writes a transfer and a ledger entry. Requests carry a client request ID, and callers may retry after a timeout. The team wants to preserve correct limits and ledger entries while keeping legitimate transfers responsive. You may state reasonable assumptions; explain which ones affect your design. You are the engineer asked to propose the next design and rollout.

**Turn 1: clarify and propose.** “What would you ask product, risk and operations before changing this? Sketch the data and request path. How would you ensure that two requests for the same account cannot jointly exceed the remaining allowance, while unrelated accounts can be processed efficiently? What would you measure?”

**Fixed reveal.** “A small number of business accounts now receive many simultaneous requests. The limit row for one such account becomes a hot partition/row; lock waits rise and several transactions deadlock and retry. During peak traffic the 99th percentile completion time worsens. The product owner asks for lower latency without a limit breach. How do you diagnose and revise the design, and what would you ship first?”

**Closing probe.** “Walk through a retry after an unknown outcome, a transfer that fails after a reservation, and a rollback of your change. Name one tradeoff you would accept and one result that would make you reverse the decision.”

Administration target: 10 minutes of recorded answer, with the reveal at a frozen time/turn under the Administration Policy. A candidate may use a simple diagram or text outline in a supported mode. Raters see the exact reveal timing and whether the candidate received the closing probe. There is no requirement to write code or name a vendor.

## Reviewer-only fact and answer-space blueprint

Before release, the case author must define the day/time-zone boundary, whether a limit applies to authorized versus settled amounts, partial failures/refunds, account/tenant boundary, ledger invariants, throughput range, accepted freshness, and what the product means by “completion.” The current wording deliberately invites these clarifications; it cannot be scored as a factual implementation specification until experts freeze answers or explicitly allow multiple interpretations. Illustrative fixture choices for trial only: a per-account rolling or calendar-day limit (pick one), an idempotency key unique within customer/account scope, and a ledger that must balance after committed transfers. Numerical limit, throughput and SLO values belong in the versioned case; none are assumed here.

At least two defensible solution families should survive expert review:

1. **Database transaction with a conditional allowance update and ledger write.** Atomically reserve/decrement remaining allowance within the same transactional boundary as transfer state, then make retries idempotent. Discuss isolation, contention, lock ordering, deadlock retry with bounded backoff and how an external payment side effect is reconciled. This is often simpler to operate but one hot account may still serialize and wait.
2. **Per-account serialization or partitioned command processing.** Route requests for an account through one ordered owner/queue and durable state, while processing different accounts in parallel. Define durable acknowledgement, crash recovery, duplicate handling and how the authoritative ledger/limit state stays consistent. It can reduce lock churn or smooth load but adds queue/ownership, lag and operational complexity; a single hot account still has finite throughput.
3. A **reservation/escrow or quota split** can be explored if its consistency, expiry, reconciliation and worst-case overspend bounds satisfy the business invariant. It is not automatically superior; if strict no-breach is binding, an eventually consistent cached counter alone is not sufficient.

The case tests **concurrency** (overlapping requests that can race on one account) and **parallelism** (work for independent accounts can run simultaneously) separately. A candidate should identify that a hot account creates serialization or coordination even when more workers are added. Deadlock is a cycle among lock dependencies, whereas ordinary lock wait/serialization is contention; reviewers must not treat them as synonyms. Complexity includes algorithmic/workload growth, lock/queue behavior and the human/operational cost of more components. Credit an explanation of the actual limiting resource and measurement plan over an unsupported `O(n)` label or stack choice.

| Quality/requirement axis | What a strong answer reasons about | Weak or invalid shortcut |
| --- | --- | --- |
| Money/limit correctness | Atomic enforcement under races, precise limit window, transfer/ledger state, idempotent retries, recovery/reconciliation. | Read-then-write counter without a concurrency guard; assuming exactly-once delivery. |
| Consistency and latency | Which state is authoritative; which reads can lag; p95/p99, lock wait, queue delay, duplicate rates; latency cost of stronger coordination. | “Use eventual consistency” while still promising a strict no-breach rule. |
| Hot key and throughput | Per-account versus cross-account capacity, partition skew, bounded queues/backpressure, account-local serialization and overload behavior. | Add shards/workers while keeping every request on the same hot row. |
| Deadlock and failure | Lock order/transaction size, deadlock detection, safe retries, ambiguous external outcome and compensating/reconciliation path. | Retry blindly, double-charge, or count every slow request as deadlock. |
| Product and rollout | Prioritize correctness/user harm, define degraded behavior, staged migration, observability, rollback and decision trigger. | Claim a faster design without a correctness or customer-impact test. |

## Dimension-level scoring opportunities

Use the universal `0–4` strength anchors and evidence-span rules in [scoring-model.md](../scoring-model.md). The examples below describe `2` (plausible with gap), `3` (specific and defensible) and `4` (survives reveal and names residual risk). They are **not** required phrases or a fixed architecture answer key.

| Dimension | Elicitation and observable evidence | `2` example | `3` example | `4` example / `NA` condition |
| --- | --- | --- | --- | --- |
| `Q` requirement discovery | Opening question: asks about limit semantics, users, failure harms, traffic, latency, retries or external side effects; states assumptions. | Names a relevant missing fact but designs as though it were known. | Prioritizes correctness/limit and latency questions and branches design on answers. | Identifies a consequential ambiguity (such as authorization vs settlement) and shows how different answers change the design; `NA` only if clarification was omitted by administration. |
| `P` product priority | First design and reveal: chooses what to protect/ship first and explains customer and business consequences. | Says correctness matters but gives no sequencing or degraded behavior. | Protects a stated invariant, picks a feasible first mitigation and explains latency/cost impact. | Provides a measurable release/rollback threshold and addresses false rejection/availability as well as breach risk; `NA` only if no product choice was asked. |
| `B` boundaries/data flow | Sketches request, authoritative allowance, transfer and ledger state, idempotency and failure boundaries. | Coherent components but one important race/commit boundary is vague. | Explains an atomic or serialized mechanism and independent-account parallelism. | Walks through duplicate and failure interleavings without losing the invariant, while naming an unresolved boundary; `NA` only if design path was not requested. |
| `T` quality tradeoff | Reveal: compares consistency, hot-key throughput, latency, operational complexity and at least one alternative. | Names a tradeoff but not its mechanism or cost. | Explains why chosen coordination meets the invariant and where p99/throughput suffers. | Compares two viable approaches under different workload/semantics and gives a metric/condition for switching; `NA` only if no alternative or quality goal was elicited. |
| `O` operation/failure | Reveal/closing: diagnoses wait vs deadlock, safe retry, backpressure, metrics, staged rollout/rollback. | Gives monitoring or retry plan with a material safety gap. | Distinguishes contention from deadlock and names safe retry plus a rollout check. | Covers ambiguous outcomes/reconciliation and a tested rollback, with residual incident risk; `NA` if the reveal/closing probe was not administered. |
| `V` revision | Explicitly changes or defends design in response to hot-account evidence. | Adds workers/cache without checking the new constraint. | Revises bottleneck mechanism and preserves correctness. | Revises priority/design/measurement coherently, including what earlier assumption failed; `NA` if the fixed reveal was not delivered. |

Do not reward verbosity, a named database, algorithm jargon or a diagram by itself. If the response gives an unusual but valid scheme, raters test its invariants and consequences rather than compare it with the listed solution families. If the prompt/reveal contains contradictory facts, hold the case and do not convert the resulting uncertainty into candidate zeros.

## E02/E03/E05B checks

- **Content review:** two or more independent architecture/product reviewers (count to be registered) test race/failure interleavings, two viable designs, exact limit semantics, realistic latency/throughput facts and ten-minute burden. A bank-domain reviewer checks vocabulary and whether required facts are supplied.
- **Trial:** ask volunteers what “limit,” “deadlock,” “completion” and “ledger” meant, and whether the reveal changed their design. Track familiarity and whether domain knowledge, rather than reasoning, predicts the answer. Revise through a new candidate version.
- **Calibration:** blind raters score concise, novel-valid, fluent-but-incorrect, domain-naive and diagram/text answers; record `NA/UNK`, cited spans and disagreement. Compare transcript correction and direct recording review.
- **Transfer:** use an unseen product domain and a written/diagrammed work sample with race/failure scenarios; blind reviewers judge correctness, requirements, tradeoffs, operation and revision. Later work evidence, if available, is separate and opportunity-adjusted. Compare the verbal case with an equal-time design task.

Exposure to a public “bank hot account” interview pattern is a specific rival. Record prior familiarity; hold out this mechanism family when testing transfer. The candidate case is **not ready for release** until facts, level, role trace, anchors and administration policy are frozen and independently reviewed.
