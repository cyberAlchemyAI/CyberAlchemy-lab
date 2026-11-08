# Detailed revised work pack

All tasks are proposed. Write scopes are future v2 namespaces; this review creates no v2 implementation. Inherited C01–C10 and new I01–I12 remain traceable in revised-plan.json.

## S00 — Formalize successor meanings and independently required statements

Dependencies: none; formalization first. Layer: N0. Working unit: `SWU-S00`.

Write scope: `craft/formalization/candidates/relational-theorem-checker/v2/s00/`. Findings: I01, I03, I04, I05, I07, I11, I12.

### Inputs

- Current F0 semantic definitions and audited statement types
- REVIEW.md findings F01-F05/F10
- DESIGN-PROPOSAL.md proposed defaults

### Outputs

- semantic-contract.md
- RequirementSemantics.lean
- RequiredStatements.lean
- decisions.json
- assumption-register.json

### Algorithm

- Define graph-member contextual conformance and exact target-kind meaning independently from a projector.
- Specify fixed-domain recursive ordinary extension and explicit condition-status meanings.
- Fix projection, existential view, support, closure, old-model expansion and root-boundary theorem types; check well-formed Lean types.
- Record choices for target-kind view, domain growth and context/epoch; never define correctness as checker success.
- Define candidate validity versus member observation, potential/active/fulfilled norm meanings, exact evaluation keys and conflicts.
- Fix checked text encoding for node kinds, sealed producer policy and exact model/claim scope.

### Edge cases

- Unasserted valid edge
- Non-contract allowed F0 target
- New scope outside current domain
- No conformance or no initial seed
- Supplied truth versus authenticated truth

### Acceptance criteria

- Independent definitions and required types compile under the pinned policy.
- Every new guarantee and assumption has a requirement ID; deferred negation has no runtime rule.
- Source meanings and proposed defaults are reviewable before schema/runtime changes.
- Independent source-faithful and generic model classes are named; no observation truth is defined as checker success.

### Verification

- Lean type-check required definitions/statements without custom axioms or sorry.
- Review definitions against concrete rich and collapsed examples.
- Execute the new boundary controls listed in the acceptance criteria and retain exact scoped outcomes.

## S01 — Build semantic requirement ledger and premise-removal challenges

Dependencies: S00. Layer: N0. Working unit: `SWU-S01`.

Write scope: `craft/formalization/candidates/relational-theorem-checker/v2/s01/`. Findings: I08, I11.

### Inputs

- S00 requirement IDs
- Existing coverage ledger and countermodels

### Outputs

- requirements.json
- mutation-catalog.json
- adequacy-report.json

### Algorithm

- Map each selected source requirement to an independent predicate, statement, assumption or unsupported status.
- Attach positive/negative cases and applicable mutant removing exactly one required condition.
- Run named controls; retain countermodels that show why a premise is necessary.
- Keep every inherited unsupported item until its own source/meaning evidence exists.
- Classify every individual source review and select/defer each improvement against literal source text.

### Edge cases

- Duplicate assessment token
- Scope/version substitution
- Missing graph membership
- Revocation removed
- Conflict interpreted as explosion

### Acceptance criteria

- No selected requirement is silently unclassified.
- All applicable named mutants are detected; exclusions have explicit reasons.
- The ledger distinguishes structural checks, supplied truth and semantic theorems.

### Verification

- Validate requirement references and current source bindings.
- Run the finite semantic witness/mutation suite; record exact failed property and profile.

## S02 — Prove the contextual graph-to-fact bridge

Dependencies: S01. Layer: N0. Working unit: `SWU-S02`.

Write scope: `craft/formalization/candidates/relational-theorem-checker/v2/s02/`. Findings: I03, I07, I08.

### Inputs

- S00 independent projection targets
- S01 required positive/negative cases
- F0 invariant and graph definitions

### Outputs

- ContextProjection.lean
- ProjectionProofs.lean
- projection-fixtures.json
- projection-audit.json

### Algorithm

- Enumerate member conformance assertions of a graph satisfying the selected invariant.
- Project exact subject/target references and scope, plus checked target-kind observations.
- Build complete support sets for deduplicated initial atoms and derive the unary existential view.
- Prove soundness, completeness, support validity and exact existential correspondence.
- Prove independent node-kind projection and kind-vocabulary/domain membership; nonmember validity cannot create a source fact.

