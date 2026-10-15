"""Register exact original-byte integration without claiming full source closure."""
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
    assert proof['result'] == 'candidate-fragment-pass' and proof['new_declaration_count'] == 14
    assert len(proof['records']) == audit['resolved_source_phase_pairs'] == 8
    assert len(proof['reused_dependencies']) == 242 and proof['runtime_composed_cases'] == 12
    assert audit['verification'] == binding(HERE / 'verification.json')
    index, seq, plan = read(N / 'formal-preparation-index.json'), read(N / 'sequential-review.json'), read(H / 'execution/plan.json')
    progress = next(task for task in plan['tasks'] if task['id'] == 'N01')['progress']
    assert index['total_distinct_new_candidate_theorems'] == seq['candidate_fragment_theorems'] == progress['candidate_fragment_theorems'] == 1872
    assert not index.get('original_byte_pipeline_packages')
    assert seq['current_unit'] == 'K04' and seq['accepted_meaning_count'] == 4
    assert index['inherited_discharges'] == seq['new_inherited_discharges'] == progress['inherited_discharges'] == 0
    files = {'verification': 'verification.json', 'import_resolution_audit': 'import-resolution-audit.json',
             'candidate_api_contract': 'candidate-api-contract.json', 'model_review': 'MODEL-REVIEW.md',
             'refinement_matrix': 'refinement-matrix.json', 'next_implementation_plan': 'NEXT-IMPLEMENTATION.md',
             'independent_formalization': 'FORMALIZATION.md', 'control_index': 'control-index.json',
             'context_pack': 'context-pack.json', 'component_completion_audit': 'component-completion-audit.json'}
    package = {'unit': 'K02-original-byte-pipeline', 'kind': 'relation.addresses-intent',
               'theorems': 14, 'general_declarations': 14, 'worked_control_declarations': 0,
               'original_byte_pipeline_exact': True, 'complete_source_refinement': False, 'inherited_discharges': 0}
    for key, name in files.items():
        package[key] = binding(HERE / name)
    driver = N / 'check_current_review.py'
    source = driver.read_text()
    marker = "index.get('preflight_reuse_packages', [])):"
    end = '    assert len(declarations) == len(set(declarations))'
    assert source.count(marker) == source.count(end) == 1
    block = '''        if package.get('original_byte_pipeline_exact'):
            assert proof['original_byte_pipeline_exact'] and proof['eighteen_remaining_source_policies_preserved']
            assert proof['all_supplied_captures_guarded'] and proof['new_general_declarations']==14
            assert proof['new_worked_control_declarations']==0 and len(proof['records'])==8
            assert proof['runtime_composed_cases']==12 and len(proof['reused_dependencies'])==242
            for flag in ['catalog_to_typed_context_adapters','complete_catalog_manifest_enforced',
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
            assert len(controls['runtime_cases'])==12 and controls['captured_context_is_synthetic']
            assert not controls['real_authoritative_snapshot_provider'] and not controls['catalog_to_typed_context_adapters']
            runtime=ROOT/proof['sources'][-1]['path']
            assert runtime.stem=='OriginalByteRuntimeControls'
            assert re.findall(r'^#eval (.*?)(?=\\n#eval |\\nend )',runtime.read_text(),re.M|re.S)==[case['expression'] for case in controls['runtime_cases']]
            for row in proof['records']:
                if Path(row['source']['path']).stem=='OriginalByteRuntimeControls':
                    assert row['runtime_composed_cases']==12
                    assert (ROOT/row['log']['path']).read_text().strip().splitlines()==[case['expected'] for case in controls['runtime_cases']]
            api=read(ROOT/package['candidate_api_contract']['path'])
            assert not api['caller_AST_allowed'] and api['original_fourteen_field_source_preserved']
            assert not api['complete_catalog_manifest_enforced'] and not api['selected_digest_profile_provenance_bound']
            matrix=read(ROOT/package['refinement_matrix']['path'])
            assert set(matrix['theorem_targets'])==set(proof['new_declarations']) and not matrix['whole_original_source_interpretation']
            completion=read(ROOT/package['component_completion_audit']['path'])
            assert not completion['N01_accepted'] and completion['inherited_discharges']==0
'''
    source = source.replace(marker, "index.get('preflight_reuse_packages', []) +\n                    index.get('original_byte_pipeline_packages', [])):").replace(end, block + end)
    compile(source, str(driver), 'exec')
    out = H / 'execution/PROGRESS.md'
    text = out.read_text()
    old = 'making 1872 distinct verified candidate declarations in total.'
    assert text.count(old) == 1
    text = text.replace(old, 'and original relation byte integration adds 14, making 1886 distinct verified candidate declarations in total.')
    text += '''

Original relation byte integration

K02-original-byte-pipeline proves a raw byte entrypoint exactly equivalent to the
original full structural IntentSourcePipeline.Meaning plus independent combined
budget/preflight/scalar-byte meanings and the exact source revision digest join.
It accepts no caller AST. All supplied source, qualifier and ordered catalog capture
occurrences are preflighted before the original typed pipeline. Fourteen new general
declarations pass eight fresh new-module compile/replay calls, twenty-eight axiom
inspections, eight import audits and twelve runtime controls per phase. Exact prior
matching-phase outputs of 121 unchanged dependency modules were reused; those modules
were not rebuilt. This is not independent checking or measured operational limits.

The nineteen-slot original source policy is preserved with only parses replaced;
the full original SourceInterpretation still requires the other eighteen genuine
policy premises. Complete raw catalog-to-typed-context adapters/manifest coverage,
binding the chosen profile to owned selection evidence, authentic providers,
mandatory consumers, whole-theory closure, independent checking, all seven extensions
and final measured-use assessment remain required. The original source bytes succeed
with coherent synthetic contexts; the old placeholder source digest refuses. This
does not authenticate the synthetic catalog roots.

All 263 inherited IDs remain open; 90 original discharges retain scope. Four actual
meaning assessments remain recorded; K04 and global policies remain pending. Only
N00 is accepted. The full plan remains active and incomplete.
'''
    index['original_byte_pipeline_packages'] = [package]
    index['original_byte_pipeline_candidate_theorems'] = 14
    index['total_distinct_new_candidate_theorems'] = 1886
    seq['candidate_fragment_theorems'] = 1886
    seq['candidate_original_byte_pipeline_packages'] = 1
    progress['candidate_fragment_theorems'] = 1886
    progress['original_byte_pipeline_candidate_theorems'] = 14
    progress['candidate_original_byte_pipeline_packages'] = 1
    for key, name in files.items():
        progress['K02_original_byte_pipeline_' + key] = binding(HERE / name)
    save(N / 'formal-preparation-index.json', index)
    save(N / 'sequential-review.json', seq)
    changed = {str((N / name).relative_to(ROOT)) for name in ['formal-preparation-index.json', 'sequential-review.json']}
    for value in progress.values():
        if isinstance(value, dict) and value.get('path') in changed:
            value.update(binding(ROOT / value['path']))
    save(H / 'execution/plan.json', plan)
    driver.write_text(source)
    out.write_text(text)
    print('Registered 14 original byte-pipeline declarations; 1886 total; zero inherited discharges.')

if __name__ == '__main__':
    run()
