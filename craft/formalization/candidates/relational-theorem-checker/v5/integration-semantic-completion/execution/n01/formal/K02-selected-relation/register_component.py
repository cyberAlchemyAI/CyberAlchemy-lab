"""Register checked selected-profile composition, retaining all closure boundaries."""
from pathlib import Path
import hashlib, json
HERE = Path(__file__).resolve().parent
N, H, ROOT = HERE.parents[1], HERE.parents[3], HERE.parents[9]
def binding(path): return {'path':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def read(path): return json.loads(path.read_text())
def save(path,value): path.write_text(json.dumps(value,indent=2)+'\n')
def run():
    proof, audit = read(HERE/'verification.json'),read(HERE/'import-resolution-audit.json')
    assert proof['result']=='candidate-fragment-pass' and proof['new_declaration_count']==10
    assert len(proof['records'])==audit['resolved_source_phase_pairs']==8
    assert len(proof['reused_dependencies'])==258 and proof['runtime_composed_cases']==22
    assert audit['verification']==binding(HERE/'verification.json')
    assert proof['selected_digest_profile_provenance_bound'] and proof['profile_frame_is_relation_world_frame']
    assert proof['full_budget_before_any_capture_processing'] and proof['current_api_capture_manifest_complete']
    index,seq,plan=read(N/'formal-preparation-index.json'),read(N/'sequential-review.json'),read(H/'execution/plan.json')
    progress=next(t for t in plan['tasks'] if t['id']=='N01')['progress']
    assert index['total_distinct_new_candidate_theorems']==seq['candidate_fragment_theorems']==progress['candidate_fragment_theorems']==1908
    assert not index.get('selected_relation_packages')
    assert seq['current_unit']=='K04' and seq['accepted_meaning_count']==4
    assert index['inherited_discharges']==seq['new_inherited_discharges']==progress['inherited_discharges']==0
    files={'verification':'verification.json','import_resolution_audit':'import-resolution-audit.json',
           'candidate_api_contract':'candidate-api-contract.json','model_review':'MODEL-REVIEW.md',
           'refinement_matrix':'refinement-matrix.json','next_implementation_plan':'NEXT-IMPLEMENTATION.md',
           'independent_formalization':'FORMALIZATION.md','control_index':'control-index.json',
           'context_pack':'context-pack.json','fixture_validation':'fixture-validation.json',
           'component_completion_audit':'component-completion-audit.json'}
    driver=N/'check_current_review.py';source=driver.read_text()
    marker="index.get('catalog_snapshot_packages', [])):"
    end='    assert len(declarations) == len(set(declarations))'
    assert source.count(marker)==source.count(end)==1
    block='''        if package.get('selected_relation_entry_exact'):
            assert proof['original_byte_pipeline_exact'] and proof['eighteen_remaining_source_policies_preserved']
            assert proof['all_supplied_captures_guarded'] and proof['new_general_declarations']==10
            assert proof['new_worked_control_declarations']==0 and len(proof['records'])==8
            assert proof['runtime_composed_cases']==22 and len(proof['reused_dependencies'])==258
            assert proof['catalog_to_typed_context_adapters'] and proof['complete_context_snapshot_field_coverage']
            assert proof['selected_digest_profile_provenance_bound'] and proof['profile_frame_is_relation_world_frame']
            assert proof['current_api_capture_manifest_complete'] and proof['full_budget_before_any_capture_processing']
            assert proof['preflight_order']=='bootstrap profile captures before profile decoding; selected-profile relation captures before relation/catalog decoding'
            for flag in ['nested_artifact_body_content_refinement_proved','complete_catalog_manifest_enforced',
                         'owned_selected_profile_without_root_premise','local_dependency_rebuild',
                         'supported_resource_envelope_measured','real_authoritative_snapshot_provider',
                         'live_consumer_integration','N03_API_freeze']:
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
            assert audit['verification']==package['verification'] and audit['resolved_source_phase_pairs']==8
            controls=read(ROOT/package['control_index']['path'])
            assert len(controls['runtime_cases'])==22 and controls['captured_context_is_synthetic']
            assert not controls['real_authoritative_snapshot_provider'] and not controls['fixture_serializer_proved']
            runtime=ROOT/proof['sources'][-1]['path']
            assert runtime.stem=='SelectedRelationControls'
            assert re.findall(r'^#eval (.*?)(?=\\n#eval |\\nend )',runtime.read_text(),re.M|re.S)==[case['expression'] for case in controls['runtime_cases']]
            for row in proof['records']:
                if Path(row['source']['path']).stem=='SelectedRelationControls':
                    assert row['runtime_composed_cases']==22
                    assert (ROOT/row['log']['path']).read_text().strip().splitlines()==[case['expected'] for case in controls['runtime_cases']]
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert not api['caller_AST_allowed'] and not api['caller_typed_catalogs_allowed']
            assert not api['caller_relation_digest_profile_allowed'] and not api['caller_separate_profile_frame_allowed']
            assert api['original_source_semantics_preserved'] and api['complete_context_snapshot_field_coverage']
            assert api['selected_digest_profile_provenance_bound'] and api['single_frame']=='world.frame'
            assert not api['nested_artifact_body_content_refinement_proved'] and not api['world_and_claim_authenticity_proved']
            matrix=read(ROOT/package['refinement_matrix']['path'])
            assert set(matrix['theorem_targets'])==set(proof['new_declarations']) and not matrix['whole_original_source_interpretation']
            completion=read(ROOT/package['component_completion_audit']['path'])
            assert not completion['N01_accepted'] and completion['inherited_discharges']==0
            fixture=read(ROOT/package['fixture_validation']['path'])
            assert fixture['result']=='concrete-fixture-byte-join-pass' and fixture['check_count']==4
            assert fixture['all_frames_match_relation_world'] and fixture['issuance_bytes_and_manifests_exact']
            assert fixture['captured_context_is_synthetic'] and not fixture['fixture_serializer_proved']
            assert not fixture['real_authoritative_snapshot_provider']
'''
    source=source.replace(marker,"index.get('catalog_snapshot_packages', []) +\n                    index.get('selected_relation_packages', [])):").replace(end,block+end)
    compile(source,str(driver),'exec')
    progress_path=H/'execution/PROGRESS.md';text=progress_path.read_text()
    old='making 1908 distinct verified candidate declarations in total.'
    assert text.count(old)==1
    text=text.replace(old,'and selected-profile original relation composition adds 10, making 1918 distinct verified candidate declarations in total.')
    text+='''

Selected-profile original relation composition

K02-selected-relation checks one full budget over authority, every declaration and
selection occurrence, source, qualifiers and all three complete context snapshots.
It derives the relation digest profile from checked profile evidence under the exact
original World frame. The new composite entrypoint has no separate relation profile,
profile frame, caller AST or typed catalog arguments. Its exact theorem preserves
the independent original captured-context relation meaning, selected-profile evidence
meaning and shared actual-byte/count limits.

Guard ordering is profile preflight before profile decoding, then all five relation
preflights under the derived selected profile before relation/catalog decoding. It
does not assert all global preflights precede profile decoding. Owned selection still
requires the actual authoritative snapshot premise; structural success does not
provide a real owner/provider. Ten general declarations pass eight fresh new-module
compile/replay calls, twenty axiom inspections, eight import audits and twenty-two
runtime controls per phase. Four concrete fixture byte/source/frame joins pass.
The 129 unchanged dependency modules are reused from exact corresponding registered
phase outputs, not rebuilt. Same-kernel replay is not independent checking.

The current API capture manifest is complete for its raw inputs. Future nested source,
provider and World adapters must extend it. Full nested artifact provenance, all 18
non-parser source-policy realizations, authentic World/claim, mandatory consumers,
whole-theory obligations, independent checking, measured limits and all seven
extension integrations remain necessary. All 263 inherited IDs remain open and 90
original discharges retain scope. K04/global reviews remain pending; only N00 is
accepted. The complete plan remains active.
'''
    completion={'task':'N01','unit':'K02-selected-relation','result':'component-complete-with-explicit-integration-gaps',
                'verification':binding(HERE/'verification.json'),'review':binding(HERE/'MODEL-REVIEW.md'),
                'api':binding(HERE/'candidate-api-contract.json'),'matrix':binding(HERE/'refinement-matrix.json'),
                'fixture_validation':binding(HERE/'fixture-validation.json'), 'next_implementation':binding(HERE/'NEXT-IMPLEMENTATION.md'),
                'requirements':[{'id':'shared-full-actual-byte-budget','status':'proved'},
                                {'id':'checked-selected-profile-original-relation-composition','status':'proved'},
                                {'id':'single-exact-world-frame','status':'proved'},
                                {'id':'actual-root-premise-preserved','status':'proved-conditional'},
                                {'id':'concrete-fixture-byte-joins','status':'verified'},
                                {'id':'nested-source-provider-world-provenance','status':'incomplete'},
                                {'id':'actual-root-policy-provider','status':'incomplete'},
                                {'id':'complete-original-source-interpretation','status':'incomplete'},
                                {'id':'mandatory-live-consumer','status':'incomplete'},
                                {'id':'independent-checking-and-measured-limits','status':'incomplete'}],
                'N01_accepted':False,'inherited_discharges':0,'authority_effect':'none'}
    save(HERE/'component-completion-audit.json',completion)
    package={'unit':'K02-selected-relation','kind':'relation.addresses-intent','theorems':10,'general_declarations':10,
             'worked_control_declarations':0,'selected_relation_entry_exact':True,'complete_source_refinement':False,'inherited_discharges':0}
    package.update({key:binding(HERE/name) for key,name in files.items()})
    index['selected_relation_packages']=[package];index['selected_relation_candidate_theorems']=10
    index['total_distinct_new_candidate_theorems']=1918
    seq['candidate_fragment_theorems']=1918;seq['candidate_selected_relation_packages']=1
    progress.update(candidate_fragment_theorems=1918,selected_relation_candidate_theorems=10,candidate_selected_relation_packages=1)
    progress.update({'K02_selected_relation_'+key:binding(HERE/name) for key,name in files.items()})
    save(N/'formal-preparation-index.json',index);save(N/'sequential-review.json',seq)
    changed={str((N/name).relative_to(ROOT)) for name in ['formal-preparation-index.json','sequential-review.json']}
    for value in progress.values():
        if isinstance(value,dict) and value.get('path') in changed: value.update(binding(ROOT/value['path']))
    save(H/'execution/plan.json',plan);driver.write_text(source);progress_path.write_text(text)
    print('Registered 10 selected-relation declarations; 1918 total; zero inherited discharges.')
if __name__=='__main__':run()
