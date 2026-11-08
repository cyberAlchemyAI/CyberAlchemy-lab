"""Seal source-qualified partial primitive and nominal foundation evidence only."""
import json
import build_candidate as b
import verifier as v

def load(name): return json.loads((b.UNIT / name).read_bytes())
def unchanged(refs):
    for ref in refs:
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Changed bound bytes: ' + ref['path'])

def audit():
    context = load('context.json'); unchanged(context['sources']); b.external_current(context)
    prior = json.loads((b.BASE / 'definitions/cal.definition.schema/delivery-manifest.json').read_bytes()); unchanged(prior['files'])
    for unit in ['A04', 'C01', 'E02']:
        upstream = json.loads((b.BASE / f'units/{unit}/receipt.json').read_bytes()); unchanged(upstream['inputs'] + upstream['outputs'])
    core = load('t.json')['payload']; packet = load('correspondence.json'); model = load('model-controls.json')
    graph = load('dependency-graph.json'); source = load('source-checks.json'); lower = load('lower-use-checks.json'); foundation = load('foundation-draft-review.json')
    counts = {'controls': 36, 'nonentailment_query_outcomes': 6, 'source_units': 22, 'mapped_clauses': 36,
              'encoded_clauses': 14, 'deferred_clauses': 13, 'required_populations': 8, 'unresolved_populations': 14}
    fresh = load('fresh-model-stdout.txt')
    if any(fresh[k] != n for k,n in counts.items()) or fresh['result'] != model['status'] or len(core['declarations']) != 34:
        raise ValueError('Wrong primary model/type denominator')
    for name in ['contract-check', 'lower-contract']:
        if load(name+'-stdout.txt')['status'] != 'structurally-valid': raise ValueError('Input contract failed')
    if (len(graph['nodes']),len(graph['edges']),len(graph['missing_or_quarantined_interpretations'])) != (29,49,22): raise ValueError('Wrong dependency denominator')
    if load('fresh-dependency-stdout.txt')['result'] != 'PASS-for-exact-authored-and-transitive-uses' or graph['edge_denominator'] != 'requires-independent-review': raise ValueError('Dependency review ceiling lost')
    for g in [graph,load('foundation-dependency-graph.json')]:
        if sorted(len(x['members']) for x in g['cycle_reviews']) != [2,4] or any(x['disposition'] != 'unresolved-cycle-classification' for x in g['cycle_reviews']): raise ValueError('Unresolved semantic cycles concealed')
    if len(source['checks']) != 12 or not all(x['result'] is True for x in source['checks']) or load('fresh-source-stdout.txt')['result'] != source['status']: raise ValueError('Source checks or replay failed')
    if not source['source_testable_conditions'][1]['result'].startswith('PARTIAL:') or source['source_location']['repository_identity_authenticated'] is not False: raise ValueError('Mirror mistaken for live producer authentication')
    if (lower['reference_controls'],lower['rejected_reference_controls'],lower['specialization_controls']) != (8,7,4) or load('fresh-lower-stdout.txt')['result'] != lower['status']: raise ValueError('Lower-use denominator or replay failed')
    if lower['targets_added_to_primary_T'] is not False or lower['actual_lower_layer_semantic_preservation'] != 'not-established': raise ValueError('Target assumed or preservation invented')
    expected = {'source_units':180,'mapped_clauses':287,'encoded_clauses':79,'explanatory_clauses':69,'deferred_clauses':139,'required_populations':68,'unresolved_populations':97}
    if foundation['counts'] != expected or foundation['foundation_partial_drafts'] != 8 or foundation['F01_T_family_result'] != 'PARTIAL' or foundation['F01_joint_review_exit'] != 'not-ready': raise ValueError('False foundational completion')
    if (foundation['authored_dependency_nodes'],foundation['authored_dependency_edges'],foundation['missing_counterpart_packets']) != (34,59,26): raise ValueError('Wrong joint dependency denominator')
    witness = foundation['nominal_witness']
    if witness['encoded_clauses_satisfied'] != 79 or witness['required_populations_satisfied'] != 68 or witness['reviewed_carrier_alignments']: raise ValueError('False nominal model or alignment claim')
    if load('fresh-foundation-stdout.txt')['result'] != foundation['status'] or foundation['source_owner_accepted_whole_translations'] != 0 or foundation['whole_definition_proofs'] != 0 or foundation['remaining_current_identities_without_per_definition_T_draft'] != 175: raise ValueError('Wrong joint replay or project claim')
    if len(packet['source_precedence']['conflicts']) != 5 or core['assumptions'] or packet['assumption_links'] or core['source_fidelity'] != 'pending': raise ValueError('Findings or assumptions altered')
    for evidence in [model,lower,foundation]:
        if evidence['semantic_ready'] is not False or evidence['source_fidelity'] != 'pending': raise ValueError('Readiness or fidelity fabricated')
        if evidence.get('mechanized_proof',False) is not False: raise ValueError('Whole proof fabricated')
        unchanged(evidence['checker_bindings']); unchanged(evidence.get('input_refs',[]))
        if evidence['runtime_bindings'] != v.f.current_bindings(): raise ValueError('Checker runtime drift')
    unchanged(list(source['selected_inputs'].values()))
    for stem in ['build','model-check','source-check','dependency-check','lower-check','foundation-check','contract-check','lower-contract','fresh-model','fresh-dependency','fresh-source','fresh-lower','fresh-foundation']:
        if (b.UNIT/(stem+'-stderr.txt')).read_bytes(): raise ValueError('Unresolved execution failure: '+stem)
    for name in ['REVIEW.md','foundation-draft-review.md']:
        if not (b.UNIT/name).is_file(): raise ValueError('Aspect review missing')
    selected = b.r.verify(b.snapshot(),b.ROOT); b.external_current(context)
    if selected['files'] != 201 or len(prior['files']) != 1065: raise ValueError('Wrong preservation denominator')
    return context,core,packet,counts,selected

