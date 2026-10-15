"""Register scoped capture candidate proofs; keep all inherited/owner gates pending."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;N=HERE.parents[1];H=HERE.parents[3];ROOT=HERE.parents[9]
def b(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def run():
    v=read(HERE/'verification.json');a=read(HERE/'import-resolution-audit.json')
    assert v['result']=='candidate-fragment-pass' and v['new_declaration_count']==50
    assert len(v['records'])==50 and sum(x['inspected_declarations'] for x in v['records'])==468
    assert a['result']=='import-resolution-audit-pass' and a['resolved_source_phase_pairs']==50 and a['verification']==b(HERE/'verification.json')
    assert v['uniform_digest_profile_guard_proved'] is True and v['authenticated_capture_proved'] is False
    index=read(N/'formal-preparation-index.json');seq=read(N/'sequential-review.json');plan=read(H/'execution/plan.json');progress=next(t for t in plan['tasks'] if t['id']=='N01')['progress']
    assert index['total_distinct_new_candidate_theorems']==seq['candidate_fragment_theorems']==progress['candidate_fragment_theorems']==935
    assert not index.get('capture_projection_packages') and seq['current_unit']=='K04'
    assert index['inherited_discharges']==seq['new_inherited_discharges']==progress['inherited_discharges']==0
    p=HERE/'MODEL-REVIEW.md';s=p.read_text();s+=f"\nFresh verification passes 50 new declarations (18 general/field/boundary results\nand 32 worked controls), through 50 compile/replay invocations, 468 dependency-\ninclusive axiom inspections and 50 matching-phase import audits. Only the allowed\nstandard axioms occur. Fresh compilation/elaboration took {sum(x['seconds'] for x in v['records']):.3f} seconds\ntotal, with a {max(x['seconds'] for x in v['records']):.3f}-second maximum module. These timings are not runtime\nresource measurements. Same pinned-kernel replay is not independent checking.\n";p.write_text(s)
    matrix=read(HERE/'refinement-matrix.json');matrix['status']='candidate-capture-and-retained-catalog-staging-verified';matrix['verification']=b(HERE/'verification.json');matrix['import_resolution_audit']=b(HERE/'import-resolution-audit.json');save(HERE/'refinement-matrix.json',matrix)
    files={'verification':'verification.json','import_resolution_audit':'import-resolution-audit.json','candidate_api_contract':'candidate-api-contract.json','capture_policy_obligations':'capture-policy-obligations.json','model_review':'MODEL-REVIEW.md','refinement_matrix':'refinement-matrix.json','next_implementation_plan':'NEXT-IMPLEMENTATION.md'}
    package={'unit':'K02-binding-capture','kind':'relation.addresses-intent','theorems':50,'capture_envelope_adequacy_proved':True,'record_to_entry_projection_proved':True,'retained_catalog_staging_proved':True,'uniform_digest_profile_guard_proved':True,'authenticated_capture_proved':False,'complete_source_refinement':False,'inherited_discharges':0}
    for k,file in files.items():package[k]=b(HERE/file)
    index['capture_projection_packages']=[package];index['capture_projection_candidate_theorems']=50;index['total_distinct_new_candidate_theorems']=985;save(N/'formal-preparation-index.json',index)
    seq['candidate_fragment_theorems']=985;seq['candidate_capture_projection_packages']=1;save(N/'sequential-review.json',seq)
    progress['candidate_fragment_theorems']=985;progress['capture_projection_candidate_theorems']=50;progress['candidate_capture_projection_packages']=1
    for k,file in files.items():progress['K02_binding_capture_'+k]=b(HERE/file)
    for value in progress.values():
        if isinstance(value,dict) and value.get('path') in {str((N/'formal-preparation-index.json').relative_to(ROOT)),str((N/'sequential-review.json').relative_to(ROOT))}:value.update(b(ROOT/value['path']))
    save(H/'execution/plan.json',plan)
    p=N/'check_current_review.py';s=p.read_text();marker="index.get('binding_record_packages', [])):";assert s.count(marker)==1;s=s.replace(marker,"index.get('binding_record_packages', []) +\n                    index.get('capture_projection_packages', [])):")
    marker='    assert len(declarations) == len(set(declarations))';assert s.count(marker)==1
    block='''        if package.get('record_to_entry_projection_proved'):
            assert proof['capture_envelope_adequacy_proved'] is True
            assert proof['record_to_entry_projection_proved'] is True
            assert proof['retained_catalog_staging_proved'] is True
            assert proof['uniform_digest_profile_guard_proved'] is True
            assert proof['conditional_capture_contract_specified'] is True
            assert proof['digest_algorithm_realized'] is False
            assert proof['digest_computation_proved'] is False
            assert proof['byte_to_AST_correspondence_proved'] is False
            assert proof['byte_parser_proved'] is False
            assert proof['authentic_review_provider_realized'] is False
            assert proof['authenticated_capture_proved'] is False
            assert proof['full_source_policy_realization_proved'] is False
            assert proof['whole_K02_source_refinement_proved'] is False
            assert proof['supported_resource_envelope_measured'] is False
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['worked_control_declarations'] == len(capture['cases']) == 32
            assert capture['bytes_are_synthetic_and_not_parsed'] is True
            assert capture['digest_is_uncomputed_synthetic_label'] is True
            assert capture['review_roots_are_synthetic'] is True
            policies = read(ROOT / package['capture_policy_obligations']['path'])
            assert len(policies['rows']) == 5 and policies['realized_count'] == 0
            assert {row['id'] for row in policies['rows']} == {'P01','P02','P03','P04','P05'}
            assert not any(row['realized'] or row['inherited_discharge'] for row in policies['rows'])
            assert policies['whole_K02_policy_count'] == 19
            assert policies['whole_K02_policy_realization_proved'] is False
            api = read(ROOT / package['candidate_api_contract']['path'])
            assert api['N03_API_freeze'] is False
            assert api['uniform_digest_profile_guard_proved'] is True
            assert api['expected_profile_ownership_proved'] is False
            assert api['digest_computation_proved'] is False
            assert api['authenticated_capture_proved'] is False
            assert api['public_outcome_classification_implemented'] is False
'''
    p.write_text(s.replace(marker,block+marker))
    p=H/'execution/PROGRESS.md';s=p.read_text();s=s.replace('making 935 distinct verified candidate declarations in total.','and capture-to-entry/retained-catalog staging adds 50, making 985 distinct verified candidate declarations in total.')
    s+='''
K02-binding-capture connects complete record AST decoding to a derived catalog
entry and retains full records/envelopes beside the projected catalog. Exact
ordered preparation preserves every input; structural guards reject missing
roots, conflicting identity bytes and inconsistent tokens/targets. Review exposed
an additional gap: old entries omit digest-profile revisions. The new explicit
requested-profile guard rejects wrong or mixed profiles before that projection.
All 50 new declarations (18 general results plus 32 worked controls) pass 50 fresh
compile/replay invocations, 468 dependency-inclusive axiom inspections and 50
matching-phase import audits. Synthetic controls explicitly show that adequate
byte length and nonempty digest labels do not authenticate captured content.
Five capture provider requirements are explicit and unrealized; all nineteen
whole K02 source policies, byte/Schema/digest/authentic-provider bridges,
public outcomes/resources, full source/effect/theory and mandatory independent
closure remain open. The total is 985 distinct candidate declarations. All 263
inherited IDs remain pending, all 90 original discharges retain scope, K00-K03
actual meanings retain scope, K04/D01-D08 remain pending, N01 is in progress,
N02/N03 remain unstarted and only N00 is accepted (1/20). The complete original
41-kind/550-pair/seven-extension plan and actual final new use assessment stay active.
''';p.write_text(s)
    print('Registered 50 capture-to-entry/catalog-staging declarations; total 985; all 263 inherited IDs pending; K04 remains current.')
if __name__=='__main__':run()
