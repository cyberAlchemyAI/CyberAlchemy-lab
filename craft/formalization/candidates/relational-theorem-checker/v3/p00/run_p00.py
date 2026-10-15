"""Formalization-first task execution with actual kernel compilation."""
from pathlib import Path
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'execution'))
import support as s

all_criteria = ['P00-C1', 'P00-C2', 'P00-C3']
selectors = [
    (s.SOURCE, 'P00 acceptance', 'Every new claim has an independent definition, hypotheses and a claim ceiling.', all_criteria),
    (s.V2 / 's00/semantic-contract.md', 'scope and semantics', 'This is a finite, positive, candidate-only profile.', ['P00-C1', 'P00-C3']),
    (s.V2 / 's00/RequirementSemantics.lean', 'MemberConformance', 'abbrev MemberConformance (g : Relational.Graph) (x : ConformanceTuple) : Prop :=\n  Inv g ∧ ∃ e ∈ g.assertions, ∃ ver ev,\n    Relational.Logic.ConformsAt g e x.scope ver ev ∧ e.source = x.subject ∧ e.target = x.target', ['P00-C1', 'P00-C3']),
    (s.V2 / 's03/RecursiveConservativity.lean', 'arbitrary-model expansion', 'theorem every_old_model_expands : RequiredConservativity := by\n  intro base expanded e F M model\n  exact ⟨Relative e.added M,expansion_valid e model,fun a old => old_unchanged e old⟩', ['P00-C1', 'P00-C2']),
    (s.V2 / 's04/ConditionSemantics.lean', 'activation and supplied truth', 'theorem activation_needs_holds : Successor.Required.ActivationNeedsHolds := by\n  intro g f es k h; exact h.2.2.2.2.2', ['P00-C1', 'P00-C2']),
    (s.V2 / 's14/final-review.json', 'actual review scope', '"deployment_or_publication_authorized_by_review": false', ['P00-C3']),
]
s.context('P00', selectors, [
    {'decision': 'saved-vs-fresh', 'selected': 'Separate RecordedCurrent from invocation-owned FreshQualified; saved metadata cannot supply a replay event.', 'type': 'nonblocking', 'basis': 'P00 contract'},
    {'decision': 'extensions', 'selected': 'All seven extensions selected by actual user response; each later formalizes its own new meaning.', 'type': 'user-resolved'},
    {'decision': 'source-preservation', 'selected': 'Read-only inherited imports and current bindings; all new files in v3.', 'type': 'constraint'},
    {'decision': 'context-persistence', 'selected': 'Selector context was read before source authoring; persisted here before validation/acceptance. Initial source authoring preceded persisted pack creation.', 'type': 'execution-order-disclosure'},
])

