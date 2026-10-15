"""Register quantified parser soundness without inferring completeness or original semantic discharge."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;N=HERE.parents[1];H=HERE.parents[3];ROOT=HERE.parents[9]
def b(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def run():
    v=read(HERE/'verification.json');a=read(HERE/'import-resolution-audit.json')
    assert v['result']=='candidate-fragment-pass' and v['new_declaration_count']==23
    assert len(v['records'])==48 and sum(r['inspected_declarations'] for r in v['records'])==350
    assert a['result']=='import-resolution-audit-pass' and a['resolved_source_phase_pairs']==48 and a['verification']==b(HERE/'verification.json')
    assert v['complete_JSON_parser_soundness_proved'] and v['UTF8_byte_document_soundness_proved'] and not v['complete_JSON_parser_proved']
    index=read(N/'formal-preparation-index.json');seq=read(N/'sequential-review.json');plan=read(H/'execution/plan.json');progress=next(t for t in plan['tasks'] if t['id']=='N01')['progress']
    assert index['total_distinct_new_candidate_theorems']==seq['candidate_fragment_theorems']==progress['candidate_fragment_theorems']==1329
    assert not index.get('json_soundness_packages') and seq['current_unit']=='K04'
    assert index['inherited_discharges']==seq['new_inherited_discharges']==progress['inherited_discharges']==0
    p=HERE/'MODEL-REVIEW.md';p.write_text(p.read_text()+f"\nFresh verification passes all 23 new general results through 48 compile/replay\ninvocations, 350 dependency-inclusive axiom inspections and 48 matching-phase\nimport audits. Only allowed standard axioms occur. Compilation/elaboration took\n{sum(r['seconds'] for r in v['records']):.3f} seconds total, with a {max(r['seconds'] for r in v['records']):.3f}-second maximum module.\nThose timings are not runtime limits. No new finite controls were substituted\nfor the quantified proofs. Same-kernel replay is not independent proof checking.\nGrammar completeness, budget sufficiency and all inherited discharges remain open.\n")
    matrix=read(HERE/'refinement-matrix.json');matrix['import_resolution_audit']=b(HERE/'import-resolution-audit.json');save(HERE/'refinement-matrix.json',matrix)
    files={'verification':'verification.json','import_resolution_audit':'import-resolution-audit.json','candidate_api_contract':'candidate-api-contract.json','model_review':'MODEL-REVIEW.md','refinement_matrix':'refinement-matrix.json','next_implementation_plan':'NEXT-IMPLEMENTATION.md'}
    package={'unit':'K02-json-soundness','kind':'relation.addresses-intent','theorems':23,'recursive_JSON_parser_soundness_proved':True,'complete_JSON_parser_soundness_proved':True,'UTF8_byte_document_soundness_proved':True,'complete_JSON_parser_proved':False,'recursion_budget_sufficiency_proved':False,'existing_scalar_AST_conversion_proved':False,'authenticated_capture_proved':False,'complete_source_refinement':False,'inherited_discharges':0}
    for key,file in files.items():package[key]=b(HERE/file)
    index['json_soundness_packages']=[package];index['json_soundness_candidate_theorems']=23;index['total_distinct_new_candidate_theorems']=1352;save(N/'formal-preparation-index.json',index)
    seq['candidate_fragment_theorems']=1352;seq['candidate_json_soundness_packages']=1;save(N/'sequential-review.json',seq)
    progress['candidate_fragment_theorems']=1352;progress['json_soundness_candidate_theorems']=23;progress['candidate_json_soundness_packages']=1
    for key,file in files.items():progress['K02_json_soundness_'+key]=b(HERE/file)
    for value in progress.values():
        if isinstance(value,dict) and value.get('path') in {str((N/'formal-preparation-index.json').relative_to(ROOT)),str((N/'sequential-review.json').relative_to(ROOT))}:value.update(b(ROOT/value['path']))
    save(H/'execution/plan.json',plan)
    p=N/'check_current_review.py';s=p.read_text();marker="index.get('json_parser_packages', [])):";assert s.count(marker)==1
    s=s.replace(marker,"index.get('json_parser_packages', []) +\n                    index.get('json_soundness_packages', [])):")
    marker='    assert len(declarations) == len(set(declarations))';assert s.count(marker)==1
    block='''        if package.get('recursive_JSON_parser_soundness_proved'):
            for key in ['recursive_JSON_parser_soundness_proved','recursive_value_soundness_proved',
                        'recursive_array_body_soundness_proved','recursive_object_body_soundness_proved',
                        'post_comma_nonempty_guarantees_proved','source_whitespace_separator_reconstruction_proved',
                        'exact_consumed_suffix_soundness_proved','complete_JSON_parser_implemented',
                        'complete_JSON_parser_soundness_proved','UTF8_byte_document_soundness_proved',
                        'invalid_grammar_inputs_refused_proved','recursive_value_progress_proved']:
                assert proof[key] is True
            for key in ['complete_JSON_parser_proved','complete_JSON_parser_completeness_proved',
                        'recursion_budget_sufficiency_proved','existing_scalar_AST_conversion_proved',
                        'original_capture_to_AST_bridge_proved','grammar_standard_translation_proved',
                        'byte_parser_proved','authenticated_capture_proved','whole_K02_source_refinement_proved',
                        'supported_resource_envelope_measured','candidate_parser_profile_owner_accepted']:
                assert proof[key] is False
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['new_worked_control_declarations'] == 0
            assert capture['original_source_bytes_parsed'] is False
            assert capture['original_source_capture_authenticated'] is False
            api = read(ROOT / package['candidate_api_contract']['path'])
            assert api['N03_API_freeze'] is False
            assert api['complete_JSON_parser_soundness_proved'] is True
            assert api['UTF8_byte_document_soundness_proved'] is True
            assert api['complete_JSON_parser_proved'] is False
            assert api['complete_JSON_parser_completeness_proved'] is False
            assert api['recursion_budget_sufficiency_proved'] is False
            assert api['existing_scalar_AST_conversion_proved'] is False
            assert api['candidate_parser_profile_owner_accepted'] is False
            assert api['replacement_character_recovery'] is False
            assert api['public_outcome_classification_implemented'] is False
'''
    p.write_text(s.replace(marker,block+marker))
    p=H/'execution/PROGRESS.md';s=p.read_text().replace('making 1329 distinct verified candidate declarations in total.','and complete recursive parser soundness adds 23, making 1352 distinct verified candidate declarations in total.')
    s+='''
K02-json-soundness closes the quantified recursive grammar soundness gap for all
fuel values. Source spans reconstruct whitespace, commas, colons, quoted keys,
value words, closing delimiters and exact suffixes under the existing independent
grammar. Simultaneous fuel induction proves value/array/object mode soundness and
nonempty post-comma body results. Actual wrapped document and UTF-8 success now
imply DocumentMeaning and ByteDocumentMeaning; invalid-meaning inputs are refused
and successful values consume a nonempty word. All 23 new general results pass
48 fresh compile/replay invocations, 350 dependency-inclusive axiom inspections
and 48 matching-phase import audits. No finite controls substitute for these
quantified statements. The total is 1352 distinct candidate declarations.
Complete valid-input acceptance, sufficient wrapper fuel and both-direction
parser exactness remain unproved; soundness permits false refusals. Timings are
not runtime limits and same-kernel replay is not independent checking. Scalar-AST
conversion, RFC/Schema translation, actual capture/digest/authentic providers,
nineteen K02 policies, public outcomes/resources, original relation/effect/theory
and mandatory independent closure remain open. All 263 inherited IDs remain
pending and all 90 original discharges retain scope. K00–K03 actual meanings retain
scope; K04/D01–D08 remain pending. N01 is in progress, N02/N03 unstarted and only
N00 accepted (1/20). The full 41-kind/550-pair/seven-extension plan and final actual
new bounded-use assessment remain active.
''';p.write_text(s)
    print('Registered 23 quantified parser soundness declarations; total 1352; completeness/budget and all 263 inherited IDs remain open.')
if __name__=='__main__':run()
