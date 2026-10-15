"""Register exact string candidates without accepting or discharging original obligations."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;N=HERE.parents[1];H=HERE.parents[3];ROOT=HERE.parents[9]
def b(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def run():
    v=read(HERE/'verification.json');a=read(HERE/'import-resolution-audit.json');ra=read(HERE/'JSON-string-reference-audit.json')
    assert v['result']=='candidate-fragment-pass' and v['new_declaration_count']==82
    assert len(v['records'])==30 and sum(x['inspected_declarations'] for x in v['records'])==316
    assert a['result']=='import-resolution-audit-pass' and a['resolved_source_phase_pairs']==30 and a['verification']==b(HERE/'verification.json')
    assert ra['result']=='JSON-string-reference-corpus-audit-pass' and ra['case_count']==36 and ra['worked_proof_controls']==55
    assert v['JSON_whole_string_decoder_proved'] is True and v['complete_JSON_parser_proved'] is False
    index=read(N/'formal-preparation-index.json');seq=read(N/'sequential-review.json');plan=read(H/'execution/plan.json');progress=next(t for t in plan['tasks'] if t['id']=='N01')['progress']
    assert index['total_distinct_new_candidate_theorems']==seq['candidate_fragment_theorems']==progress['candidate_fragment_theorems']==1052
    assert not index.get('json_string_packages') and seq['current_unit']=='K04'
    assert index['inherited_discharges']==seq['new_inherited_discharges']==progress['inherited_discharges']==0
    p=HERE/'MODEL-REVIEW.md';s=p.read_text();s+=f"\nFresh verification passes 82 new declarations (27 general results and 55 worked\ncontrols), through 30 compile/replay invocations, 316 dependency-inclusive axiom\ninspections and 30 matching-phase import audits. Only allowed standard axioms\noccur. Fresh compilation/elaboration took {sum(x['seconds'] for x in v['records']):.3f} seconds total,\nwith a {max(x['seconds'] for x in v['records']):.3f}-second maximum module. These are not runtime resource limits.\nAll 36 strict string reference cases match; 19 additional controls cover exact\nsuffixes, invalid scalar inputs and UTF-8 composition. Same-kernel replay and\nPython comparison are not independent proof checking. Full document parsing,\nscalar-AST conversion and authenticated source closure remain open.\n";p.write_text(s)
    matrix=read(HERE/'refinement-matrix.json');matrix['import_resolution_audit']=b(HERE/'import-resolution-audit.json');save(HERE/'refinement-matrix.json',matrix)
    files={'verification':'verification.json','import_resolution_audit':'import-resolution-audit.json','JSON_string_reference_audit':'JSON-string-reference-audit.json','candidate_api_contract':'candidate-api-contract.json','model_review':'MODEL-REVIEW.md','refinement_matrix':'refinement-matrix.json','next_implementation_plan':'NEXT-IMPLEMENTATION.md'}
    package={'unit':'K02-json-strings','kind':'relation.addresses-intent','theorems':82,'JSON_string_unit_decoder_proved':True,'JSON_quoted_prefix_decoder_proved':True,'JSON_whole_string_decoder_proved':True,'UTF8_whole_string_composition_proved':True,'complete_JSON_parser_proved':False,'existing_scalar_AST_conversion_proved':False,'authenticated_capture_proved':False,'complete_source_refinement':False,'inherited_discharges':0}
    for k,file in files.items():package[k]=b(HERE/file)
    index['json_string_packages']=[package];index['json_string_candidate_theorems']=82;index['total_distinct_new_candidate_theorems']=1134;save(N/'formal-preparation-index.json',index)
    seq['candidate_fragment_theorems']=1134;seq['candidate_json_string_packages']=1;save(N/'sequential-review.json',seq)
    progress['candidate_fragment_theorems']=1134;progress['json_string_candidate_theorems']=82;progress['candidate_json_string_packages']=1
    for k,file in files.items():progress['K02_json_strings_'+k]=b(HERE/file)
    for value in progress.values():
        if isinstance(value,dict) and value.get('path') in {str((N/'formal-preparation-index.json').relative_to(ROOT)),str((N/'sequential-review.json').relative_to(ROOT))}:value.update(b(ROOT/value['path']))
    save(H/'execution/plan.json',plan)
    p=N/'check_current_review.py';s=p.read_text();marker="index.get('json_byte_packages', [])):";assert s.count(marker)==1;s=s.replace(marker,"index.get('json_byte_packages', []) +\n                    index.get('json_string_packages', [])):")
    marker='    assert len(declarations) == len(set(declarations))';assert s.count(marker)==1
    block='''        if package.get('JSON_string_unit_decoder_proved'):
            for key in ['JSON_string_unit_decoder_proved','JSON_quoted_prefix_decoder_proved',
                        'JSON_whole_string_decoder_proved','UTF8_whole_string_composition_proved',
                        'string_grammar_soundness_proved','string_grammar_completeness_proved',
                        'string_exact_suffix_proved','input_derived_sufficient_fuel_proved',
                        'UTF16_units_retained_in_decoder']:
                assert proof[key] is True
            for key in ['complete_JSON_parser_implemented','complete_JSON_parser_proved',
                        'existing_scalar_AST_conversion_proved','original_capture_to_AST_bridge_proved',
                        'grammar_standard_translation_proved','byte_parser_proved',
                        'authenticated_capture_proved','whole_K02_source_refinement_proved',
                        'supported_resource_envelope_measured','candidate_parser_profile_owner_accepted']:
                assert proof[key] is False
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['worked_control_declarations'] == 55
            assert len(capture['string_reference_cases']) == 36
            assert len(capture['scalar_only_controls']) == 2
            assert len(capture['quoted_prefix_controls']) == 8
            assert len(capture['byte_controls']) == 9
            assert capture['byte_inputs_are_synthetic'] is True
            assert capture['original_source_capture_authenticated'] is False
            audit = read(ROOT / package['JSON_string_reference_audit']['path'])
            assert audit['result'] == 'JSON-string-reference-corpus-audit-pass'
            assert audit['case_count'] == len(audit['cases']) == 36
            assert len(audit['additional_control_names']) == 19
            assert all(row['expected_units'] == row['actual_reference_units'] for row in audit['cases'])
            assert audit['complete_JSON_parser_proved'] is False
            assert audit['existing_scalar_AST_conversion_proved'] is False
            assert audit['candidate_parser_profile_owner_accepted'] is False
            assert audit['N03_schema_freeze'] is False
            api = read(ROOT / package['candidate_api_contract']['path'])
            assert api['N03_API_freeze'] is False
            assert api['JSON_whole_string_decoder_proved'] is True
            assert api['UTF8_whole_string_composition_proved'] is True
            assert api['complete_JSON_parser_proved'] is False
            assert api['existing_scalar_AST_conversion_proved'] is False
            assert api['candidate_parser_profile_owner_accepted'] is False
            assert api['replacement_character_recovery'] is False
            assert api['public_outcome_classification_implemented'] is False
'''
    p.write_text(s.replace(marker,block+marker))
    p=H/'execution/PROGRESS.md';s=p.read_text();s=s.replace('making 1052 distinct verified candidate declarations in total.','and exact JSON string decoding adds 82, making 1134 distinct verified candidate declarations in total.')
    s+='''
K02-json-strings now proves exact simple/hexadecimal escapes, string-unit prefixes,
quoted prefixes, whole-string consumption and complete UTF-8 string composition
against the previously registered independent grammar. Exact scalar suffixes,
UTF-16 unit bounds, deterministic meanings and input-length-derived sufficient
fuel are proved. Unpaired escaped surrogate units are retained; direct raw
surrogates, malformed escapes, unclosed quotes and trailing token text are refused.
All 82 new declarations (27 general results and 55 controls) pass 30 fresh compile/
replay invocations, 316 dependency-inclusive axiom inspections and 30 matching-phase
import audits. Thirty-six strict string reference cases match, with nineteen
additional scalar/suffix/UTF-8 controls. The registered total is 1134 candidate
declarations. Compilation timings are not measured runtime limits; same-kernel
replay/reference comparison are not independent checking. Full JSON document
parsing, scalar-AST conversion, standard/Schema translation, original capture,
digest/authentic providers, nineteen K02 source policies, public outcomes/resources,
original relation/effect/theory closure and mandatory independent closure remain
open. All 263 inherited IDs remain pending and all 90 original discharges retain
scope. Actual K00–K03 meanings retain scope; K04/D01–D08 remain pending. N01 is in
progress, N02/N03 unstarted and only N00 accepted (1/20). The full seven-extension,
41-kind/550-pair plan and final actual new bounded-use assessment stay active.
''';p.write_text(s)
    print('Registered 82 JSON string declarations; total 1134; all 263 inherited IDs pending; K04 remains current.')
if __name__=='__main__':run()
