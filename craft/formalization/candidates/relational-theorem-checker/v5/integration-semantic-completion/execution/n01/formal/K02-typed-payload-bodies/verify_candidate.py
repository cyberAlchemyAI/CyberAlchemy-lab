"""Fresh-check this component; reuse exact prior dependency outputs by phase."""
from pathlib import Path
import hashlib, json, os, re, shutil, subprocess, time

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[5]
ROOT = BASE.parents[3]

def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

def check_tree(value):
    if isinstance(value, dict):
        if {'path', 'sha256'} <= value.keys():
            assert binding(ROOT / value['path']) == {key: value[key] for key in ['path', 'sha256']}
        for child in value.values():
            check_tree(child)
    elif isinstance(value, list):
        for child in value:
            check_tree(child)

def run():
    driver = binding(Path(__file__))
    predecessor_names = ['K02-retained-catalogs']
    priors, prior_bindings, prior_audits = [], [], []
    pool = {}
    for name in predecessor_names:
        report_path = HERE.parent / name / 'verification.json'
        audit_path = HERE.parent / name / 'import-resolution-audit.json'
        prior, audit = json.loads(report_path.read_text()), json.loads(audit_path.read_text())
        check_tree(prior)
        check_tree(audit)
        assert prior['result'] == 'candidate-fragment-pass'
        assert audit['result'] == 'import-resolution-audit-pass' and audit['verification'] == binding(report_path)
        priors.append(prior)
        prior_bindings.append(binding(report_path))
        prior_audits.append(binding(audit_path))
        for record in prior['records'] + prior.get('reused_dependencies', []):
            output = record.get('olean', record.get('reused_output'))
            key = (record['phase'], Path(output['path']).name)
            entry = {'phase': record['phase'], 'source': record['source'],
                     'prior_output': output, 'prior_verification': binding(report_path)}
            if key in pool:
                assert pool[key]['source'] == entry['source'], key
                assert pool[key]['prior_output']['sha256'] == output['sha256'], key
            else:
                pool[key] = entry
    context_path, controls_path = HERE / 'context-pack.json', HERE / 'control-index.json'
    context, controls = json.loads(context_path.read_text()), json.loads(controls_path.read_text())
    check_tree(context)
    check_tree(controls)
    fixture_report = json.loads((HERE / 'fixture-validation.json').read_text())
    check_tree(fixture_report)
    assert fixture_report['result'] == 'complete-typed-body-control-inputs-pass'
    stable_fixture = binding(HERE / 'fixture-validation.json')
    stable = [binding(context_path), binding(controls_path), *prior_bindings, *prior_audits]
    lock_path = BASE / 'v1/formal/toolchain-lock.json'
    lock = json.loads(lock_path.read_text())
    runtime = BASE / 'v1/formal/.toolcache/lean-4.33.1-linux'
    lean, kernel = runtime / 'bin/lean', runtime / 'lib/lean/libleanshared.so'
    assert binding(lean)['sha256'] == lock['lean_binary_sha256']
    assert binding(kernel)['sha256'] == lock['lean_shared_library_sha256']
    sources = [HERE / (name + '.lean') for name in
               ['TypedBodyCombinators', 'BodyStringProfiles', 'CompleteBodyProfiles', 'TypedBodyControls']]
    captured = [binding(path) for path in sources]
    names = []
    for path in sources:
        code = path.read_text()
        short = re.findall(r'^theorem (\w+)', code, re.M)
        assert short == re.findall(r'^#print axioms (\w+)$', code, re.M)
        executable = '\n'.join(line for line in code.splitlines() if not line.lstrip().startswith('--'))
        # Hostile JSON fixtures contain the literal authority_effect "admit".
        # It is data, not a Lean admission command. Keep executable checks and
        # the kernel's exact axiom inspection, while excluding string contents.
        executable = re.sub(r'"(?:\\.|[^"\\])*"', '""', executable)
        assert not re.search(r'\b(sorry|admit|native_decide|axiom)\b', executable)
        names += ['RelationalSuccessor.CandidateTypedBodies.' + name for name in short]
    assert len(names) == len(set(names)) == 12
    expressions = re.findall(r'^#eval (.*?)(?=\n#eval |\nend )', sources[-1].read_text(), re.M | re.S)
    assert expressions == [case['expression'] for case in controls['runtime_cases']]
    assert len(expressions) == 313
    allowed, records, import_records, reused = {'propext', 'Quot.sound', 'Classical.choice'}, [], [], []
    for phase in ['compile', 'replay']:
        build = HERE / phase
        build.mkdir(exist_ok=True)
        for path in build.glob('*.olean'):
            path.unlink()
        for (entry_phase, _), entry in sorted(pool.items()):
            if entry_phase != phase:
                continue
            prior_output = ROOT / entry['prior_output']['path']
            assert binding(prior_output) == entry['prior_output']
            target = build / prior_output.name
            shutil.copy2(prior_output, target)
            assert binding(target)['sha256'] == entry['prior_output']['sha256']
            reused.append(dict(entry, reused_output=binding(target)))
        for path in sources:
            assert binding(Path(__file__)) == driver and [binding(path) for path in sources] == captured
            output, log = build / (path.stem + '.olean'), build / (path.stem + '.log')
            argv = [str(lean), '-o', str(output), str(path)]
            started = time.monotonic()
            result = subprocess.run(argv, cwd=HERE, env=dict(os.environ, LEAN_PATH=str(build)),
                                    capture_output=True, text=True, timeout=300)
            log.write_text(result.stdout + result.stderr)
            assert result.returncode == 0 and 'warning:' not in result.stdout, (path.name, result.stdout, result.stderr)
            axioms = sorted({atom.strip() for group in re.findall(r'depends on axioms: \[([^]]*)\]', result.stdout)
                             for atom in group.split(',') if atom.strip()})
            inspected = len(re.findall(r'(?:depends on axioms:|does not depend on any axioms)', result.stdout))
            assert inspected == len(re.findall(r'^#print axioms ', path.read_text(), re.M))
            assert set(axioms) <= allowed
            row = {'phase': phase, 'source': binding(path), 'argv': argv, 'cwd': str(HERE),
                   'LEAN_PATH': str(build), 'exit_code': 0, 'log': binding(log), 'olean': binding(output),
                   'seconds': round(time.monotonic() - started, 3), 'axioms': axioms,
                   'inspected_declarations': inspected}
            if path == sources[-1]:
                raw_lines=iter(result.stdout.strip().splitlines())
                lines=[]
                for line in raw_lines:
                    if line=='some':
                        continuation=next(raw_lines)
                        assert continuation.startswith('  "')
                        line='some '+continuation.strip()
                    lines.append(line)
                assert len(lines)==len(controls['runtime_cases'])==313
                for line,case in zip(lines,controls['runtime_cases'],strict=True):
                    if case['expected_kind']=='literal':assert line==case['expected'],(case['id'],line)
                    else:
                        assert case['expected_kind']=='json-body' and line.startswith('some '),case['id']
                        assert json.loads(json.loads(line[5:]))==case['expected_body'],case['id']
                row['runtime_composed_cases'] = 313
            records.append(row)
            print(phase, path.stem, row['seconds'], flush=True)
            deps = subprocess.run([str(lean), '--deps', str(path)], cwd=HERE,
                                  env=dict(os.environ, LEAN_PATH=str(build)), capture_output=True, text=True, timeout=30)
            assert deps.returncode == 0 and not deps.stderr
            origins = []
            for line in deps.stdout.splitlines():
                dependency = Path(line.strip()).resolve()
                assert dependency.is_file()
                if dependency.is_relative_to(build):
                    fresh = [record for record in records if record['phase'] == phase and
                             Path(record['olean']['path']).name == dependency.name]
                    cached = [record for record in reused if record['phase'] == phase and
                              Path(record['reused_output']['path']).name == dependency.name]
                    assert len(fresh) + len(cached) == 1
                    expected = fresh[0]['olean'] if fresh else cached[0]['reused_output']
                    assert binding(dependency) == expected
                    origin = 'fresh-local-module' if fresh else 'exact-verified-prior-phase-output'
                else:
                    assert dependency.is_relative_to(runtime / 'lib/lean')
                    origin = 'pinned-runtime-library'
                origins.append(dict(binding(dependency), origin=origin))
            import_records.append({'phase': phase, 'source': binding(path), 'dependencies': origins})
    assert binding(Path(__file__)) == driver and [binding(path) for path in sources] == captured
    assert [binding(context_path), binding(controls_path),
            *[binding(ROOT / item['path']) for item in prior_bindings + prior_audits]] == stable
    for prior in priors:
        check_tree(prior)
    assert binding(HERE / 'fixture-validation.json') == stable_fixture
    check_tree(fixture_report)
    import generate_profiles
    generated,trace,roots=generate_profiles.compile_profiles()
    generation=json.loads((HERE/'generation-audit.json').read_text());check_tree(generation)
    assert generated==(HERE/'CompleteBodyProfiles.lean').read_text()
    assert trace==generation['assertion_trace'] and generation['profile_count']==len(roots)==7
    assert generation['record_type_count']==14 and generation['complete_record_field_count']==150
    assert generation['active_assertion_nodes']==204 and not generation['unsupported_assertions_ignored']
    report = {'task':'N01','unit':'K02-typed-payload-bodies','result':'candidate-fragment-pass',
              'method':'Fresh fixed-kind typed body decoder compile/replay with independent component meanings and exact prior matching-phase imports; generation/fixture comparisons are not general source-schema correspondence.',
              'driver':driver,'compiler':binding(lean),'kernel_library':binding(kernel),
              'toolchain_lock':binding(lock_path),'context_pack':binding(context_path),
              'control_index':binding(controls_path),'fixture_validation':binding(HERE/'fixture-validation.json'),
              'generation_audit':binding(HERE/'generation-audit.json'),
              'prior_verifications':prior_bindings,'prior_import_audits':prior_audits,
              'reused_dependencies':reused,'sources':captured,'records':records,'new_declarations':names,
              'new_declaration_count':12,'new_general_declarations':12,'new_worked_control_declarations':0,
              'runtime_composed_cases':313,'schema_comparison_cases':296,
              'complete_body_reconstruction_cases':8,'exact_identity_cases':7,'generic_unique_array_cases':2,
              'profile_count':7,'record_type_count':14,'complete_record_field_count':150,'active_assertion_nodes':204,
              'allowed_axioms':sorted(allowed),'complete_fixed_kind_record_meanings_proved':True,
              'exact_pinned_body_schema_references_retained':True,'all_original_fields_represented':True,
              'original_revision_occurrences_preserved':True,'whole_typed_value_array_uniqueness':True,
              'all_active_schema_assertions_audited':True,'heterogeneous_typed_body_family_present':True,
              'catalog_wide_dispatcher_proved':False,'generic_schema_compiler_correspondence_proved':False,
              'python_lean_general_correspondence_proved':False,'general_body_reconstruction_proved':False,
              'approved_kind_specific_payload_decoders_realized':False,'all_original_source_policy_providers_realized':False,
              'local_dependency_rebuild':False,'raw_source_refinement_proved':False,'independent_checker_run':False,
              'supported_resource_envelope_measured':False,'real_authoritative_snapshot_provider':False,
              'live_consumer_integration':False,'integrated_into_full_entrypoint':False,'N03_API_freeze':False,
              'inherited_discharges':0,'N01_accepted':False,'authority_effect':'none'}
    (HERE / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    audit = {'task': 'N01', 'unit': 'K02-typed-payload-bodies', 'result': 'import-resolution-audit-pass',
             'driver': driver, 'verification': binding(HERE / 'verification.json'),
             'resolved_source_phase_pairs': len(import_records), 'records': import_records,
             'claim_scope': 'New imports exactly resolved; dependencies reused, same-kernel checking is not independent.',
             'inherited_discharges': 0, 'authority_effect': 'none'}
    (HERE / 'import-resolution-audit.json').write_text(json.dumps(audit, indent=2) + '\n')
    print('PASS: 12 general declarations; 8 fresh new-module invocations; 313 runtime observations per phase.', flush=True)

if __name__ == '__main__':
    run()
