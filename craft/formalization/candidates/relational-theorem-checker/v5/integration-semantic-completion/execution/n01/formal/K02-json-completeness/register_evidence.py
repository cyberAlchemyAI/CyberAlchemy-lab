"""Register raw grammar exactness; preserve pending semantic and authentication work."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;N=HERE.parents[1];H=HERE.parents[3];ROOT=HERE.parents[9]
def b(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def run():
    v=read(HERE/'verification.json');a=read(HERE/'import-resolution-audit.json')
    assert v['result']=='candidate-fragment-pass' and v['new_declaration_count']==40
    assert len(v['records'])==56 and sum(r['inspected_declarations'] for r in v['records'])==430
    assert a['result']=='import-resolution-audit-pass' and a['resolved_source_phase_pairs']==56 and a['verification']==b(HERE/'verification.json')
    assert v['complete_JSON_parser_proved'] and v['recursion_budget_sufficiency_proved'] and v['UTF8_byte_document_exactness_proved']
    assert not v['whole_K02_source_refinement_proved'] and not v['independent_checker_run']
    index=read(N/'formal-preparation-index.json');seq=read(N/'sequential-review.json');plan=read(H/'execution/plan.json');progress=next(t for t in plan['tasks'] if t['id']=='N01')['progress']
    assert index['total_distinct_new_candidate_theorems']==seq['candidate_fragment_theorems']==progress['candidate_fragment_theorems']==1352
    assert not index.get('json_completeness_packages') and seq['current_unit']=='K04'
    assert index['inherited_discharges']==seq['new_inherited_discharges']==progress['inherited_discharges']==0
    files={'verification':'verification.json','import_resolution_audit':'import-resolution-audit.json','candidate_api_contract':'candidate-api-contract.json','model_review':'MODEL-REVIEW.md','refinement_matrix':'refinement-matrix.json','next_implementation_plan':'NEXT-IMPLEMENTATION.md'}
    package={'unit':'K02-json-completeness','kind':'relation.addresses-intent','theorems':40,'complete_JSON_grammar_refinement_proved':True,'complete_JSON_parser_soundness_proved':True,'complete_JSON_parser_completeness_proved':True,'complete_JSON_parser_proved':True,'recursion_budget_sufficiency_proved':True,'UTF8_byte_document_exactness_proved':True,'existing_scalar_AST_conversion_proved':False,'authenticated_capture_proved':False,'complete_source_refinement':False,'inherited_discharges':0}
    for key,file in files.items():package[key]=b(HERE/file)
    index['json_completeness_packages']=[package];index['json_completeness_candidate_theorems']=40;index['total_distinct_new_candidate_theorems']=1392;save(N/'formal-preparation-index.json',index)
    seq['candidate_fragment_theorems']=1392;seq['candidate_json_completeness_packages']=1;save(N/'sequential-review.json',seq)
    progress['candidate_fragment_theorems']=1392;progress['json_completeness_candidate_theorems']=40;progress['candidate_json_completeness_packages']=1
    for key,file in files.items():progress['K02_json_completeness_'+key]=b(HERE/file)
    for value in progress.values():
        if isinstance(value,dict) and value.get('path') in {str((N/'formal-preparation-index.json').relative_to(ROOT)),str((N/'sequential-review.json').relative_to(ROOT))}:value.update(b(ROOT/value['path']))
    save(H/'execution/plan.json',plan)
    p=N/'check_current_review.py';s=p.read_text();marker="index.get('json_soundness_packages', [])):";assert s.count(marker)==1
    s=s.replace(marker,"index.get('json_soundness_packages', []) +\n                    index.get('json_completeness_packages', [])):")
    marker='    assert len(declarations) == len(set(declarations))';assert s.count(marker)==1
    block='''        if package.get('complete_JSON_grammar_refinement_proved'):
            for key in ['complete_JSON_grammar_refinement_proved','grammar_only_start_whitespace_lemmas_proved',
                        'recursive_value_grammar_completeness_proved','recursive_items_grammar_completeness_proved',
                        'recursive_members_grammar_completeness_proved','consumed_word_fuel_bound_proved',
                        'recursion_budget_sufficiency_proved','complete_JSON_parser_implemented',
                        'complete_JSON_parser_soundness_proved','complete_JSON_parser_completeness_proved',
                        'complete_JSON_parser_proved','wrapped_value_exactness_proved','document_exactness_proved',
                        'UTF8_byte_document_exactness_proved','independent_meaning_uniqueness_proved',
                        'none_iff_no_meaning_proved']:
                assert proof[key] is True
            for key in ['existing_scalar_AST_conversion_proved','original_capture_to_AST_bridge_proved',
                        'grammar_standard_translation_proved','supported_resource_envelope_measured',
                        'candidate_parser_profile_owner_accepted','authenticated_capture_proved',
                        'whole_K02_source_refinement_proved','byte_parser_proved']:
                assert proof[key] is False
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['new_worked_control_declarations'] == 0
            assert capture['original_source_bytes_parsed'] is False
            assert capture['original_source_capture_authenticated'] is False
            api = read(ROOT / package['candidate_api_contract']['path'])
            for key in ['complete_JSON_parser_soundness_proved','complete_JSON_parser_completeness_proved',
                        'complete_JSON_parser_proved','recursion_budget_sufficiency_proved',
                        'UTF8_byte_document_exactness_proved']:
                assert api[key] is True
            for key in ['N03_API_freeze','existing_scalar_AST_conversion_proved',
                        'original_capture_to_AST_bridge_proved','candidate_parser_profile_owner_accepted',
                        'replacement_character_recovery','public_outcome_classification_implemented',
                        'supported_resource_envelope_measured','authenticated_capture_proved',
                        'independent_checker_run']:
                assert api[key] is False
'''
    p.write_text(s.replace(marker,block+marker))
    p=H/'execution/PROGRESS.md';s=p.read_text();old='making 1352 distinct verified candidate declarations in total.';assert s.count(old)==1
    s=s.replace(old,'and full raw parser completeness/exactness adds 40, making 1392 distinct verified candidate declarations in total.')
    s+='''
K02-json-completeness closes valid-grammar acceptance and sufficient wrapper fuel
for the unchanged raw parser and independent grammar. Mutual grammar induction
covers all thirteen value/items/members constructors with the bound
2 * consumed word length < fuel; the actual 2 * input.length + 1 budget is proved
sufficient. Value-prefix, document and UTF-8 byte-document results now hold in
both directions, with unique raw meanings and none iff no meaning. All 40 new
results pass 56 fresh compile/replay invocations, 430 dependency-inclusive axiom
inspections and 56 matching-phase import audits. The total is 1392 distinct
candidate declarations. Historical soundness-only reports keep their original
scope; this new package closes their listed completeness/budget gaps.
These are raw-grammar theorems, not external-standard translation, scalar-AST
conversion, original fixture parsing, digest/authentication, Schema or nineteen
K02 source-policy proofs. Public outcomes, measured runtime limits, original
semantic/effect/theory closure and mandatory independent checking remain open.
All 263 inherited IDs remain pending; all 90 original discharges retain scope.
K00–K03 actual meanings retain scope; K04 and D01–D08 remain pending. N01 remains
in progress, N02/N03 unstarted and only N00 accepted (1/20). The full formalization-
first, all-41-kind/550-pair/seven-extension plan and actual new final bounded-use
assessment remain active. Next is independent scalar-string conversion meaning
before implementing/composing conversion with exact byte-document parsing.
''';p.write_text(s)
    print('Registered 40 general raw parser completeness/exactness declarations; total 1392; all 263 inherited IDs remain pending.')
if __name__=='__main__':run()
