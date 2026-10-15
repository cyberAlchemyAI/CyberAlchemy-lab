"""Register exact retained-catalog parity without closing inherited obligations."""
from pathlib import Path
import hashlib, json
HERE = Path(__file__).resolve().parent
N, H, ROOT = HERE.parents[1], HERE.parents[3], HERE.parents[9]
def binding(path): return {'path':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def read(path): return json.loads(path.read_text())
def save(path,value): path.write_text(json.dumps(value,indent=2)+'\n')
def run():
    proof,audit=read(HERE/'verification.json'),read(HERE/'import-resolution-audit.json')
    assert proof['result']=='candidate-fragment-pass' and proof['new_declaration_count']==9
    assert len(proof['records'])==audit['resolved_source_phase_pairs']==8
    assert len(proof['reused_dependencies'])==276 and proof['runtime_composed_cases']==18
    assert audit['verification']==binding(HERE/'verification.json')
    assert proof['catalog_reparse_eliminated'] and proof['full_public_result_and_refusal_parity_proved']
    index,seq,plan=read(N/'formal-preparation-index.json'),read(N/'sequential-review.json'),read(H/'execution/plan.json')
    progress=next(t for t in plan['tasks'] if t['id']=='N01')['progress']
    assert index['total_distinct_new_candidate_theorems']==seq['candidate_fragment_theorems']==progress['candidate_fragment_theorems']==1938
    assert not index.get('retained_catalog_packages')
    assert seq['current_unit']=='K04' and seq['accepted_meaning_count']==4
    assert index['inherited_discharges']==seq['new_inherited_discharges']==progress['inherited_discharges']==0
    files={'verification':'verification.json','import_resolution_audit':'import-resolution-audit.json',
           'candidate_api_contract':'candidate-api-contract.json','model_review':'MODEL-REVIEW.md',
           'refinement_matrix':'refinement-matrix.json','next_implementation_plan':'NEXT-IMPLEMENTATION.md',
           'independent_formalization':'FORMALIZATION.md','control_index':'control-index.json',
           'context_pack':'context-pack.json','component_completion_audit':'component-completion-audit.json'}
    driver=N/'check_current_review.py';source=driver.read_text()
    marker="index.get('nested_provenance_packages', [])):"
    end='    assert len(declarations) == len(set(declarations))'
    assert source.count(marker)==source.count(end)==1
    block="        if package.get('retained_catalog_entry_exact'):\n            assert proof['new_general_declarations']==9 and proof['new_worked_control_declarations']==0\n            assert len(proof['records'])==8 and proof['runtime_composed_cases']==18\n            assert len(proof['reused_dependencies'])==276\n            for flag in ['catalog_reparse_eliminated','retained_certificates_exact',\n                         'selected_public_result_parity_proved','full_public_result_and_refusal_parity_proved',\n                         'catalog_parity_uses_independent_captured_meaning','original_byte_pipeline_exact',\n                         'eighteen_remaining_source_policies_preserved','all_supplied_captures_guarded',\n                         'selected_digest_profile_provenance_bound','profile_frame_is_relation_world_frame',\n                         'current_api_capture_manifest_complete','full_budget_before_any_capture_processing',\n                         'nested_full_body_digest_alignment_proved','ordered_complete_nested_manifest_enforced',\n                         'all_original_nested_artifact_occurrences_checked']:\n                assert proof[flag] is True\n            for flag in ['local_dependency_rebuild','supported_resource_envelope_measured',\n                         'real_authoritative_snapshot_provider','live_consumer_integration','N03_API_freeze',\n                         'owned_selected_profile_without_root_premise','approved_kind_specific_payload_decoders_realized',\n                         'all_original_source_policy_providers_realized']:\n                assert proof[flag] is False\n            pool={}\n            for prior_ref,audit_ref in zip(proof['prior_verifications'],proof['prior_import_audits'],strict=True):\n                prior,prior_audit=read(ROOT/prior_ref['path']),read(ROOT/audit_ref['path'])\n                assert prior['result']=='candidate-fragment-pass' and prior_audit['verification']==prior_ref\n                for row in prior['records']+prior.get('reused_dependencies',[]):\n                    output=row.get('olean',row.get('reused_output'))\n                    key=(row['phase'],Path(output['path']).name)\n                    item=(row['source']['path'],row['source']['sha256'],output['sha256'])\n                    if key in pool:assert pool[key]==item\n                    else:pool[key]=item\n            actual={}\n            for row in proof['reused_dependencies']:\n                key=(row['phase'],Path(row['reused_output']['path']).name)\n                assert key not in actual\n                actual[key]=(row['source']['path'],row['source']['sha256'],row['reused_output']['sha256'])\n                assert row['reused_output']['sha256']==row['prior_output']['sha256']\n                assert (ROOT/row['reused_output']['path']).parent==package_dir/row['phase']\n            assert actual==pool\n            audit=read(ROOT/package['import_resolution_audit']['path'])\n            assert audit['verification']==package['verification'] and audit['resolved_source_phase_pairs']==8\n            controls=read(ROOT/package['control_index']['path'])\n            assert len(controls['runtime_cases'])==18 and controls['captured_context_is_synthetic']\n            assert not controls['real_authoritative_snapshot_provider'] and not controls['fixture_serializer_proved']\n            runtime=ROOT/proof['sources'][-1]['path']\n            assert runtime.stem=='CachedControls'\n            assert re.findall(r'^#eval (.*?)(?=\\n#eval |\\nend )',runtime.read_text(),re.M|re.S)==[case['expression'] for case in controls['runtime_cases']]\n            for row in proof['records']:\n                if Path(row['source']['path']).stem=='CachedControls':\n                    assert row['runtime_composed_cases']==18\n                    assert (ROOT/row['log']['path']).read_text().strip().splitlines()==[case['expected'] for case in controls['runtime_cases']]\n            api=read(ROOT/package['candidate_api_contract']['path'])\n            assert api['public_success_and_refusal_parity_proved'] and api['catalog_reparse_eliminated']\n            assert api['retained_state_is_internal'] and api['original_source_semantics_preserved']\n            assert api['single_frame']=='world.frame'\n            for flag in ['caller_AST_allowed','caller_typed_catalogs_allowed',\n                         'caller_relation_digest_profile_allowed','caller_separate_profile_frame_allowed',\n                         'caller_expected_nested_catalog_allowed','all_original_source_policy_providers_realized',\n                         'world_and_claim_authenticity_proved','N03_API_freeze']:\n                assert api[flag] is False\n            matrix=read(ROOT/package['refinement_matrix']['path'])\n            assert set(matrix['theorem_targets'])==set(proof['new_declarations']) and not matrix['whole_original_source_interpretation']\n            fixture=read(ROOT/package['fixture_validation']['path'])\n            assert fixture['result']=='concrete-nested-fixture-join-pass' and fixture['nested_occurrence_count']==20\n            policies=read(ROOT/package['source_policy_realization_map']['path'])\n            assert policies['remaining_slot_count']==18 and not policies['unconditional_original_source_interpretation_proved']\n            assert all(row['status']=='provider-realization-incomplete' and not row['inherited_discharge'] for row in policies['rows'])\n            completion=read(ROOT/package['component_completion_audit']['path'])\n            assert completion['result']=='component-complete-with-explicit-integration-gaps'\n            assert completion['inherited_discharges']==0 and not completion['N01_accepted']\n"
    source=source.replace(marker,"index.get('nested_provenance_packages', []) +\n                    index.get('retained_catalog_packages', [])):").replace(end,block+end)
    compile(source,str(driver),'exec')
    completion={'task':'N01','unit':HERE.name,'result':'component-complete-with-explicit-integration-gaps',
                'verification':binding(HERE/'verification.json'),'review':binding(HERE/'MODEL-REVIEW.md'),
                'api':binding(HERE/'candidate-api-contract.json'),'matrix':binding(HERE/'refinement-matrix.json'),
                'next_implementation':binding(HERE/'NEXT-IMPLEMENTATION.md'),
                'requirements':[{'id':'retained-certified-captures-and-catalogs','status':'proved'},
                                {'id':'complete-public-selected-and-nested-outcome-parity','status':'proved'},
                                {'id':'independent-full-meaning-equivalence','status':'proved'},
                                {'id':'catalog-reread-elimination','status':'implemented-and-proved'},
                                {'id':'original-source-interpretation','status':'conditional-on-exact-eighteen-policy-premises'},
                                {'id':'actual-source-root-world-and-selection-providers','status':'incomplete'},
                                {'id':'approved-kind-specific-decoders-and-mandatory-consumers','status':'incomplete'},
                                {'id':'independent-checking-and-operational-resource-measurement','status':'incomplete'}],
                'N01_accepted':False,'inherited_discharges':0,'authority_effect':'none'}
    save(HERE/'component-completion-audit.json',completion)
    package={'unit':HERE.name,'kind':'relation.addresses-intent','theorems':9,'general_declarations':9,
             'worked_control_declarations':0,'retained_catalog_entry_exact':True,'complete_source_refinement':False,'inherited_discharges':0}
    package.update({key:binding(HERE/name) for key,name in files.items()})
    package['fixture_validation']=proof['fixture_validation']
    package['source_policy_realization_map']=read(HERE/'context-pack.json')['original_remaining_policy_map']
    index['retained_catalog_packages']=[package];index['retained_catalog_candidate_theorems']=9
    index['total_distinct_new_candidate_theorems']=1947
    seq['candidate_fragment_theorems']=1947;seq['candidate_retained_catalog_packages']=1
    progress.update(candidate_fragment_theorems=1947,retained_catalog_candidate_theorems=9,candidate_retained_catalog_packages=1)
    progress.update({'K02_retained_catalog_'+key:binding(HERE/name) for key,name in files.items()})
    save(N/'formal-preparation-index.json',index);save(N/'sequential-review.json',seq)
    changed={str((N/name).relative_to(ROOT)) for name in ['formal-preparation-index.json','sequential-review.json']}
    for value in progress.values():
        if isinstance(value,dict) and value.get('path') in changed: value.update(binding(ROOT/value['path']))
    progress_path=H/'execution/PROGRESS.md';text=progress_path.read_text()
    old='making 1938 distinct verified candidate declarations in total.'
    assert text.count(old)==1
    text=text.replace(old,'and retained certified catalogs add 9, making 1947 distinct verified candidate declarations in total.')
    text+='\n\nRetained certified catalogs\n\nK02-retained-catalogs keeps the five checked relation captures and all three decoded\ncatalogs in internal state through selected-profile and full nested checking. The\nnew full entrypoint eliminates catalog reparsing and has the same complete public\nsuccesses and refusals as its predecessor for every input. Independent full meaning\nand the conditional original interpretation with eighteen policy premises remain.\n\nNine general declarations pass eight fresh new-module compile/replay calls and\neighteen runtime observations per phase, including twelve complete result equality\ncomparisons. Exact matching-phase outputs of 138 prior modules are reused, without\nrebuilding or modifying registered predecessors. Same-kernel replay is not\nindependent checking. Operational speed and retained-state memory are unmeasured.\n\nActual source/root/World/selection providers, approved kind-specific payloads, all\nnon-parser policies, mandatory consumers, remaining relation/extension integration,\nwhole-theory obligations, independent checking, measured limits and actual final\nassessment remain required. All 263 inherited obligations remain open; 90 original\ndischarges retain scope. K00–K03 meanings are accepted; K04/global reviews remain\npending. Only N00 is accepted and the full twenty-task plan remains active.\n'
    save(H/'execution/plan.json',plan);driver.write_text(source);progress_path.write_text(text)
    print('Registered 9 retained-catalog declarations; 1947 total; zero inherited discharges.')
if __name__=='__main__':run()
