"""Register fixed-kind complete record proofs; retain every integration gap."""
from pathlib import Path
import hashlib, json

HERE = Path(__file__).resolve().parent
N, H, ROOT = HERE.parents[1], HERE.parents[3], HERE.parents[9]
def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
def read(path): return json.loads(path.read_text())
def save(path, value): path.write_text(json.dumps(value, indent=2)+'\n')

AUDIT_BLOCK = '''        if package.get('complete_fixed_kind_records_exact'):
            assert proof['new_general_declarations']==12 and proof['new_worked_control_declarations']==0
            assert len(proof['records'])==8 and len(proof['reused_dependencies'])==284
            assert proof['runtime_composed_cases']==313 and proof['schema_comparison_cases']==296
            assert proof['profile_count']==7 and proof['record_type_count']==14
            assert proof['complete_record_field_count']==150 and proof['active_assertion_nodes']==204
            for flag in ['complete_fixed_kind_record_meanings_proved','exact_pinned_body_schema_references_retained',
                         'all_original_fields_represented','original_revision_occurrences_preserved',
                         'whole_typed_value_array_uniqueness','all_active_schema_assertions_audited',
                         'heterogeneous_typed_body_family_present']:
                assert proof[flag] is True
            for flag in ['catalog_wide_dispatcher_proved','generic_schema_compiler_correspondence_proved',
                         'python_lean_general_correspondence_proved','general_body_reconstruction_proved',
                         'approved_kind_specific_payload_decoders_realized','all_original_source_policy_providers_realized',
                         'local_dependency_rebuild','real_authoritative_snapshot_provider',
                         'live_consumer_integration','integrated_into_full_entrypoint','N03_API_freeze',
                         'supported_resource_envelope_measured']:
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
            assert len(controls['runtime_cases'])==313 and not controls['independent_checker_run']
            assert not controls['real_authoritative_source_provider']
            runtime=ROOT/proof['sources'][-1]['path']
            assert runtime.stem=='TypedBodyControls'
            assert re.findall(r'^#eval (.*?)(?=\\n#eval |\\nend )',runtime.read_text(),re.M|re.S)==[c['expression'] for c in controls['runtime_cases']]
            for row in proof['records']:
                if Path(row['source']['path']).stem=='TypedBodyControls':
                    raw_lines=iter((ROOT/row['log']['path']).read_text().strip().splitlines())
                    lines=[]
                    for line in raw_lines:
                        if line=='some':
                            continuation=next(raw_lines)
                            assert continuation.startswith('  "')
                            line='some '+continuation.strip()
                        lines.append(line)
                    assert len(lines)==row['runtime_composed_cases']==313
                    for line,case in zip(lines,controls['runtime_cases'],strict=True):
                        if case['expected_kind']=='literal': assert line==case['expected']
                        else:
                            assert case['expected_kind']=='json-body' and line.startswith('some ')
                            assert json.loads(json.loads(line[5:]))==case['expected_body']
            generation=read(ROOT/package['generation_audit']['path'])
            assert generation['result']=='complete-pinned-schema-generation-pass'
            assert generation['profile_count']==7 and generation['record_type_count']==14
            assert generation['complete_record_field_count']==150
            assert len(generation['assertion_trace'])==generation['active_assertion_nodes']==204
            assert generation['generated_source']==proof['sources'][2]
            assert generation['all_declared_properties_required_verified']
            assert not generation['unsupported_assertions_ignored'] and not generation['general_schema_compiler_correspondence_proved']
            fixture=read(ROOT/package['fixture_validation']['path'])
            assert fixture['result']=='complete-typed-body-control-inputs-pass'
            assert fixture['schema_comparison_cases']==296 and fixture['runtime_composed_cases']==313
            assert fixture['full_body_count']==8 and fixture['identity_count']==7
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert api['whole_record_success_iff_independent_meaning_proved']
            assert api['record_type_count']==14 and api['complete_field_count']==150 and api['kind_count']==7
            assert api['exact_goal_identity_field']=='goal_id' and api['other_identity_field']=='node_id'
            for flag in ['caller_approval_boolean_allowed','caller_schema_override_allowed','source_fields_trimmed',
                         'candidate_kind_parameter_is_authority','catalog_wide_dispatcher_proved',
                         'general_schema_compiler_correspondence_proved','python_lean_general_correspondence_proved',
                         'general_body_reconstruction_proved','owned_schema_admission_proved',
                         'source_kind_profile_binding_proved','integrated_into_full_entrypoint','N03_API_freeze']:
                assert api[flag] is False
            matrix=read(ROOT/package['refinement_matrix']['path'])
            assert set(matrix['theorem_targets'])==set(proof['new_declarations'])
            assert not matrix['whole_original_source_interpretation'] and not matrix['catalog_wide_dispatcher_proved']
            policies=read(ROOT/package['remaining_policy_map']['path'])
            assert policies['remaining_slot_count']==18
            assert all(r['status']=='provider-realization-incomplete' and not r['inherited_discharge'] for r in policies['rows'])
            completion=read(ROOT/package['component_completion_audit']['path'])
            assert completion['result']=='component-complete-with-explicit-integration-gaps'
            assert completion['new_general_theorems']==12 and completion['inherited_discharges']==0
            assert not completion['N01_accepted']
'''

