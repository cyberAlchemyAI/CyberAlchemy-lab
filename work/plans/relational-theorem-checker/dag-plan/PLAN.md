# Relational model and theorem checker plan

> Generated from [PLAN-SOURCE.json](../PLAN-SOURCE.json).
> Standalone candidate. 33/35 tasks accepted with hash-bound evidence; see task receipts for review scope. No formal Invoke admission is claimed.

The plan contains **35 tasks**, **40 working units**, **56 dependency edges**, **31 execution waves**, and **five layer evidence gates**.

## Reading map

- [Full Mermaid DAG](DAG.md) and [machine-readable graph](dag.json)
- [Task board and working units](WORK-PACK.md)
- [Execution protocol and waves](EXECUTION-PACK.md)
- [Validation strategy](VALIDATION-STRATEGY.md) and [planning check](receipts/planning-check.json)
- [Planning provenance](PLANNING-PROVENANCE.json)

## Layer closure

| Layer | Gate | Allowed conclusion |
|---|---|---|
| L0 | [G0](work-pack/tasks/G0.md) | Three-kind slice with independent semantics and a general checker soundness theorem. |
| L1 | [G1](work-pack/tasks/G1.md) | Faithful selected registry with explicit structural and semantic coverage. |
| L2 | [G2](work-pack/tasks/G2.md) | Supported non-rule extensions only; rule obligations remain open for L3. |
| L3 | [G3](work-pack/tasks/G3.md) | Supported finite rule profiles with derivation, closure and protected-lineage evidence. |
| L4 | [G4](work-pack/tasks/G4.md) | Reviewed candidate workflow and bounded-use recommendation; no actual admission or deployment. |

## Start here

Start with F0 formalization: P01 defines normative relational semantics and theorem targets; P03 formalizes typed finite inputs and independent validity; P04 defines the pure reference checker in Lean; P05 proves general soundness and closes the formalization review. B00 then refreshes execution source bindings and P02 aligns the candidate schemas/APIs and decoder with the proved model. All later tasks depend transitively on accepted P05 evidence.
Use the captured research sources for formalization. If the later B00 refresh detects relevant drift, invalidate the affected formal evidence and replan/reprove before adapters proceed. Existing schemas/APIs remain draft projections until P02 alignment. Earlier research documents retain their captured bytes; this plan supersedes their prior implementation ordering.

## First phase exit evidence

- Reviewed independent semantic definitions
- Lean reference checker over typed finite graphs
- General checker soundness theorem
- Checked inhabited example
- Exact statement, dependency and transitive-axiom audit

## Scheduling

No durations or deadlines are assigned. Longest paths are dependency-depth paths, not a duration-based critical path.
Estimate effort and dates after selecting the L0 semantic contract, reviewer capacity and proof toolchain. Dependency depth is the ordering metric currently supported by evidence.

## Scope and preserved state

Future implementation is proposed under `craft/formalization/candidates/relational-theorem-checker/v1/`. Tasks do not authorize edits to immutable authority records, existing Lean modules, live governance stores, runtime state, credentials or keys. The final output is a bounded-use recommendation.

## Decisions before dependent work

| Decision | Due before | Owner role | Direction to record |
|---|---|---|---|
| D00 | P03 | proof reviewer | Pin the initial Lean toolchain, approved axioms and exact required soundness statement. Record reproducible checked proof dependencies and retain parser, hashing and compiled-runtime assumptions explicitly. |
| D01 | P01 | semantic reviewer | Select the L0 graph invariant and normative qualifier/reference semantics. Use the three-kind slice and smallest meaningful invariant from the analysis; record a reviewed contract in P01. |
| D02 | C02 | schema and governance reviewer | Select the companion/successor carrier policy for full registry coverage. Keep frozen Typed Relation/v2 bytes and propose a separate explicit carrier profile. |
| D03 | E02 | semantic and proof reviewers | Select the first supported extension profiles and exact compatibility promises. Instance additions under fixed theory first; add definitional new-kind profiles only with evidence. |
| D04 | I02 | semantic and governance reviewers | Select protected conclusions and legitimate exact-scope root justification. Constrain targetVersion, effect, scope and epoch; preserve independently justified existing facts. |
| D05 | R02 | proof and integration reviewers | Select toolchain, proof-submission isolation, accepted axioms and evidence thresholds. Pin dependencies and replay isolated submissions with exact statement and axiom audits. |

## Non-regression contract

- Formal semantics, a Lean reference checker and its general soundness proof precede runtime adapters and schema/API alignment.
- Exact ordered relation pairs; never the Cartesian product of source and target projections.
- Validity is independent of the checker result.
- Nonempty checked models for selected use cases; no vacuous readiness.
- Conformance does not justify admission; independently justified admission may coexist.
- No bounded-search exhaustion is labeled theorem evidence.
- Complete hard obligations are independently generated; submitted lists cannot shrink them.
- Preserve parser, hashing and compiled-runtime trust boundaries until separately verified.
- Candidate evaluation does not create authority, runtime activation or external effect.
