"""Fresh phase-bound runtime comparisons for the corrected numeric explanation."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[9]


def binding(path): return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def run():
    driver_binding = binding(Path(__file__))
    verification = json.loads((HERE / 'verification.json').read_text())
    lean = ROOT / verification['compiler']['path']; assert binding(lean) == verification['compiler']
    source = HERE / 'NumericRepresentationProbe.lean'
    source_binding = binding(source)
    assert not any(line.startswith('theorem ') for line in source.read_text().splitlines())
    data = (HERE / 'fixtures/authority-rounded-noninteger-byte.json').read_bytes()
    code = source.read_text()
    literal = re.search(r'^def counter : CandidateBindingCapture.Envelope := ⟨\[(.*?)\],(\d+),bootstrap.ref,"([^"]+)"⟩$', code, re.M)
    assert literal and bytes(int(value) for value in literal.group(1).split(',') if value.strip()) == data
    assert int(literal.group(2)) == len(data) and literal.group(3) == hashlib.sha256(data).hexdigest()
    key = json.loads(data)['binding_revision_key']
    expected_ref = 'def expected : RevisionRef := ⟨⟨' + ','.join(json.dumps(key[field]) for field in ['owner','artifact','revision']) + '⟩,"' + hashlib.sha256(data).hexdigest() + '"⟩'
    assert expected_ref in code and b'123.000000000000000000000001' in data
    assert re.findall(r'^#eval CandidateNumberParser.decodeTokenEpoch (.*)$', code, re.M) == [json.dumps(value) for value in ['42.0','4.2e1','-0','123.000000000000000000000001','01','0.5']]
    assert '#eval (prepareAuthority bootstrap limits.perCaptureBytes frame root expected counter).isSome' in code
    expected = ['some 42', 'some 42', 'some 0', 'none', 'none', 'none', 'false']
    outputs = {(row['phase'], Path(row['source']['path']).stem): row['olean'] for row in verification['records']}
    records = []
    for phase in ['compile', 'replay']:
        assert binding(source) == source_binding and binding(Path(__file__)) == driver_binding
        build = HERE / phase; output = build / 'NumericRepresentationProbe.olean'; log = build / 'NumericRepresentationProbe.log'
        env = dict(os.environ, LEAN_PATH=str(build))
        result = subprocess.run([str(lean), '-o', str(output), str(source)], cwd=HERE, env=env,
                                capture_output=True, text=True, timeout=240)
        log.write_text(result.stdout + result.stderr)
        assert result.returncode == 0 and not result.stderr and 'warning:' not in result.stdout, result.stdout + result.stderr
        assert result.stdout.strip().splitlines() == expected, result.stdout
        deps = subprocess.run([str(lean), '--deps', str(source)], cwd=HERE, env=env, capture_output=True, text=True, timeout=30)
        assert deps.returncode == 0 and not deps.stderr
        dependencies = []
        for line in deps.stdout.splitlines():
            path = Path(line).resolve()
            if (phase, path.stem) in outputs:
                assert path == build / (path.stem + '.olean') and binding(path) == outputs[phase, path.stem]
            else:
                assert path.is_relative_to(lean.parents[1] / 'lib/lean')
            dependencies.append(binding(path))
        records.append({'phase': phase, 'source': binding(source), 'olean': binding(output), 'log': binding(log),
                        'exit_code': result.returncode, 'expected_outputs': expected, 'imports': dependencies})
        print(phase, 'numeric-representation-comparison-pass', flush=True)
    assert binding(source) == source_binding and binding(Path(__file__)) == driver_binding
    report = {'task': 'N01', 'unit': 'K02-profile-evidence', 'result': 'numeric-representation-comparison-pass',
              'driver': driver_binding, 'main_verification': binding(HERE / 'verification.json'),
              'counterexample': binding(HERE / 'fixtures/authority-rounded-noninteger-byte.json'),
              'correction': binding(HERE / 'NUMERIC-REPRESENTATION-CORRECTION.md'), 'records': records,
              'new_declarations': 0, 'independent_checker_run': False, 'inherited_discharges': 0, 'authority_effect': 'none'}
    (HERE / 'representation-comparison-probe.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__': run()
