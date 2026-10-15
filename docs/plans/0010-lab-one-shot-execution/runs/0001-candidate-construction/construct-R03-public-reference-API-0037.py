"""Author a successor preserving frozen v36 and its complete test obligations."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
PARENT = INTERFACE / 'api-v36'
API = INTERFACE / 'api-v37'
COMPOSITION_PARENT = INTERFACE / 'classification-preparation-v1'
COMPOSITION = INTERFACE / 'classification-preparation-v2'
SOURCE = '1c32032bf01bf9327f8bf2efb731ac30a0970734cd408307ddbe97c6b7a5b1fa'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def methods(path):
    return {node.name: ast.dump(node, include_attributes=False)
            for node in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}


def main():
    assert not API.exists() and not COMPOSITION.exists()
    assert bind(PARENT / 'source-manifest.json')['sha256'] == SOURCE
    spec = importlib.util.spec_from_file_location('_cal_API37_authoring_parent_guard', PARENT / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    guard.verify(SOURCE)
    shutil.copytree(PARENT, API, ignore=shutil.ignore_patterns(
        'receipts', '__pycache__', 'source-manifest.json', 'contract-profile.json',
        'freeze_classification.py', 'test-expectation-revisions.json'))
    shutil.copytree(COMPOSITION_PARENT, COMPOSITION, ignore=shutil.ignore_patterns('__pycache__', 'receipts'))
    proxy = API / 'classification_preparation.py'
    text = proxy.read_text()
    assert text.count('classification-preparation-v1') == 1
    proxy.write_text(text.replace('classification-preparation-v1', 'classification-preparation-v2').replace(
        '_classification_preparation_v1', '_classification_preparation_v2'))
    preparation = COMPOSITION / 'preparation.py'
    text = preparation.read_text()
    marker = '\n\nclass RuleFailure(Exception):'
    assert text.count(marker) == 1
    helper = '''

PUBLIC_REF_FIELDS=('scope_ref','identity_ref','version_ref','carrier_ref','byte_sha256')


def public_artifact_ref(header):
    """Project a validated candidate header into the original public reference.

    Contract-selection metadata stays on its independently validated proposal
    target. It is not a sixth public reference axis. Unknown fields are refused.
    """
    require(type(header) is dict and set(header) in
            (set(PUBLIC_REF_FIELDS),set(PUBLIC_REF_FIELDS)|{'candidate_contract_binding'}),
            'undeclared artifact reference field or missing public field')
    if 'candidate_contract_binding' in header:
        binding=header['candidate_contract_binding']
        require(type(binding) is dict and set(binding)=={'ref','sha256'},
                'candidate contract binding shape differs')
    return {key:copy.deepcopy(header[key]) for key in PUBLIC_REF_FIELDS}
'''
    text = text.replace(marker, helper + marker)
    old = "require(headers.get(message[key]['version_ref'])==message[key],"
    new = "require(public_artifact_ref(headers[message[key]['version_ref']])==message[key],"
    assert text.count(old) == 1
    # Keep the unresolved-version refusal explicit before indexing a header.
    new = "require(message[key]['version_ref'] in headers,'classification requested revision is unresolved')\n            " + new
    text = text.replace(old, new)
    ast.parse(text)
    preparation.write_text(text)
    fixture = API / 'classification_fixture.py'
    text = fixture.read_text()
    old = "'subject': subject, 'scheme': targets[0]['artifact'], 'value': targets[1]['artifact'],"
    new = "'subject': subject, 'scheme': composition.public_artifact_ref(targets[0]['artifact']), 'value': composition.public_artifact_ref(targets[1]['artifact']),"
    assert text.count(old) == 1
    fixture.write_text(text.replace(old, new))
    auth = API / 'auth.py'
    text = auth.read_text()
    old = 'current-participation-v3/packages/0001/period.json'
    assert text.count(old) == 1
    auth.write_text(text.replace(old, 'current-participation-v4/packages/0001/period.json'))
    bridge = API / 'source_bridge.py'
    text = bridge.read_text()
    assert text.count('_cal_api_v36_custody_context_v8') == 1
    bridge.write_text(text.replace('_cal_api_v36_custody_context_v8', '_cal_api_v37_custody_context_v8'))
    retained = []
    for path in PARENT.rglob('*.py'):
        if 'receipts' in path.parts or '__pycache__' in path.parts or path.name == 'freeze_classification.py':
            continue
        current = API / path.relative_to(PARENT)
        assert methods(path) == methods(current), path.name
        retained.extend(str(path.relative_to(PARENT)) + ':' + name for name in methods(path))
    assert len(retained) == 275
    for directory in (API, COMPOSITION):
        for path in directory.rglob('*.py'):
            ast.parse(path.read_bytes())
    output = RUN / 'API37-public-reference-construction-0001.json'
    report = {'schema_version': 'lab-successor-construction/v1-candidate',
              'result': 'AUTHORED', 'parent_source_binding': bind(PARENT / 'source-manifest.json'),
              'retained_exact_test_method_ASTs': retained, 'retained_exact_method_count': 275,
              'changed_files': [bind(path) for path in [proxy, preparation, fixture, auth, bridge]],
              'changes': ['Original public ArtifactRef has five fields; candidate contract metadata stays on the validated proposal target.',
                          'Compare requested exact references with an explicit closed projection of validated prospective headers.',
                          'Termination selects the qualified Source4 period through the captured exact binding.',
                          'Successor has its own Context module namespace.'],
              'source_frozen': False, 'runtime_qualified': False, 'new_fixture_effects': 0,
              'original_public_contracts': 34, 'remaining_qualified_operations': 21,
              'original_plan_tasks': 46, 'maximum_Session_seconds': 900,
              'source_callbacks_replaced': False, 'clock_replaced': False,
              'authority_effect': 'none', 'actual_owner_outcome': None}
    with output.open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'AUTHORED', 'retained_exact_methods': 275,
                      'report_binding': bind(output), 'source_frozen': False}), flush=True)


if __name__ == '__main__':
    main()
