# Successor work-pack: bounded task specifications

Status: proposal. All commands/checks below describe future verification, not execution performed by this review. Each task owns one working unit and writes only under its proposed v2 subdirectory. No code implementation directory is created here.

The task execution contract is the machine-readable [plan](plan-proposal.json). Inputs are current scoped exports; semantic/source/statement drift requires recapture. No task may alter accepted v1 bytes to pass a successor test.

## S00 — Formalize successor meanings and independently required statements

Layer: N0. Dependencies: none; formalization first. Working unit: SWU-S00.

Write scope: `/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v2/s00`.

Inputs: Current F0 semantic definitions and audited statement types; REVIEW.md findings F01-F05/F10; DESIGN-PROPOSAL.md proposed defaults.

Outputs: `semantic-contract.md`, `RequirementSemantics.lean`, `RequiredStatements.lean`, `decisions.json`, `assumption-register.json`.

Ordered algorithm:

1. Define graph-member contextual conformance and exact target-kind meaning independently from a projector.
2. Specify fixed-domain recursive ordinary extension and explicit condition-status meanings.
3. Fix projection, existential view, support, closure, old-model expansion and root-boundary theorem types; check well-formed Lean types.
4. Record choices for target-kind view, domain growth and context/epoch; never define correctness as checker success.

Edge/failure cases: Unasserted valid edge; Non-contract allowed F0 target; New scope outside current domain; No conformance or no initial seed; Supplied truth versus authenticated truth.

Acceptance:

- Independent definitions and required types compile under the pinned policy.
- Every new guarantee and assumption has a requirement ID; deferred negation has no runtime rule.
- Source meanings and proposed defaults are reviewable before schema/runtime changes.

Verification / required evidence:

- Lean type-check required definitions/statements without custom axioms or sorry.
- Review definitions against concrete rich and collapsed examples.

## S01 — Build semantic requirement ledger and premise-removal challenges

Layer: N0. Dependencies: S00. Working unit: SWU-S01.

Write scope: `/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v2/s01`.

Inputs: S00 requirement IDs; Existing coverage ledger and countermodels.

Outputs: `requirements.json`, `mutation-catalog.json`, `adequacy-report.json`.

Ordered algorithm:

1. Map each selected source requirement to an independent predicate, statement, assumption or unsupported status.
2. Attach positive/negative cases and applicable mutant removing exactly one required condition.
3. Run named controls; retain countermodels that show why a premise is necessary.
4. Keep every inherited unsupported item until its own source/meaning evidence exists.

Edge/failure cases: Duplicate assessment token; Scope/version substitution; Missing graph membership; Revocation removed; Conflict interpreted as explosion.

Acceptance:

- No selected requirement is silently unclassified.
- All applicable named mutants are detected; exclusions have explicit reasons.
- The ledger distinguishes structural checks, supplied truth and semantic theorems.

Verification / required evidence:

- Validate requirement references and current source bindings.
- Run the finite semantic witness/mutation suite; record exact failed property and profile.

## S02 — Prove the contextual graph-to-fact bridge

Layer: N0. Dependencies: S01. Working unit: SWU-S02.

Write scope: `/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v2/s02`.

Inputs: S00 independent projection targets; S01 required positive/negative cases; F0 invariant and graph definitions.

Outputs: `ContextProjection.lean`, `ProjectionProofs.lean`, `projection-fixtures.json`, `projection-audit.json`.

Ordered algorithm:

1. Enumerate member conformance assertions of a graph satisfying the selected invariant.
2. Project exact subject/target references and scope, plus checked target-kind observations.
3. Build complete support sets for deduplicated initial atoms and derive the unary existential view.
4. Prove soundness, completeness, support validity and exact existential correspondence.

Edge/failure cases: Two edges supporting one atom; Wrong scope/target kind/target revision; Valid edge absent from graph; No assertion facts; Out-of-domain scope requires another baseline.

Acceptance:

- Required independent theorem types are proved and audited.
- A specific contract/scope query cannot use only unary conformance.
- v1 meanings are unchanged and domain/profile differences are explicit.

Verification / required evidence:

- Fresh kernel replay of required statements and axiom/dependency closure.
- Execute wrong-contract, wrong-scope, wrong-kind, nonmember and duplicate-support controls.

## S03 — Prove finite recursive fresh-definition expansion

Layer: N1. Dependencies: S02. Working unit: SWU-S03.

Write scope: `/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v2/s03`.

Inputs: S00 extension contract; Existing generic derivation/closure proofs; S02 contextual vocabulary.

Outputs: `RecursiveExtension.lean`, `RecursiveConservativity.lean`, `recursive-countermodels.json`, `recursion-audit.json`.

Ordered algorithm:

1. Fix old interpretation for an arbitrary old semantic model.
2. Iterate only fresh ordinary heads over the finite typed universe with positive old/fresh bodies.
3. Prove monotonicity, stabilization, closure, old-reduct equality and every-old-model expansion.
4. Check all producer roles and reject old/protected heads or changed domain/roots.

Edge/failure cases: Seeded cycle; Unseeded cycle; Nonempty valid old baseline; Old rule/predicate mutation; Fresh protected predicate; Domain growth.

Acceptance:

- Every old model expands under independently checked profile hypotheses.
- Unseeded cycles create no facts; protected/root inventories are preserved.
- Unsupported domain/old-head changes remain blocked with precise reasons.

Verification / required evidence:

- Audit exact general conservativity/termination statements in Lean.
- Run multi-step/cycle and hostile old-head/root controls.

## S04 — Formalize interpreted conditions and stress source mappings

Layer: N1. Dependencies: S01. Working unit: SWU-S04.

Write scope: `/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v2/s04`.

Inputs: S00 condition/source contracts; Legacy acts-for/inherits-contract source records; Typed stress semantics.

Outputs: `InterpretationSemantics.lean`, `ConditionSemantics.lean`, `MappingStatements.lean`, `field-map.json`.

Ordered algorithm:

1. Define exact source qualifier interpretation witnesses and context bindings.
2. Separate holds, explicit does-not-hold and unknown; positive conclusions require checked holds.
3. Map every selected field into typed input or explicit unsupported/opaque status.
4. Define/prove supported mapping and snapshot soundness without asserting external authenticity.

Edge/failure cases: Opaque period without interpretation; Missing condition/gate; Wrong node kind/revision; Revocation boundary; Overrides and redelegation chains.

Acceptance:

- All fields and assumptions are accounted for.
- Missing interpretation remains unknown rather than false or permission.
- No unsupported chain/override meaning is silently supplied.

Verification / required evidence:

- Compile independent mapping/condition statement targets and prove supported correspondence.
- Review field maps against literal source shapes and typed stress records.

## S05 — Align successor transports and implement checked projection

Layer: N2. Dependencies: S02. Working unit: SWU-S05.

Write scope: `/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v2/s05`.

Inputs: S02 formal projector and support proofs; Main and stress current CLI contracts.

Outputs: `request.schema.json`, `support.schema.json`, `projection-adapter.py`, `capability-manifest.json`, `transport-audit.json`.

Ordered algorithm:

1. Version contextual input/output/profile transports without changing reserved v1 contracts.
2. Strictly decode, bind sources and generate typed projection input.
3. Check projection/support witnesses against exact graph/profile identity.
4. Publish explicit domain, target-kind, theorem and trust requirements.

Edge/failure cases: Duplicate JSON keys; Wrong rich predicate arity/sort; Dangling support edge; Altered assessment binding; Older v1 receipt used for v2.

Acceptance:

- Transport outputs agree with formal projection on selected controls.
- Missing projection proof/support or changed identities block result readiness.
- Adapter remains a tested trust boundary unless equivalence is separately proved.

Verification / required evidence:

- Schema positive/negative validation and fresh kernel differential projection checks.
- Retain v1 fixture regression and reject old/new profile substitution.

## S06 — Integrate recursive profile and complete new obligation inventory

Layer: N2. Dependencies: S03, S05. Working unit: SWU-S06.

Write scope: `/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v2/s06`.

Inputs: S03 actual recursion hypotheses and proofs; S05 profile transports; Existing exact statement verifier/obligation generator.

Outputs: `recursive-runtime.py`, `obligation-catalog.json`, `rule-bundle.schema.json`, `recursive-workflow-audit.json`.

Ordered algorithm:

1. Classify actual old/fresh vocabulary, rules, domain and roots.
2. Independently generate the complete new required obligations, including projection and actual recursion hypotheses.
3. Check certificates, complete closures, exact witnesses and general expansion evidence.
4. Aggregate only allowed current evidence methods; preserve unknown/unsupported/stale outcomes.

Edge/failure cases: Caller-shrunken inventory; Weakened expansion statement; Cyclic certificate without earlier premises; Nonempty old baseline; Mixed domain/fact/rule changes.

Acceptance:

- Recursive ordinary cases become supported only with the new proof profile.
- Actual hypotheses/witnesses and general theorems are separately discharged.
- No assumption that the new inventory must still contain exactly 15 obligations.

Verification / required evidence:

- Fresh complete recursive proposal replay plus missing/wrong/stale evidence controls.
- Independently compare required versus returned obligation IDs.

## S07 — Implement explicit registry-to-stress adapters

Layer: N2. Dependencies: S04, S05. Working unit: SWU-S07.

Write scope: `/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v2/s07`.

Inputs: S04 field mappings and condition proofs; Typed stress CLIs and assessment sources; S05 binding transports.