### Edge cases

- Two edges supporting one atom
- Wrong scope/target kind/target revision
- Valid edge absent from graph
- No assertion facts
- Out-of-domain scope requires another baseline

### Acceptance criteria

- Required independent theorem types are proved and audited.
- A specific contract/scope query cannot use only unary conformance.
- v1 meanings are unchanged and domain/profile differences are explicit.
- Target-kind projection has independently fixed soundness/completeness and exact vocabulary/domain targets.

### Verification

- Fresh kernel replay of required statements and axiom/dependency closure.
- Execute wrong-contract, wrong-scope, wrong-kind, nonmember and duplicate-support controls.
- Execute the new boundary controls listed in the acceptance criteria and retain exact scoped outcomes.

## S04 — Formalize interpreted conditions and stress source mappings

Dependencies: S01. Layer: N1. Working unit: `SWU-S04`.

Write scope: `craft/formalization/candidates/relational-theorem-checker/v2/s04/`. Findings: I04, I05, I08.

### Inputs

- S00 condition/source contracts
- Legacy acts-for/inherits-contract source records
- Typed stress semantics

### Outputs

- InterpretationSemantics.lean
- ConditionSemantics.lean
- MappingStatements.lean
- field-map.json

### Algorithm

- Define exact source qualifier interpretation witnesses and context bindings.
- Separate holds, explicit does-not-hold and unknown; positive conclusions require checked holds.
- Map every selected field into typed input or explicit unsupported/opaque status.
- Define/prove supported mapping and snapshot soundness without asserting external authenticity.
- Fix evaluation keys and consistent selected statuses; contradictory holds/does-not-hold blocks positive projection.
- Prove potential inheritance independently of condition evaluation; active norms/conflicts require exact holds evidence.

### Edge cases

- Opaque period without interpretation
- Missing condition/gate
- Wrong node kind/revision
- Revocation boundary
- Overrides and redelegation chains
- Opposite selected statuses at same exact evaluation key
- Same condition name at different context or revision
- Potential norm with false or missing condition

### Acceptance criteria

- All fields and assumptions are accounted for.
- Missing interpretation remains unknown rather than false or permission.
- No unsupported chain/override meaning is silently supplied.
- Contradictory selected evaluations cannot project holds; potential and active norm/conflict statements are distinct.

### Verification

- Compile independent mapping/condition statement targets and prove supported correspondence.
- Review field maps against literal source shapes and typed stress records.
- Execute the new boundary controls listed in the acceptance criteria and retain exact scoped outcomes.

## S15 — Specify registered baselines, profiles and obligation catalogs

Dependencies: S01. Layer: N0. Working unit: `SWU-S15`.

Write scope: `craft/formalization/candidates/relational-theorem-checker/v2/s15/`. Findings: I02, I03, I09, I10.

### Inputs

- S00 independent definitions and required statement types
- Current source/implementation review and exact predecessor evidence

### Outputs

- BaselineContract.lean
- baseline.schema.json
- profile.schema.json
- obligation-catalog.json
- baseline-controls.json

### Algorithm

- Define graph, registry, theory, source, interpretation, policy, toolchain and epoch identity; distinguish canonical object identity from exact byte bindings.
- Specify selected immutable reference-to-content/kind policy and independently checked baseline registration, without organizational admission.
- Define producer-aware profiles, exact independent theorem catalogs and change-to-required-obligation selection; counts are generated, not caller-selected.
- Specify stronger executable profile versus generic theory mapping and unsupported/mixed change handling.

### Edge cases

- Nonempty old rules
- Same reference changed content/kind
- Caller-shrunken catalog
- Old receipt substituted for new profile
- New kind/scope outside domain

### Acceptance criteria

- Valid nonempty old-rule baselines can be represented without relaxed proof requirements.
- Each supported change has an exact generated obligation inventory and checked manifest binding.
- Same-reference semantic substitution and stale catalogs/toolchain are rejected.

### Verification

- Pinned Lean exact statement/proof audit for formal guarantees; no custom axioms or sorry.
- Execute named meaningful positive/negative/context/drift controls and bind exact evidence.

## S16 — Prove sealed observations and supported derivation leaves

