"""Exercise the original native package guard without host credentials or Sessions."""
import ast
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v78'
CONTEXT = BASE / 'current-context-delivery-v9'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    bridge = API / 'custody_context_sessions.py'
    old = next(node.value.value for node in ast.walk(ast.parse(bridge.read_bytes()))
               if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'MAPPING_PIN' for t in node.targets))
    package = BASE / 'current-mapped-context-v4/packages/0001/manifest.json'
    correct = bind(package)['sha256']
    assert old != correct
    name = '_cal_API78_mapping_guard_diagnosis'
    spec = importlib.util.spec_from_file_location(name, CONTEXT / '__init__.py', submodule_search_locations=[str(CONTEXT)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    selected = __import__(name + '.generation', fromlist=['selected_mapping'])
    refused = False
    try:
        selected.selected_mapping(old)
    except ValueError as error:
        assert error.args == ('independent native mapped package differs',)
        refused = True
    assert refused
    mapping, native, manifest = selected.selected_mapping(correct)
    assert len(mapping['rows']) == 25 and len(manifest['files']) > 0
    files = [bind(path) for path in [bridge, package, CONTEXT / 'generation.py', CONTEXT / 'source-manifest.json', Path(__file__).resolve()]]
    observations = []
    for path in sorted((API / 'receipts/per-call-observations').glob('*.json')):
        value = json.loads(path.read_bytes())
        reply = value['actual_public_reply']
        if reply.get('operation') == 'context.get' and reply.get('kind') == 'error':
            assert reply['message']['code'] == 'integrity-failed'
            observations.append({'binding': bind(path), 'test_ref': value['test_ref'],
                                 'operation': 'context.get', 'public_code': 'integrity-failed'})
    assert len(observations) >= 2
    result = {'schema_version': 'lab-native-package-selection-diagnosis/v1-candidate',
              'result': 'PASS', 'files': files, 'stale_declared_package_sha256': old,
              'actual_current_package_binding': bind(package), 'original_stale_pin_refused': True,
              'original_current_pin_cold_replay_passed': True,
              'native_rows': 25, 'native_cut': native['cut'], 'public_failure_observations': observations,
              'source_callbacks_replaced': False, 'clock_replaced': False,
              'host_credentials_created': 0, 'Sessions_created': 0,
              'current_Machine_qualified': False, 'whole_API_qualified': False,
              'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False}
    out = RUN / 'API78-mapping-pin-diagnosis-0001.json'
    with out.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'PASS', 'diagnosis_binding': bind(out), 'stale_pin_refused': refused,
                      'correct_pin_cold_replay': True, 'public_failure_observations': len(observations)}), flush=True)


if __name__ == '__main__':
    main()
