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
        if package.get('automatic_body_dispatch_exact'):
            assert proof['new_general_declarations']==13 and proof['new_worked_control_declarations']==0
            assert len(proof['records'])==6 and len(proof['reused_dependencies'])==292
            assert proof['runtime_composed_cases']==395 and proof['schema_comparison_cases']==296
            assert proof['wrapper_kind_cases']==49 and proof['wrapper_identity_mismatch_cases']==7
            assert proof['unused_and_root_alignment_cases']==14 and proof['profile_count']==7
            for flag in ['automatic_source_discriminant_dispatch_proved','complete_fixed_kind_record_meanings_preserved',
                         'selected_kind_equals_body_constructor','all_payload_records_and_roots_aligned',
                         'candidate_full_entrypoint_composed','candidate_full_acceptance_iff_original_meaning_and_alignment',
                         'eighteen_remaining_source_policies_preserved','original_nested_checks_and_complete_captures_preserved']:
                assert proof[flag] is True
            for flag in ['all_original_payload_roles_supported','actual_source_identity_ownership_proved',
                         'general_schema_compiler_correspondence_proved','python_lean_general_correspondence_proved',
                         'general_body_reconstruction_proved','owned_schema_admission_proved',
                         'all_original_source_policy_providers_realized','approved_kind_specific_payload_decoders_realized',
                         'local_dependency_rebuild','supported_resource_envelope_measured','real_authoritative_snapshot_provider',
                         'live_consumer_integration','mandatory_consumers_integrated','N03_API_freeze']:
                assert proof[flag] is False
            audit=read(ROOT/package['import_resolution_audit']['path'])
            assert audit['verification']==package['verification'] and audit['resolved_source_phase_pairs']==6
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
            assert len(controls['runtime_cases'])==395 and controls['schema_comparison_cases']==296
            assert controls['wrapper_kind_cases']==49 and controls['unused_and_root_alignment_cases']==14
            assert controls['captured_context_is_synthetic'] and not controls['all_original_payload_roles_supported']
            runtime=ROOT/proof['sources'][-1]['path']
            assert runtime.stem=='DispatchControls'
            assert re.findall(r'^#eval (.*?)(?=\n#eval |\nend )',runtime.read_text(),re.M|re.S)==[c['expression'] for c in controls['runtime_cases']]
            for row in proof['records']:
                if Path(row['source']['path']).stem=='DispatchControls':
                    assert (ROOT/row['log']['path']).read_text().strip().splitlines()==[c['expected'] for c in controls['runtime_cases']]
                    assert row['runtime_composed_cases']==395
            gaps=read(ROOT/package['source_role_gap_map']['path'])
            assert gaps['result']=='source-role-scope-audit-with-explicit-gaps'
            assert gaps['supported_body_count']==len(gaps['supported_body_profiles'])==7
            assert len(gaps['remaining_roles'])==3 and gaps['remaining_non_parser_policy_slots']==18
            assert not gaps['all_original_payload_roles_supported'] and not gaps['actual_owned_role_provider']
            manifest=read(ROOT/gaps['original_profile_manifest']['path'])
            assert gaps['supported_body_profiles']==manifest['profiles']
            assert {row['role'] for row in gaps['remaining_roles']}=={'decision','satisfaction-test','excluded-or-other-payload-artifact'}
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert api['candidate_full_entrypoint_composed'] and api['all_payload_records_and_roots_aligned']
            assert api['all_original_nested_capture_checks_preserved'] and api['original_semantic_interpretation_conditional_on_eighteen_policies']
            for flag in ['caller_kind_override_allowed','caller_schema_override_allowed','caller_approval_boolean_allowed',
                         'caller_typed_catalogs_allowed','whole_original_source_interpretation_proved',
                         'all_original_payload_roles_supported','general_schema_compiler_correspondence_proved',
                         'owned_schema_admission_proved','actual_source_identity_ownership_proved',
                         'mandatory_consumers_integrated','independent_checker_run','N03_API_freeze']:
                assert api[flag] is False
            matrix=read(ROOT/package['refinement_matrix']['path'])
            assert set(matrix['theorem_targets'])==set(proof['new_declarations'])
            assert not matrix['whole_original_source_interpretation'] and not matrix['complete_supporting_role_providers']
            completion=read(ROOT/package['component_completion_audit']['path'])
            assert completion['result']=='component-complete-with-explicit-integration-gaps'
            assert completion['new_general_theorems']==13 and completion['inherited_discharges']==0
            assert not completion['N01_accepted'] and not completion['all_original_payload_roles_supported']