Dependencies: S02, S15. Layer: N0. Working unit: `SWU-S16`.

Write scope: `craft/formalization/candidates/relational-theorem-checker/v2/s16/`. Findings: I01, I07.

### Inputs

- S00 independent definitions and required statement types
- Current source/implementation review and exact predecessor evidence

### Outputs

- ProducerPolicy.lean
- SupportedObservations.lean
- SupportLineage.lean
- sealed-producer-controls.json

### Algorithm

- Define sealed source observations and permitted derived ordinary signals as orthogonal to root roles.
- Reject caller seeds and rule heads for sealed predicates; accept observations only from an exact checked projector.
- Prove source observation membership/derivability corresponds to independently defined member-source meaning with valid support leaves.
- Preserve root lineage separately; allow derived informational heads only under the selected producer policy.

### Edge cases

- Constant-only semantic head
- Caller-injected kind/conformance
- Nonmember valid edge
- Multiple source supports
- Derived signal reads sealed observation

### Acceptance criteria

- ConformsTo and TargetKind cannot be fabricated by caller seeds or ordinary rules in this profile.
- Exact source-support and producer-coverage statements are independently audited.
- Derived signals remain useful without becoming independent roots.

### Verification

- Pinned Lean exact statement/proof audit for formal guarantees; no custom axioms or sorry.
- Execute named meaningful positive/negative/context/drift controls and bind exact evidence.

## S03 — Prove finite recursive fresh-definition expansion

Dependencies: S16. Layer: N1. Working unit: `SWU-S03`.

Write scope: `craft/formalization/candidates/relational-theorem-checker/v2/s03/`. Findings: I01, I02, I10.

### Inputs

- S00 extension contract
- Existing generic derivation/closure proofs
- S02 contextual vocabulary

### Outputs

- RecursiveExtension.lean
- RecursiveConservativity.lean
- recursive-countermodels.json
- recursion-audit.json

### Algorithm

- Fix old interpretation for an arbitrary old semantic model.
- Iterate only fresh ordinary heads over the finite typed universe with positive old/fresh bodies.
- Prove monotonicity, stabilization, closure, old-reduct equality and every-old-model expansion.
- Check all producer roles and reject old/protected heads or changed domain/roots.
- Preserve old rules/facts exactly; allow only declared fresh derived ordinary heads and retain sealed observation producer restrictions.

### Edge cases

- Seeded cycle
- Unseeded cycle
- Nonempty valid old baseline
- Old rule/predicate mutation
- Fresh protected predicate
- Domain growth

### Acceptance criteria

- Every old model expands under independently checked profile hypotheses.
- Unseeded cycles create no facts; protected/root inventories are preserved.
- Unsupported domain/old-head changes remain blocked with precise reasons.
- Only declared derived heads are allowed; old rules and initial facts are byte/meaning bound and unchanged.

### Verification

- Audit exact general conservativity/termination statements in Lean.
- Run multi-step/cycle and hostile old-head/root controls.
- Execute the new boundary controls listed in the acceptance criteria and retain exact scoped outcomes.

## S17 — Establish early grounding bounds and runtime feasibility

Dependencies: S02, S15, S16. Layer: N1. Working unit: `SWU-S17`.

Write scope: `craft/formalization/candidates/relational-theorem-checker/v2/s17/`. Findings: I06.

### Inputs

- S00 independent definitions and required statement types
- Current source/implementation review and exact predecessor evidence

### Outputs

- ResourceContract.lean
- preflight-bounds.json
- feasibility-probe.json
- budget-controls.json

### Algorithm

- Calculate conservative substitution, atom-universe, stress candidate and conflict-pair bounds before product allocation.
- Instrument small bounded reference probes with declared stage ceilings; distinguish estimates from observations.
- If the reference exceeds the intended envelope, select a smaller explicit profile or bring necessary equivalence work forward before broadening runtime.
- Define unknown resource-exhaustion outputs; partial closure cannot supply absence or readiness.

### Edge cases

- Large variable count with tiny input
- Small graph and huge domain
- Budget exceeded before allocation
- Proof replay timeout
- Overconservative bound

### Acceptance criteria

- Feasibility and exhaustion contracts exist before rich runtime integration.
- Over-budget inputs stop before expensive products; stage counters substantiate behavior.
- No unsupported throughput or wall-clock completion guarantee is issued.

