# Implementation-informed review

The successor direction remains useful: preserve contextual conformance, support finite ordinary recursion, and map the two stress relations into checked profiles. The implementation shows four missing prerequisite tasks and tighter definition boundaries before runtime integration.

These findings distinguish prospective design holes from v1 failures. The current workflow intentionally supports its captured empty-rule/ReviewSignal profile. Nothing here establishes a false v1 admission. Original accepted artifacts are preserved; R06/G4 still need actual human assessment.

## A concrete semantic producer gap

Suppose the graph supports `ConformsTo(A, ContractA, Scope1)` but no assertion about ContractB. A generic positive rule `Conforms(A) → ConformsTo(A, ContractB, Scope1)` can be well typed if its constants are in the domain and the target predicate is ordinary. A derivation proves consequence of that rule. It does not prove an assessment for ContractB exists. The current generic normalizer accepts this ordinary-rule shape; the current captured workflow blocks its new head. The successor must seal observation producers while permitting rules to derive separately defined informational signals.

A second example: `require Ship` under condition `ApprovalGranted` becomes a potential inherited norm in the stress profile without a condition assessment. That is coherent inheritance meaning. Calling it active requires an exact holds witness. Calling it fulfilled requires separate action evidence.

## Findings and required changes

### I01 — Seal semantic observation producers

Prospective design gap. ConformsTo and TargetKind are ordinary fresh predicates in the proposal. Generic RuleValid and normalization permit ordinary heads and ordinary seeds. A valid derivation can therefore establish logical consequence without establishing graph-source meaning. Current captured workflow rejects these new heads; this is not a reproduced v1 false acceptance. Seal observation producers separately from authority root roles.

Evidence: [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:89). Tasks: S16.

### I02 — Move baseline/profile design before integration

Implementation dependency gap. Classifier baseline(), integration capture() and bundle execution_profile() bind the captured empty-rule graph and ReviewSignal vocabulary. S06 asks for nonempty old baselines before S09 introduces successor baseline design. Specify registered baseline/profile/catalog contracts earlier; S09 should qualify application.

Evidence: [integration.py](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/integration/integration.py:28). Tasks: S15.

### I03 — Specify target-kind encoding and finite domain

Prospective definition gap. ValueSort has no kind sort. TargetKind(reference,contract) needs a checked text literal in the domain and an independent node-kind projection. New targets/scopes/kind values cannot silently satisfy domain_same during rule-only expansion.

Evidence: [InferenceCore.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/derivations/InferenceCore.lean:5). Tasks: S00, S02, S15.

### I04 — Define contextual assessment keys and contradictions

Semantic contract gap. Unique tokens do not define how different assessments for the same condition/context disagree. Stress conformance rows permit accepted=true and accepted=false. Require consistent selected evaluations for an exact key, or report an explicit conflict/invalid diagnostic blocking positive projection. Missing stays unknown; issuer truth remains assumed.

Evidence: [ObligationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/ObligationSemantics.lean:35). Tasks: S04, S07.

### I05 — Separate potential norms, activation and fulfillment

Meaning gap. Matches compares condition labels and interpreted flags. Origin and closure propagate norms without condition evaluation; ConflictPair compares a same-condition require/forbid pair. These are potential norms/conflicts. ActiveNorm requires an exact holds assessment; fulfillment requires separate action evidence.

Evidence: [ObligationSemantics.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/ObligationSemantics.lean:5). Tasks: S04, S07.

### I06 — Protect resource budgets before broadening runtime

Implementation/resource gap. choices constructs d^k candidates before sort filtering. Stress workUnits computes candidateFacts and closure before checking budget. Finite termination and post-computation logical budgets do not establish time or RSS ceilings. Add early conservative bounds and measured stage ceilings before rich runtime integration.

Evidence: [StressCheckers.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressCheckers.lean:25). Tasks: S17, S11, S12.

### I07 — Separate candidate validity from observed membership

Definition-composition gap. InstanceValid, ConformsAt and delegation Effective intentionally evaluate a supplied candidate without Recorded membership. Origin requires membership. Keep candidate meanings and define separate observed predicates requiring exact membership/support at projection leaves. Do not strengthen accepted definitions globally.

