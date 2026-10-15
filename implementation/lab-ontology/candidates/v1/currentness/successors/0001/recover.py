"""Recover only absent owned code and produce currentness successor witnesses."""
import argparse
import copy
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import portable as P

HERE, ROOT = P.HERE, P.ROOT


def emit(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as out:
        out.write(json.dumps(value, indent=2, sort_keys=True) + '\n')


def run(pin):
    P.require(P.binding(HERE / 'source-manifest.json')['sha256'] == pin, 'producer source manifest differs')
    m = P.load(HERE / 'source-manifest.json')
    for row in m['files']:
        P.original(row)
    for row in m['historical_file_bindings']:
        if row['path'] not in P.EXPECTED:
            P.original(row)
        else:
            P.require(P.EXPECTED[row['path']] == row['sha256'], 'historical locator digest differs')
    output = HERE / 'proof/0001'
    output.mkdir(parents=True, exist_ok=False)
    result = {'result': 'FAIL', 'authority_effect': 'none', 'actual_owner_outcome': None,
              'producer_source_sha256': pin, 'checked_at': datetime.now(timezone.utc).isoformat(),
              'external_repository_written': False, 'private_state_rehydrated': False,
              'original_acceptance_preserved': True, 'task_complete': False, 'goal_complete': False}
    try:
        first = P.observe_ref()
        ref = output / 'refs/main.commit-line'
        ref.parent.mkdir()
        with ref.open('xb') as out:
            out.write((P.COMMIT + '\n').encode('ascii'))
        build = P.load(ROOT / m['original_build_binding']['path'])
        target = Path(build['target'])
        P.require(not target.exists(), 'only absent owned native code roots may be recreated')
        env = dict(os.environ)
        env.pop('CARGO_TARGET_DIR', None)
        env.pop('RUSTFLAGS', None)
        observations = []
        commands = [('build', build['command']), ('native-tests', ['cargo', 'test', '--offline', '--locked', '--manifest-path',
                    build['command'][5], '--target-dir', str(target)])]
        for label, command in commands:
            with (output / (label + '.stdout')).open('xb') as stdout, (output / (label + '.stderr')).open('xb') as stderr:
                process = subprocess.run(command, env=env, stdout=stdout, stderr=stderr)
            observations.append({'producer': label, 'command': command, 'exit_code': process.returncode, 'terminal_observed': True})
            P.require(process.returncode == 0, label + ' failed')
        P.original(build['executable_binding'])
        native = ROOT / '.local/lab-candidate-code/O03-currentness-0001/lab-ontology-native'
        native.parent.mkdir(parents=True, exist_ok=False)
        with native.open('xb') as out:
            out.write(Path(P.EXE).read_bytes())
        native.chmod(0o755)
        P.require(P.binding(native)['sha256'] == P.EXE_SHA, 'portable executable is not byte-identical')
        last = P.observe_ref()
        witness = {'result': 'PASS', 'authority_effect': 'none', 'source_manifest_binding': P.binding(HERE / 'source-manifest.json'),
                   'ref_before': first, 'ref_after': last, 'portable_ref_binding': P.binding(ref),
                   'portable_native_binding': P.binding(native), 'native_observations': observations,
                   'original_native_build_binding': m['original_build_binding'],
                   'claim_ceiling': 'Exact locator byte equivalence and current branch resolution only; original runtime proof is retained, not rerun or admitted.'}
        emit(output / 'locator-witness.json', witness)
        common = m['files'] + [P.binding(HERE / 'source-manifest.json'), P.binding(output / 'locator-witness.json'), P.binding(ref), P.binding(native)]
        common += [P.binding(output / (label + suffix)) for label, _ in commands for suffix in ['.stdout', '.stderr']]
        receipts = []
        for item in m['predecessor_receipts']:
            original = P.load(ROOT / item['binding']['path'])
            successor = copy.deepcopy(original)
            routes = []
            rows = []
            for row in original['files']:
                if row['path'] in P.EXPECTED:
                    replacement = P.binding(ref if row['path'] == P.REF else native)
                    routes.append({'historical_binding': row, 'portable_binding': replacement,
                                   'semantics': 'resolved-ref-commit-line' if row['path'] == P.REF else 'byte-identical-rebuilt-code'})
                    rows.append(replacement)
                else:
                    rows.append(row)
            rows += common + [item['binding']]
            successor.update(schema_version='lab-portable-currentness-successor/v1-candidate', predecessor_schema_version=original['schema_version'],
                             predecessor_receipt_binding=item['binding'], portable_locator_routes=routes,
                             currentness_witness_binding=P.binding(output / 'locator-witness.json'),
                             original_checks_posture='retained historical terminal proof; native regressions rerun in this witness',
                             files=sorted({r['path']: r for r in rows}.values(), key=lambda r: r['path']))
            P.check_partition(original, successor)
            path = HERE / 'receipts' / (item['task'] + '-0002.json')
            emit(path, successor)
            P.verify_receipt(path)
            receipts.append(P.binding(path))
        result.update(result='PASS', successor_receipt_bindings=receipts, portable_ref_binding=P.binding(ref),
                      portable_native_binding=P.binding(native), native_observations=observations,
                      historical_closure_count=len(m['historical_file_bindings']), original_native_byte_identity=True)
    except BaseException as error:
        result['failure'] = str(error)
    emit(output / 'result.json', result)
    print(json.dumps(result), flush=True)
    return 0 if result['result'] == 'PASS' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.source_sha256))