### Verification

- Pinned Lean exact statement/proof audit for formal guarantees; no custom axioms or sorry.
- Execute named meaningful positive/negative/context/drift controls and bind exact evidence.

## S18 — Qualify source interpretations and richer baseline transitions

Dependencies: S02, S04, S15, S16. Layer: N1. Working unit: `SWU-S18`.

Write scope: `craft/formalization/candidates/relational-theorem-checker/v2/s18/`. Findings: I03, I08, I09, I11.

### Inputs

- S00 independent definitions and required statement types
- Current source/implementation review and exact predecessor evidence

### Outputs

- SourceInterpretation.lean
- BaselineTransition.lean
- source-map.json
- transition-controls.json

### Algorithm

- Map exact selected fields into independent meanings, accounting for evidence lists, endpoint fragments, opaque qualifiers and additional stress inputs.
- Separate rule-only extension from graph, initial-fact, domain, assessment and interpretation changes.
- Prove the declared initial projection/view relationship for richer migration; do not claim fixed domain or every-old-model expansion when hypotheses differ.
- Qualify selected richer baseline and source/interpretation bindings; preserve unselected semantics as unsupported.

### Edge cases

- Multiple evidence tokens
- Registry pair outside F0
- New scope/kind literal
- Opaque period
- Changed interpretation at same source
- Same reference changed content

### Acceptance criteria

- Selected mappings have independently checked witnesses and explicit field coverage.
- Richer transitions satisfy their distinct declared change class and theorem/validation targets.
- All relation improvements are selected or deferred; review does not discharge unsupported meanings.

### Verification

- Pinned Lean exact statement/proof audit for formal guarantees; no custom axioms or sorry.
- Execute named meaningful positive/negative/context/drift controls and bind exact evidence.

## S05 — Align successor transports and implement checked projection

Dependencies: S17, S18. Layer: N2. Working unit: `SWU-S05`.

Write scope: `craft/formalization/candidates/relational-theorem-checker/v2/s05/`. Findings: I01, I02, I03, I06, I08, I10.

### Inputs

- S02 formal projector and support proofs
- Main and stress current CLI contracts

### Outputs

- request.schema.json
- support.schema.json
- projection-adapter.py
- capability-manifest.json
- transport-audit.json

### Algorithm

- Version contextual input/output/profile transports without changing reserved v1 contracts.
- Strictly decode, bind sources and generate typed projection input.
- Check projection/support witnesses against exact graph/profile identity.
- Publish explicit domain, target-kind, theorem and trust requirements.
- Use earlier baseline/profile/catalog, sealed producer checks, qualified mappings and early work ceilings.
- Version transport mapping and trusted import/statement catalog together; do not conflate tested decoder with proved equivalence.

### Edge cases

- Duplicate JSON keys
- Wrong rich predicate arity/sort
- Dangling support edge
- Altered assessment binding
- Older v1 receipt used for v2
- Caller seed or rule head for a sealed observation
- Reference kind/content substitution
- Preflight budget refuses before Cartesian construction

### Acceptance criteria

- Transport outputs agree with formal projection on selected controls.
- Missing projection proof/support or changed identities block result readiness.
- Adapter remains a tested trust boundary unless equivalence is separately proved.
- Caller/rule-injected sealed facts, profile/catalog substitution and over-budget preflight controls are rejected.

### Verification

- Schema positive/negative validation and fresh kernel differential projection checks.
- Retain v1 fixture regression and reject old/new profile substitution.
- Execute the new boundary controls listed in the acceptance criteria and retain exact scoped outcomes.

## S06 — Integrate recursive profile and complete new obligation inventory

Dependencies: S03, S05. Layer: N2. Working unit: `SWU-S06`.

Write scope: `craft/formalization/candidates/relational-theorem-checker/v2/s06/`. Findings: I01, I02, I06, I10.

### Inputs

- S03 actual recursion hypotheses and proofs
- S05 profile transports
- Existing exact statement verifier/obligation generator

### Outputs

- recursive-runtime.py
- obligation-catalog.json
- rule-bundle.schema.json
- recursive-workflow-audit.json

### Algorithm