Outputs: `interpretation.schema.json`, `delegation-adapter.py`, `inheritance-adapter.py`, `mapping-audit.json`.

Ordered algorithm:

1. Resolve exact registry/source and interpretation record versions.
2. Check endpoint kinds and every mapped qualifier; create typed stress inputs with exact snapshot binding.
3. Evaluate only supported direct delegation and fixed norm profiles.
4. Export scoped condition/norm facts with checked support and residual assumptions.

Edge/failure cases: Malformed/opaque interval; Missing policy or gate; Condition mismatch; Stale snapshot; Overrides; Permitted redelegation without supported chain.

Acceptance:

- Exact mappings are checked; registry semantic ledger only advances for discharged named items.
- Typed profile successes cannot be generalized to unmapped legacy inputs.
- Inheritance does not produce fulfillment or admission.

Verification / required evidence:

- Differential mapping controls against typed stress examples and source records.
- Kernel witness/revocation/origin controls plus strict interpretation transports.

## S08 — Publish explanations and current capability/status documentation

Layer: N3. Dependencies: S05. Working unit: SWU-S08.

Write scope: `/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v2/s08`.

Inputs: S05 checked support and manifests; Current baseline receipts, pending human review; Existing CLI outcomes/certificates.

Outputs: `explain.py`, `CURRENT-STATUS.md`, `API.md`, `explanation-fixtures.json`, `docs-audit.json`.

Ordered algorithm:

1. Render exact assertion, assessment, target kind, scope, projection, rule substitution and theorem scope.
2. Display supplied-truth assumptions and lossy unary views explicitly.
3. Generate separate machine/acceptance/human/authority statuses and link historical designs.
4. Describe main and stress exit conventions and optional future HTTP design accurately.

Edge/failure cases: Partial closure/search; Unsupported profile; Stale explanation input; Same atom with multiple supports; Saved machine pass with pending human review.

Acceptance:

- Explanations identify concrete source and blocking obligation without upgrading readiness.
- Current index contradicts no accepted current operation/status evidence.
- No historical source/accepted export is silently rewritten.

Verification / required evidence:

- Check explanation fixtures/links and exact currentness/status mappings.
- Conduct usability review with the wrong-contract/scope example.

## S09 — Qualify composed contexts and successor shadow baselines

Layer: N3. Dependencies: S06, S07, S08. Working unit: SWU-S09.

Write scope: `/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v2/s09`.

Inputs: Integrated rich/recursive/mapping profiles; Existing candidate application currentness model.

Outputs: `successor-baseline.schema.json`, `shadow-adapter.py`, `application-qualification.json`.

Ordered algorithm:

1. Register a newly checked successor snapshot and its exact semantic profile/manifest.
2. Bind proposals to that explicit before-state and generated evidence dependencies.
3. Recheck full required evidence and all source/context/epoch identities before shadow replacement.
4. Apply a second supported edit only after the successor baseline is independently qualified.

Edge/failure cases: Old baseline receipt after first apply; Condition/epoch/source drift during replay; Changed verifier policy; Reused review label; Noncooperating external writer.

Acceptance:

- Two supported shadow edits use two valid exact baselines with no transplanted old receipts.
- Every drift case blocks application; authority posture remains none.
- Local cooperative locking is described with its actual limits.

Verification / required evidence:

- Run two-step candidate application and review-to-apply drift controls.
- Inspect retained immutable before/after snapshots and complete obligation outcomes.

## S10 — Qualify end-to-end trust boundaries and regression

Layer: N3. Dependencies: S09. Working unit: SWU-S10.

Write scope: `/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v2/s10`.

Inputs: All integrated profiles, proofs, transports and baseline evidence.

Outputs: `qualification-suite.json`, `trust-boundary-report.md`, `qualification-audit.json`.

Ordered algorithm:

1. Replay independent exact theorem catalog and actual model/projection witnesses.
2. Exercise hostile transports, role substitution, stale imports/sources and missing hard obligations.
3. Compare every retained v1 guarantee with scoped successor behavior.
4. Record tested versus proved decoder/evaluator boundaries and remaining unsupported semantics.

Edge/failure cases: Same-kernel versus second-kernel wording; Supplied accepted flag falsely described as authentication; Countermodel for wrong implication; Resource exhaustion; Incomplete closure reported complete.

Acceptance:

- No successor guarantee is based on metadata flags alone.
- Every retained guarantee and new requirement has current scoped evidence.
- Trust assumptions and unsupported legacy items remain explicit.

Verification / required evidence:

- Run meaningful formal/transport/workflow hostile controls for changed surfaces.
- Audit exact proof statements, source closure, axioms and regression mapping.

## S11 — Measure stage costs and richer-profile workload growth

Layer: N4. Dependencies: S10. Working unit: SWU-S11.

