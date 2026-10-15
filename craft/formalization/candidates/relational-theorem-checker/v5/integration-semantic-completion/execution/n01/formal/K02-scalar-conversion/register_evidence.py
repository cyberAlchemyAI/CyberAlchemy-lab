"""Register exact scalar conversion without inferring source authentication or inherited closure."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;N=HERE.parents[1];H=HERE.parents[3];ROOT=HERE.parents[9]
def b(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def run():
    v=read(HERE/'verification.json');a=read(HERE/'import-resolution-audit.json')
    assert v['result']=='candidate-fragment-pass' and v['new_declaration_count']==95
    assert v['new_general_declarations']==52 and v['new_worked_control_declarations']==43
    assert len(v['records'])==68 and sum(r['inspected_declarations'] for r in v['records'])==620
    assert a['result']=='import-resolution-audit-pass' and a['resolved_source_phase_pairs']==68 and a['verification']==b(HERE/'verification.json')
    assert v['existing_scalar_AST_conversion_proved'] and v['scalar_byte_document_exactness_proved'] and v['representation_outcome_exactness_proved']
    assert not v['whole_K02_source_refinement_proved'] and not v['independent_checker_run']
    index=read(N/'formal-preparation-index.json');seq=read(N/'sequential-review.json');plan=read(H/'execution/plan.json');progress=next(t for t in plan['tasks'] if t['id']=='N01')['progress']
    assert index['total_distinct_new_candidate_theorems']==seq['candidate_fragment_theorems']==progress['candidate_fragment_theorems']==1392
    assert not index.get('scalar_conversion_packages') and seq['current_unit']=='K04'
    assert index['inherited_discharges']==seq['new_inherited_discharges']==progress['inherited_discharges']==0
    files={'verification':'verification.json','import_resolution_audit':'import-resolution-audit.json','candidate_api_contract':'candidate-api-contract.json','model_review':'MODEL-REVIEW.md','refinement_matrix':'refinement-matrix.json','next_implementation_plan':'NEXT-IMPLEMENTATION.md','independent_formalization':'FORMALIZATION.md'}
    package={'unit':'K02-scalar-conversion','kind':'relation.addresses-intent','theorems':95,'general_declarations':52,'worked_control_declarations':43,'recursive_scalar_AST_conversion_proved':True,'existing_scalar_AST_conversion_proved':True,'composed_scalar_byte_parser_proved':True,'representation_outcome_exactness_proved':True,'original_capture_to_AST_bridge_proved':False,'authenticated_capture_proved':False,'complete_source_refinement':False,'inherited_discharges':0}
    for key,file in files.items():package[key]=b(HERE/file)
    index['scalar_conversion_packages']=[package];index['scalar_conversion_candidate_theorems']=95;index['total_distinct_new_candidate_theorems']=1487;save(N/'formal-preparation-index.json',index)
    seq['candidate_fragment_theorems']=1487;seq['candidate_scalar_conversion_packages']=1;save(N/'sequential-review.json',seq)
    progress['candidate_fragment_theorems']=1487;progress['scalar_conversion_candidate_theorems']=95;progress['candidate_scalar_conversion_packages']=1
    for key,file in files.items():progress['K02_scalar_conversion_'+key]=b(HERE/file)
    for value in progress.values():
        if isinstance(value,dict) and value.get('path') in {str((N/'formal-preparation-index.json').relative_to(ROOT)),str((N/'sequential-review.json').relative_to(ROOT))}:value.update(b(ROOT/value['path']))
    save(H/'execution/plan.json',plan)
    p=N/'check_current_review.py';s=p.read_text();marker="index.get('json_completeness_packages', [])):";assert s.count(marker)==1
    s=s.replace(marker,"index.get('json_completeness_packages', []) +\n                    index.get('scalar_conversion_packages', [])):")
    marker='    assert len(declarations) == len(set(declarations))';assert s.count(marker)==1
    block='''        if package.get('recursive_scalar_AST_conversion_proved'):
            for key in ['UTF16_scalar_string_conversion_proved','existing_scalar_AST_conversion_proved',
                        'recursive_scalar_AST_conversion_proved','scalar_string_conversion_exactness_proved',
                        'scalar_AST_conversion_exactness_proved','original_numeric_lexemes_preserved',
                        'ordered_array_object_lengths_preserved','decoded_duplicate_keys_retained',
                        'composed_scalar_byte_parser_proved','scalar_byte_document_exactness_proved',
                        'representation_outcome_classification_implemented','representation_outcome_exactness_proved',
                        'unsupported_outcome_valid_raw_grammar_proved','unsupported_outcome_no_scalar_meaning_proved']:
                assert proof[key] is True
            for key in ['original_capture_to_AST_bridge_proved','grammar_standard_translation_proved',
                        'supported_resource_envelope_measured','candidate_parser_profile_owner_accepted',
                        'authenticated_capture_proved','whole_K02_source_refinement_proved',
                        'replacement_character_recovery','public_outcome_classification_implemented','byte_parser_proved']:
                assert proof[key] is False
            assert proof['new_general_declarations'] == package['general_declarations'] == 52
            assert proof['new_worked_control_declarations'] == package['worked_control_declarations'] == 43
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['new_general_declarations'] == 52
            assert capture['new_worked_control_declarations'] == 43
            assert capture['original_source_bytes_parsed'] is False
            assert capture['original_source_capture_authenticated'] is False
            reference = read(ROOT / capture['reference_controls']['path'])
            assert reference['reference_string_cases'] == len(reference['rows']) == 34
            assert reference['control_declarations'] == 43
            api = read(ROOT / package['candidate_api_contract']['path'])
            for key in ['existing_scalar_AST_conversion_proved','recursive_scalar_AST_conversion_proved',
                        'composed_scalar_byte_parser_proved','scalar_byte_document_exactness_proved',
                        'representation_outcome_classification_implemented','representation_outcome_exactness_proved']:
                assert api[key] is True
            for key in ['N03_API_freeze','original_capture_to_AST_bridge_proved','replacement_character_recovery',
                        'public_outcome_classification_implemented','candidate_parser_profile_owner_accepted',
                        'supported_resource_envelope_measured','authenticated_capture_proved','independent_checker_run']:
                assert api[key] is False
'''
    p.write_text(s.replace(marker,block+marker))
    p=H/'execution/PROGRESS.md';s=p.read_text();old='making 1392 distinct verified candidate declarations in total.';assert s.count(old)==1
    s=s.replace(old,'and exact scalar conversion/composition adds 95, making 1487 distinct verified candidate declarations in total.')
    s+='''
K02-scalar-conversion closes the independent raw UTF-16/scalar-string and six-
constructor ordered AST conversion gap. Soundness/completeness, unique interpreted
values and exact refusals are proved for all finite inputs. BMP scalar/pair bounds
are checked before character construction; no replacement recovery occurs. Number
lexemes, array order and all ordered object entries/lengths are retained; an
unsupported nested key/value refuses the whole conversion. Original byte-document
composition is exact. The representation classifier now proves distinct invalid
syntax, valid raw but unsupported scalar representation, and converted outcomes.
A real byte document with a raw key and its escaped equivalent retains duplicate
decoded entries, and the separate existing binding-object checker refuses them.
All 52 general results and 43 controls (including 34 strict UTF-16 reference cases)
pass 68 fresh compile/replay invocations, 620 dependency-inclusive axiom inspections
and 68 matching-phase import audits. The total is 1487 distinct candidate
declarations. Compilation timings are not measured runtime limits; same-kernel
replay is not independent closure checking. Original owned source capture binding,
record/Schema composition, computed digests, authentic providers, nineteen K02
policies, external-standard translation, accepted profile, full public diagnostics,
resources and inherited/theory/independent closure remain open. All 263 inherited
IDs remain pending and all 90 original discharges retain scope. K00–K03 actual
meanings retain scope; K04 and D01–D08 remain pending. N01 remains in progress,
N02/N03 unstarted and only N00 accepted (1/20). Next is formalizing exact byte-to-
binding-record/source-envelope meaning before composing those implementations.
The full 41-kind/550-pair/seven-extension plan and new final bounded-use assessment
remain active. No commit, publication, deployment or promotion occurs.
''';p.write_text(s)
    print('Registered 95 scalar-conversion/composition declarations; total 1487; all 263 inherited IDs remain pending.')
if __name__=='__main__':run()