- Classify actual old/fresh vocabulary, rules, domain and roots.
- Independently generate the complete new required obligations, including projection and actual recursion hypotheses.
- Check certificates, complete closures, exact witnesses and general expansion evidence.
- Aggregate only allowed current evidence methods; preserve unknown/unsupported/stale outcomes.
- Consume registered nonempty baselines/generated catalogs; replace captured ReviewSignal/CORE assumptions only in the new selected profile.

### Edge cases

- Caller-shrunken inventory
- Weakened expansion statement
- Cyclic certificate without earlier premises
- Nonempty old baseline
- Mixed domain/fact/rule changes

### Acceptance criteria

- Recursive ordinary cases become supported only with the new proof profile.
- Actual hypotheses/witnesses and general theorems are separately discharged.
- No assumption that the new inventory must still contain exactly 15 obligations.

### Verification

- Fresh complete recursive proposal replay plus missing/wrong/stale evidence controls.
- Independently compare required versus returned obligation IDs.

## S07 — Implement explicit registry-to-stress adapters

Dependencies: S04, S05, S18. Layer: N2. Working unit: `SWU-S07`.

Write scope: `craft/formalization/candidates/relational-theorem-checker/v2/s07/`. Findings: I04, I05, I08.

### Inputs

- S04 field mappings and condition proofs
- Typed stress CLIs and assessment sources
- S05 binding transports

### Outputs

- interpretation.schema.json
- delegation-adapter.py
- inheritance-adapter.py
- mapping-audit.json

### Algorithm

- Resolve exact registry/source and interpretation record versions.
- Check endpoint kinds and every mapped qualifier; create typed stress inputs with exact snapshot binding.
- Evaluate only supported direct delegation and fixed norm profiles.
- Export scoped condition/norm facts with checked support and residual assumptions.
- Expose PotentialNorm, ActiveNorm and ActiveConflict distinctly; keep inheritance and conformance independent.
- Select exact contextual evaluations; block contradictory/mismatched evidence without executing arbitrary condition strings.

### Edge cases

- Malformed/opaque interval
- Missing policy or gate
- Condition mismatch
- Stale snapshot
- Overrides
- Permitted redelegation without supported chain

### Acceptance criteria

- Exact mappings are checked; registry semantic ledger only advances for discharged named items.
- Typed profile successes cannot be generalized to unmapped legacy inputs.
- Inheritance does not produce fulfillment or admission.
- Unknown/false/conflicting conditions cannot activate norms; potential norm output remains available under its own meaning.

### Verification

- Differential mapping controls against typed stress examples and source records.
- Kernel witness/revocation/origin controls plus strict interpretation transports.
- Execute the new boundary controls listed in the acceptance criteria and retain exact scoped outcomes.

## S08 — Publish explanations and current capability/status documentation

Dependencies: S05. Layer: N3. Working unit: `SWU-S08`.

Write scope: `craft/formalization/candidates/relational-theorem-checker/v2/s08/`. Findings: I07, I11, I12.

### Inputs

- S05 checked support and manifests
- Current baseline receipts, pending human review
- Existing CLI outcomes/certificates

### Outputs

- explain.py
- CURRENT-STATUS.md
- API.md
- explanation-fixtures.json
- docs-audit.json

### Algorithm

- Render exact assertion, assessment, target kind, scope, projection, rule substitution and theorem scope.
- Display supplied-truth assumptions and lossy unary views explicitly.
- Generate separate machine/acceptance/human/authority statuses and link historical designs.
- Describe main and stress exit conventions and optional future HTTP design accurately.
- Label observed/candidate, supplied/proved, potential/active/fulfilled and exact model classes; distinguish complete versus partial evidence.

### Edge cases

- Partial closure/search
- Unsupported profile
- Stale explanation input
- Same atom with multiple supports
- Saved machine pass with pending human review

### Acceptance criteria

- Explanations identify concrete source and blocking obligation without upgrading readiness.
- Current index contradicts no accepted current operation/status evidence.
- No historical source/accepted export is silently rewritten.
- Each explanation names its exact model class, claimed query/closure scope and source versus supplied-truth leaves.

### Verification

- Check explanation fixtures/links and exact currentness/status mappings.
- Conduct usability review with the wrong-contract/scope example.
- Execute the new boundary controls listed in the acceptance criteria and retain exact scoped outcomes.

## S09 — Qualify composed contexts and successor shadow baselines

