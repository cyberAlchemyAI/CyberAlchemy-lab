# Source Claim Ledger

Target: Alloy and TLA+/PlusCal for DomainSpec v2 modeling.

| ID | Claim | Source kind | Evidence | Local reading | Status |
| --- | --- | --- | --- | --- | --- |
| C1 | Alloy is an open-source language and analyzer for software modeling. | primary-source | S1 | Treat Alloy as a modeling/checking surface, not an implementation language. | accepted |
| C2 | Alloy models evolving structures as constraints and the Analyzer finds satisfying structures or counterexamples. | primary-source | S2, S4 | Strong fit for DomainSpec concept and relationship graph questions. | accepted |
| C3 | Alloy `check` searches for counterexamples and Alloy commands are bounded by scopes. | related-source | S5 | Alloy output should be read as bounded counterexample evidence unless scope discipline is explicit. | accepted |
| C4 | Alloy 6 adds mutable state and temporal logic; temporal model checking may depend on external NuSMV or nuXmv tools. | primary-source | S1, S3 | Alloy can model some dynamic behavior, but DomainSpec should still prefer TLA+ for saga execution unless the hard problem is graph structure. | accepted |
| C5 | TLA+ models systems above code level, commonly uses TLC, and PlusCal is an easier entry point for many engineers. | primary-source | S7 | Use PlusCal when the first DomainSpec temporal model benefits from pseudocode-like syntax. | accepted |
| C6 | TLA+ is state-based: behavior is a sequence of states and steps are pairs of consecutive states. | primary-source | S7 | This directly matches saga traces, compensation ordering, retry, and acceptance transitions. | accepted |
| C7 | TLA+ tools include TLC model checking, SANY parsing, a PlusCal translator, and other CLI tools through `tla2tools.jar`. | primary-source | S8 | A future task can run parser/model-check gates without adding a bespoke interpreter. | accepted |
| C8 | TLC checks finite models, while TLAPS supports deductive reasoning about infinite-state specs. | primary-source | S9 | Do not call a TLC run an unbounded proof; keep model-check and theorem-proof labels separate. | accepted |
| C9 | The existing DCB saga witness is a bounded TypeScript witness, not a proof. | local-inference | L3, L4, L6 | Keep TypeScript as extraction/witness layer, then promote targeted obligations. | accepted |
| C10 | DCB is a freshness and acceptance wrapper around proof evidence, not the behavioral proof engine. | local-inference | L4, L5, L6 | Any Alloy or TLA result should be accepted through freshness guards if non-rerunnable facts are involved. | accepted |
| C11 | TLA+/PlusCal is the first formal promotion path when temporal saga behavior is the hard class. | operator-reading | L3, L4, L5 | Use TLA+ for success safety, failure safety, compensation ordering, retries, liveness, and freshness acceptance traces. | accepted |
| C12 | Alloy is the first formal alternate when relationship graph completeness is the hard class. | operator-reading | L3, L4, L5, L6 | Use Alloy for participants, typed edges, missing compensation links, and bounded counterexample discovery. | accepted |
| C13 | `orchestrates` remains a local graph residue because DomainSpec relationships type it as `Workflow -> Operation[]`, while the saga pilot needs Saga to coordinate operations. | local-inference | L2, L5, L6 | Alloy is a good place to expose this as a counterexample or signature mismatch before mutating relationships. | open |
| C14 | Formal tool adoption should start from generated examples and validation fixtures, not by rewriting DomainSpec around a tool. | operator-reading | L1-L9 | Build adapters and examples first; promote only after tool runs pass. | accepted |

## Source-Kind Rules

- `primary-source`: stated by the main tool/source.
- `related-source`: stated by related documentation or non-local supporting material.
- `local-inference`: inferred from source-backed material in this repo.
- `analogy`: useful mapping, not source meaning.
- `operator-reading`: practical design interpretation for DomainSpec v2.
- `open-residue`: unresolved question or future task.

## Open Claim Residue

| ID | Question | Blocking artifact | Next route |
| --- | --- | --- | --- |
| R1 | Is the Alloy sketch syntactically valid and does it produce the intended missing-compensation counterexample? | `examples/OrderFulfillmentSaga.alloy` is unvalidated | task-session with Alloy Analyzer or CLI |
| R2 | Is the TLA+ sketch syntactically valid and does TLC find or reject the intended traces? | `examples/OrderFulfillmentSaga.tla` is unvalidated | task-session with `tla2tools.jar` |
| R3 | Should DomainSpec promote a `Saga -> Operation[]` relationship or represent Saga as Workflow specialization? | `orchestrates` residue | definitions-governance or dispatch-spec |
| R4 | What JSON shape should TypeScript emit for Alloy/TLA generation? | no extractor contract yet | implementation-readiness |
