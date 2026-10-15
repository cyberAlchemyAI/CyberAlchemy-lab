"""Register parser implementation and partial proofs without inferring complete grammar adequacy."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;N=HERE.parents[1];H=HERE.parents[3];ROOT=HERE.parents[9]
def b(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def run():
    v=read(HERE/'verification.json');a=read(HERE/'import-resolution-audit.json');ra=read(HERE/'JSON-document-reference-audit.json')
    assert v['result']=='candidate-fragment-pass' and v['new_declaration_count']==101
    assert len(v['records'])==44 and sum(r['inspected_declarations'] for r in v['records'])==470
    assert a['result']=='import-resolution-audit-pass' and a['resolved_source_phase_pairs']==44 and a['verification']==b(HERE/'verification.json')
    assert ra['result']=='JSON-document-reference-corpus-audit-pass' and ra['case_count']==62 and ra['worked_proof_controls']==83
    assert v['JSON_primitive_dispatcher_proved'] and v['complete_JSON_parser_implemented'] and not v['complete_JSON_parser_proved']
    index=read(N/'formal-preparation-index.json');seq=read(N/'sequential-review.json');plan=read(H/'execution/plan.json');progress=next(t for t in plan['tasks'] if t['id']=='N01')['progress']
    assert index['total_distinct_new_candidate_theorems']==seq['candidate_fragment_theorems']==progress['candidate_fragment_theorems']==1228
    assert not index.get('json_parser_packages') and seq['current_unit']=='K04'
    assert index['inherited_discharges']==seq['new_inherited_discharges']==progress['inherited_discharges']==0
    p=HERE/'MODEL-REVIEW.md';p.write_text(p.read_text()+f"\nFresh verification passes 101 candidate declarations (18 general/interface/composition\nresults and 83 worked controls) through 44 compile/replay invocations, 470\ndependency-inclusive axiom inspections and 44 matching-phase import audits.\nOnly allowed standard axioms occur. Compilation/elaboration took\n{sum(r['seconds'] for r in v['records']):.3f} seconds total and {max(r['seconds'] for r in v['records']):.3f} seconds for the maximum module;\nthese are not runtime limits. All 62 full-document reference cases agree, with\n21 additional byte/scalar/boundary controls. Same-kernel replay and reference\ncomparison are not independent proof checking. Complete recursive grammar\nsoundness/completeness and budget sufficiency remain unproved.\n")
    matrix=read(HERE/'refinement-matrix.json');matrix['import_resolution_audit']=b(HERE/'import-resolution-audit.json');save(HERE/'refinement-matrix.json',matrix)
    files={'verification':'verification.json','import_resolution_audit':'import-resolution-audit.json','JSON_document_reference_audit':'JSON-document-reference-audit.json','candidate_api_contract':'candidate-api-contract.json','model_review':'MODEL-REVIEW.md','refinement_matrix':'refinement-matrix.json','next_implementation_plan':'NEXT-IMPLEMENTATION.md'}
    package={'unit':'K02-json-parser','kind':'relation.addresses-intent','theorems':101,'JSON_primitive_dispatcher_proved':True,'complete_JSON_parser_implemented':True,'recursive_structural_termination_checked':True,'complete_JSON_parser_proved':False,'recursion_budget_sufficiency_proved':False,'existing_scalar_AST_conversion_proved':False,'authenticated_capture_proved':False,'complete_source_refinement':False,'inherited_discharges':0}
    for key,file in files.items():package[key]=b(HERE/file)
    index['json_parser_packages']=[package];index['json_parser_candidate_theorems']=101;index['total_distinct_new_candidate_theorems']=1329;save(N/'formal-preparation-index.json',index)
    seq['candidate_fragment_theorems']=1329;seq['candidate_json_parser_packages']=1;save(N/'sequential-review.json',seq)
    progress['candidate_fragment_theorems']=1329;progress['json_parser_candidate_theorems']=101;progress['candidate_json_parser_packages']=1
    for key,file in files.items():progress['K02_json_parser_'+key]=b(HERE/file)
    for value in progress.values():
        if isinstance(value,dict) and value.get('path') in {str((N/'formal-preparation-index.json').relative_to(ROOT)),str((N/'sequential-review.json').relative_to(ROOT))}:value.update(b(ROOT/value['path']))
    save(H/'execution/plan.json',plan)
    p=N/'check_current_review.py';s=p.read_text();marker="index.get('json_token_packages', [])):";assert s.count(marker)==1
    s=s.replace(marker,"index.get('json_token_packages', []) +\n                    index.get('json_parser_packages', [])):")
    marker='    assert len(declarations) == len(set(declarations))';assert s.count(marker)==1
    block='''        if package.get('JSON_primitive_dispatcher_proved'):
            for key in ['independent_primitive_container_meanings_specified','JSON_primitive_dispatcher_proved',
                        'primitive_grammar_soundness_proved','primitive_grammar_completeness_proved',
                        'primitive_boundary_qualification_proved','primitive_exact_suffix_and_progress_proved',
                        'complete_JSON_parser_implemented','recursive_structural_termination_checked',
                        'UTF8_implemented_parser_composition_proved']:
                assert proof[key] is True
            for key in ['complete_JSON_parser_proved','complete_JSON_parser_soundness_proved',
                        'complete_JSON_parser_completeness_proved','recursion_budget_sufficiency_proved',
                        'existing_scalar_AST_conversion_proved','original_capture_to_AST_bridge_proved',
                        'grammar_standard_translation_proved','byte_parser_proved',
                        'authenticated_capture_proved','whole_K02_source_refinement_proved',
                        'supported_resource_envelope_measured','candidate_parser_profile_owner_accepted']:
                assert proof[key] is False
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['worked_control_declarations'] == 83
            assert len(capture['document_reference_cases']) == 62
            assert len(capture['byte_controls']) == 10
            assert len(capture['scalar_controls']) == 2
            assert len(capture['invalid_byte_controls']) == 4
            assert len(capture['primitive_boundary_controls']) == 5
            assert capture['original_source_capture_authenticated'] is False
            audit = read(ROOT / package['JSON_document_reference_audit']['path'])
            assert audit['result'] == 'JSON-document-reference-corpus-audit-pass'
            assert audit['case_count'] == len(audit['cases']) == 62
            assert len(audit['additional_control_names']) == 21
            assert all(row['expected'] == row['actual_reference'] for row in audit['cases'])
            assert audit['complete_JSON_parser_implemented'] is True
            assert audit['complete_JSON_parser_proved'] is False
            assert audit['recursion_budget_sufficiency_proved'] is False
            assert audit['existing_scalar_AST_conversion_proved'] is False
            assert audit['candidate_parser_profile_owner_accepted'] is False
            assert audit['N03_schema_freeze'] is False
            api = read(ROOT / package['candidate_api_contract']['path'])
            assert api['N03_API_freeze'] is False
            assert api['complete_JSON_parser_implemented'] is True
            assert api['complete_JSON_parser_proved'] is False
            assert api['recursion_budget_sufficiency_proved'] is False
            assert api['existing_scalar_AST_conversion_proved'] is False
            assert api['candidate_parser_profile_owner_accepted'] is False
            assert api['replacement_character_recovery'] is False
            assert api['public_outcome_classification_implemented'] is False
'''
    p.write_text(s.replace(marker,block+marker))
    p=H/'execution/PROGRESS.md';s=p.read_text().replace('making 1228 distinct verified candidate declarations in total.','and primitive/recursive parser work adds 101, making 1329 distinct verified candidate declarations in total.')
    s+='''
K02-json-parser defines independent primitive/container-body meanings before
implementation, proves exact primitive dispatch/boundary qualification, unique
results/progress and bridges to the existing grammar. The full raw recursive
value/array/object/document and UTF-8 wrapper are implemented; every mutually
recursive call decreases fuel. Ordered duplicate decoded keys, original number
lexemes and escaped unpaired UTF-16 units are retained. Invalid trailing letters,
separator placements, trailing commas and malformed UTF-8 are exercised.
All 101 candidate declarations (18 general/interface/composition results and 83
controls) pass 44 fresh compile/replay invocations, 470 dependency-inclusive axiom
inspections and 44 matching-phase import audits. Sixty-two full-document reference
cases agree; twenty-one additional byte/scalar/boundary controls are bound.
The total is 1329 distinct candidate declarations. Full recursive grammar
soundness/completeness and sufficient wrapper fuel remain unproved; termination,
finite corpus and implemented-parser byte composition do not substitute for them.
Compilation/elaboration depth/timings are not measured runtime limits. Scalar-AST
conversion, RFC/Schema translation, actual capture/digest/authentic providers,
nineteen K02 policies, public outcomes/resources, original relation/effect/theory
and mandatory independent closure remain open. All 263 inherited IDs remain
pending and all 90 original discharges retain scope. K00–K03 actual meanings retain
scope; K04/D01–D08 remain pending. N01 is in progress, N02/N03 unstarted and only
N00 accepted (1/20). The complete 41-kind/550-pair/seven-extension plan and final
actual new bounded-use assessment remain active.
''';p.write_text(s)
    print('Registered 101 parser candidate declarations; total 1329; full recursive adequacy still open; all 263 inherited IDs pending.')
if __name__=='__main__':run()
