"""Register automatic dispatch and guarded entry proofs; retain every integration gap."""
from pathlib import Path
import hashlib, json

HERE = Path(__file__).resolve().parent
N, H, ROOT = HERE.parents[1], HERE.parents[3], HERE.parents[9]
def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
def read(path): return json.loads(path.read_text())
def save(path, value): path.write_text(json.dumps(value, indent=2)+'\n')

AUDIT_BLOCK = r'''
        if package.get('complete_supporting_decision_family_exact'):
            assert proof['new_general_declarations']==12 and proof['new_worked_control_declarations']==0
            assert len(proof['records'])==8 and len(proof['reused_dependencies'])==298
            assert proof['runtime_composed_cases']==458 and proof['prior_endpoint_schema_cases']==296
            assert proof['decision_schema_cases']==69 and proof['wrapper_kind_cases']==64
            assert proof['wrong_identity_cases']==8 and proof['profile_count']==8
            assert proof['record_type_count']==3 and proof['complete_decision_field_count']==23
            assert proof['active_assertion_nodes']==30
            for flag in ['complete_decision_schema_decoder_realized','original_endpoint_meanings_bidirectionally_preserved',
                         'automatic_source_discriminant_dispatch_proved','complete_fixed_kind_record_meanings_preserved',
                         'decision_tag_excludes_endpoint_selector_proved','all_payload_records_and_roots_aligned',
                         'candidate_full_entrypoint_composed','candidate_full_acceptance_iff_original_meaning_and_alignment',
                         'eighteen_remaining_source_policies_preserved','original_nested_checks_and_complete_captures_preserved']:
                assert proof[flag] is True
            for flag in ['decision_authority_proved','all_original_payload_roles_supported',
                         'actual_source_identity_ownership_proved','general_schema_compiler_correspondence_proved',
                         'python_lean_general_correspondence_proved','general_body_reconstruction_proved',
                         'owned_schema_admission_proved','all_original_source_policy_providers_realized',
                         'approved_kind_specific_payload_decoders_realized','local_dependency_rebuild',
                         'supported_resource_envelope_measured','real_authoritative_snapshot_provider',
                         'live_consumer_integration','mandatory_consumers_integrated','N03_API_freeze']:
                assert proof[flag] is False
            audit=read(ROOT/package['import_resolution_audit']['path'])
            assert audit['verification']==package['verification'] and audit['resolved_source_phase_pairs']==8
            pool={}
            for prior_ref in proof['prior_verifications']:
                prior=read(ROOT/prior_ref['path'])
                for row in prior['records']+prior.get('reused_dependencies',[]):
                    output=row.get('olean',row.get('reused_output'))
                    key=(row['phase'],Path(output['path']).name)
                    value=(row['source']['path'],row['source']['sha256'],output['sha256'])
                    if key in pool: assert pool[key]==value
                    else: pool[key]=value
            actual={}
            for row in proof['reused_dependencies']:
                key=(row['phase'],Path(row['reused_output']['path']).name)
                assert key not in actual
                actual[key]=(row['source']['path'],row['source']['sha256'],row['reused_output']['sha256'])
                assert row['reused_output']['sha256']==row['prior_output']['sha256']
                assert (ROOT/row['reused_output']['path']).parent==package_dir/row['phase']
            assert actual==pool
            controls=read(ROOT/package['control_index']['path'])
            assert len(controls['runtime_cases'])==458 and controls['prior_endpoint_schema_cases']==296
            assert controls['decision_schema_cases']==len(controls['decision_inputs'])==69
            assert controls['wrapper_kind_cases']==64 and controls['captured_context_is_synthetic']
            assert not controls['all_original_payload_roles_supported'] and not controls['independent_checker_run']
            runtime=ROOT/proof['sources'][-1]['path']
            assert runtime.stem=='SupportingControls'
            assert re.findall(r'^#eval (.*?)(?=\n#eval |\nend )',runtime.read_text(),re.M|re.S)==[c['expression'] for c in controls['runtime_cases']]
            for row in proof['records']:
                if Path(row['source']['path']).stem=='SupportingControls':
                    assert (ROOT/row['log']['path']).read_text().strip().splitlines()==[c['expected'] for c in controls['runtime_cases']]
                    assert row['runtime_composed_cases']==458
            generation=read(ROOT/package['generation_audit']['path'])
            assert generation['result']=='complete-decision-schema-generation-pass'
            assert generation['generated_source']==proof['sources'][0]
            assert generation['record_type_count']==3 and generation['complete_record_field_count']==23
            assert len(generation['assertion_trace'])==generation['active_assertion_nodes']==30
            assert generation['all_declared_fields_required_verified'] and not generation['unsupported_assertions_ignored']
            assert not generation['general_schema_compiler_correspondence_proved']
            manifest=read(ROOT/package['profile_manifest']['path'])
            assert len(manifest['profiles'])==1 and manifest['profiles'][0]['kind']=='decision'
            decision=manifest['profiles'][0]
            schema=read(ROOT/decision['schema']['path']);artifact=read(ROOT/decision['artifact']['path'])
            assert artifact['schema_digest']==decision['schema']['sha256']
            assert decision['schema_ref']==artifact['schema_ref']=='cal.schema.decision/v1'
            assert decision['identity_field']=='node_id' and decision['source_status']=='candidate-unadmitted'
            assert set(decision['required_fields'])==set(schema['required']) and len(schema['required'])==14
            gaps=read(ROOT/package['source_role_gap_map']['path'])
            assert gaps['result']=='supporting-source-scope-audit-with-explicit-gaps'
            assert gaps['supported_body_count']==len(gaps['supported_body_profiles'])==8
            assert gaps['decision_complete_shape_decoder_realized'] and gaps['supported_body_profiles'][-1]==decision
            assert len(gaps['remaining_roles'])==3 and gaps['remaining_non_parser_policy_slots']==18
            assert not gaps['all_original_payload_roles_supported'] and not gaps['actual_owned_role_provider']
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert api['candidate_full_entrypoint_composed'] and api['all_payload_records_and_roots_aligned']
            assert api['complete_decision_schema_decoder_realized'] and api['original_endpoint_meanings_bidirectionally_preserved']
            assert api['supported_body_profiles']==8 and not api['decision_authority_proved']
            for flag in ['whole_original_source_interpretation_proved','all_original_payload_roles_supported',
                         'general_schema_compiler_correspondence_proved','owned_schema_admission_proved',
                         'actual_source_identity_ownership_proved','mandatory_consumers_integrated',
                         'independent_checker_run','N03_API_freeze']:
                assert api[flag] is False
            matrix=read(ROOT/package['refinement_matrix']['path'])
            assert set(matrix['theorem_targets'])==set(proof['new_declarations'])
            assert not matrix['whole_original_source_interpretation'] and not matrix['complete_supporting_role_providers']
            completion=read(ROOT/package['component_completion_audit']['path'])
            assert completion['result']=='component-complete-with-explicit-integration-gaps'
            assert completion['new_general_theorems']==12 and completion['inherited_discharges']==0
            assert not completion['N01_accepted'] and not completion['all_original_payload_roles_supported']
'''

