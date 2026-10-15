"""Retain exact candidate O05 construction, regression and cold evidence."""
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import traceback

RECEIPTS = Path(__file__).resolve().parent
ROOT = RECEIPTS.parents[5]
ADAPTERS = ROOT / 'implementation/lab-ontology/candidates/v1/migration/adapters'
sys.path.insert(0, str(ADAPTERS))
from check import SourceTranslation, signed_catalog, bind, sha, parse, require, original, load_package, validate_payload, build, record_bytes, verify_observations

RUN = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'


def emit(path, value):
    with path.open('x') as stream:
        stream.write(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + '\n')


def execute(label, args, output, timeout):
    with (output / (label + '.stdout')).open('xb') as stdout, (output / (label + '.stderr')).open('xb') as stderr:
        process = subprocess.run(args, cwd=ROOT, stdout=stdout, stderr=stderr, timeout=timeout)
    return {'label': label, 'command': args, 'returncode': process.returncode}


def main():
    started = time.perf_counter()
    number = max([int(p.stem) for p in RECEIPTS.iterdir() if p.is_file() and p.stem.isdigit()] + [0]) + 1
    output = RECEIPTS / f'{number:04d}'; output.mkdir()
    context = parse((RUN / 'context-O05.json').read_bytes()); frozen = {}
    for b in context['source_bindings']:
        original({k: b[k] for k in ('path', 'sha256')}); frozen[b['path']] = {k: b[k] for k in ('path', 'sha256')}
    for path in ('implementation/lab-ontology/candidates/v1/receipts/O02/0004.json',
                 'implementation/lab-ontology/candidates/v1/receipts/O04/0001.json'):
        receipt = parse((ROOT / path).read_bytes())
        require(receipt['result'] == 'PASS' and receipt['task_complete'] is True, 'upstream task scope incomplete')
        for b in receipt['files']:
            p = ROOT / b['path']
            require(p.is_file() and sha(p.read_bytes()) == b['sha256'], 'upstream source/evidence changed')
            frozen[b['path']] = b
    package = ROOT / parse((ADAPTERS / 'build-scope.json').read_bytes())['output_root']
    files = load_package(package); pin = sha(files['manifest.json'])
    for p in [*(p for p in ADAPTERS.iterdir() if p.is_file()),
              *[package / name for name in files], RUN / 'context-O05.json', Path(__file__).resolve()]:
        b = bind(p); frozen[b['path']] = b
    emit(output / 'frozen-inputs.json', {'authority_effect': 'none', 'actual_owner_outcome': None,
        'independent_manifest_binding': bind(package / 'manifest.json'), 'files': list(frozen.values())})
    jobs = [('import-guards', [sys.executable, '-m', 'unittest', 'discover', '-s', str(ADAPTERS), '-p', 'test_import.py', '-v'], 90),
            ('inventory-regression', [sys.executable, '-m', 'unittest', 'discover', '-s', str(ROOT / 'docs/migration-plans/lab-selected-slice'), '-p', 'test_inventory.py', '-v'], 60),
            ('cold-reconstruction', [sys.executable, str(ADAPTERS / 'cold.py'), str(package), pin], 120),
            ('native-regression', ['cargo', 'test', '--locked', '--offline', '--manifest-path',
                str(ROOT / 'implementation/lab-ontology/candidates/v1/adapters/native/Cargo.toml'),
                '--target-dir', '/tmp/cal-O05-native-regression'], 180)]
    errors = []; checks = []; observations = {}; commands = []
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(execute, label, args, output, timeout) for label, args, timeout in jobs]
            for future in futures:
                commands.append(future.result())
        require(all(c['returncode'] == 0 for c in commands), 'one or more suites failed; original logs preserved')
        for label, count in [('import-guards', 48), ('inventory-regression', 42)]:
            raw = (output / (label + '.stderr')).read_text()
            require(f'Ran {count} tests' in raw and raw.rstrip().endswith('OK'), 'complete suite result required: ' + label)
            rows = [{'suite': label, 'test': line.split(' ... ')[0], 'result': 'PASS'}
                for line in raw.splitlines() if line.endswith(' ... ok')]
            require(len(rows) == count, 'suite result inventory differs'); checks.extend(rows)
        raw = (output / 'native-regression.stdout').read_text()
        native_checks = [{'suite': 'native-regression', 'test': line.split(' ... ')[0], 'result': 'PASS'}
            for line in raw.splitlines() if line.startswith('test ') and line.endswith(' ... ok')]
        require(len(native_checks) == 23 and '0 failed' in raw, 'all 23 inherited native regressions required')
        checks.extend(native_checks)
        cold = parse((output / 'cold-reconstruction.stdout').read_bytes())
        require(cold['result'] == 'PASS' and cold['same_original_bytes'] is True, 'cold reconstruction incomplete')
        observations['cold_reconstruction'] = cold
        with signed_catalog() as (catalog, operations):
            translator = SourceTranslation(catalog, operations)
            observations['warm_validation'] = validate_payload(files, translator, pin, native=True)
            verify_observations(translator.selection)
        repeated = build()
        require(set(repeated) == set(files) and all(repeated[k] == files[k] for k in files), 'repeated build differs')
        observations['repeated_build'] = {'result': 'PASS', 'files_compared': len(files), 'same_original_bytes': True,
            'core_sha256': parse(files['manifest.json'])['core_sha256']}
        emit(output / 'observations.json', observations)
    except Exception as error:
        errors.append({'error': str(error), 'traceback': traceback.format_exc()})
    drift = [b['path'] for b in frozen.values() if not (ROOT / b['path']).is_file()
        or sha((ROOT / b['path']).read_bytes()) != b['sha256']]
    passed = bool(not errors and not drift and len(checks) == 113
        and 'repeated_build' in observations and 'warm_validation' in observations)
    sources = list(frozen.values()) + [bind(p) for p in output.iterdir() if p.is_file()]
    receipt = {'schema_version': 'lab-O05-exact-source-adaptation-proof/v1-candidate', 'task': 'O05',
        'result': 'PASS' if passed else 'FLAG', 'task_complete': passed,
        'completion_mode': 'candidate-implementation-verified', 'authority_effect': 'none', 'actual_owner_outcome': None,
        'files': sources, 'source_bindings': context['source_bindings'], 'source_drift': drift, 'errors': errors,
        'tests': len(checks), 'checks': checks, 'commands': commands, 'observations': observations,
        'duration_seconds': time.perf_counter() - started,
        'manifest_binding': bind(package / 'manifest.json'),
        'counts': parse(files['manifest.json'])['counts'], 'items_reconciled': 140, 'blocked_dependency_revisions': 9,
        'package_bytes': sum(len(raw) for raw in files.values()),
        'verified_obligation_ids': ['I1', 'I2', 'I3', 'I4', 'I5', 'I6'] if passed else [],
        'domain_instances_conformed': 0, 'global_typed_relations_created': 0, 'source_effects_applied': 0,
        'source_bodies_copied': 0, 'remaining_obligations': [] if passed else ['Finish O05 exact adaptation and validation.'],
        'downstream_obligations': ['O03/O06: source-backed query and pilot consumers must retain private posture and blocked/ambiguous dependency evidence.',
            'R03/W07: independent signed Project/Product endpoint coupling and full workflow completion remain open.',
            'S02/R08: exact source-use/privacy, local predicate/profile, generator/output and confidence ownership require actual reviewed owner outcomes.',
            'Domain adapters remain separate: no actual Product, Capability, Project, actor, Policy or Challenge instance is inferred from legacy metadata.'],
        'claim_ceiling': 'Complete O05 candidate construction criteria only: all 140 selected dispositions reconciled; 220 exact schema-valid Lab metadata/local interpretation carriers; original source, selector and blocked dependency witnesses; unchanged native source sealed/replayed in owned stores; repeated/cold byte parity. No raw private prose copy, source script execution, transitive closure, Lab domain conformance, global typed axis, canonical admission, ontology adoption, live operation or actual owner outcome.'}
    path = output.with_suffix('.json'); emit(path, receipt)
    print(json.dumps({'result': receipt['result'], 'task_complete': passed, 'tests': len(checks),
        'receipt': path.relative_to(ROOT).as_posix(), 'counts': receipt['counts'], 'source_drift': drift,
        'errors': [e['error'] for e in errors], 'package_bytes': receipt['package_bytes']}, sort_keys=True))
    return 0 if passed else 1


if __name__ == '__main__':
    sys.exit(main())