def main():
    context,core,packet,counts,selected = audit()
    status = {'authority_effect':'none','goal_status':'active','latest_candidate_draft':'F01-T.cal.definition.semantic-primitive',
              'current_definitions':183,'admitted_source_versions':189,'per_definition_T_candidate_drafts':8,
              'foundations_family_result':'PARTIAL','foundations_joint_review_exit':'not-ready',
              'remaining_current_identities_without_per_definition_T_draft':175,
              'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,
              'source_files_current':201,'external_selected_local_files_current':1,'prior_candidate_files_preserved':1065,
              'next_independent_unit':'I04.1','full_project_completion':'not-established',
              'foundation_review_ref':b.ref(b.UNIT/'foundation-draft-review.json')}
    b.put('episode-status.json',status)
    b.put('coverage-row.json',{'authority_effect':'none','definition_id':core['source']['definition_id'],'source':core['source'],
              'interpretation_ref':b.ref(b.UNIT/'t.json'),'correspondence_ref':b.ref(b.UNIT/'correspondence.json'),
              'static_ir_ref':b.ref(b.UNIT/'static-ir.json'),'review_ref':b.ref(b.UNIT/'REVIEW.md'),
              'model_evidence_ref':b.ref(b.UNIT/'model-controls.json'),'source_checks_ref':b.ref(b.UNIT/'source-checks.json'),
              'lower_use_ref':b.ref(b.UNIT/'lower-use-checks.json'),'dependency_graph_ref':b.ref(b.UNIT/'dependency-graph.json'),
              'character_accounting_complete':True,**counts,'explanatory_clauses':9,'direct_semantic_uses':8,
              'source_fidelity':'pending','semantic_ready':False,'whole_definition_translation':'pending','whole_definition_proof':None,
              'actual_lower_layer_semantic_preservation':'not-established','semantic_closure':'unresolved-22-missing-counterparts-and-two-components',
              'canonical_legacy_source_currentness':'not-established; declared producer file absent',
              'owner_review':{'status':'pending','source_owner_ref':'role:definition-owner','owner_principal_ref':None,'decision_ref':None,
                              'findings':[x['finding_id'] for x in packet['source_precedence']['conflicts']]}})
    outputs=[b.ref(path) for path in sorted(b.UNIT.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc']
    b.put('receipt.json',{'schema_version':'definition-assurance-unit-receipt/v1-candidate','unit_id':'F01-T.cal.definition.semantic-primitive',
              'authority_effect':'none','goal_status':'active','task_result':'PARTIAL: source-accounted local primitive admissibility and exact lower references verified; owner fidelity, actual meaning preservation, populations and closure unresolved',
              'inputs':context['sources'],'external_inputs':context['external_sources'],'outputs':outputs,
              'validation':{**counts,'declarations':34,'actual_bounded_source_checks':12,'reference_controls':8,'rejected_reference_controls':7,'specialization_controls':4,
                            'foundation_partial_drafts':8,'nominal_encoded_clauses_satisfied':79,'nominal_required_populations_satisfied':68,
                            'source_files_current':201,'external_selected_local_files_current':1,'prior_candidate_files_preserved':1065,
                            'fresh_contract_model_dependency_source_lower_and_foundation_replays':'PASS'},
              'preserved_attempts':[{'path':'attempt-001-foundation-population-key','result':'superseded-failed-checker','cause':'Corrected clause_id lookup to declared population_id; prior code and failure logs retained.'}],
              'review_disposition':{'kind':'candidate-agent-self-review','reviewer':'agent:Codex','result':'Exact partial evidence only; no owner decision or meaning-aligned whole-source consistency accepted.'},
              'source_binding_check':selected,'coverage_row_ref':b.ref(b.UNIT/'coverage-row.json'),
              'foundation_review_ref':b.ref(b.UNIT/'foundation-draft-review.json'),
              'whole_definition_translation':'pending','source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,
              'foundations_family_result':'PARTIAL','source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,
              'next_independent_unit':'I04.1','full_project_completion':'not-established'})
    files=[b.ref(path) for folder in [b.BASE,b.IMPL] for path in sorted(folder.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc']
    b.put('delivery-manifest.json',{'schema_version':'definition-assurance-delivery-manifest/v1-candidate','authority_effect':'none','files':sorted(files,key=lambda x:x['path']),
              'claim_ceiling':'Exact preserved bytes and partial primitive/lower-reference controls; eight partial foundations with a nominal unaligned finite witness. No whole fidelity, source alignment, actual preservation, authenticated authority, canonical combined consistency or episode completion.'})
    print(json.dumps({'result':'PARTIAL-DRAFT-VERIFIED','candidate_files':len(files),**status,**counts},indent=2,sort_keys=True))

if __name__ == '__main__': main()