def run():
    proof, audit = read(HERE/'verification.json'), read(HERE/'import-resolution-audit.json')
    assert proof['result']=='candidate-fragment-pass' and proof['new_declaration_count']==12
    assert len(proof['records'])==audit['resolved_source_phase_pairs']==8
    assert len(proof['reused_dependencies'])==284 and proof['runtime_composed_cases']==313
    assert audit['verification']==binding(HERE/'verification.json')
    index,seq,plan=read(N/'formal-preparation-index.json'),read(N/'sequential-review.json'),read(H/'execution/plan.json')
    progress=next(t for t in plan['tasks'] if t['id']=='N01')['progress']
    assert index['total_distinct_new_candidate_theorems']==seq['candidate_fragment_theorems']==progress['candidate_fragment_theorems']==1947
    assert not index.get('typed_payload_packages')
    assert seq['current_unit']=='K04' and seq['accepted_meaning_count']==4
    assert index['inherited_discharges']==seq['new_inherited_discharges']==progress['inherited_discharges']==0
    files={'verification':'verification.json','import_resolution_audit':'import-resolution-audit.json',
           'candidate_api_contract':'candidate-api-contract.json','model_review':'MODEL-REVIEW.md',
           'refinement_matrix':'refinement-matrix.json','next_implementation_plan':'NEXT-IMPLEMENTATION.md',
           'independent_formalization':'FORMALIZATION.md','control_index':'control-index.json',
           'context_pack':'context-pack.json','generation_audit':'generation-audit.json',
           'fixture_validation':'fixture-validation.json','component_completion_audit':'component-completion-audit.json'}
    driver=N/'check_current_review.py'; source=driver.read_text()
    marker="index.get('retained_catalog_packages', [])):"
    end="    for preparation in index.get('payload_provider_preparations', []):"
    assert source.count(marker)==source.count(end)==1
    source=source.replace(marker,"index.get('retained_catalog_packages', []) +\n                    index.get('typed_payload_packages', [])):")
    source=source.replace(end,AUDIT_BLOCK+end)
    compile(source,str(driver),'exec')
    completion={'task':'N01','unit':HERE.name,'result':'component-complete-with-explicit-integration-gaps',
                'verification':binding(HERE/'verification.json'),'review':binding(HERE/'MODEL-REVIEW.md'),
                'new_general_theorems':12,'inherited_discharges':0,'N01_accepted':False,'authority_effect':'none',
                'requirements':[{'id':'complete-fixed-kind-record-denotations','status':'proved'},
                                {'id':'nullable-strings-constrained-arrays-and-objects','status':'proved'},
                                {'id':'exact-original-schema-generation','status':'audited-not-generally-proved'},
                                {'id':'catalog-wide-dispatcher-and-provenance-binding','status':'incomplete'},
                                {'id':'general-body-reconstruction-and-source-correspondence','status':'incomplete'},
                                {'id':'owned-admission-and-eighteen-source-policy-providers','status':'incomplete'},
                                {'id':'full-entrypoint-mandatory-consumers-and-independent-checking','status':'incomplete'}]}
    save(HERE/'component-completion-audit.json',completion)
    package={'unit':HERE.name,'kind':'relation.addresses-intent','theorems':12,'general_declarations':12,
             'worked_control_declarations':0,'complete_fixed_kind_records_exact':True,
             'complete_source_refinement':False,'inherited_discharges':0}
    package.update({k:binding(HERE/v) for k,v in files.items()})
    package['remaining_policy_map']=read(HERE/'context-pack.json')['remaining_policy_map']
    index['typed_payload_packages']=[package];index['typed_payload_candidate_theorems']=12
    index['total_distinct_new_candidate_theorems']=1959
    seq.update(candidate_fragment_theorems=1959,candidate_typed_payload_packages=1)
    progress.update(candidate_fragment_theorems=1959,candidate_typed_payload_packages=1,typed_payload_candidate_theorems=12)
    progress.update({'K02_typed_payload_'+k:binding(HERE/v) for k,v in files.items()})
    save(N/'formal-preparation-index.json',index);save(N/'sequential-review.json',seq)
    changed={str((N/v).relative_to(ROOT)) for v in ['formal-preparation-index.json','sequential-review.json']}
    for value in progress.values():
        if isinstance(value,dict) and value.get('path') in changed: value.update(binding(ROOT/value['path']))
    progress_path=H/'execution/PROGRESS.md'; text=progress_path.read_text()
    old='making 1947 distinct verified candidate declarations in total.'
    assert text.count(old)==1
    text=text.replace(old,'and complete fixed-kind payload decoders add 12, making 1959 distinct verified candidate declarations in total.')
    text+='\n\nComplete fixed-kind payload bodies\n\nSeven original candidate body profiles now have complete typed record decoders\nwith success iff independent record meaning. Fourteen record types retain all\n150 root and nested fields. The exact generation audit covers 204 active assertion\nnodes; it is not a general schema-compiler correspondence proof. Repeated history\nrecords remain permitted where the source schema permits them. Nullable strings,\nconditional Intent evidence and whole-value uniqueness retain their exact scope.\n\nTwelve general declarations pass eight fresh new-module compile/replay calls and\n313 runtime observations per phase, including 296 schema comparisons, eight\nwhole-body reconstructions, seven identities and two generic uniqueness controls.\nExact matching-phase outputs of 142 prior modules are reused. Same-kernel replay\nis not independent checking. Fixture agreement is not general correspondence.\n\nCatalog-wide dispatch, source-kind/profile provenance, general reconstruction and\nraw/schema/Python/Lean correspondence, actual owned admission and all eighteen\nsource-policy providers, full-entrypoint and mandatory-consumer integration remain.\nAll 263 inherited obligations remain open; 90 original discharges retain scope.\nK00–K03 meanings are accepted, K04/global assessments remain pending, and only N00\nis accepted in the active twenty-task plan.\n'
    save(H/'execution/plan.json',plan);driver.write_text(source);progress_path.write_text(text)
    print('Registered 12 fixed-kind record declarations; 1959 total; zero inherited discharges.')

if __name__=='__main__': run()
