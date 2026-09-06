# Related Framework Crosswalk

Target: Alloy and TLA+/PlusCal for DomainSpec v2 modeling.

| Framework or paper | Why included | Source kind | Closes residue | Boundary |
| --- | --- | --- | --- | --- |
| Alloy Tools | Main graph-structure modeling candidate | primary-source | R1, graph completeness lane | borrow |
| TLA+ and PlusCal | Main temporal behavior modeling candidate | primary-source | R2, temporal saga lane | borrow |
| TLC | Executable finite-model gate for TLA+ specs | primary-source | R2 | borrow-carefully |
| TLAPS | Later deductive proof path for stable TLA+ theorems | primary-source | proof label separation | future-work |
| TypeScript SagaSpec harness | Existing repo-local bounded witness and extraction path | local-source | R4 | borrow-carefully |
| DCB | Freshness acceptance guard around proof/model evidence | local-source | proof acceptance boundary | borrow-carefully |
| Lean | Deferred theorem prover option from prior language tournament | local-source | theorem proof future | future-work |

## Inclusion Rule

Include related work only when it closes a named residue, clarifies a source
claim, or prevents a dangerous analogy. Do not build unbounded background.

## Bridge Decisions

| Concept | Decision | Rationale | Follow-up |
| --- | --- | --- | --- |
| Alloy for graph completeness | promotion-candidate | Matches bounded relational counterexamples over DomainSpec edges. | Validate `examples/OrderFulfillmentSaga.alloy`. |
| TLA+/PlusCal for temporal saga behavior | promotion-candidate | Matches state-based execution traces, safety, liveness, and compensation behavior. | Validate `examples/OrderFulfillmentSaga.tla`. |
| TypeScript as extractor | borrow-carefully | Already works locally and can emit fixtures, but is not proof. | Define JSON fixture contract. |
| DCB as freshness guard | borrow-carefully | Valuable for non-rerunnable facts and acceptance races only. | Keep `AcceptSagaProofFreshnessClaim` boundary. |
| Lean for this first pass | future-work | Too expensive until theorem is narrow and stable. | Reassess after TLA+/Alloy results. |
| "Alloy/TLA proves DomainSpec correctness" | block | Overclaims tool output and ignores extraction/fixture correctness. | Use precise result labels. |
