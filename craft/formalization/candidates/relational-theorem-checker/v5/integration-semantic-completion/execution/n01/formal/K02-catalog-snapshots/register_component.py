"""Register exact complete context snapshot integration without claiming full source closure."""
from pathlib import Path
import hashlib, json

HERE = Path(__file__).resolve().parent
N, H, ROOT = HERE.parents[1], HERE.parents[3], HERE.parents[9]

def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

def read(path):
    return json.loads(path.read_text())

def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')

def run():
    proof, audit = read(HERE / 'verification.json'), read(HERE / 'import-resolution-audit.json')
    assert proof['result'] == 'candidate-fragment-pass' and proof['new_declaration_count'] == 22
    assert len(proof['records']) == audit['resolved_source_phase_pairs'] == 8
    assert len(proof['reused_dependencies']) == 250 and proof['runtime_composed_cases'] == 17
    assert audit['verification'] == binding(HERE / 'verification.json')
    index, seq, plan = read(N / 'formal-preparation-index.json'), read(N / 'sequential-review.json'), read(H / 'execution/plan.json')
    progress = next(task for task in plan['tasks'] if task['id'] == 'N01')['progress']
    assert index['total_distinct_new_candidate_theorems'] == seq['candidate_fragment_theorems'] == progress['candidate_fragment_theorems'] == 1886
    assert not index.get('catalog_snapshot_packages')
    assert seq['current_unit'] == 'K04' and seq['accepted_meaning_count'] == 4
    assert index['inherited_discharges'] == seq['new_inherited_discharges'] == progress['inherited_discharges'] == 0
    files = {'verification': 'verification.json', 'import_resolution_audit': 'import-resolution-audit.json',
             'candidate_api_contract': 'candidate-api-contract.json', 'model_review': 'MODEL-REVIEW.md',
             'refinement_matrix': 'refinement-matrix.json', 'next_implementation_plan': 'NEXT-IMPLEMENTATION.md',
             'independent_formalization': 'FORMALIZATION.md', 'control_index': 'control-index.json',
             'context_pack': 'context-pack.json', 'component_completion_audit': 'component-completion-audit.json', 'schema_validation': 'schema-validation.json', 'schema': 'catalog-snapshot.schema.json'}
    package = {'unit': 'K02-catalog-snapshots', 'kind': 'relation.addresses-intent',
               'theorems': 22, 'general_declarations': 22, 'worked_control_declarations': 0,
               'catalog_snapshot_entry_exact': True, 'complete_source_refinement': False, 'inherited_discharges': 0}
    for key, name in files.items():
        package[key] = binding(HERE / name)
    driver = N / 'check_current_review.py'
    source = driver.read_text()
    marker = "index.get('original_byte_pipeline_packages', [])):"
    end = '    assert len(declarations) == len(set(declarations))'
    assert source.count(marker) == source.count(end) == 1
    block = '''        if package.get('catalog_snapshot_entry_exact'):
            assert proof['original_byte_pipeline_exact'] and proof['eighteen_remaining_source_policies_preserved']
            assert proof['all_supplied_captures_guarded'] and proof['new_general_declarations']==22
            assert proof['new_worked_control_declarations']==0 and len(proof['records'])==8
            assert proof['runtime_composed_cases']==17 and len(proof['reused_dependencies'])==250
            assert proof['catalog_to_typed_context_adapters'] and proof['complete_context_snapshot_field_coverage']
            assert not proof['nested_artifact_body_content_refinement_proved']
            for flag in ['complete_catalog_manifest_enforced',
                         'selected_digest_profile_provenance_bound','local_dependency_rebuild',
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
            assert len(controls['runtime_cases'])==17 and controls['captured_context_is_synthetic']
            assert not controls['real_authoritative_snapshot_provider'] and not controls['fixture_serializer_proved']
            runtime=ROOT/proof['sources'][-1]['path']
            assert runtime.stem=='CatalogRuntimeControls'
            assert re.findall(r'^#eval (.*?)(?=\\n#eval |\\nend )',runtime.read_text(),re.M|re.S)==[case['expression'] for case in controls['runtime_cases']]
            for row in proof['records']:
                if Path(row['source']['path']).stem=='CatalogRuntimeControls':
                    assert row['runtime_composed_cases']==17
                    assert (ROOT/row['log']['path']).read_text().strip().splitlines()==[case['expected'] for case in controls['runtime_cases']]
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert not api['caller_AST_allowed'] and not api['caller_typed_catalogs_allowed']
            assert api['original_source_semantics_preserved'] and api['complete_context_snapshot_field_coverage']
            assert not api['selected_digest_profile_provenance_bound'] and not api['nested_artifact_body_content_refinement_proved']
            matrix=read(ROOT/package['refinement_matrix']['path'])
            assert set(matrix['theorem_targets'])==set(proof['new_declarations']) and not matrix['whole_original_source_interpretation']
            completion=read(ROOT/package['component_completion_audit']['path'])
            assert not completion['N01_accepted'] and completion['inherited_discharges']==0
            schema_report=read(ROOT/package['schema_validation']['path'])
            assert schema_report['result']=='decoded-shape-controls-pass' and schema_report['check_count']==33
            assert schema_report['original_full_record_and_bytes_retained']
            assert not schema_report['raw_schema_equivalence_proved'] and not schema_report['authentic_snapshot_proved']
            assert all(row['expected_valid']==row['observed_valid'] for row in schema_report['checks'])
'''
    source = source.replace(marker, "index.get('original_byte_pipeline_packages', []) +\n                    index.get('catalog_snapshot_packages', [])):").replace(end, block + end)
    compile(source, str(driver), 'exec')
    out = H / 'execution/PROGRESS.md'
    text = out.read_text()
    old = 'making 1886 distinct verified candidate declarations in total.'
    assert text.count(old) == 1
    text = text.replace(old, 'and complete original context snapshot integration adds 22, making 1908 distinct verified candidate declarations in total.')
    text += '''

Complete original catalog snapshots

K02-catalog-snapshots derives all three original typed catalog contexts from exact
checked snapshot bytes; the entrypoint accepts no separate typed catalogs or ASTs.
Every metadata receipt/binding, payload record/binding/approval and owned resolution/
role record/root is retained, including duplicates, aliases and unused entries. All
five captures share one budget/preflight boundary before typed decoding. Its main
entrypoint is proved exactly equivalent to independent full snapshot meanings plus
the original guarded source-byte relation meaning.

Twenty-two general declarations pass eight fresh new-module compile/replay calls,
forty-four axiom inspections, eight exact import audits and seventeen runtime controls
per phase. Thirty-three decoded-shape checks pass and exact original source bytes/
body are retained. The 125 unchanged dependency modules were not rebuilt; their
registered corresponding phase outputs were verified and reused. Same-kernel replay
is not independent checking and build time is not measured operational limits.

The fixed manifest is complete for the five current context snapshot inputs. A
snapshot's integrity does not authenticate its statements, verify every nested
artifact hash or prove body/content provenance. Complete future profile/provider/
world capture composition, owned selected-profile binding, genuine source-policy
premises, mandatory consumers, whole-theory obligations, independent checking,
measured limits, all seven extensions and final actual assessment remain required.
All 263 inherited IDs remain open; 90 original discharges retain scope. K04/global
reviews remain pending. Only N00 is accepted; the complete plan remains active.
'''
    index['catalog_snapshot_packages'] = [package]
    index['catalog_snapshot_candidate_theorems'] = 22
    index['total_distinct_new_candidate_theorems'] = 1908
    seq['candidate_fragment_theorems'] = 1908
    seq['candidate_catalog_snapshot_packages'] = 1
    progress['candidate_fragment_theorems'] = 1908
    progress['catalog_snapshot_candidate_theorems'] = 22
    progress['candidate_catalog_snapshot_packages'] = 1
    for key, name in files.items():
        progress['K02_catalog_snapshot_' + key] = binding(HERE / name)
    save(N / 'formal-preparation-index.json', index)
    save(N / 'sequential-review.json', seq)
    changed = {str((N / name).relative_to(ROOT)) for name in ['formal-preparation-index.json', 'sequential-review.json']}
    for value in progress.values():
        if isinstance(value, dict) and value.get('path') in changed:
            value.update(binding(ROOT / value['path']))
    save(H / 'execution/plan.json', plan)
    driver.write_text(source)
    out.write_text(text)
    print('Registered 22 original byte-pipeline declarations; 1908 total; zero inherited discharges.')

if __name__ == '__main__':
    run()