Evidence: [SemanticLogic.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/semantic-logic/v1/SemanticLogic.lean:7). Tasks: S00, S02, S16.

### I08 — Give source interpretations and data transitions their own task

Implementation/profile gap. Registry qualifiers are closed nonempty strings. F0 uses three kinds and a single conformance evidence token; registry uses plural evidence references and broader pair sets. Stress adds actions, conditions and assessments absent from legacy qualifiers. Rich baseline capture and source/fact/domain changes need distinct change classes and obligations.

Evidence: [RegistryChecker.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/registry/RegistryChecker.lean:35). Tasks: S18, S15, S05, S07.

### I09 — Bind reference meaning across snapshots

Identity contract gap. Graph invariants give local id/version uniqueness, not global immutability of content or kind. Existing byte bindings detect selected drift but do not authenticate issuers. Qualify immutable ref-to-content/kind bindings across snapshots or require a changed revision; reject same-reference substitution.

Evidence: [RelationalInput.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/formal/core/RelationalInput.lean:43). Tasks: S15, S18, S09.

### I10 — Version generic theory and executable profile separately

Integration contract gap. Frontend requires exact mandatory CORE and unique rule id/version; TheoryValid checks a more general logical theory. The verifier has a fixed import list and trusted catalogs. Specify stronger executable profile and checked mapping, update trusted catalogs from independent statement types, and retain decoder/generator trust limits.

Evidence: [frontend.py](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/inference/profile/frontend.py:51). Tasks: S15, S05, S06, S10.

### I11 — Resolve source wording before stronger theorem claims

Source-definition improvement. Each captured source was inspected. fulfills-request operational text says fulfillment while its question says intended fulfillment. successor-of specifies supersedes but leaves actual lifecycle/currentness policy outside generic strings. Role/posture declarations often mix intent, attempt and result. Fix independently reviewed meanings before promoting any stronger claim.

Evidence: [normalized-registry.json](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/registry/normalized-registry.json:1846). Tasks: S00, S01, S18.

### I12 — Expose exact claim and model class in outcomes

API/definition gap. Derivation proves one query; checked closure proves profile-relative nonderivability; a countermodel refutes one implication. Stress certificates check listed Origins and shape, not GraphValid, a requested query or completeness. Closed, ModelValid and SemanticModel differ. Compose exact required obligations and name the result claim accurately.

Evidence: [StressCheckers.lean](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v1/relation-stress/v1/implementation/StressCheckers.lean:46). Tasks: S08, S10.

## What remains useful

Retain exact endpoint/version/evidence checks, generic positive derivation and complete-closure theorems, independent root lineage, checked countermodels and universal structural preservation. No blanket cycle ban, mandatory gate, global single-assessment restriction or new negation is proposed. Instead each successor profile declares its permitted producers, interpretation, model class and change classes.

## Review package

- [DEFINITION-REVIEW.md](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/relational-theorem-checker/reviews/2026-10-09/implementation-analysis/DEFINITION-REVIEW.md): every selected current production declaration and the 17 proposed concepts.
- [RELATION-REVIEW.md](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/relational-theorem-checker/reviews/2026-10-09/implementation-analysis/RELATION-REVIEW.md): all 41 relation sources with specific gaps, improvements and controls.
- [DESIGN-AMENDMENTS.md](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/relational-theorem-checker/reviews/2026-10-09/implementation-analysis/DESIGN-AMENDMENTS.md): exact producer, condition, source, baseline and API boundaries.
- [REVISED-PLAN.md](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/relational-theorem-checker/reviews/2026-10-09/implementation-analysis/REVISED-PLAN.md): corrected DAG and delivery milestones.
- [WORK-PACK.md](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/relational-theorem-checker/reviews/2026-10-09/implementation-analysis/WORK-PACK.md): detailed work for each task.

## Verification ceiling

The package validator checks exhaustive inventory coverage within the declared module selection, exact current source bytes, preserved accepted evidence, finding/task traceability and DAG dependencies. A readonly probe exercises current Python normalization. No successor Lean proof, performance qualification, runtime API or human assessment is created by this review. See validation-report.json and probe-report.json for exact results.