Dependencies: S06, S07, S08. Layer: N3. Working unit: `SWU-S09`.

Write scope: `craft/formalization/candidates/relational-theorem-checker/v2/s09/`. Findings: I02, I09.

### Inputs

- Integrated rich/recursive/mapping profiles
- Existing candidate application currentness model

### Outputs

- shadow-adapter.py
- application-qualification.json
- baseline-registration-qualification.json

### Algorithm

- Register a newly checked successor snapshot and its exact semantic profile/manifest.
- Bind proposals to that explicit before-state and generated evidence dependencies.
- Recheck full required evidence and all source/context/epoch identities before shadow replacement.
- Apply a second supported edit only after the successor baseline is independently qualified.
- Consume previously specified baseline/profile schema; qualify two-step application with fresh evidence after each transition.

### Edge cases

- Old baseline receipt after first apply
- Condition/epoch/source drift during replay
- Changed verifier policy
- Reused review label
- Noncooperating external writer

### Acceptance criteria

- Two supported shadow edits use two valid exact baselines with no transplanted old receipts.
- Every drift case blocks application; authority posture remains none.
- Local cooperative locking is described with its actual limits.
- Same-reference content/kind substitution and old-baseline receipt reuse are blocked.

### Verification

- Run two-step candidate application and review-to-apply drift controls.
- Inspect retained immutable before/after snapshots and complete obligation outcomes.
- Execute the new boundary controls listed in the acceptance criteria and retain exact scoped outcomes.

## S10 — Qualify end-to-end trust boundaries and regression

Dependencies: S09. Layer: N3. Working unit: `SWU-S10`.

Write scope: `craft/formalization/candidates/relational-theorem-checker/v2/s10/`. Findings: I01, I04, I05, I10, I12.

### Inputs

- All integrated profiles, proofs, transports and baseline evidence

### Outputs

- qualification-suite.json
- trust-boundary-report.md
- qualification-audit.json

### Algorithm

- Replay independent exact theorem catalog and actual model/projection witnesses.
- Exercise hostile transports, role substitution, stale imports/sources and missing hard obligations.
- Compare every retained v1 guarantee with scoped successor behavior.
- Record tested versus proved decoder/evaluator boundaries and remaining unsupported semantics.
- Include sealed producer attacks, contradictory context status, inactive potential norms, model-class mismatch and limited certificate claims.

### Edge cases

- Same-kernel versus second-kernel wording
- Supplied accepted flag falsely described as authentication
- Countermodel for wrong implication
- Resource exhaustion
- Incomplete closure reported complete

### Acceptance criteria

- No successor guarantee is based on metadata flags alone.
- Every retained guarantee and new requirement has current scoped evidence.
- Trust assumptions and unsupported legacy items remain explicit.
- The limited stress certificate cannot be reported as whole-graph or complete-query qualification.

### Verification

- Run meaningful formal/transport/workflow hostile controls for changed surfaces.
- Audit exact proof statements, source closure, axioms and regression mapping.
- Execute the new boundary controls listed in the acceptance criteria and retain exact scoped outcomes.

## S11 — Measure stage costs and richer-profile workload growth

Dependencies: S10. Layer: N4. Working unit: `SWU-S11`.

Write scope: `craft/formalization/candidates/relational-theorem-checker/v2/s11/`. Findings: I06.

### Inputs

- Qualified rich/recursive/condition workflows
- Recorded v1 costs

### Outputs

- benchmark-profile.json
- stage-measurements.json
- performance-baseline.md

### Algorithm

- Instrument hashing, compilation, projection, grounding, saturation, proof/witness checks and application.
- Vary domain size, arity, variables/rule, edges, chain/cycle depth and dependency size.
- Separate cold/warm process costs and report exactly observed resources.
- Select declared budgets/optimization target from measured dominant stages.
- Extend early S17 feasibility measurements to full qualified end-to-end costs.

### Edge cases

- Timeout at any stage
- Memory ceiling
- Exponential untyped substitution enumeration
- Concurrent runs
- Small graph with large registry compile

### Acceptance criteria

- Recorded measurements distinguish stage costs and execution limits from logical verdicts.
- No unsupported throughput/scale promise is made.
- A reviewable bottleneck selection precedes optimization.

### Verification