def run():
    proof, audit = read(HERE/'verification.json'), read(HERE/'import-resolution-audit.json')
    assert proof['result']=='candidate-fragment-pass' and proof['new_declaration_count']==12
    assert len(proof['records'])==audit['resolved_source_phase_pairs']==8
    assert len(proof['reused_dependencies'])==298 and proof['runtime_composed_cases']==458
    assert audit['verification']==binding(HERE/'verification.json')
    index,seq,plan=read(N/'formal-preparation-index.json'),read(N/'sequential-review.json'),read(H/'execution/plan.json')
    progress=next(t for t in plan['tasks'] if t['id']=='N01')['progress']
    assert index['total_distinct_new_candidate_theorems']==seq['candidate_fragment_theorems']==progress['candidate_fragment_theorems']==1972
    assert not index.get('supporting_source_packages')
    assert seq['current_unit']=='K04' and seq['accepted_meaning_count']==4
    assert index['inherited_discharges']==seq['new_inherited_discharges']==progress['inherited_discharges']==0
    files={'verification':'verification.json','import_resolution_audit':'import-resolution-audit.json',
           'candidate_api_contract':'candidate-api-contract.json','model_review':'MODEL-REVIEW.md',
           'refinement_matrix':'refinement-matrix.json','next_implementation_plan':'NEXT-IMPLEMENTATION.md',
           'independent_formalization':'FORMALIZATION.md','control_index':'control-index.json',
           'context_pack':'context-pack.json','source_role_gap_map':'source-role-gap-map.json','generation_audit':'generation-audit.json',
           'profile_manifest':'profile-manifest.json','component_completion_audit':'component-completion-audit.json'}
    driver=N/'check_current_review.py'; source=driver.read_text()
    marker="index.get('body_dispatch_packages', [])):"
    end="    for preparation in index.get('payload_provider_preparations', []):"
    assert source.count(marker)==source.count(end)==1
    source=source.replace(marker,"index.get('body_dispatch_packages', []) +\n                    index.get('supporting_source_packages', [])):")
    source=source.replace(end,AUDIT_BLOCK+end)
    compile(source,str(driver),'exec')
    completion={'task':'N01','unit':HERE.name,'result':'component-complete-with-explicit-integration-gaps',
                'verification':binding(HERE/'verification.json'),'review':binding(HERE/'MODEL-REVIEW.md'),
                'new_general_theorems':12,'all_original_payload_roles_supported':False,'inherited_discharges':0,'N01_accepted':False,'authority_effect':'none',
                'requirements':[{'id':'complete-original-decision-body','status':'proved-complete-record-meaning'},
                                {'id':'extended-family-and-original-endpoint-equivalence','status':'proved'},
                                {'id':'candidate-full-entry-alignment-and-exactness','status':'proved'},
                                {'id':'original-semantic-interpretation','status':'conditional-on-eighteen-policy-premises'},
                                {'id':'actual-decision-authority-and-role-interpretation','status':'incomplete'},
                                {'id':'satisfaction-test-and-excluded-unused-source-providers','status':'incomplete'},
                                {'id':'general-source-correspondence-consumers-independent-checking','status':'incomplete'}]}
    save(HERE/'component-completion-audit.json',completion)
    package={'unit':HERE.name,'kind':'relation.addresses-intent','theorems':12,'general_declarations':12,
             'worked_control_declarations':0,'complete_supporting_decision_family_exact':True,
             'complete_source_refinement':False,'inherited_discharges':0}
    package.update({k:binding(HERE/v) for k,v in files.items()})
    package['remaining_policy_map']=read(HERE/'context-pack.json')['remaining_policy_map']
    index['supporting_source_packages']=[package];index['supporting_source_candidate_theorems']=12
    index['total_distinct_new_candidate_theorems']=1984
    seq.update(candidate_fragment_theorems=1984,candidate_supporting_source_packages=1)
    progress.update(candidate_fragment_theorems=1984,candidate_supporting_source_packages=1,supporting_source_candidate_theorems=12)
    progress.update({'K02_supporting_source_'+k:binding(HERE/v) for k,v in files.items()})
    save(N/'formal-preparation-index.json',index);save(N/'sequential-review.json',seq)
    changed={str((N/v).relative_to(ROOT)) for v in ['formal-preparation-index.json','sequential-review.json']}
    for value in progress.values():
        if isinstance(value,dict) and value.get('path') in changed: value.update(binding(ROOT/value['path']))
    progress_path=H/'execution/PROGRESS.md'; text=progress_path.read_text()
    old='making 1972 distinct verified candidate declarations in total.'
    assert text.count(old)==1
    text=text.replace(old,'and complete Decision/extended-family integration adds 12, making 1984 distinct verified candidate declarations in total.')
    text+='\n\nComplete Decision and extended supporting family\n\nDecision/v1 now has a complete typed decoder for three record types, 23 fields\nand all 30 active assertion nodes. Twelve new general declarations prove exact\nDecision record meaning, source tag and extended family dispatch, bidirectional\npreservation of all seven earlier endpoint meanings and candidate full entry\nwith complete all-record/root alignment. Original interpretation still requires\nall eighteen non-parser policy premises. Schema validity does not prove authority.\n\nEight fresh compile/replay module calls and 458 runtime observations per phase\npass: 296 prior endpoint cases, 69 Decision schema controls, sixteen kind/identity\nobservations, sixty-four wrapper/body kind combinations, eight wrong identities\nand five boundaries. Exact phase outputs of 149 prior modules are reused. The\noriginal schemas allow repeated relation records and whitespace under minLength=1;\nthose accepted shapes remain preserved. Same-kernel replay is not independent.\n\nDecision shape decoding is realized; actual Decision admission, decision-maker\nauthority and role interpretation remain missing. Satisfaction-test tokens still\nlack owned source-kind/schema mapping, and excluded/unused artifacts need complete\nproviders. The old synthetic opaque String fixture still refuses under the typed\nfamily, so an all-role end-to-end success is not claimed. Authentic source/root/\nowner/World/selection providers, general correspondence, mandatory consumers,\nindependent checking, measured limits and the full relation/extension work remain.\nAll 263 inherited obligations are open; 90 original discharges retain scope. K04\nand global reviews stay pending; only N00 is accepted in the active twenty-task plan.\n'
    save(H/'execution/plan.json',plan);driver.write_text(source);progress_path.write_text(text)
    print('Registered 12 complete Decision/supporting-family declarations; 1984 total; zero inherited discharges.')

if __name__=='__main__': run()
