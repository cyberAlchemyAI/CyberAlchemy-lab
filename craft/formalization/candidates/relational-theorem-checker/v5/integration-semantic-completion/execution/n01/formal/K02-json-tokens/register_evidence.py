"""Register exact token candidate evidence, with no original semantic admission."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;N=HERE.parents[1];H=HERE.parents[3];ROOT=HERE.parents[9]
def b(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def run():
    v=read(HERE/'verification.json');a=read(HERE/'import-resolution-audit.json');ra=read(HERE/'JSON-token-reference-audit.json')
    assert v['result']=='candidate-fragment-pass' and v['new_declaration_count']==94
    assert len(v['records'])==32 and sum(r['inspected_declarations'] for r in v['records'])==340
    assert a['result']=='import-resolution-audit-pass' and a['resolved_source_phase_pairs']==32 and a['verification']==b(HERE/'verification.json')
    assert ra['result']=='JSON-token-reference-corpus-audit-pass' and ra['case_count']==38 and ra['worked_proof_controls']==63
    assert v['JSON_number_prefix_decoder_proved'] is True and v['complete_JSON_parser_proved'] is False
    index=read(N/'formal-preparation-index.json');seq=read(N/'sequential-review.json');plan=read(H/'execution/plan.json');progress=next(t for t in plan['tasks'] if t['id']=='N01')['progress']
    assert index['total_distinct_new_candidate_theorems']==seq['candidate_fragment_theorems']==progress['candidate_fragment_theorems']==1134
    assert not index.get('json_token_packages') and seq['current_unit']=='K04'
    assert index['inherited_discharges']==seq['new_inherited_discharges']==progress['inherited_discharges']==0
    p=HERE/'MODEL-REVIEW.md';p.write_text(p.read_text()+f"\nFresh verification passes 94 new declarations (31 general results and 63 worked\ncontrols), with 32 compile/replay invocations, 340 dependency-inclusive axiom\ninspections and 32 matching-phase import audits. Only allowed standard axioms\noccur. Compilation/elaboration took {sum(r['seconds'] for r in v['records']):.3f} seconds total and\n{max(r['seconds'] for r in v['records']):.3f} seconds for the maximum module; these are not measured runtime limits.\nAll 38 exact whole-number reference cases agree; 25 further controls bind literal,\nnumber-prefix and whitespace behavior. Same-kernel replay and reference comparison\nare not independent proof checking. No inherited ID is discharged.\n")
    matrix=read(HERE/'refinement-matrix.json');matrix['import_resolution_audit']=b(HERE/'import-resolution-audit.json');save(HERE/'refinement-matrix.json',matrix)
    files={'verification':'verification.json','import_resolution_audit':'import-resolution-audit.json','JSON_token_reference_audit':'JSON-token-reference-audit.json','candidate_api_contract':'candidate-api-contract.json','model_review':'MODEL-REVIEW.md','refinement_matrix':'refinement-matrix.json','next_implementation_plan':'NEXT-IMPLEMENTATION.md'}
    package={'unit':'K02-json-tokens','kind':'relation.addresses-intent','theorems':94,'maximal_run_scanner_proved':True,'JSON_whitespace_scanner_proved':True,'JSON_literal_prefix_decoder_proved':True,'JSON_number_prefix_decoder_proved':True,'JSON_whole_number_decoder_proved':True,'complete_JSON_parser_proved':False,'existing_scalar_AST_conversion_proved':False,'authenticated_capture_proved':False,'complete_source_refinement':False,'inherited_discharges':0}
    for key,file in files.items():package[key]=b(HERE/file)
    index['json_token_packages']=[package];index['json_token_candidate_theorems']=94;index['total_distinct_new_candidate_theorems']=1228;save(N/'formal-preparation-index.json',index)
    seq['candidate_fragment_theorems']=1228;seq['candidate_json_token_packages']=1;save(N/'sequential-review.json',seq)
    progress['candidate_fragment_theorems']=1228;progress['json_token_candidate_theorems']=94;progress['candidate_json_token_packages']=1
    for key,file in files.items():progress['K02_json_tokens_'+key]=b(HERE/file)
    for value in progress.values():
        if isinstance(value,dict) and value.get('path') in {str((N/'formal-preparation-index.json').relative_to(ROOT)),str((N/'sequential-review.json').relative_to(ROOT))}:value.update(b(ROOT/value['path']))
    save(H/'execution/plan.json',plan)
    p=N/'check_current_review.py';s=p.read_text();marker="index.get('json_string_packages', [])):";assert s.count(marker)==1
    s=s.replace(marker,"index.get('json_string_packages', []) +\n                    index.get('json_token_packages', [])):")
    marker='    assert len(declarations) == len(set(declarations))';assert s.count(marker)==1
    block='''        if package.get('JSON_number_prefix_decoder_proved'):
            for key in ['maximal_run_scanner_proved','JSON_whitespace_scanner_proved',
                        'JSON_literal_prefix_decoder_proved','JSON_number_prefix_decoder_proved',
                        'JSON_whole_number_decoder_proved','number_value_boundary_completeness_proved',
                        'original_number_lexemes_retained','exact_token_suffix_proved',
                        'primitive_document_boundary_contract_specified']:
                assert proof[key] is True
            for key in ['complete_JSON_parser_implemented','complete_JSON_parser_proved',
                        'existing_scalar_AST_conversion_proved','original_capture_to_AST_bridge_proved',
                        'grammar_standard_translation_proved','byte_parser_proved',
                        'authenticated_capture_proved','whole_K02_source_refinement_proved',
                        'supported_resource_envelope_measured','candidate_parser_profile_owner_accepted']:
                assert proof[key] is False
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['worked_control_declarations'] == 63
            assert len(capture['whole_number_reference_cases']) == 38
            assert len(capture['number_prefix_controls']) == 10
            assert len(capture['literal_prefix_controls']) == 9
            assert len(capture['whitespace_controls']) == 6
            assert capture['original_source_capture_authenticated'] is False
            audit = read(ROOT / package['JSON_token_reference_audit']['path'])
            assert audit['result'] == 'JSON-token-reference-corpus-audit-pass'
            assert audit['case_count'] == len(audit['cases']) == 38
            assert len(audit['additional_control_names']) == 25
            assert all(row['expected_token'] == row['actual_reference_token'] for row in audit['cases'])
            assert audit['complete_JSON_parser_proved'] is False
            assert audit['existing_scalar_AST_conversion_proved'] is False
            assert audit['candidate_parser_profile_owner_accepted'] is False
            assert audit['N03_schema_freeze'] is False
            api = read(ROOT / package['candidate_api_contract']['path'])
            assert api['N03_API_freeze'] is False
            assert api['JSON_number_prefix_decoder_proved'] is True
            assert api['JSON_whole_number_decoder_proved'] is True
            assert api['complete_JSON_parser_proved'] is False
            assert api['existing_scalar_AST_conversion_proved'] is False
            assert api['candidate_parser_profile_owner_accepted'] is False
            assert api['replacement_character_recovery'] is False
            assert api['public_outcome_classification_implemented'] is False
'''
    p.write_text(s.replace(marker,block+marker))
    p=H/'execution/PROGRESS.md';s=p.read_text().replace('making 1134 distinct verified candidate declarations in total.','and exact whitespace/literal/number token scanning adds 94, making 1228 distinct verified candidate declarations in total.')
    s+='''
K02-json-tokens formalizes independent maximal-run, literal/number-prefix and
value-boundary interfaces, then proves generic runs, exact JSON whitespace,
literal prefixes, number prefixes and whole-number consumption. Exact original
number lexemes and suffixes, deterministic results, progress and numeric ASCII
round trips are proved. Maximal numeric scanning refuses leading-zero or
incomplete fraction/exponent continuations instead of accepting an earlier digit.
Value-boundary completeness is proved; token-prefix success is explicitly not
whole-document acceptance. All 94 new declarations (31 general results and 63
controls) pass 32 fresh compile/replay invocations, 340 dependency-inclusive axiom
inspections and 32 matching-phase import audits. Thirty-eight whole-number
reference cases agree; twenty-five additional literal/suffix/whitespace controls
are bound. The registered total is 1228 candidate declarations. Timings are not
runtime limits and replay/reference comparisons are not independent checking.
Mutual containers/document parsing, scalar-AST conversion, RFC/Schema translation,
original capture/digest/authentic providers, nineteen K02 policies, distinct public
outcomes/resources, original relation/effect/theory and mandatory independent
closure remain open. All 263 inherited IDs remain pending and all 90 original
discharges retain scope. K00–K03 actual meanings retain scope; K04/D01–D08 remain
pending. N01 is in progress, N02/N03 unstarted and only N00 accepted (1/20).
The full 41-kind/550-pair/seven-extension plan and final actual new use assessment
remain active.
''';p.write_text(s)
    print('Registered 94 token candidate declarations; total 1228; all 263 inherited IDs pending; K04 remains current.')
if __name__=='__main__':run()