(HERE / 'semantic-delta.md').write_text('''# Evidence and operational semantic delta

The v3 candidate retains v2 source meanings and adds explicit evidence and invocation contracts. `MemberConformance` still requires an invariant graph, member assertion, exact endpoints/revisions/scope and accepted supplied assessment. `ConformsTo`/`TargetKind`/`Conforms` remain sealed observations. Derived informational signals create no independent roots. `SourceFaithful` names equality of sealed interpretations to source observations; generic Horn models may contain additional sealed truths. `EvaluationKey` binds the condition revision, profile, context, endpoints, scope and epoch. Potential norms retain their origins; activation additionally requires consistent exact holds evidence. No fulfillment meaning is supplied before E03.

`EvidenceComplete` compares the manifest to independently fixed catalog and layout inventories. Registration has 17 normative obligations, rule-only has 20, and richer migration has 18. The current stronger registration implementation will retain its 20-obligation identity-extension qualification. Missing/reordered modules, shrunken catalogs and substituted identities cannot satisfy the contract. Combined witnesses have one compiled module; staged witnesses have data, typed, closure and expansion modules. General replay, projection and dependency evidence are required separately.

`RecordedCurrent` adds actual-currentness assumptions about every authoritative artifact. Those are host/hash assumptions and do not authenticate an issuer. `FreshQualified` also requires a successful verifier event with exact identity in the current nonempty invocation session. The verifier acceptance predicate is not a caller JSON flag. The actual runtime must issue this event only after exact statement/definition/axiom replay and concrete-value checks. A saved current manifest with an empty live event history cannot be freshly qualified. Fresh qualification describes the invocation; the saved result remains inspection evidence and cannot itself authorize a later application.

Unknown-resource, cancellation and unavailable-required-policy outcomes cannot claim derivation, complete closure, absence or shadow readiness. Qualified outcome is a necessary permission, not sufficient evidence for every claim: complete closure and well-typed in-profile query checks are still required for absence. All claims carry model class, query scope, change class, source profile, truth assumptions and evidence mode. Process success and semantic yes remain distinct.

Publication has prepared, committed and reconciliation-required states. A qualified publication is committed, uses the mediated writer boundary, matches the reviewed/observed generation and successor identity, and has fresh qualification. This is an abstract contract with explicit hypotheses, not a Lean proof of filesystem atomicity or durability. S09's file replacement is not an arbitrary-writer CAS. P08 must supply actual crash/recovery and durable-publication evidence within its stated boundary.

The rule-only theorem is retained for every arbitrary old model under CheckedExtension with fixed graph/domain/facts/roots/interpretation/context and fresh positive ordinary heads. Finite computed closure is a separate guarantee. Graph/domain/fact growth uses the separate initial-view transition profile; lifecycle change in E04 needs new obligations. No negation, root amplification, redelegation, general condition execution, overrides, authenticated external truth or live authority is inferred.

Required statement types and pure-value premise-removal controls are kernel-compiled before result serializers. The controls demonstrate inventory/identity failure, saved-current-without-fresh-replay and unary loss of exact target/scope. Imported v2 theorem aliases retain activation and arbitrary-old-model semantics. Inherited compiled modules are byte-current checked inputs, not a new independent-kernel replay. Same pinned Lean kernel, hash/host/compiler and externally supplied truth remain explicit assumptions.

Actual v2 feedback remains bound to its original worked packet. V1 R06/G4 remain pending. No deployment, publication or admission is authorized. Authority effect: none.
''')
s.write(HERE / 'assumptions.json', {'schema': 'relational.v3-assumptions/v1', 'items': [
    {'id': 'A-HOST', 'meaning': 'Host executes pinned compiler and does not forge verifier events or files.', 'proved': False},
    {'id': 'A-HASH', 'meaning': 'Byte hashing and canonical identity implementation correspond to recorded inputs.', 'proved': False},
    {'id': 'A-DECODER', 'meaning': 'JSON/normalization/generator is a tested boundary; E05 narrows IR trust but does not silently prove raw JSON.', 'proved': False},
    {'id': 'A-KERNEL', 'meaning': 'Fresh checking uses the same pinned Lean kernel; E06 independently studies another checker.', 'proved': False},
    {'id': 'A-TRUTH', 'meaning': 'Accepted assessments, policy/gate decisions, clocks and condition/action evidence truth are supplied.', 'proved': False},
    {'id': 'A-WRITER', 'meaning': 'Publication operates within the explicitly mediated/cooperating local writer boundary.', 'proved': False},
    {'id': 'A-DURABILITY', 'meaning': 'OS storage durability and crash recovery require P08 evidence, not graph theorems.', 'proved': False},
]})
s.write(HERE / 'decisions.json', {'schema': 'relational.v3-decisions/v1', 'selected_extensions': ['E00','E01','E02','E03','E04','E05','E06'], 'actual_selection_answer': 'Core plus all extensions (Recommended)', 'saved_result_authorizes_application': False, 'inherited_semantics': 'unchanged v2 meanings', 'baseline_transport': 'explicit named byte-bound v2 adapter, never relabel baseline schema', 'layout': 'staged default only after P02/P03 equivalence controls', 'publication_boundary': 'mediated/cooperating local candidate store', 'authority_effect': 'none'})
imports, dependency = s.predecessor_imports()
records = s.compile_modules(HERE / 'build', [(n,HERE/(n+'.lean')) for n in ['EvidenceSemantics','RequiredEvidenceStatements','EvidenceControls']], imports=[imports])
s.write(HERE / 'kernel-evidence.json', {'result': 'pass', 'modules': records, 'inherited_dependency_binding': dependency, 'toolchain': s.binding(s.lean_path()), 'scope': 'New independent definition/statement targets and pure-value controls compiled; inherited source/olean bytes checked.', 'fresh_independent_second_kernel': False, 'authority_effect': 'none'})
names = ['complete-manifest','missing-module-rejected','missing-obligation-rejected','wrong-proposal-rejected','reordered-modules-rejected','saved-current-not-fresh','unary-target-scope-loss','resource-cancellation-policy-blocks-claims','retained-active-needs-holds','retained-every-old-model-expands']
controls = [{'name': n, 'result': 'pass', 'method': 'actual-new-Lean-compilation'} for n in names]
s.write(HERE / 'controls.json', {'result': 'pass', 'controls': controls})
s.accept('P00', [
    'The independent EvidenceComplete/RecordedCurrent/FreshQualified, resource outcomes and mediated publication meanings are specified with explicit host/truth/decoder/kernel assumptions.',
    'All new required target types, proofs and pure-value controls compile under the byte-pinned Lean kernel without custom axioms or admitted proofs.',
    'Inherited meanings are imported/aliased unchanged; actual feedback remains v2 scoped and original v1 gates remain pending.'
], controls, extra=[HERE/'EvidenceControls.lean',HERE/'kernel-evidence.json',HERE/'controls.json',HERE/'run_p00.py'])
print('P00 accepted: formal semantic delta and actual kernel controls')
