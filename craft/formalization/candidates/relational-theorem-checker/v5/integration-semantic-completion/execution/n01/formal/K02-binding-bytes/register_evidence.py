"""Register original byte-record/capture correspondence without authentic source or inherited closure."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;N=HERE.parents[1];H=HERE.parents[3];ROOT=HERE.parents[9]
def b(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def run():
    v=read(HERE/'verification.json');a=read(HERE/'import-resolution-audit.json')
    assert v['result']=='candidate-fragment-pass' and v['new_declaration_count']==72
    assert v['new_general_declarations']==44 and v['new_worked_control_declarations']==28
    assert len(v['records'])==118 and sum(r['inspected_declarations'] for r in v['records'])==1120
    assert a['result']=='import-resolution-audit-pass' and a['resolved_source_phase_pairs']==118 and a['verification']==b(HERE/'verification.json')
    assert v['byte_record_and_capture_refinement_proved'] and v['capture_direct_independent_refusal_meanings_proved']
    assert v['original_binding_fixture_bytes_kernel_checked'] and v['original_binding_fixture_count']==2
    assert not v['digest_algorithm_realized'] and not v['authenticated_capture_proved']
    assert not v['whole_K02_source_refinement_proved'] and not v['independent_checker_run']
    index=read(N/'formal-preparation-index.json');seq=read(N/'sequential-review.json');plan=read(H/'execution/plan.json');progress=next(t for t in plan['tasks'] if t['id']=='N01')['progress']
    assert index['total_distinct_new_candidate_theorems']==seq['candidate_fragment_theorems']==progress['candidate_fragment_theorems']==1487
    assert not index.get('byte_binding_packages') and seq['current_unit']=='K04'
    assert index['inherited_discharges']==seq['new_inherited_discharges']==progress['inherited_discharges']==0
    driver=N/'check_current_review.py';s=driver.read_text();categoryMarker="index.get('scalar_conversion_packages', [])):";endMarker='    assert len(declarations) == len(set(declarations))'
    assert s.count(categoryMarker)==s.count(endMarker)==1
    readout=H/'execution/PROGRESS.md';old='making 1487 distinct verified candidate declarations in total.';assert readout.read_text().count(old)==1
    files={'verification':'verification.json','import_resolution_audit':'import-resolution-audit.json','candidate_api_contract':'candidate-api-contract.json','model_review':'MODEL-REVIEW.md','refinement_matrix':'refinement-matrix.json','next_implementation_plan':'NEXT-IMPLEMENTATION.md','independent_formalization':'FORMALIZATION.md'}
    package={'unit':'K02-binding-bytes','kind':'relation.addresses-intent','theorems':72,'general_declarations':44,'worked_control_declarations':28,'byte_record_and_capture_refinement_proved':True,'raw_binding_record_parser_proved':True,'byte_parser_proved':True,'original_capture_to_AST_bridge_proved':True,'original_binding_fixture_bytes_kernel_checked':True,'retained_byte_envelope_frame_exactness_proved':True,'byte_catalog_staging_exactness_proved':True,'capture_direct_independent_refusal_meanings_proved':True,'digest_algorithm_realized':False,'authenticated_capture_proved':False,'complete_source_refinement':False,'inherited_discharges':0}
    for key,file in files.items():package[key]=b(HERE/file)
    index['byte_binding_packages']=[package];index['byte_binding_candidate_theorems']=72;index['total_distinct_new_candidate_theorems']=1559;save(N/'formal-preparation-index.json',index)
    seq['candidate_fragment_theorems']=1559;seq['candidate_byte_binding_packages']=1;save(N/'sequential-review.json',seq)
    progress['candidate_fragment_theorems']=1559;progress['byte_binding_candidate_theorems']=72;progress['candidate_byte_binding_packages']=1
    for key,file in files.items():progress['K02_binding_bytes_'+key]=b(HERE/file)
    for value in progress.values():
        if isinstance(value,dict) and value.get('path') in {str((N/'formal-preparation-index.json').relative_to(ROOT)),str((N/'sequential-review.json').relative_to(ROOT))}:value.update(b(ROOT/value['path']))
    save(H/'execution/plan.json',plan)
    s=s.replace(categoryMarker,"index.get('scalar_conversion_packages', []) +\n                    index.get('byte_binding_packages', [])):")
    block='''        if package.get('byte_record_and_capture_refinement_proved'):
            for key in ['byte_record_and_capture_refinement_proved','raw_binding_record_parser_proved',
                        'binding_record_bytes_exactness_proved','binding_record_all_fields_preserved',
                        'original_capture_to_AST_bridge_proved','original_binding_fixture_bytes_kernel_checked',
                        'byte_parser_proved','retained_byte_envelope_frame_exactness_proved',
                        'byte_catalog_staging_exactness_proved','ordered_all_input_capture_meaning_proved',
                        'record_outcome_exactness_proved','capture_outcome_exactness_proved',
                        'capture_direct_independent_refusal_meanings_proved','capture_parser_policy_adapter_implemented',
                        'remaining_capture_policies_unchanged_proved','conditional_capture_evidence_bridge_proved',
                        'unrelated_AST_byte_regression_refused','record_capture_outcome_classification_implemented']:
                assert proof[key] is True
            for key in ['digest_algorithm_realized','authenticated_capture_proved',
                        'authenticated_full_source_policy_realization_proved','JSON_schema_semantics_interpreter_proved',
                        'binding_schema_AST_correspondence_proved','grammar_standard_translation_proved',
                        'candidate_parser_profile_owner_accepted','supported_resource_envelope_measured',
                        'public_outcome_classification_implemented','raw_source_refinement_proved',
                        'whole_K02_source_refinement_proved','independent_checker_run']:
                assert proof[key] is False
            assert proof['new_general_declarations'] == package['general_declarations'] == 44
            assert proof['new_worked_control_declarations'] == package['worked_control_declarations'] == 28
            assert proof['original_binding_fixture_count'] == 2
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['new_general_declarations'] == 44
            assert capture['new_worked_control_declarations'] == 28
            assert capture['original_source_bytes_parsed'] is True
            assert capture['original_source_capture_authenticated'] is False
            original = read(ROOT / capture['original_byte_controls']['path'])
            assert original['worked_control_declarations'] == 6
            assert len(original['fixtures']) == 2
            controlSource = (ROOT / original['controls']['path']).read_text()
            for fixture in original['fixtures']:
                match = re.search(r"^def " + fixture['kind'] + r"Bytes : CandidateJsonBytes.Bytes := \\[(.*?)\\]$", controlSource, re.M)
                assert match
                actual = bytes(int(token) for token in match.group(1).split(',') if token.strip())
                assert actual == (ROOT / fixture['original_bytes']['path']).read_bytes()
                assert len(actual) == fixture['byte_length']
                assert fixture['synthetic_reference_and_review_roots'] is True
            controls = read(ROOT / capture['capture_control_index']['path'])
            assert controls['worked_control_declarations'] == len(controls['names']) == 22
            assert controls['digest_labels_uncomputed'] is True
            assert controls['profile_and_review_roots_synthetic'] is True
            api = read(ROOT / package['candidate_api_contract']['path'])
            for key in ['byte_record_and_capture_refinement_proved','raw_binding_record_parser_proved',
                        'original_capture_to_AST_bridge_proved','original_binding_fixture_bytes_kernel_checked',
                        'byte_parser_proved','capture_direct_independent_refusal_meanings_proved',
                        'record_capture_outcome_classification_implemented']:
                assert api[key] is True
            for key in ['N03_API_freeze','digest_algorithm_realized','authenticated_capture_proved',
                        'authenticated_full_source_policy_realization_proved','binding_schema_AST_correspondence_proved',
                        'supported_resource_envelope_measured','public_outcome_classification_implemented',
                        'candidate_parser_profile_owner_accepted','independent_checker_run']:
                assert api[key] is False
'''
    driver.write_text(s.replace(endMarker,block+endMarker))
    s=readout.read_text().replace(old,'and original byte-record/capture/catalog work adds 72, making 1559 distinct verified candidate declarations in total.')
    s+='''
K02-binding-bytes closes original bytes-to-complete-binding-record and retained-
capture/frame/list/catalog preparation correspondence. Independent meanings use
raw grammar/scalar AST and complete record/envelope/frame meanings; callers do
not supply an unrelated AST at new byte entrypoints. Three direct capture-refusal
corollaries state grammar/scalar/record causes without an intermediate classifier
premise. Record and capture outcomes distinguish malformed syntax, unsupported
scalar representation, invalid record, inadequate envelope and stale frame.
Original resolution/role fixture bytes (2621/1848) match the exact kernel literals
and decode into expected complete records; capture and catalog controls retain
those bytes. The old AST-input interface accepts a valid AST with unrelated [1,2]
bytes; the new byte-input interface refuses them. The parse-policy adapter retains
all separate digest/owned-profile/Schema/review requirements unchanged.
All 44 general results and 28 controls pass 118 fresh compile/replay invocations,
1120 dependency-inclusive axiom inspections and 118 matching-phase import audits.
The total is 1559 distinct candidate declarations. Recursion settings affect proof
elaboration only; compilation timings are not measured runtime limits and replay
uses the same kernel, not mandatory independent checking. Original fixture roots
are synthetic and capture digest labels remain uncomputed. Computed digests,
authentically selected profiles, full Schema/authentic evidence, nineteen complete
K02 source policies, full source/world/Selection/qualifier joins, standard/profile,
public diagnostics/resources and inherited/theory/independent closure remain open.
All 263 inherited IDs remain pending and all 90 original discharges retain scope.
K00–K03 actual meanings retain scope; K04 and D01–D08 remain pending. N01 remains in
progress, N02/N03 unstarted and only N00 accepted (1/20). Next is formalizing the
pinned digest-profile and byte/digest computation bridge before implementation.
The full 41-kind/550-pair/seven-extension plan and actual new final bounded-use
assessment remain active. No commit, publication, deployment or promotion occurs.
''';readout.write_text(s)
    print('Registered 72 byte-record/capture/catalog declarations; total 1559; all 263 inherited IDs remain pending.')
if __name__=='__main__':run()
