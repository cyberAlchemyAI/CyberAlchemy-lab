"""Register checked complete nested source provenance, retaining all closure boundaries."""
from pathlib import Path
import hashlib, json
HERE = Path(__file__).resolve().parent
N, H, ROOT = HERE.parents[1], HERE.parents[3], HERE.parents[9]
def binding(path): return {'path':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def read(path): return json.loads(path.read_text())
def save(path,value): path.write_text(json.dumps(value,indent=2)+'\n')
def run():
    proof, audit = read(HERE/'verification.json'),read(HERE/'import-resolution-audit.json')
    assert proof['result']=='candidate-fragment-pass' and proof['new_declaration_count']==20
    assert len(proof['records'])==audit['resolved_source_phase_pairs']==10
    assert len(proof['reused_dependencies'])==266 and proof['runtime_composed_cases']==21
    assert audit['verification']==binding(HERE/'verification.json')
    assert proof['selected_digest_profile_provenance_bound'] and proof['profile_frame_is_relation_world_frame']
    assert proof['full_budget_before_any_capture_processing'] and proof['current_api_capture_manifest_complete']
    index,seq,plan=read(N/'formal-preparation-index.json'),read(N/'sequential-review.json'),read(H/'execution/plan.json')
    progress=next(t for t in plan['tasks'] if t['id']=='N01')['progress']
    assert index['total_distinct_new_candidate_theorems']==seq['candidate_fragment_theorems']==progress['candidate_fragment_theorems']==1918
    assert not index.get('nested_provenance_packages')
    assert seq['current_unit']=='K04' and seq['accepted_meaning_count']==4
    assert index['inherited_discharges']==seq['new_inherited_discharges']==progress['inherited_discharges']==0
    files={'verification':'verification.json','import_resolution_audit':'import-resolution-audit.json',
           'candidate_api_contract':'candidate-api-contract.json','model_review':'MODEL-REVIEW.md',
           'refinement_matrix':'refinement-matrix.json','next_implementation_plan':'NEXT-IMPLEMENTATION.md',
           'independent_formalization':'FORMALIZATION.md','control_index':'control-index.json',
           'context_pack':'context-pack.json','fixture_validation':'fixture-validation.json',
           'component_completion_audit':'component-completion-audit.json', 'source_policy_realization_map':'source-policy-realization-map.json'}
    driver=N/'check_current_review.py';source=driver.read_text()
    marker="index.get('selected_relation_packages', [])):"
    end='    assert len(declarations) == len(set(declarations))'
    assert source.count(marker)==source.count(end)==1
    block='''        if package.get('nested_provenance_entry_exact'):
            assert proof['original_byte_pipeline_exact'] and proof['eighteen_remaining_source_policies_preserved']
            assert proof['all_supplied_captures_guarded'] and proof['new_general_declarations']==20
            assert proof['new_worked_control_declarations']==0 and len(proof['records'])==10
            assert proof['runtime_composed_cases']==21 and len(proof['reused_dependencies'])==266
            assert proof['catalog_to_typed_context_adapters'] and proof['complete_context_snapshot_field_coverage']
            assert proof['selected_digest_profile_provenance_bound'] and proof['profile_frame_is_relation_world_frame']
            assert proof['current_api_capture_manifest_complete'] and proof['full_budget_before_any_capture_processing']
            assert proof['nested_full_body_digest_alignment_proved'] and proof['ordered_complete_nested_manifest_enforced']
            assert proof['all_original_nested_artifact_occurrences_checked']
            assert proof['preflight_order']=='full parent+nested budget; original selected parent; checked catalog reparse; exact nested manifest; all nested preflights; nested document decoders'
            for flag in ['nested_artifact_body_content_refinement_proved','complete_catalog_manifest_enforced',
                         'owned_selected_profile_without_root_premise','local_dependency_rebuild',
                         'supported_resource_envelope_measured','real_authoritative_snapshot_provider',
                         'live_consumer_integration','N03_API_freeze','approved_kind_specific_payload_decoders_realized','all_original_source_policy_providers_realized','catalog_reparse_eliminated']:
                assert proof[flag] is False
            pool={}
            for prior_ref,audit_ref in zip(proof['prior_verifications'],proof['prior_import_audits'],strict=True):
                prior=read(ROOT/prior_ref['path']);prior_audit=read(ROOT/audit_ref['path'])
                assert prior['result']=='candidate-fragment-pass'
                assert prior_audit['verification']==prior_ref and prior_audit['result']=='import-resolution-audit-pass'
                for row in prior['records']+prior.get('reused_dependencies',[]):
                    output=row.get('olean',row.get('reused_output'))
                    key=(row['phase'],Path(output['path']).name)
                    item=(row['source']['path'],row['source']['sha256'],output['sha256'])
                    if key in pool:assert pool[key]==item
                    else:pool[key]=item
            actual={}
            for row in proof['reused_dependencies']:
                key=(row['phase'],Path(row['reused_output']['path']).name)
                assert key not in actual
                actual[key]=(row['source']['path'],row['source']['sha256'],row['reused_output']['sha256'])
                assert row['reused_output']['sha256']==row['prior_output']['sha256']
                assert (ROOT/row['reused_output']['path']).parent==package_dir/row['phase']
            assert actual==pool
            audit=read(ROOT/package['import_resolution_audit']['path'])
            assert audit['verification']==package['verification'] and audit['resolved_source_phase_pairs']==10
            controls=read(ROOT/package['control_index']['path'])
            assert len(controls['runtime_cases'])==21 and controls['captured_context_is_synthetic']
            assert not controls['real_authoritative_snapshot_provider'] and not controls['fixture_serializer_proved']
            runtime=ROOT/proof['sources'][-1]['path']
            assert runtime.stem=='NestedControls'
            assert re.findall(r'^#eval (.*?)(?=\\n#eval |\\nend )',runtime.read_text(),re.M|re.S)==[case['expression'] for case in controls['runtime_cases']]
            for row in proof['records']:
                if Path(row['source']['path']).stem=='NestedControls':
                    assert row['runtime_composed_cases']==21
                    assert (ROOT/row['log']['path']).read_text().strip().splitlines()==[case['expected'] for case in controls['runtime_cases']]
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert not api['caller_AST_allowed'] and not api['caller_typed_catalogs_allowed']
            assert not api['caller_relation_digest_profile_allowed'] and not api['caller_separate_profile_frame_allowed']
            assert api['original_source_semantics_preserved'] and api['all_original_nested_artifact_occurrences_checked']
            assert api['ordered_complete_nested_manifest_enforced'] and api['owned_binding_header_key_kind_frame_review_checked']
            assert not api['caller_expected_nested_catalog_allowed']
            assert api['selected_digest_profile_provenance_bound'] and api['single_frame']=='world.frame'
            assert not api['all_original_source_policy_providers_realized'] and not api['world_and_claim_authenticity_proved']
            matrix=read(ROOT/package['refinement_matrix']['path'])
            assert set(matrix['theorem_targets'])==set(proof['new_declarations']) and not matrix['whole_original_source_interpretation']
            completion=read(ROOT/package['component_completion_audit']['path'])
            assert not completion['N01_accepted'] and completion['inherited_discharges']==0
            fixture=read(ROOT/package['fixture_validation']['path'])
            assert fixture['result']=='concrete-nested-fixture-join-pass' and fixture['fixture_count']==7
            assert fixture['content_literal_count']==27 and fixture['nested_occurrence_count']==20
            assert fixture['complete_original_primary_body_retained'] and fixture['nested_full_body_digest_alignment']
            assert all(row['document_body_digest_match'] for row in fixture['nested_checks'])
            assert fixture['all_frames_match_relation_world'] and fixture['issuance_bytes_and_manifests_exact']
            assert fixture['captured_context_is_synthetic'] and not fixture['fixture_serializer_proved']
            assert not fixture['real_authoritative_snapshot_provider']
            policies=read(ROOT/package['source_policy_realization_map']['path'])
            contract=(ROOT/policies['original_contract']['path']).read_text().split('structure Policies')[1].split('structure PolicyMeaning')[0]
            slots=set(re.findall(r'^  (\\w+) :',contract,re.M))-{'parses'}
            assert slots=={row['slot'] for row in policies['rows']} and len(slots)==policies['remaining_slot_count']==18
            assert all(row['status']=='provider-realization-incomplete' and not row['inherited_discharge'] for row in policies['rows'])
            assert not policies['unconditional_original_source_interpretation_proved']
'''
    source=source.replace(marker,"index.get('selected_relation_packages', []) +\n                    index.get('nested_provenance_packages', [])):").replace(end,block+end)
    compile(source,str(driver),'exec')
    progress_path=H/'execution/PROGRESS.md';text=progress_path.read_text()
    old='making 1918 distinct verified candidate declarations in total.'
    assert text.count(old)==1
    text=text.replace(old,'and complete nested source provenance adds 20, making 1938 distinct verified candidate declarations in total.')
    text+='\n\nComplete nested original source provenance\n\nK02-nested-provenance derives the complete ordered nested manifest from captured\nmetadata/payload/owned contexts and checks exact byte/body/full-digest agreement.\nAll records, roots, duplicates and unused entries remain present. Every supplied\nparent and nested occurrence shares a full budget before any capture-dependent\nprocessing. Complete original formats remain intact; owned BindingRecord header\nkey/kind/body/frame/review fields are checked against their retained entries.\n\nThe exact full entrypoint preserves original selected-profile and relation meanings\nand the ordered nested document meanings. A conditional capstone constructs the\ncomplete original SourceInterpretation using the exact 18 remaining policy premises.\nThose provider premises are explicitly mapped and still unrealized; no authenticity\nis inferred from coherent bytes, schemas, hashes or synthetic grants/reviews.\n\nTwenty general declarations pass ten fresh new-module compile/replay calls, forty\naxiom inspections, ten exact import audits and twenty-one runtime cases per phase.\nSeven source fixtures, twenty-seven literal contents and twenty nested occurrences\nare checked. The 133 unchanged dependencies reuse exact registered corresponding\nphase outputs, not rebuilds. Replay is same-kernel, not independent checking.\n\nCatalog bytes are currently reread after original parent checking; retaining their\ncertified ASTs will remove that extra work before operational resource claims.\nActual kind-specific payload schemas, source/root/World/selection providers, all\nnon-parser policies, mandatory consumers, remaining relation/extension integration,\nwhole-theory obligations, independent checking, measured limits and actual final\nassessment remain required. All 263 inherited obligations remain open; 90 original\ndischarges retain scope. K04/global reviews remain pending. Only N00 is accepted\nand the complete twenty-task, seven-extension plan remains active.\n'
    completion={'task':'N01','unit':'K02-nested-provenance','result':'component-complete-with-explicit-integration-gaps',
                'verification':binding(HERE/'verification.json'),'review':binding(HERE/'MODEL-REVIEW.md'),
                'api':binding(HERE/'candidate-api-contract.json'),'matrix':binding(HERE/'refinement-matrix.json'),
                'fixture_validation':binding(HERE/'fixture-validation.json'), 'next_implementation':binding(HERE/'NEXT-IMPLEMENTATION.md'),
                'requirements':[{'id':'shared-parent-plus-nested-budget','status':'proved'}, {'id':'complete-ordered-nested-manifest','status':'proved'}, {'id':'exact-nested-byte-body-full-digest','status':'proved'},
                                {'id':'checked-selected-profile-original-relation-composition','status':'proved'},
                                {'id':'single-exact-world-frame','status':'proved'},
                                {'id':'actual-root-premise-preserved','status':'proved-conditional'},
                                {'id':'concrete-fixture-byte-body-digest-joins','status':'verified'}, {'id':'original-source-interpretation','status':'proved-conditional-on-exact-remaining-policies'},
                                {'id':'nested-source-provider-world-provenance','status':'incomplete'},
                                {'id':'actual-root-policy-provider','status':'incomplete'},
                                {'id':'complete-original-source-interpretation','status':'incomplete'},
                                {'id':'mandatory-live-consumer','status':'incomplete'},
                                {'id':'independent-checking-and-measured-limits','status':'incomplete'}],
                'N01_accepted':False,'inherited_discharges':0,'authority_effect':'none'}
    save(HERE/'component-completion-audit.json',completion)
    package={'unit':'K02-nested-provenance','kind':'relation.addresses-intent','theorems':20,'general_declarations':20,
             'worked_control_declarations':0,'nested_provenance_entry_exact':True,'complete_source_refinement':False,'inherited_discharges':0}
    package.update({key:binding(HERE/name) for key,name in files.items()})
    index['nested_provenance_packages']=[package];index['nested_provenance_candidate_theorems']=20
    index['total_distinct_new_candidate_theorems']=1938
    seq['candidate_fragment_theorems']=1938;seq['candidate_nested_provenance_packages']=1
    progress.update(candidate_fragment_theorems=1938,nested_provenance_candidate_theorems=20,candidate_nested_provenance_packages=1)
    progress.update({'K02_nested_provenance_'+key:binding(HERE/name) for key,name in files.items()})
    save(N/'formal-preparation-index.json',index);save(N/'sequential-review.json',seq)
    changed={str((N/name).relative_to(ROOT)) for name in ['formal-preparation-index.json','sequential-review.json']}
    for value in progress.values():
        if isinstance(value,dict) and value.get('path') in changed: value.update(binding(ROOT/value['path']))
    save(H/'execution/plan.json',plan);driver.write_text(source);progress_path.write_text(text)
    print('Registered 20 nested-provenance declarations; 1938 total; zero inherited discharges.')
if __name__=='__main__':run()
