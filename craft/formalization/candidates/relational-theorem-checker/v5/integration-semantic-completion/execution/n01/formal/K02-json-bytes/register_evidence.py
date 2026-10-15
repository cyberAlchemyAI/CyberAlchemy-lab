"""Register exact UTF-8/document-meaning candidates without any inherited admission."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;N=HERE.parents[1];H=HERE.parents[3];ROOT=HERE.parents[9]
def b(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def run():
    v=read(HERE/'verification.json');a=read(HERE/'import-resolution-audit.json');ra=read(HERE/'UTF8-reference-audit.json')
    assert v['result']=='candidate-fragment-pass' and v['new_declaration_count']==67
    assert len(v['records'])==24 and sum(x['inspected_declarations'] for x in v['records'])==246
    assert a['result']=='import-resolution-audit-pass' and a['resolved_source_phase_pairs']==24 and a['verification']==b(HERE/'verification.json')
    assert ra['result']=='UTF8-reference-corpus-audit-pass' and ra['case_count']==39 and ra['worked_proof_controls']==47
    assert v['UTF8_byte_decoder_proved'] is True and v['complete_JSON_parser_proved'] is False
    index=read(N/'formal-preparation-index.json');seq=read(N/'sequential-review.json');plan=read(H/'execution/plan.json');progress=next(t for t in plan['tasks'] if t['id']=='N01')['progress']
    assert index['total_distinct_new_candidate_theorems']==seq['candidate_fragment_theorems']==progress['candidate_fragment_theorems']==985
    assert not index.get('json_byte_packages') and seq['current_unit']=='K04'
    assert index['inherited_discharges']==seq['new_inherited_discharges']==progress['inherited_discharges']==0
    p=HERE/'MODEL-REVIEW.md';s=p.read_text();s+=f"\nFresh verification passes all 67 new declarations (20 general/meaning/encoding\nresults and 47 worked controls), through 24 compile/replay invocations, 246\ndependency-inclusive axiom inspections and 24 matching-phase import audits.\nOnly allowed standard axioms occur. Fresh compilation/elaboration took\n{sum(x['seconds'] for x in v['records']):.3f} seconds total, with a {max(x['seconds'] for x in v['records']):.3f}-second maximum module. These timings are\nnot measured runtime limits. All 39 strict UTF-8 reference cases match.\nSame pinned-kernel replay and Python corpus comparison are not independent\nproof checking. Full JSON parsing and scalar-AST/source/authentic closure remain open.\n";p.write_text(s)
    matrix=read(HERE/'refinement-matrix.json');matrix['import_resolution_audit']=b(HERE/'import-resolution-audit.json');save(HERE/'refinement-matrix.json',matrix)
    files={'verification':'verification.json','import_resolution_audit':'import-resolution-audit.json','UTF8_reference_audit':'UTF8-reference-audit.json','candidate_api_contract':'candidate-api-contract.json','model_review':'MODEL-REVIEW.md','refinement_matrix':'refinement-matrix.json','next_implementation_plan':'NEXT-IMPLEMENTATION.md'}
    package={'unit':'K02-json-bytes','kind':'relation.addresses-intent','theorems':67,'UTF8_byte_decoder_proved':True,'independent_complete_JSON_document_meaning_specified':True,'complete_JSON_parser_proved':False,'existing_scalar_AST_conversion_proved':False,'authenticated_capture_proved':False,'complete_source_refinement':False,'inherited_discharges':0}
    for k,file in files.items():package[k]=b(HERE/file)
    index['json_byte_packages']=[package];index['json_byte_candidate_theorems']=67;index['total_distinct_new_candidate_theorems']=1052;save(N/'formal-preparation-index.json',index)
    seq['candidate_fragment_theorems']=1052;seq['candidate_json_byte_packages']=1;save(N/'sequential-review.json',seq)
    progress['candidate_fragment_theorems']=1052;progress['json_byte_candidate_theorems']=67;progress['candidate_json_byte_packages']=1
    for k,file in files.items():progress['K02_json_bytes_'+k]=b(HERE/file)
    for value in progress.values():
        if isinstance(value,dict) and value.get('path') in {str((N/'formal-preparation-index.json').relative_to(ROOT)),str((N/'sequential-review.json').relative_to(ROOT))}:value.update(b(ROOT/value['path']))
    save(H/'execution/plan.json',plan)
    p=N/'check_current_review.py';s=p.read_text();marker="index.get('capture_projection_packages', [])):";assert s.count(marker)==1;s=s.replace(marker,"index.get('capture_projection_packages', []) +\n                    index.get('json_byte_packages', [])):")
    # Namespace accounting must retain outer namespaces across mutual blocks.
    marker='                elif ended:\n                    namespaces.pop()';assert s.count(marker)==1
    s=s.replace(marker,'                elif re.match(r"^(mutual|section(?: [\\w.]+)?)$", line):\n                    namespaces.append(None)\n                elif ended:\n                    namespaces.pop()')
    s=s.replace("'.'.join(namespaces + [theorem.group(1)])","'.'.join([part for part in namespaces if part is not None] + [theorem.group(1)])")
    marker='    assert len(declarations) == len(set(declarations))';assert s.count(marker)==1
    block='''        if package.get('UTF8_byte_decoder_proved'):
            assert proof['UTF8_byte_decoder_proved'] is True
            assert proof['UTF8_grammar_soundness_proved'] is True
            assert proof['UTF8_grammar_completeness_proved'] is True
            assert proof['UTF8_complete_consumption_proved'] is True
            assert proof['UTF8_scalar_range_proved'] is True
            assert proof['independent_complete_JSON_document_meaning_specified'] is True
            assert proof['UTF16_units_retained_in_grammar'] is True
            assert proof['complete_JSON_parser_implemented'] is False
            assert proof['complete_JSON_parser_proved'] is False
            assert proof['existing_scalar_AST_conversion_proved'] is False
            assert proof['original_capture_to_AST_bridge_proved'] is False
            assert proof['grammar_standard_translation_proved'] is False
            assert proof['byte_parser_proved'] is False
            assert proof['authenticated_capture_proved'] is False
            assert proof['whole_K02_source_refinement_proved'] is False
            assert proof['supported_resource_envelope_measured'] is False
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['worked_control_declarations'] == 47
            assert capture['utf8_reference_case_count'] == len(capture['utf8_reference_cases']) == 39
            assert len(capture['grammar_control_names']) == 8
            assert capture['candidate_parser_profile_owner_accepted'] is False
            audit = read(ROOT / package['UTF8_reference_audit']['path'])
            assert audit['result'] == 'UTF8-reference-corpus-audit-pass'
            assert audit['case_count'] == len(audit['cases']) == 39
            assert all(row['expected_scalars'] == row['actual_reference_scalars'] for row in audit['cases'])
            assert audit['complete_JSON_parser_proved'] is False
            assert audit['existing_scalar_AST_conversion_proved'] is False
            assert audit['candidate_parser_profile_owner_accepted'] is False
            assert audit['N03_schema_freeze'] is False
            api = read(ROOT / package['candidate_api_contract']['path'])
            assert api['N03_API_freeze'] is False
            assert api['UTF8_byte_decoder_proved'] is True
            assert api['complete_JSON_parser_proved'] is False
            assert api['existing_scalar_AST_conversion_proved'] is False
            assert api['candidate_parser_profile_owner_accepted'] is False
            assert api['replacement_character_recovery'] is False
            assert api['public_outcome_classification_implemented'] is False
'''
    p.write_text(s.replace(marker,block+marker))
    p=H/'execution/PROGRESS.md';s=p.read_text();s=s.replace('making 985 distinct verified candidate declarations in total.','and exact UTF-8/document-meaning work adds 67, making 1052 distinct verified candidate declarations in total.')
    s+='''
K02-json-bytes proves complete shortest-form UTF-8 prefix/stream decoding with
independent byte/numeric meanings, exact original suffix/complete consumption,
scalar bounds, deterministic meanings and byte-length-derived sufficient fuel.
The independent full JSON document grammar retains original number lexemes,
ordered duplicate decoded object members and UTF-16 string units. Review found
an actual representation gap: escaped unpaired surrogates belong to raw JSON
syntax but cannot silently become the existing scalar-string AST. Raw units
therefore retain this distinction pending explicit conversion/profile outcomes.
All 67 new declarations (20 general results and 47 controls) pass 24 fresh compile/
replay invocations, 246 dependency-inclusive axiom inspections and 24 matching-phase
import audits. All 39 strict UTF-8 reference cases match; eight grammar controls
retain duplicate keys, surrogate units and equivalent supplementary spellings.
Full JSON unit/string/value/document parsing, scalar-AST conversion, RFC/Schema
translation, original capture/digest/authentic provider bridges, nineteen K02
policies, public outcomes/resources, whole-source/effect/theory and mandatory
independent closure remain open. The registered total is 1052 candidate declarations.
All 263 inherited IDs remain pending and all 90 original discharges retain scope.
K00-K03 actual meanings retain scope; K04/D01-D08 remain pending. N01 is in
progress, N02/N03 are unstarted and only N00 is accepted (1/20). The full
41-kind/550-pair/seven-extension plan and final actual new use assessment stay active.
''';p.write_text(s)
    print('Registered 67 UTF-8/document-meaning declarations; total 1052; all 263 inherited IDs pending; K04 remains current.')
if __name__=='__main__':run()