Write scope: `/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v2/s11`.

Inputs: Qualified rich/recursive/condition workflows; Recorded v1 costs.

Outputs: `benchmark-profile.json`, `stage-measurements.json`, `performance-baseline.md`.

Ordered algorithm:

1. Instrument hashing, compilation, projection, grounding, saturation, proof/witness checks and application.
2. Vary domain size, arity, variables/rule, edges, chain/cycle depth and dependency size.
3. Separate cold/warm process costs and report exactly observed resources.
4. Select declared budgets/optimization target from measured dominant stages.

Edge/failure cases: Timeout at any stage; Memory ceiling; Exponential untyped substitution enumeration; Concurrent runs; Small graph with large registry compile.

Acceptance:

- Recorded measurements distinguish stage costs and execution limits from logical verdicts.
- No unsupported throughput/scale promise is made.
- A reviewable bottleneck selection precedes optimization.

Verification / required evidence:

- Run declared finite benchmark workloads with stage timing/RSS/work counters.
- Check exhausted jobs return unknown and cannot issue complete readiness.

## S12 — Optimize measured bottlenecks with equivalence evidence

Layer: N4. Dependencies: S11. Working unit: SWU-S12.

Write scope: `/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v2/s12`.

Inputs: S11 measured target and budgets; Reference grounding/closure and immutable compilation policy.

Outputs: `optimized-grounding.py`, `OptimizationEquivalence.lean`, `optimization-audit.json`.

Ordered algorithm:

1. Enumerate sort-compatible substitutions and index matching only where measurement warrants.
2. Prove reference/optimized grounding or closure equality for the declared profile.
3. If compilation reuse is selected, validate source/import/toolchain/policy identities before reuse.
4. Retain uncached full replay and fresh pre/post application checks; no readiness cache.

Edge/failure cases: Changed import with unchanged display version; Same facts different support multiplicity; Cache corruption; Changed target profile; Timeout/resource boundary.

Acceptance:

- Selected optimization has exact equivalence or remains disabled.
- Invalid/stale artifacts cannot authorize proof or readiness.
- Measured before/after results use the same workload and scoped guarantees.

Verification / required evidence:

- Kernel equivalence proof plus finite differential/hostile optimization controls.
- Repeat only relevant measured benchmark and drift cases.

## S13 — Run representative rich-profile shadow pilot

Layer: N4. Dependencies: S12. Working unit: SWU-S13.

Write scope: `/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v2/s13`.

Inputs: Qualified optimized or reference fallback runtime; S01 requirement cases and explanation fixtures.

Outputs: `pilot-report.json`, `review-packet.md`, `feedback-template.md`.

Ordered algorithm:

1. Run actual rich conformance, recursive chain/cycle, mapped delegation/inheritance and two-step shadow cases.
2. Exercise wrong context/target, missing interpretation, stale evidence and unknown witness/resource cases.
3. Publish concise worked explanations, complete hard inventories, measured costs and exact remaining limits.
4. Request actual human meaning, diagnostic and bounded-use assessment only after concrete evidence exists.

Edge/failure cases: Scope bleed; Unseeded cycle; Expired delegation; Inherited but unfulfilled norm; Machine pass misread as human approval.

Acceptance:

- Machine results cover supported positives and meaningful negative/unknown/stale paths.
- Human feedback is recorded only from actual responses.
- Any revisions remain explicit and do not relabel v1 R06/G4 as complete.

Verification / required evidence:

- Execute declared representative local workflows and validate saved outcome/provenance bindings.
- Review worked examples against requirement IDs and returned explanations.

## S14 — Review successor use and retain original unresolved human gates

Layer: N4. Dependencies: S13. Working unit: SWU-S14.

Write scope: `/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v2/s14`.

Inputs: Current pilot/proof/requirement evidence; Actual human feedback if supplied; Original R06/G4 status.

Outputs: `final-review.json`, `bounded-use-recommendation.md`, `requirement-audit.json`.

Ordered algorithm:

1. Audit each successor task/requirement and retained layer guarantee.
2. Evaluate actual semantic and diagnostic feedback separately from proof validity.
3. Record qualified/deferred use and unsupported profiles without deployment authority.
4. Keep original human gates pending unless a direct response expressly assesses their reviewed artifacts.

Edge/failure cases: Human requests revisions; No human response; Scope of new response differs from v1 review; Stale review artifacts; Plan receipt mistaken for proof.

Acceptance:

- Final use recommendation cites real human feedback and current scoped evidence.
- Missing/revision feedback leaves use qualification pending, not fabricated.
- No live authority/runtime publication or completion claim follows from this review alone.

Verification / required evidence:

- Read-only exact acceptance/evidence audit and direct feedback review.
- Verify all relevant source/proposal/feedback bindings before a candidate recommendation.
