"""Build a source-bound review and non-executed successor plan.

This script performs inventory/accounting checks and writes planning artifacts.
It does not qualify relations, compile proofs, mutate accepted evidence or accept
the proposed successor work.
"""
import collections
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'craft/formalization').is_dir())
B = ROOT / 'craft/formalization/candidates/relational-theorem-checker'

def read(p):
    return json.loads(p.read_text())

def bind(p):
    return {'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}

def verify(ref):
    p = ROOT / ref['path']
    assert bind(p) == ref, 'Stale source: ' + ref['path']
    return p

def write(name, value):
    p = HERE / name
    if isinstance(value, str):
        p.write_text(value)
    else:
        p.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def link(p, label):
    return f'[{label}]({p})'

FAMILIES = {
    'definitions-identity-lineage': ['asserts-identity-of', 'carries-definition', 'derives-from', 'instance-of', 'originates-from', 'profiled-by', 'successor-of', 'binds-implementation'],
    'authority-governance-membership': ['acts-for', 'assigned-to', 'member-of', 'scopes-authority-over', 'has-capability', 'governed-by', 'inherits-contract'],
    'evidence-conformance-assessment': ['conforms-to', 'evaluates', 'evidence-bears-on', 'realizes', 'violates'],
    'execution-output-fulfillment': ['declares-effect-on', 'materializes-consequence', 'performs', 'produces', 'fulfills-request'],
    'context-intent-views': ['frames', 'consumes-view', 'requests-resolution-of', 'addresses-intent'],
    'research-learning-improvement': ['addresses-improvement-target', 'applies-lesson', 'challenges', 'contributes-to', 'engages-inquiry', 'tests-hypothesis', 'uses-method', 'uses-tool'],
    'failure-response-control': ['affects', 'controls', 'occurs-during', 'responds-to'],
}
FAMILY = {'relation.' + k: group for group, names in FAMILIES.items() for k in names}

FIELD_SPECIAL = {
    'effective_period': ('HalfOpenInterval', 'Decode a declared interval into start/stop in one owned time domain; prove start ≤ epoch < stop and reject malformed or incomparable intervals.'),
    'revocation_state': ('RevocationSnapshot', 'Resolve an exact revocation record and as-of epoch; missing status remains unknown and never means unrevoked.'),
    'definition_sha256': ('DefinitionContentCommitment', 'Bind the resolved definition revision to exact content bytes under the stated hash assumption; a matching digest is not ownership or approval.'),
    'view_digest': ('ViewContentCommitment', 'Bind consumption to an immutable view content identity; do not infer source currentness from a digest.'),
    'cursor': ('ViewCursor', 'Define cursor meaning in the selected view revision, including its allowed range and consumed extent; it is not a global clock.'),
    'polarity': ('EvidencePolarity', 'Use an owner-defined support/contradict domain; polarity toward a claim is distinct from truth or acceptance of that claim.'),
    'instruction_precedence': ('PrecedencePolicy', 'Resolve a versioned precedence policy and prove its selected ordering; no arbitrary integer or source order can silently choose the governing instruction.'),
    'succession_effect': ('SuccessionEffect', 'Distinguish continues from supersedes; prove replacement requires the supersedes value and the separately qualified lifecycle operation.'),
    'intended_outcome': ('DeclaredOutcome', 'Resolve a versioned declared outcome; stating the desired result cannot establish that it happened.'),
    'declaration_basis': ('DeclarationBasis', 'Resolve the source basis for the capability declaration; a declaration does not prove successful performance or permission.'),
    'session_ref': ('SessionRevisionRef', 'Resolve the exact attributable session and its frame; name matching alone does not authenticate the actor.'),
    'action_receipt_ref': ('ActionReceiptRevisionRef', 'Resolve an exact action/output receipt with owner and provenance; distinguish local execution evidence from external-world authenticity.'),
    'applicability_assessment_ref': ('AssessmentRevisionRef', 'Resolve an assessment for this exact lesson revision, subject and frame under an owned assessment policy.'),
    'binding_ref': ('BindingRevisionRef', 'Resolve a relation-specific binding record with exact roles, endpoint revisions, owner and lifecycle; shared spelling does not make binding meanings interchangeable.'),
    'relation_record_ref': ('LifecycleRelationRecordRef', 'Resolve the lifecycle-bearing assignment record with exact assignee and role/responsibility revisions.'),
    'delegation_ref': ('DelegationRevisionRef', 'Resolve the exact delegation, agent and principal; retain scope/action/time/redelegation restrictions and source membership.'),
    'scope_ref': ('OwnedScopeRevisionRef', 'Resolve the exact scope and its owner-defined inclusion relation; prove scope/endpoint/frame agreement and preserve every ancestor restriction rather than treating a scope token as permission.'),
}

def field_contract(field):
    if field in FIELD_SPECIAL:
        return FIELD_SPECIAL[field]
    if field.endswith('_version_ref') or field.endswith('_revision_ref'):
        return ('ExactRevisionRef', 'Resolve the exact typed target or governed subject revision specified by this relation; reject stale revisions and prove endpoint/record correspondence.')
    if field.endswith('_ref'):
        return ('OwnedTypedReference', 'Resolve the opaque source token through a versioned owner-selected catalog; prove reference role, endpoint and frame agreement. Unresolved tokens stay unsupported.')
    if field.endswith('_role') or field.endswith('_kind'):
        return ('OwnedRoleCode', 'Define the relation-specific role/code domain and its effect on meaning; membership in a code catalog is not authority, execution or success.')
    if field.endswith('_scope') or field in ['scope_ref', 'claim_scope', 'impact_scope']:
        return ('OwnedScope', 'Define the owned scope domain, its exact identity and permitted inclusion relation; preserve subject/target/context distinctions and forbid scope widening.')
    if field.endswith('_posture') or field in ['challenge_mode', 'consumption_purpose', 'evaluation_purpose']:
        return ('OwnedPostureCode', 'Define the exact posture/mode/purpose domain and distinguish declaration, attempted action, observation and accepted evidence; do not equate a label with successful execution.')
    raise AssertionError('Missing proposed interpretation for ' + field)

EXTENSIONS = [
    ('E00', 'Condition expressions', 'v3/e00/ExpressionSemantics.lean', 'v3/e00/adapter.py',
     'An expression and its root revision are caller supplied. Different ASTs under the same root revision receive different definition identities; no owned catalog chooses the intended AST. Opposing active norms have no winner policy.',
     'Resolve the owned root revision to immutable expression content, preserve the frame and norm origin, and explicitly define conflict/precedence handling. Supplied leaf truth remains a declared boundary.',
     ['definition_resolution_unique', 'owned_activation_exact', 'unknown_never_activates', 'activation_preserves_origin'],
     '128 nodes, depth 16, 64 distinct keys and 128 evaluation records.'),
    ('E01', 'Evidence collections', 'v3/e01/EvidenceCollectionSemantics.lean', 'v3/e01/mapper.py',
     'Any accepted exact support is the chosen policy, not a quorum or issuer hierarchy. Individual legacy assessments lack revisions and issuer authentication; identity is relative to the normalized graph.',
     'Resolve individually versioned assessments, exact issuers and an owned aggregation policy. Preserve the existing any-support profile and opaque comma-token migration. Add quorum or disagreement policies only with separate definitions and proofs.',
     ['owned_supports_exact', 'all_valid_supports_retained', 'aggregation_policy_separation', 'legacy_projection_preserved'],
     '64 selected references; snapshot membership rather than individual issuer currentness.'),
    ('E02', 'Redelegation', 'v3/e02/ChainSemantics.lean', 'v3/e02/chain_adapter.py',
     'All edge words are generated before path filtering. The 4096-word ceiling can refuse sparse graphs; a no answer concerns only the declared source/depth. Gate, revocation and clock facts are supplied.',
     'Prove adjacency/visited-set traversal equivalent to the bounded joined simple-path universe. Preserve all required support paths and uncertainty provenance, and distinguish completed absence from resource cutoff. Add exact snapshot/revocation provenance.',
     ['adjacency_universe_exact', 'all_path_supports_exact', 'chain_non_amplification', 'completed_bounded_absence_sound'],
     '32 nodes, 64 hops, depth 4, at most 4096 edge words in the accepted implementation.'),
    ('E03', 'Fulfillment', 'v3/e03/FulfillmentSemantics.lean', 'v3/e03/fulfillment_adapter.py',
     'The caller supplies the criterion universe. A reduced universe can be a different valid fulfilled snapshot. Action/output/evaluation truth is supplied, and only one evaluation per criterion is allowed. The universal theorem establishes positive fulfillment; a complete independent three-way verdict contract is still needed.',
     'Resolve the requirement revision to the exact owned criterion universe, bind execution/output provenance and assessment policy, and prove yes/no/unknown semantics under explicit well-formedness. Define whether a negative evaluation with unaccepted action/output is admissible refutation evidence.',
     ['owned_criteria_complete', 'owned_fulfillment_exact', 'requirement_revision_invalidates', 'fulfillment_verdict_sound_complete'],
     'Nonempty exact named criteria, one selected evaluation per criterion; no general conflict aggregation.'),
    ('E04', 'Lifecycle', 'v3/e04/LifecycleSemantics.lean', 'v3/e04/lifecycle_adapter.py',
     'Eligibility=yes and accepted review are supplied keyed values. The public transition does not consume a complete core qualification. Storage-primitive crash probes do not cover fresh proof creation through the whole public commit path.',
     'Consume an independently checked composed qualification certificate and actual exact owner review. Prove well-formed state and semantic invariant preservation, then test crashes across the public qualify/recapture/commit path in isolated stores.',
     ['transition_requires_complete_qualification', 'transition_preserves_well_formed_state', 'transition_preserves_semantic_invariant', 'recovery_is_not_a_fresh_event'],
     'One owned cooperating local store; no hostile-process or distributed authority guarantee.'),
    ('E05', 'Checked IR', 'v3/e05/ImportCorrectness.lean', 'v3/e05/adapter.py',
     'The universal theorem begins after Python byte decoding and emission. Whole decoded-value witnesses do not universally prove raw parsing or domain semantic import.',
     'Define a restricted byte grammar and a proof-producing parser or independently verified parse certificate. Prove complete byte consumption, IR denotation and each domain import composition. Keep hash/host assumptions visible.',
     ['parse_certificate_sound', 'byte_to_ir_denotation', 'domain_import_composition', 'raw_binding_preserved'],
     '16 items, 8192 tree visits, depth 32; earlier encodings timed out.'),
    ('E06', 'Independent checking', 'v3/e06/translation-contract.md', 'v3/e06/run_sample_controls.py',
     'One 18-declaration theorem closure is independently checked. There is no E06 qualification adapter or whole-core coverage. A valid proof under substituted definitions can still be accepted by a kernel.',
     'Inventory every required theorem/declaration closure for the new profile, anchor statements and semantic definitions independently, and implement explicit feature/axiom/resource/disagreement policies. First check substantial core and semantic examples; then require complete mandatory closure coverage before claiming whole-profile independent assurance.',
     ['trusted_challenge_matches_export', 'semantic_definition_closure_anchored', 'required_check_inventory_complete', 'combined_assurance_has_no_missing_result'],
     'Tiny sample only, no axioms, Nat/String extensions disabled; costs cannot predict whole-core checking.'),
]

def task(i, title, deps, layer, outputs, criteria, failures, owner='implementation/proof reviewer'):
    return {'id': i, 'title': title, 'depends_on': deps, 'layer': layer, 'status': 'proposed',
            'owner_role': owner, 'owner_assignment': None, 'outputs': outputs,
            'exit_criteria': criteria, 'failure_controls': failures,
            'formalization_before_runtime': True, 'implementation_authorized_by_this_plan': False}

def main():
    ledger_path = B/'v1/coverage/semantics/semantic-coverage-ledger.json'
    registry_path = B/'v1/registry/normalized-registry.json'
    ledger, registry = read(ledger_path), read(registry_path)
    relation_review = read(B/'v2/s14/requirement-audit.json')
    old_review = {r['relation']: r for r in relation_review['relations']}
    assert len(FAMILY) == len(ledger['rows']) == registry['kind_count'] == 41
    kinds = {k['id']: k for k in registry['kinds']}
    assert set(kinds) == set(FAMILY) == {r['id'] for r in ledger['rows']}
    source_inputs = [ledger_path, registry_path, B/'v2/s14/requirement-audit.json',
        B/'v4/gate-closure/execution/closure-completion.json', B/'v4/gate-closure/execution/final-readout-verification.json',
        B/'v1/pilot/reviews/2026-10-10-r06-g4-v4/extensions-annex.md',
        B/'v3/execution/reviews/2026-10-10-seven-extensions-r06-g4/PLAN.md',
        B/'v3/execution/reviews/2026-10-10-seven-extensions-r06-g4/boundary-observations.json',
        B/'v3/e03/fulfillment.schema.json', B/'v3/e05/CanonicalIR.lean',
        B/'v3/e04/store.py', B/'v3/e01/migration-review.md',
        ROOT/'docs/plans/relational-theorem-checker/PLAN-SOURCE.json']
    for e in EXTENSIONS:
        source_inputs += [B/e[2], B/e[3]]
    for r in ledger['rows']:
        source_inputs.append(verify(r['source']))
        for o in r['obligations']:
            for ref in o.get('evidence', []):
                verify(ref)
    source_inputs = sorted(set(source_inputs))
    completion = read(B/'v4/gate-closure/execution/closure-completion.json')
    for key in ['execution_plan', 'final_audit', 'current_original_view', 'original_plan_snapshot']:
        verify(completion[key])
    current = read(verify(completion['current_original_view']))
    assert current['counts']['accepted'] == 35 and current['overlay_accepted'] == ['R06', 'G4']
    unsupported, discharged, relation_units = [], [], []
    totals = collections.Counter()
    family_totals = collections.Counter()
    relation_md = 'Per-relation review of all 41 inherited kinds\n\n'
    relation_md += 'All proposed types, predicates and proof statements below are design hypotheses requiring exact owner review. No new inherited obligation is discharged by this document. Source strings remain opaque in accepted profiles until a new checked mapping is established.\n\n'
    for index, r in enumerate(ledger['rows']):
        k = kinds[r['id']]
        assert k['version'] == r['version'] and k['source'] == r['source']
        expected = {r['id']+':ordered-signature', r['id']+':qualifier-shape', r['id']+':operational-effect'}
        expected |= {r['id']+':meaning:'+f for f in k['fields']}
        expected |= {r['id']+':forbidden:'+str(i) for i in range(len(k['forbidden_inferences']))}
        assert expected == {o['id'] for o in r['obligations']}
        assert len(expected) == len(r['obligations'])
        group = FAMILY[r['id']]
        unit_id = f'K{index:02}'
        unit_obs = []
        relation_md += f'\n**{unit_id} — {r["id"]}**\n\n'
        relation_md += link(verify(r['source']), 'Exact source declaration') + '\n\n'
        relation_md += '**Question:** ' + k['unique_question'] + '\n\n'
        relation_md += '**Source effect:** ' + k['operational_effect'] + '\n\n'
        fragment = old_review[r['id']]['implemented_fragment'] or 'No additional implemented semantic fragment; the wider improvement is deferred'
        relation_md += '**Current evidence:** ' + fragment + '. This does not discharge the source-wide remainder.\n\n'
        relation_md += '**Proposed qualifier interpretations:**\n\n'
        for o in r['obligations']:
            if o['status'] == 'discharged':
                discharged.append({'kind': r['id'], **o})
                if ':meaning:' in o['id']:
                    relation_md += '- '+o['id'].split(':meaning:')[1]+': retain the proved '+str(o.get('claim_scope'))+' meaning and its exact evidence.\n'
                continue
            category = 'qualifier-meaning' if ':meaning:' in o['id'] else 'forbidden-inference' if ':forbidden:' in o['id'] else 'operational-effect'
            totals[category] += 1
            family_totals[group] += 1
            item = {'id': o['id'], 'kind': r['id'], 'kind_version': r['version'], 'source': r['source'],
                    'category': category, 'source_statement': o['statement'], 'source_status': o['status'],
                    'hard': o['hard'], 'family': group, 'work_unit': unit_id, 'proposed_status': 'not-started',
                    'owner_assignment': None, 'discharge_evidence': [], 'owner_meaning_decision': None,
                    'cannot_discharge_from_extension_receipt_alone': True}
            if category == 'qualifier-meaning':
                field = o['id'].split(':meaning:')[1]
                typ, detail = field_contract(field)
                item.update(field=field, proposed_type=typ, missing=detail,
                            theorem_target='Successful exact-token decoding and owner resolution ↔ the independently defined qualifier meaning, under explicit catalog/snapshot well-formedness.',
                            controls=['unresolved token', 'wrong role', 'wrong endpoint/revision/frame', 'same catalog revision with changed content'])
                relation_md += '- '+field+' → proposed `'+typ+'`: '+detail+'\n'
            elif category == 'operational-effect':
                item.update(missing='An owner-reviewed relation-specific Meaning predicate and source refinement; distinguish recorded claims, checked snapshot truth and actual local/external execution.',
                            theorem_target='relationChecker_k(S,a)=true ↔ Meaning_k(S,a), with source-to-typed refinement and every external premise named.',
                            controls=['nonvacuous positive instance', 'weaker recorded-only statement substituted', 'effect/authority claimed without independent premise'])
            else:
                item.update(missing='An exact typed conclusion predicate for this label and a nonvacuous scoped non-entailment witness; a globally forbidden rule additionally needs closure/protected-state preservation.',
                            theorem_target='∃ M, ModelOf(T_k,M) ∧ Meaning_k(M,a) ∧ ¬ Conclusion_k_label(M,a). Separately prove effect/inference invariants where required.',
                            controls=['antecedent actually holds', 'conclusion actually absent/false in witness', 'complete intended theory and exact conclusion pinned', 'extra rule introduces forbidden inference'])
            unsupported.append(item)
            unit_obs.append(o['id'])
        relation_md += '\n**Effect proof required:** independently define the exact question/effect, resolve source roles and revisions, prove checker equivalence and map the immutable source declaration to that definition. “Records only” must not become an empty predicate that vacuously ignores the intended connection.\n\n'
        relation_md += '**Forbidden conclusions requiring separate meaning and evidence:** '+', '.join(k['forbidden_inferences'])+'. Each needs an exact conclusion definition and satisfiable scoped countermodel. An exclusion is non-entailment, not a claim that the conclusion is always false.\n\n'
        relation_md += '**Work order:** definition and owner interpretation → exact formal proof/challenge → companion mapping/runtime adapter → actual positive and boundary evidence → per-obligation review.\n'
        relation_units.append({'id': unit_id, 'kind': r['id'], 'family': group, 'source': r['source'],
            'source_question': k['unique_question'], 'source_effect': k['operational_effect'],
            'source_ordered_pairs': k['pairs'], 'semantic_signature_branch_count': len(k['pairs']),
            'baseline_unsupported_obligations': unit_obs, 'baseline_unsupported_count': len(unit_obs),
            'status': 'proposed', 'owner_role': 'relation-definition owner plus semantic/proof reviewer', 'owner_assignment': None,
            'formalization_task': 'N01', 'proof_task': 'N02', 'runtime_task': 'N12', 'final_coverage_task': 'N16',
            'ordered_steps': ['owned-definition-brief', 'formalize-independent-meaning', 'review-exact-meaning', 'prove-mapping-and-required-laws', 'implement-versioned-adapter', 'run-real-kernel-cases', 'accept-each-exact-obligation'],
            'requires_all_obligations': True})
    assert dict(totals) == {'qualifier-meaning':74, 'operational-effect':41, 'forbidden-inference':148}
    assert len(unsupported) == 263 and len(discharged) == 90
    assert len({o['id'] for o in unsupported}) == 263
    assert sum(u['semantic_signature_branch_count'] for u in relation_units) == 550
    source_manifest = {'schema':'relational.successor-review-evidence/v1', 'method':'Current selected-source inspection, exact inventory/accounting and SHA256 verification; existing theorem executions reused, no new proof compilation.',
        'sources':[bind(p) for p in source_inputs], 'original_gate_completion':bind(B/'v4/gate-closure/execution/closure-completion.json'),
        'external_primary_sources':[{'title':'Lean proof validation and intended statement matching','url':'https://lean-lang.org/doc/reference/latest/ValidatingProofs/'},
                                    {'title':'JSON grammar and interoperability','url':'https://www.rfc-editor.org/rfc/rfc8259'}],
        'authority_effect':'none'}
    write('evidence-manifest.json',source_manifest)
    write('inherited-obligations.json', {'schema':'relational.inherited-obligation-review/v1', 'source_ledger':bind(ledger_path),
        'source_registry':bind(registry_path), 'counts':dict(totals), 'total_pending':263, 'retained_discharged_count':90,
        'full_source_semantics_proved':False, 'obligations':unsupported, 'authority_effect':'none'})
    write('relation-work-pack.json', {'schema':'relational.semantic-kind-work-pack/v1', 'status':'proposed-not-executed',
        'units':relation_units, 'total_kinds':41, 'total_inherited_obligations':263,
        'families':[{'id':g,'kinds':['relation.'+x for x in names], 'obligations':family_totals[g]} for g,names in FAMILIES.items()]})
    write('RELATION-REVIEW.md',relation_md)
    write('FORMALIZATION.md',FORMALIZATION)
    tasks = make_tasks()
    ids = {t['id'] for t in tasks}
    assert len(ids) == len(tasks)
    assert tasks[0]['id'] == 'N00' and tasks[0]['depends_on'] == []
    seen = set()
    while len(seen)<len(tasks):
        ready = {t['id'] for t in tasks if set(t['depends_on']) <= seen} - seen
        assert ready, 'Cycle or missing dependency'
        seen |= ready
    plan = {'schema':'relational.integration-semantic-completion-plan/v1', 'date':'2026-10-10',
        'status':'proposed-not-executed', 'formalization_first':True, 'first_task':'N00',
        'scope':'All seven extension integration gaps and exact inherited 263 obligations for a versioned bounded successor profile.',
        'retained_original_acceptance':bind(B/'v4/gate-closure/execution/closure-completion.json'),
        'source_obligation_inventory':bind(HERE/'inherited-obligations.json'), 'relation_work_pack':bind(HERE/'relation-work-pack.json'),
        'tasks':tasks, 'implementation_authorized_by_this_plan':False, 'authority_effect':'none',
        'completion_policy':{'baseline_ids':263,'required_discharge_count':263,'original_discharged_items_retained':90,
            'owner_retirement_counts_as_discharge':False,'unsupported_counts_as_discharge':False,
            'require_all_new_integration_obligations':True,'require_actual_successor_assessment':True,
            'independent_checking_completion_requires_all_mandatory_selected_closures':True}}
    write('plan.json',plan)
    write('PLAN.md',make_plan_md(tasks,family_totals))
    write('implementation-layering.md',LAYERING)
    write('REVIEW.md',make_review(totals,family_totals))
    prior_audit = read(B/'v4/gate-closure/execution/h01/predecessor-current-audit.json')
    accepted_sources = {x['path']:x['sha256'] for x in prior_audit['source_bindings']}
    matched = 0
    for ref in source_manifest['sources']:
        verify(ref)
        if ref['path'] in accepted_sources:
            assert ref['sha256'] == accepted_sources[ref['path']], 'Changed accepted predecessor source'
            matched += 1
    local_links = 0
    for p in HERE.glob('*.md'):
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',p.read_text()):
            if target.startswith(('https://','http://','#')):
                continue
            assert Path(target).is_absolute() and Path(target).is_file(), 'Broken local link: '+target
            local_links += 1
    task_map = {t['id']:t for t in tasks}
    for t in tasks:
        for dep in t['depends_on']:
            assert task_map[dep]['layer'] <= t['layer'], 'Layer dependency regression'
    assert sorted(x for u in relation_units for x in u['baseline_unsupported_obligations']) == sorted(x['id'] for x in unsupported)
    write('validation.json',{'result':'pass','method':'Planning consistency checks, not implementation acceptance',
        'kinds_accounted':41,'original_obligation_ids_accounted':353,'retained_discharged':90,'inherited_pending':263,
        'pending_by_category':dict(totals),'source_declarations_current':41,'forbidden_label_spellings':len({o['source_statement'] for o in unsupported if o['category']=='forbidden-inference'}),
        'qualifier_name_spellings':len({o['field'] for o in unsupported if o['category']=='qualifier-meaning'}),
        'family_partition_complete':True,'dag_acyclic':True,'tasks':len(tasks),'dependency_edges':sum(len(t['depends_on']) for t in tasks),
        'formalization_is_first':True,'implementation_executed':False,'new_theorems_proved':0,'new_obligations_discharged':0,
        'selected_source_bindings':len(source_inputs),
        'selected_predecessor_bindings_matching_accepted_audit':matched,
        'local_markdown_links_checked':local_links, 'layer_dependencies_non_regressing':True,
        'source_id_partition_exact':True, 'semantic_signature_branches_accounted':550,
        'original_R06_G4_completion_current':True, 'authority_effect':'none'})
    print(json.dumps({'review':str(HERE/'REVIEW.md'),'pending':263,'categories':dict(totals),'tasks':len(tasks),'source_bindings':len(source_inputs),'implementation_executed':False},indent=2))

FORMALIZATION = '''Formalization contract for the proposed successor

This is a theorem specification, not compiled Lean code. Every formula below is a proposed target. All new models and policies require owner interpretation and exact statement/definition review. Existing v1–v4 artifacts are immutable inputs.

1. Define shared semantic objects first.

`RevisionRef = (artifact_id, revision, content_binding)`. References retain type/role. `Frame = (profile_revision, subject_revision, target_revision, context_revision, scope_revision, snapshot_revision, epoch, time_domain)`. A snapshot binds its owner-selected sources, provenance, as-of boundary and completeness statement. Exact epoch equality alone is not real-world currentness.

An `OwnedCatalog` has a trusted ownership basis, immutable revision, closed unique keys and exact content. Do not treat `owner=true`, `review.accepted=true` or a matching SHA as authentication. Local actual review capture or a verified source adapter supplies the ownership premise. `WellFormedCatalog` is explicit, not an unexamined axiom. Resolving an absent entry returns unresolved/unsupported, never a default approval.

Define persistent revision keys `(owner_namespace, artifact_id, revision)` and legal catalog evolution. Uniqueness inside one snapshot is insufficient: two catalogs could otherwise approve different content under the same stable revision. Legal extension preserves all existing bindings, and content changes require a fresh revision. If a required selected revision changes, the old qualification is stale for that new target; a historical proof about its original revision remains valid in its original scope.

`Truth` keeps yes/no/unknown. Define the positive and negative meanings per operation. Distinguish rejected input, violated meaning, absent completed bounded support, unknown evidence, unsupported profile, incomplete/resource refusal, stale evidence, conflict and independent-checker disagreement. These are not all semantic false. Contradictory active norms require a declared owner policy; there is no default winner.

2. Define obligations and coverage independently of submitted results.

An `Obligation` binds its original ID, kind/source revision, owned meaning revision, exact statement and definition closure, universe/frame, required method, dependencies and trust premises. Derive all applicable obligations from the actual diff and owned profile policy. The source set contains the exact 263 inherited pending IDs; new integration obligations have separate IDs. Preserve the 90 earlier discharges and their scopes. Missing, duplicated or substituted obligations refuse readiness.

`Discharged(o,e,S)` means current exact challenge/definition matching, allowed completed evidence and owner-reviewed source refinement under the named premises. It does not mean an input label says passed. Retirement, unsupported status and a narrower unrelated theorem cannot count as discharge.

Proposed coverage theorem:

    Ready(P,S,E) → ∀ o ∈ Required(P,S), ∃ e ∈ E, Discharged(o,e,S)

Proposed full-inherited-coverage theorem:

    FullInheritedReady(S,E) →
      {o.id | o ∈ DischargedInherited(S,E)} = Original263Ids

This full criterion concerns all inherited IDs. A first narrow pilot may be ready for its owned supported subset while full inherited completion remains false. The policy, rather than the caller, chooses that subset.

3. Resolve definitions and criteria before evaluation.

Proposed catalog theorem:

    WellFormedCatalog(C) ∧ resolve(C,owner,revision)=Some d₁ ∧
      resolve(C,owner,revision)=Some d₂ → d₁=d₂

Proposed revision/content theorem:

    acceptedDefinition(C,r,h₁) ∧ acceptedDefinition(C,r,h₂) → h₁=h₂

Proposed cross-catalog preservation theorem:

    LegalCatalogExtension(C,C′) ∧ resolve(C,owner,r)=Some d
      → resolve(C′,owner,r)=Some d

Content commitments rely on the stated hash/byte-binding assumptions. They do not prove collision resistance or human authenticity. Changed content needs a new owner-approved revision, and every dependent result is invalidated or explicitly requalified.

E00 activation must use the resolved expression, exact frame and retained norm origin. E03 fulfillment must use `Criteria(resolve(requirement_revision))`, not a caller-shortened list:

    FulfilledOwned(S,r) →
      ∀ c ∈ Criteria(resolve(r)), ∃ e, ExactAcceptedSupport(S,r,c,e)

Add a well-formedness predicate for action/output/evaluation ownership and prove all three verdict rails. Current E03 normalization checks request/requirement/frame correspondence. Its generic negative criterion branch uses the criterion reference without those checks; lift normalizer obligations into a typed theorem rather than claiming stale negative evidence is accepted by the public API. Also make the admissibility of negative evidence from unaccepted actions/outputs an explicit policy.

4. Formalize every relation's actual meaning.

For each of the 41 kinds define independent `Meaning_k(S,a)` from the source question, endpoint revisions, typed qualifiers and owned evidence policy. Its definition must not call the checker it is meant to validate. Provide a satisfiable positive example so a false antecedent cannot make the proof vacuous.

    decode_k(C,S,raw)=Some a ∧ WellFormed(C,S)
      → SourceMeaning_k(C,S,raw) ↔ Meaning_k(S,a)

    relationChecker_k(S,a)=true ↔ Meaning_k(S,a)

The 74 qualifier obligations instantiate exact source-token decoding and owner resolution. The 41 effect obligations additionally identify the claim tier: recorded intent, checked supplied snapshot, executed local effect or authenticated external observation. A recorded receipt does not establish that an atomic authorized action actually ran. Execution claims require a verified state transition and an appropriate provenance adapter; external truth remains conditional on the named external evidence model.

The 148 forbidden-inference obligations require exact conclusion meanings. There are 83 distinct label spellings, but the same spelling need not denote the same predicate for every relation. For each intended non-entailment prove a nonvacuous countermodel:

    ∃ M,a, ModelOf(T_k,M) ∧ Meaning_k(M,a) ∧ ¬ Conclusion_k,label(M,a)

This establishes `T_k + Meaning_k` does not entail the conclusion. It does not establish the conclusion is always false. Non-entailment for a single relation is distinct from a global inference prohibition. Global no-authority/no-root-manufacture and identity/ownership preservation claims need transition or least-closure invariants over the full applicable rule theory. Pin that theory; adding a rule can invalidate the result.

5. Compose qualification before lifecycle commitment.

`Qualified` binds the exact source/candidate pair, definition/evidence policies, snapshot/frame, independently derived complete obligations, checked meanings, required preservation/conservativity evidence, fresh process-local event and actual exact owner review. Each component is required only when the owned profile says it applies; an unrelated yes result cannot satisfy a requirement. Projection bridges retain subject, target, scope, context and epoch across the separately defined E00–E04 types. No existential unary projection can establish conformance to an arbitrary target.

    ComposedCheck(P,S,proposal)=Accepted cert → Qualified(P,S,proposal,cert)

    transition(S,proposal,cert)=Some S′ →
      Qualified(P,S,proposal,cert) ∧ WF(S′) ∧ SemanticInvariant(S′) ∧
      PreservedHistory(S,S′) ∧ PreservedEvidence(S,S′)

Avoid a circular premise: candidate eligibility cannot require the receipt that its own future commit will create. Define pre-commit qualification and post-commit materialization separately. A future output is not already a materialized consequence. Previously recorded consequences use their own exact earlier receipts. Recovery checks recorded state and creates no fresh event.

6. Improve traversal without changing absence semantics.

Prove the adjacency/visited-set implementation enumerates exactly the effective joined simple paths represented by the old edge-word universe within the declared depth. If the result includes every support, prove complete support retention and specify ordering/canonicalization; an early existential witness is insufficient for that result contract. A cutoff gives incomplete/resource refusal, never a completed no. No result claims unbounded-chain absence.

7. Reduce transport and checker boundaries explicitly.

Specify a restricted UTF-8 JSON grammar: scalar Unicode, exact escape decoding, unique keys, full byte consumption and explicit natural-number lexemes. Choose and review handling of `-0`, exponents, fractions and escapes rather than inheriting Python coercion. JSON standard validity and this profile's narrower validity are different.

    verifyParse(bytes,certificate)=Some ir → ByteDenotes(bytes,Denote(ir))

    verifyParse(bytes,certificate)=Some ir ∧ domainImport(ir)=Some a
      → DomainByteMeaning(bytes,a)

`ByteDenotes` is an independent inductively specified grammar/denotation relation, including full consumption. `DomainByteMeaning` uses the owned domain predicates, rather than defining itself as the importer returned true. Prove uniqueness of the supported byte denotation and the exact mapping assumptions needed for domain composition.

The certificate must bind and check all raw bytes/spans, not merely repeat an emitter's expected value. An untrusted generator may propose the certificate. Hashes and host execution remain stated premises unless separately formalized. Universal refinement is distinct from finite differential tests.

For independent checking, require both valid proof and the independently anchored intended statement/semantic definitions. Inventory all mandatory closures, universes, inductives/recursors, quotients, primitive extensions and allowed axioms. Implement accept/reject/unsupported/resource/disagreement distinctly. Retain the original mandatory Lean check. The first two substantial independently checked theorems are a milestone; they do not complete whole-profile assurance. Full completion requires every mandatory selected closure to pass or a reviewed versioned narrowing that does not misreport the wider goal complete.

Lean's official guidance separates proof validity from intended statement meaning and explains challenge comparison and independent kernels: https://lean-lang.org/doc/reference/latest/ValidatingProofs/. The JSON grammar baseline is RFC 8259: https://www.rfc-editor.org/rfc/rfc8259.
'''

def make_tasks():
    return [
      task('N00','Formalize the shared meaning, ownership, frame and coverage model',[], 'L0',
           ['SharedSemantics.lean','CoverageSemantics.lean','formal-contract.md','trust-premise-register.json'],
           ['Compile common definitions/proofs for exact identities, unique owner resolution, complete obligation sets and no self-seeding qualification.','Use an owner-bound condition and two-criterion requirement as the smallest formal composition; exact replacement/omission counterexamples are stated.'],
           ['Same revision/different AST','Removed criterion','Positive caller eligibility flag with no complete qualification']),
      task('N01','Specify and review all 41 relation definitions and source meanings',['N00'],'L1',
           ['41 owner definition briefs','74 qualifier interpretations','41 effect models','148 exact conclusion definitions','owner-review/challenge manifest'],
           ['Account for all 263 IDs and retain 90 existing discharges.','Each kind has an independent satisfiable meaning, exact source refinement and declared claim tier; actual assigned owners review choices and policy ambiguity.'],
           ['Generic effect treated as complete meaning','Same label silently merged across roles','Physical/execution truth asserted from a supplied flag'], 'relation-definition owners and semantic reviewers'),
      task('N02','Prove all inherited semantic claims and mapping contracts',['N01'],'L1',
           ['41 formal relation packages','per-ID proof/challenge coverage','family theorem library'],
           ['Every one of the 263 IDs maps to exact checked statement/definitions, owner-approved interpretation and required proof or satisfiable countermodel.','Prove source mapping, qualifier agreement, effect equivalence and required closure/state invariants; no unchecked axiom hides an unresolved meaning.','Account for semantic branches over all 550 declared ordered pairs; one exemplar per kind does not establish every role-sensitive case.'],
           ['False antecedent','Wrong conclusion/theory','Weaker predicate substitution','Countermodel with no valid relation instance']),
      task('N03','Freeze successor schemas, APIs and proof-result contracts',['N00','N01'],'L1',
           ['owned-definition/requirement/evidence schemas','snapshot and qualification contracts','semantic-coverage schema','typed profile import/API specification'],
           ['Closed versioned contracts bind definitions, criteria, evidence policy, exact frames, challenge inventories and allowed result states.','Derivation of mandatory obligations is owned and independent of submitted results; migration retains old opaque tokens.'],
           ['Extra/missing field','Duplicate ID','Cross-profile receipt','Client-selected incomplete obligation universe']),
      task('N04','Implement owned source catalogs and exact snapshot resolution',['N02','N03'],'L2',
           ['definition/requirement/evidence resolvers','immutable catalog store','snapshot resolver','source adapter contracts'],
           ['Actual resolution matches reviewed formal contracts, including owner basis, immutable revisions and content conflict rejection.','Unresolved owner/token/time/provenance stays unresolved; no fabricated authentication fixture can become actual evidence.'],
           ['Same revision/content substitution','Stale catalog/snapshot','Unassigned owner','Missing source content']),
      task('N05','Integrate owned expression definitions and norm activation',['N04'],'L2',
           ['E00 successor adapter','owned activation witnesses','conflict-policy evidence'],
           ['Only the resolved AST qualifies; full origin and frame survive activation.','Unknown and conflict semantics match the reviewed policy and earlier bounded guarantees.'],
           ['Atom versus negation under one root revision','Wrong condition revision','Unknown leaf','Opposing norms with no resolution policy']),
      task('N06','Integrate versioned evidence and issuer/policy ownership',['N04'],'L2',
           ['E01 successor adapter','assessment migration','aggregation policy witnesses'],
           ['Exact assessment revision/issuer/policy supports are retained and independently checked.','Legacy opaque-token and any-support meaning preserved; alternative policies are separately versioned.'],
           ['Wrong issuer/revision','Rejected support','Policy substitution','Comma token split','Missing required support']),
      task('N07','Replace edge-word enumeration with proved bounded traversal',['N02','N03','N04'],'L2',
           ['adjacency traversal proof','E02 successor adapter','path completeness certificates'],
           ['Traversal agrees with bounded simple-path meaning, retains required support/unknown provenance and ancestor restrictions.','Incomplete traversal or unavailable resource enforcement cannot establish no.'],
           ['Cycle/no seed','Unknown ancestor','Alternate valid path','Widening delegation','Dense cutoff','Sparse graph differential universe']),
      task('N08','Integrate owner-complete fulfillment and provenance',['N04','N05','N06'],'L2',
           ['E03 successor adapter','owned requirement/criterion certificates','positive/negative/unknown witnesses'],
           ['The requirement revision fixes the entire criterion universe and exact frame.','All verdict rails have an independent meaning under proved well-formedness; action/output provenance and evidence policy are bound.'],
           ['Dropped criterion','Stale requirement','Unaccepted negative evidence policy','Wrong action/output','Intent alone']),
      task('N10','Verify byte parsing and domain semantic imports',['N02','N03','N09'],'L3',
           ['ByteSyntax.lean','ParseCertificate.lean','DomainImport.lean','E05 successor adapter'],
           ['A raw-byte parse certificate or verified decoder establishes full consumption and IR denotation.','Every composed domain importer preserves exact typed source meaning; finite differential controls supplement universal proofs.'],
           ['Malformed UTF8','Duplicate key','Trailing bytes','Surrogate/escape mismatch','Boolean/natural coercion','Emitter substitute value']),
      task('N12','Implement and qualify all 41 semantic relation adapters',['N02','N03','N04','N05','N06','N07','N08'],'L2',
           ['41 checked companion mappings','relation checker dispatcher','actual per-kind kernel cases','per-obligation acceptance candidates'],
           ['All 41 K-units execute their source-to-typed contracts with nonvacuous actual positive and negative evidence.','All 263 inherited evidence candidates bind the correct profile/source/challenge; full completion awaits final acceptance/currentness audit.'],
           ['Wrong endpoint/revision/role','Opaque unresolved qualifier','False effect inference','Missing exact inherited ID']),
      task('N09','Compose qualification with lifecycle and public commit',['N05','N06','N07','N08','N12'],'L2',
           ['ComposedEligibility.lean','E04 successor adapter','public commit/recapture harness','crash/recovery report'],
           ['Commit consumes complete current independently checked qualification and exact actual owner review.','Prove state/semantic preservation and avoid requiring the future commit receipt as its own eligibility premise.','Crash the complete public path before/after qualification, recapture, durable preparation and commit; recovery creates no new event.'],
           ['Missing hard obligation','Saved event passed as fresh','Stale head/frame','Qualification mismatch','Two writers','Orphan preparation']),
      task('N11A','Integrate independent checking for substantial selected proofs',['N02','N03'],'L3',
           ['trusted challenge/definition manifests','E06 bounded adapter','core and semantic sample evidence'],
           ['Independently check at least one substantial core theorem and one semantic theorem with complete anchored closures.','Expose feature/axiom/resource/disagreement states and retain mandatory Lean checks. This is an intermediate milestone.'],
           ['Valid proof under changed definitions','Changed statement','Missing inductive/recursor/universe','Unallowed axiom','Timeout/disagreement']),
      task('N11B','Complete independent coverage of every mandatory selected closure',['N11A','N09','N10','N12'],'L3',
           ['complete required declaration inventory','feature support matrix','full independent coverage report'],
           ['Every mandatory theorem closure for the composed successor profile passes both required checking paths with anchored definitions.','A missing/unsupported closure blocks the whole-profile claim; selected-sample progress cannot be relabeled full coverage.'],
           ['Omitted theorem/dependency','Unsupported primitive/quotient/recursor','Replaced closure pin','Partial inventory marked complete']),
      task('N13','Implement freshness, recapture and owned evidence provenance',['N04','N06','N08'],'L3',
           ['snapshot/freshness policy','revocation and action provenance adapters','recapture/invalidation witnesses'],
           ['Every claim states as-of/source completeness and its live or recorded posture.','Owner/issuer review capture or verified source adapters establish the claimed provenance; clock, cryptography and external truth premises remain explicit.'],
           ['Wrong epoch/time domain','Revocation newer than snapshot','Forged owner flag','Old execution/output evidence','Missing authentic source']),
      task('N14','Measure and enforce the composed resource envelope',['N07','N09','N10','N11B','N13'],'L3',
           ['small/boundary benchmark matrix','hard enforcement backend contract','resource failure controls'],
           ['Measure actual composed workloads and separately account for each stage and aggregate memory/time.','When a hard cap is required, exercise a real enforcement backend; cutoff/unavailability stays refusal/unknown, not a semantic negative.'],
           ['Required backend absent','Worker escapes aggregate cap','Interrupted traversal','Parser/proof size boundary','Unfinished proof marked complete']),
      task('N15','Run the composed seven-extension pilot',['N09','N10','N11B','N12','N13','N14'],'L4',
           ['integrated pilot inputs/outcomes','cross-profile lineage report','worked diagnostic packet'],
           ['Expressions, assessments, delegation, fulfillment, transport and transition use one exact owner-bound frame and independently complete obligation set.','Run legitimate completion and each missing/stale/substituted/cutoff case through the public API; no stage manufactures permission or fulfillment.'],
           ['Correct separate results from different frames','Circular self-qualification','Unknown truth converted to permission','Meaning changed after qualification']),
      task('N16','Audit every inherited and new integration obligation',['N15'],'L4',
           ['successor semantic coverage ledger','263 exact discharge receipts','new integration-obligation audit','retained 90-item regression audit'],
           ['Exactly all 263 original pending IDs are discharged under their owner-reviewed scoped meanings with current evidence.','All newly derived integration obligations pass, all 90 old discharges remain valid or explicitly versioned/requalified, and no retirement/exclusion is counted as a proof.'],
           ['263 count with wrong ID set','Duplicate/shared receipt without exact applicability','Retired item counted discharged','Stale source/challenge']),
      task('N17','Obtain actual successor meaning and use assessment',['N16'],'L4',
           ['successor review packet','actual artifact-bound human response','supported-use recommendation'],
           ['Humans review all new intended meanings, conflict/evidence policies, diagnostics and measured composed limits.','Original R06/G4 and prior P11 feedback remain their original scopes; no automatic promotion.'],
           ['Unrelated historical approval','Missing reviewed binding','Revisions/undecided converted to acceptance'], 'assigned semantic owners and human use reviewer'),
      task('N18','Publish the checked successor completion view',['N17'],'L4',
           ['final current-source/coverage audit','successor acceptance receipts','completion readout'],
           ['Every plan task, K-unit, inherited ID and required new integration/independent closure is accepted and current.','Report exact supported profile, remaining irreducible assumptions and measured bounds; keep v1–v4 acceptance unchanged.'],
           ['Label-only completion','Outdated evidence','Overclaim of unbounded or external-world truth'])
    ]

LAYERING = '''Implementation layering: extension integration and inherited semantic completion

Status: proposed, not executed. Date: 2026-10-10. Owners: role assignments pending. Target: a versioned bounded successor profile that closes the exact 263 inherited obligations and composes all seven extensions. Earlier v1–v4 guarantees and acceptance remain unchanged.

| Layer | Decision question | Minimum working unit | Outcome and reduced risk | Cost and exit evidence | Promotion |
|---|---|---|---|---|---|
| L0 — formal foundation | After this layer, we know whether an owner-bound meaning and complete qualification can be stated without substitution or circular approval. | One owned condition, one two-criterion requirement, one exact frame and independently derived obligations, all modeled before runtime. | A coherent proof target; removes caller-defined meaning/completeness. | Exact definitions, checked universal catalog/coverage proofs, typed counterexamples and explicit trust premises. Main cost: choosing independent predicates. | Continue if the model is nonvacuous and definitions are reviewable; revise if ownership/composition is circular. |
| L1 — source meaning | After this layer, we know whether every inherited source claim has an intended typed meaning and provable scope. | One K-unit fully defined/reviewed/proved, expanded by the same method to all 41 kinds. | A source-to-proof map for all 263 IDs and versioned contracts. | Owner reviews, independent meanings, mapping proofs, effect proofs and scoped countermodels. Main costs: semantic decisions and proof generalization. | Continue when the required definitions and challenges are exact; unresolved items remain visible. |
| L2 — integrated semantics | After this layer, we know whether actual adapters and lifecycle preserve those meanings under complete qualification. | Owner resolution → expression/evidence/fulfillment → composed eligibility → one local public commit. | A usable local composed checker that cannot borrow a caller's yes flag. | Actual per-kind kernel cases, complete qualification, frame-preserving imports, state invariants and public-path crash/concurrency evidence. Main costs: adapters and state integration. | Continue after meaningful positive and adversarial cases pass; preserve unknown/refusal behavior. |
| L3 — transport, assurance and operating limits | After this layer, we know whether byte transport, every required independent proof check, source recapture and resource enforcement meet the declared envelope. | One raw-byte certificate and two substantial independent proofs, then the whole required profile inventory and boundary workloads. | Explicit assurance and performance claims with complete coverage. | Parser/domain composition proofs, all mandatory anchored closures, source/freshness evidence and real resource backend tests. Main costs: parser proofs, independent feature support and kernel cost. | A sample unlocks further work; only full required coverage permits the whole-profile claim. |
| L4 — full assessed coverage | After this layer, we know whether all inherited and integration claims are current, understandable and suitable for the proposed bounded use. | End-to-end pilot followed by exact ID-set audit and actual owner/use review. | Accepted successor profile with all 263 inherited IDs discharged. | Full ledger/current-source checks, retained 90 prior discharges, new integration obligations, diagnostics and actual scoped human assessment. Main costs: exhaustive acceptance and owner coordination. | Complete only with all required evidence; do not manufacture completion by excluding or retiring items. |

The layer boundary heuristic is applied: expand the smallest slice that unlocks the next decision, then move to the next risk. Owner definition work is expensive but changes the proof target; benchmarking first would measure the wrong meaning. Independent checking and larger performance envelopes add value after actual composition exists. Families may be worked in waves; each K-unit always follows definition/review → proof → runtime → evidence.

All layers retain exact revisions, independently complete obligations, no fabricated truth/authority, no widening of previous profiles, explicit unknown/resource states and current challenge/definition bindings. Live distributed authority, arbitrary unbounded logic, every possible evidence aggregation policy and physical-world truth without an evidence model are outside this bounded successor scope. Proposed whole-profile independent checking is mandatory before that specific assurance claim; a partial sample cannot complete it.

Recommended next layer: L0, task N00. Major decisions deferred to N01/N03: actual definition owners; exact role/reference domains; negative-evidence and conflict policies; executed versus recorded effect tiers; snapshot freshness/clock model; allowed independent-kernel feature/axiom policy. Those decisions are implementation prerequisites, not prerequisites for reviewing this plan.
'''

def make_review(totals, family_totals):
    text = 'Review of extension integration and the inherited semantic backlog\n\n'
    text += 'The current checker has accepted bounded components. The missing capability is a composed, owner-resolved qualification whose obligations correspond to the intended source meanings. Original R06/G4 are complete (35/35 tasks) and are not reopened. This review proposes new work; it executes no successor runtime or proofs.\n\n'
    text += '**What the number 263 actually means.** The source ledger contains 353 obligations: 90 already discharged and 263 unsupported. The retained 90 are 82 structural signature/qualifier-shape checks (two per kind) plus eight scoped qualifier meanings across F0’s three kinds. The 263 comprise:\n\n'
    text += '| Missing claim | Count | What must be supplied |\n|---|---:|---|\n'
    text += '| Qualifier meaning | 74 | Exact typed decoding, owner resolution, revision/role/frame correspondence and source mapping. |\n| Operational effect | 41 | An independently defined intended effect, claim tier and checker/refinement proof. |\n| Forbidden inference | 148 | Exact conclusion meaning plus scoped non-entailment countermodel; full state/closure invariants where prohibition is global. |\n\n'
    text += 'These are source claims, not 263 failing theorem executions or 263 relation kinds. Every kind has residual obligations, including conforms-to (5), declares-effect-on (4) and materializes-consequence (5). F0 proved eight narrow qualifier meanings; it did not prove all surrounding prose. The 38 other legacy meanings remain unsupported as complete named profiles. Later v2 maps five selected fragments and explicitly defers 36 wider meanings. Neither that map nor seven accepted extensions automatically discharges any inherited ID.\n\n'
    text += 'Seventeen operational-effect statements use the same generic “records only” wording. Their source questions distinguish the intended relations, but their effect text alone does not define a nonvacuous proof target. The 74 unresolved qualifier claims use 69 distinct field spellings. The 148 forbidden claims use 83 distinct label spellings; shared spelling does not guarantee shared meaning. For example, authority may mean a declared scope, effective representation, permission or an institutional role. Resolve these differences in an owner-reviewed glossary.\n\n'
    text += 'The '+link(B/'v1/coverage/semantics/semantic-coverage-ledger.json','original ledger')+' remains unchanged. The '+link(HERE/'inherited-obligations.json','263-item review inventory')+' preserves every exact source ID, category, proposed proof target, missing interpretation and work unit. The '+link(HERE/'RELATION-REVIEW.md','41 relation cards')+' explain every qualifier/effect/exclusion and the existing fragment evidence. The '+link(HERE/'relation-work-pack.json','K00–K40 work pack')+' assigns every inherited item to one relation without assuming one theorem per item.\n\n'
    text += '**What is missing in each extension.**\n\n| Extension | Missing integration | Required improvement |\n|---|---|---|\n'
    for e in EXTENSIONS:
        text += '| '+e[0]+' '+e[1]+' | '+e[4]+' | '+e[5]+' |\n'
    text += '\nThe E03 generic model supplies a concrete additional formalization target: positive fulfillment has an independent quantified theorem, while negative verdict selection relies on adapter well-formedness checks for request/requirement/frame. The public normalizer rejects stale frames, so this is a missing generic bridge/verdict theorem rather than evidence of a stale-frame public acceptance bug. The successor must also choose whether an explicit no evaluation may refute fulfillment when its action/output is unaccepted. See the '+link(B/'v3/e03/FulfillmentSemantics.lean','formal definition')+' and '+link(B/'v3/e03/fulfillment_adapter.py','normalizer')+'.\n\n'
    text += '**Two worked gaps.** In E00, a root revision can accompany an atom or its negation. Different definition identities prevent a same-input contradiction, but a consumer that trusts the root revision alone still does not know the owner’s AST. In E03, removing one of two criteria and recomputing the supplied source produces a different valid fulfilled snapshot. The proof is valid relative to that smaller universe; owner-required completeness is missing. The existing '+link(B/'v3/execution/reviews/2026-10-10-seven-extensions-r06-g4/boundary-observations.json','boundary observations')+' record both cases without claiming false theorem acceptance.\n\n'
    text += '**The composition gap.** A yes expression, yes conformance, valid delegation path and fulfilled requirement cannot be combined unless their exact revisions, subjects, targets, scope, context, snapshot/epoch and owned policies agree. Eligibility must consume a complete independently derived qualification and actual exact review. E04 currently checks a supplied eligibility value. Add explicit cross-profile mapping/refinement and a composed eligibility theorem. Avoid requiring a future commit receipt to prove the eligibility of its own commit.\n\n'
    text += '**How to close a source obligation honestly.** For delegation_ref, resolve the exact delegation and prove agent/principal/role/frame agreement, not merely that the string is nonempty. For materializes-consequence’s effect, separate consistency with a supplied receipt from evidence of actual authorized atomic execution. For “evidence support does not imply truth,” define the conclusion and construct a model in which valid supporting evidence exists while the claim is false. This proves non-entailment; it does not say the claim is always false. A no-authority inference invariant across rules requires a stronger closure/state proof.\n\n'
    text += '**Completion and remaining trust.** Full inherited completion requires the exact 263 ID set discharged with owner-reviewed meanings, source refinements, current exact proofs and actual mapping/runtime evidence, while retaining the 90 earlier discharges. All newly introduced integration obligations and mandatory independent closures must also pass. A retired, narrowed or unsupported source claim stays in a separate disposition count; it cannot quietly reduce the unfinished count. Owner disagreement or missing external provenance blocks the affected claim. Formal proofs remain conditional on explicitly named external facts, clock/cryptography/host assumptions and intended-meaning review.\n\n'
    text += 'A valid proof and the intended definition are separate checks. The independent checker plan therefore pins both, following '+link('https://lean-lang.org/doc/reference/latest/ValidatingProofs/','Lean’s official validation guidance')+'. Byte parsing uses '+link('https://www.rfc-editor.org/rfc/rfc8259','RFC 8259')+' as a grammar baseline with a separately defined narrower profile.\n\n'
    text += '**Recommended work sequence.** '+link(HERE/'FORMALIZATION.md','Formalize the shared and per-relation contracts')+' first, obtain the definition decisions, prove source refinement, implement owner resolution and the semantic adapters, compose qualification/lifecycle, complete byte/independent assurance and resource evidence, then audit the entire inherited/integration inventory and obtain actual successor assessment. The '+link(HERE/'PLAN.md','detailed DAG and implementation contracts')+' and '+link(HERE/'implementation-layering.md','five decision layers')+' make those dependencies explicit.\n'
    return text

def make_plan_md(tasks, counts):
    text = 'Proposed completion plan — formalization first\n\nStatus: proposed, not executed. Date: 2026-10-10. Scope: all seven extension integration gaps and all 263 inherited obligations under an owner-reviewed versioned bounded successor profile. No accepted v1–v4 evidence is changed.\n\n'
    text += 'The existing Track I is expanded with exact inherited coverage, explicit three-way verdict/well-formedness proofs, nonvacuous forbidden-inference models, pre/post-commit separation and whole mandatory independent-closure coverage. Original gate-hardening Track H is complete and is not repeated.\n\n'
    text += 'Start with N00. The smallest formal slice is an owner-bound expression and a two-criterion requirement sharing one frame; prove unique definition resolution, owner-complete criteria and complete qualification. Then instantiate the same contracts for all 41 source kinds. No new runtime adapter starts before its independent formal meaning, mapping/proof contract and versioned schema are reviewed.\n\n'
    text += '```mermaid\nflowchart TD\n'
    for t in tasks:
        label = {'N00':'Formalize common contracts','N01':'All 41 owned meaning briefs','N02':'263 exact proof obligations','N03':'Schemas and API contracts','N04':'Owned catalogs and snapshots','N05':'E00 expressions','N06':'E01 evidence','N07':'E02 traversal','N08':'E03 fulfillment','N09':'E04 composed lifecycle','N10':'E05 byte and domain import','N11A':'E06 substantial proof milestone','N11B':'E06 complete mandatory closures','N12':'All 41 relation adapters','N13':'Provenance and freshness','N14':'Resources and benchmarks','N15':'Integrated pilot','N16':'Exact inherited and integration audit','N17':'Actual successor assessment','N18':'Checked completion view'}[t['id']]
        text += '  '+t['id']+'["'+t['id']+' '+label+'"]\n'
    for t in tasks:
        for dep in t['depends_on']:
            text += '  '+dep+' --> '+t['id']+'\n'
    text += '```\n\n'
    text += '| Task | Layer | Dependencies | Exit |\n|---|---|---|---|\n'
    for t in tasks:
        text += '| '+t['id']+' '+t['title']+' | '+t['layer']+' | '+(', '.join(t['depends_on']) or 'none')+' | '+' '.join(t['exit_criteria'])+' |\n'
    text += '\nEach task contract follows; outputs are proposed deliverables, not evidence that the task already ran.\n'
    for t in tasks:
        text += '\n**'+t['id']+' — '+t['title']+'**\n\nOwner: '+t['owner_role']+'; actual assignment pending. Dependencies: '+(', '.join(t['depends_on']) or 'none')+'.\n\n'
        text += 'Deliver: '+', '.join(t['outputs'])+'.\n\n'
        text += 'Acceptance: '+' '.join(t['exit_criteria'])+'\n\n'
        text += 'Meaningful controls: '+', '.join(t['failure_controls'])+'.\n'
    text += '\n**Relation work waves.** The partition below covers all 41 kinds and 263 inherited pending IDs. It groups reusable theories, not semantic equivalence. Each K-unit still receives its own source interpretation, proof applicability and runtime evidence.\n\n| Family | Kinds | Inherited pending IDs |\n|---|---:|---:|\n'
    for g, names in FAMILIES.items():
        text += '| '+g+' | '+str(len(names))+' | '+str(counts[g])+' |\n'
    text += '\nPrioritize carries-definition, acts-for, inherits-contract, conforms-to, produces, fulfills-request, declares-effect-on, materializes-consequence and successor-of because they connect owned meaning, obligation activation, evidence, fulfillment and state change. Follow with the remaining families; full completion requires all of them.\n\n'
    text += '**API and evidence contract.** Plan the interfaces `resolveDefinition(owner,revision,snapshot)`, `resolveRequirement(owner,revision,snapshot)`, `resolveAssessment(issuer,revision,policy,snapshot)`, `deriveRequired(profile,before,proposal)`, `qualify(profile,source,proposal)`, `verifyParse(rawBytes,certificate)`, `checkIndependent(trustedChallenge,definitionClosure,proofClosure,policy)` and `commit(expectedHead,expectedGeneration,freshQualification,ownerReview)`. Every result binds exact inputs, selected universe, frame, policy/definition revisions, evidence lineage and result state. Caller booleans do not substitute for checked certificates. Details and theorem targets precede implementation in FORMALIZATION.md.\n\n'
    text += 'L2 qualifies the owner-bound typed semantics while retaining the declared existing parser/emitter boundary. L3 adds the byte-refinement assurance in a separately versioned contract; the final N15 pilot must use the stronger transport and recapture current qualifications. Independent checker engineering can begin from N02 proof packages, but L3 promotion requires the completed L2 workflow and N11B whole mandatory coverage. Each runtime task follows independent definition/challenge → reviewed proof contract and model/mapping proofs → adapter implementation → actual witnesses and failure controls → current acceptance.\n\n'
    text += '**Full exit condition.** Every plan task and K00–K40 unit is accepted; the successor ledger contains the exact 263 inherited IDs with current scoped discharge evidence; 90 earlier discharges remain valid or explicitly requalified; all additional integration obligations pass; every mandatory selected independent closure passes; the integrated pilot and resource controls pass; actual successor-scoped human meaning/use assessment is recorded. Claims remain limited to the owned profile and explicit trust premises.\n\n'
    text += '**Real blockers to resolve during implementation.** No actual owners, source credentials, role enums or external clock/receipt authenticity can be invented. Definition ambiguity may require a new versioned companion interpretation or a source-owner revision. Such a revision needs explicit correspondence and does not silently prove the original broader claim. If a conclusion is entailed by the intended full theory, its forbidden-inference obligation needs an owner decision or model repair; do not manufacture a countermodel by weakening the theory. If an independent kernel cannot support a mandatory closure, N11B and the corresponding whole-profile assurance remain incomplete.\n\n'
    text += 'No calendar estimates are assigned before N01 exposes the semantic decisions and N11A measures real independent-checking costs. Advance by checked milestones and family batches, not by relabeling the 263-item count.\n'
    return text

if __name__ == '__main__':
    main()