- Run declared finite benchmark workloads with stage timing/RSS/work counters.
- Check exhausted jobs return unknown and cannot issue complete readiness.

## S12 — Optimize measured bottlenecks with equivalence evidence

Dependencies: S11. Layer: N4. Working unit: `SWU-S12`.

Write scope: `craft/formalization/candidates/relational-theorem-checker/v2/s12/`. Findings: I06.

### Inputs

- S11 measured target and budgets
- Reference grounding/closure and immutable compilation policy

### Outputs

- optimized-grounding.py
- OptimizationEquivalence.lean
- optimization-audit.json

### Algorithm

- Enumerate sort-compatible substitutions and index matching only where measurement warrants.
- Prove reference/optimized grounding or closure equality for the declared profile.
- If compilation reuse is selected, validate source/import/toolchain/policy identities before reuse.
- Retain uncached full replay and fresh pre/post application checks; no readiness cache.
- Optimize only a measured need; retain qualified reference fallback inside the declared envelope.

### Edge cases

- Changed import with unchanged display version
- Same facts different support multiplicity
- Cache corruption
- Changed target profile
- Timeout/resource boundary

### Acceptance criteria

- Selected optimization has exact equivalence or remains disabled.
- Invalid/stale artifacts cannot authorize proof or readiness.
- Measured before/after results use the same workload and scoped guarantees.

### Verification

- Kernel equivalence proof plus finite differential/hostile optimization controls.
- Repeat only relevant measured benchmark and drift cases.

## S13 — Run representative rich-profile shadow pilot

Dependencies: S11. Layer: N4. Working unit: `SWU-S13`.

Write scope: `craft/formalization/candidates/relational-theorem-checker/v2/s13/`. Findings: I01, I04, I05, I12.

### Inputs

- Qualified optimized or reference fallback runtime
- S01 requirement cases and explanation fixtures

### Outputs

- pilot-report.json
- review-packet.md
- feedback-template.md

### Algorithm

- Run actual rich conformance, recursive chain/cycle, mapped delegation/inheritance and two-step shadow cases.
- Exercise wrong context/target, missing interpretation, stale evidence and unknown witness/resource cases.
- Publish concise worked explanations, complete hard inventories, measured costs and exact remaining limits.
- Request actual human meaning, diagnostic and bounded-use assessment only after concrete evidence exists.
- Include producer attacks, conflicting conditions, inactive potential norms and richer baseline transitions in pilot.

### Edge cases

- Scope bleed
- Unseeded cycle
- Expired delegation
- Inherited but unfulfilled norm
- Machine pass misread as human approval

### Acceptance criteria

- Machine results cover supported positives and meaningful negative/unknown/stale paths.
- Human feedback is recorded only from actual responses.
- Any revisions remain explicit and do not relabel v1 R06/G4 as complete.

### Verification

- Execute declared representative local workflows and validate saved outcome/provenance bindings.
- Review worked examples against requirement IDs and returned explanations.

## S14 — Review successor use and retain original unresolved human gates

Dependencies: S13. Layer: N4. Working unit: `SWU-S14`.

Write scope: `craft/formalization/candidates/relational-theorem-checker/v2/s14/`. Findings: I11, I12.

### Inputs

- Current pilot/proof/requirement evidence
- Actual human feedback if supplied
- Original R06/G4 status

### Outputs

- final-review.json
- bounded-use-recommendation.md
- requirement-audit.json

### Algorithm

- Audit each successor task/requirement and retained layer guarantee.
- Evaluate actual semantic and diagnostic feedback separately from proof validity.
- Record qualified/deferred use and unsupported profiles without deployment authority.
- Keep original human gates pending unless a direct response expressly assesses their reviewed artifacts.
- Keep source-meaning decisions, proof validity and actual human feedback separately assessed.

### Edge cases

- Human requests revisions
- No human response
- Scope of new response differs from v1 review
- Stale review artifacts
- Plan receipt mistaken for proof

### Acceptance criteria

- Final use recommendation cites real human feedback and current scoped evidence.
- Missing/revision feedback leaves use qualification pending, not fabricated.
- No live authority/runtime publication or completion claim follows from this review alone.

### Verification

- Read-only exact acceptance/evidence audit and direct feedback review.
- Verify all relevant source/proposal/feedback bindings before a candidate recommendation.