'''

def run():
    proof, audit = read(HERE/'verification.json'), read(HERE/'import-resolution-audit.json')
    assert proof['result']=='candidate-fragment-pass' and proof['new_declaration_count']==13
    assert len(proof['records'])==audit['resolved_source_phase_pairs']==6
    assert len(proof['reused_dependencies'])==292 and proof['runtime_composed_cases']==395
    assert audit['verification']==binding(HERE/'verification.json')
    index,seq,plan=read(N/'formal-preparation-index.json'),read(N/'sequential-review.json'),read(H/'execution/plan.json')
    progress=next(t for t in plan['tasks'] if t['id']=='N01')['progress']
    assert index['total_distinct_new_candidate_theorems']==seq['candidate_fragment_theorems']==progress['candidate_fragment_theorems']==1959
    assert not index.get('body_dispatch_packages')
    assert seq['current_unit']=='K04' and seq['accepted_meaning_count']==4
    assert index['inherited_discharges']==seq['new_inherited_discharges']==progress['inherited_discharges']==0
    files={'verification':'verification.json','import_resolution_audit':'import-resolution-audit.json',
           'candidate_api_contract':'candidate-api-contract.json','model_review':'MODEL-REVIEW.md',
           'refinement_matrix':'refinement-matrix.json','next_implementation_plan':'NEXT-IMPLEMENTATION.md',
           'independent_formalization':'FORMALIZATION.md','control_index':'control-index.json',
           'context_pack':'context-pack.json','source_role_gap_map':'source-role-gap-map.json','component_completion_audit':'component-completion-audit.json'}
    driver=N/'check_current_review.py'; source=driver.read_text()
    marker="index.get('typed_payload_packages', [])):"
    end="    for preparation in index.get('payload_provider_preparations', []):"
    assert source.count(marker)==source.count(end)==1
    source=source.replace(marker,"index.get('typed_payload_packages', []) +\n                    index.get('body_dispatch_packages', [])):")
    source=source.replace(end,AUDIT_BLOCK+end)
    compile(source,str(driver),'exec')
    completion={'task':'N01','unit':HERE.name,'result':'component-complete-with-explicit-integration-gaps',
                'verification':binding(HERE/'verification.json'),'review':binding(HERE/'MODEL-REVIEW.md'),
                'new_general_theorems':13,'all_original_payload_roles_supported':False,'inherited_discharges':0,'N01_accepted':False,'authority_effect':'none',
                'requirements':[{'id':'automatic-seven-kind-dispatch','status':'proved'},
                                {'id':'complete-catalog-kind-and-identity-token-alignment','status':'proved'},
                                {'id':'candidate-guarded-full-entry-exactness','status':'proved'},
                                {'id':'original-semantic-interpretation','status':'conditional-on-eighteen-policy-premises'},
                                {'id':'complete-original-supporting-role-providers','status':'incomplete'},
                                {'id':'authentic-admission-identity-and-ownership','status':'incomplete'},
                                {'id':'general-source-correspondence-mandatory-consumers-independent-checking','status':'incomplete'}]}
    save(HERE/'component-completion-audit.json',completion)
    package={'unit':HERE.name,'kind':'relation.addresses-intent','theorems':13,'general_declarations':13,
             'worked_control_declarations':0,'automatic_body_dispatch_exact':True,
             'complete_source_refinement':False,'inherited_discharges':0}
    package.update({k:binding(HERE/v) for k,v in files.items()})
    package['remaining_policy_map']=read(HERE/'context-pack.json')['remaining_policy_map']
    index['body_dispatch_packages']=[package];index['body_dispatch_candidate_theorems']=13
    index['total_distinct_new_candidate_theorems']=1972
    seq.update(candidate_fragment_theorems=1972,candidate_body_dispatch_packages=1)
    progress.update(candidate_fragment_theorems=1972,candidate_body_dispatch_packages=1,body_dispatch_candidate_theorems=13)
    progress.update({'K02_body_dispatch_'+k:binding(HERE/v) for k,v in files.items()})
    save(N/'formal-preparation-index.json',index);save(N/'sequential-review.json',seq)
    changed={str((N/v).relative_to(ROOT)) for v in ['formal-preparation-index.json','sequential-review.json']}
    for value in progress.values():
        if isinstance(value,dict) and value.get('path') in changed: value.update(binding(ROOT/value['path']))
    progress_path=H/'execution/PROGRESS.md'; text=progress_path.read_text()
    old='making 1959 distinct verified candidate declarations in total.'
    assert text.count(old)==1
    text=text.replace(old,'and automatic dispatch and guarded full entry add 13, making 1972 distinct verified candidate declarations in total.')
    text+='\n\nAutomatic body dispatch and guarded candidate entry\n\nThe seven complete body profiles are selected from exact original source\ndiscriminants, including Goal without a kind field. Thirteen general declarations\nprove selector/decoder exactness, constructor consistency, all-record/root kind\nand identity-token alignment, exact guarded full entry and original interpretation\nconditional on all eighteen remaining non-parser policy premises. Existing complete\nbyte/digest, nested, frame and resource checks remain in the full meaning.\n\nSix fresh compile/replay module calls and 395 runtime observations per phase pass.\nAll 296 prior complete-schema cases use automatic selection; 49 wrapper/body kind\ncombinations, seven identity mismatches and fourteen unused/root mismatches are\nchecked. Exact phase outputs of 146 prior modules are reused. Same-kernel replay\nis not independent checking or general source-schema correspondence.\n\nThe scope audit exposes three supporting-source gaps: complete Decision providers,\nowned satisfaction-test role-to-source/profile mapping, and complete excluded/unused\nartifact providers beyond the six selected subject kinds. The old synthetic String\nfixture succeeds in its old checker and refuses in this typed candidate; that is\na demonstrated integration gap, not full end-to-end success. The seven-kind family\ndoes not replace the broader original payload scope.\n\nAuthentic root/source/owner/World/selection and all eighteen policy providers, general\nsource/reconstruction correspondence, mandatory consumers, independent checking,\nmeasured limits and the remaining relation/extension work stay required. All 263\ninherited obligations remain open; 90 original discharges retain scope. K00–K03\nmeanings are accepted, K04/global reviews remain pending and only N00 is accepted.\n'
    save(H/'execution/plan.json',plan);driver.write_text(source);progress_path.write_text(text)
    print('Registered 13 automatic-dispatch/integration declarations; 1972 total; zero inherited discharges.')

if __name__=='__main__': run()
