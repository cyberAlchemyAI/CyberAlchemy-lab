"""Offline successor checks. No host import, source freeze, or fixture effects."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-v36'
PARENT = API.parent / 'api-v35'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, body):
    with path.open('x') as stream:
        json.dump(body, stream, indent=2, sort_keys=True)
        stream.write('\n')


def methods(text):
    return {node.name: ast.dump(node, include_attributes=False)
            for node in ast.walk(ast.parse(text))
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}


def main():
    assert not (API / 'source-manifest.json').exists()
    assert not (API / 'contract-profile.json').exists()
    freezer = API / 'freeze_classification.py'
    tree = ast.parse(freezer.read_bytes())
    main_node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'main')
    replacement = next(node.value for node in ast.walk(main_node)
                       if isinstance(node, ast.Assign)
                       and any(isinstance(target, ast.Name) and target.id == 'replacement_literals'
                               for target in node.targets))
    literals = ast.literal_eval(replacement)
    spec = importlib.util.spec_from_file_location('_cal_API36_offline_freezer_check', freezer)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = {bind(path)['path']: bind(path) for path in
            [Path(__file__).resolve(), freezer, API / 'custody_context_sessions.py', API / 'guarded_reads.py']}
    checks = []
    method_rows = []
    total = 0
    for original in sorted(PARENT.rglob('*.py')):
        if any(part in original.parts for part in ('receipts', '__pycache__')):
            continue
        parent_text = original.read_text()
        original_methods = methods(parent_text)
        if not original_methods:
            continue
        successor = API / original.relative_to(PARENT)
        actual_text = successor.read_text()
        expected_text = parent_text
        for old, new in literals.items():
            actual_text = actual_text.replace(old, new)
            expected_text = expected_text.replace(old, new)
        actual_methods = methods(actual_text)
        assert set(original_methods) == set(actual_methods), original.name
        assert methods(expected_text) == actual_methods, original.name
        for path in (original, successor):
            row = bind(path)
            rows[row['path']] = row
        total += len(actual_methods)
        method_rows.append({'file': successor.relative_to(API).as_posix(),
                            'method_names': sorted(actual_methods),
                            'normalized_AST_sha256': hashlib.sha256(json.dumps(actual_methods, sort_keys=True).encode()).hexdigest()})
    assert total == 259
    checks.append('All259 inherited method names and normalized AST obligations retained')
    assert any(row['file'] == 'run_session_checks.py' for row in method_rows)
    checks.append('Session checks selected by method presence despite runner filename')
    for filename, count in [('custody_context_sessions.py', 2), ('guarded_reads.py', 1)]:
        text = (API / filename).read_text()
        assert text.count('current-source-adapter-v2/') == count
        changed = module.rebind_reader_selectors(text)
        assert changed.count('current-source-adapter-v3/') == count
        assert changed == text.replace('current-source-adapter-v2/base.py', 'current-source-adapter-v3/base.py').replace(
            'current-source-adapter-v2/model.py', 'current-source-adapter-v3/model.py')
        checks.append(filename + ': complete exact selector replacement; guards retained')
    try:
        module.rebind_reader_selectors("selected = 'current-source-adapter-v2/unknown.py'")
    except AssertionError:
        checks.append('Undeclared old reader selector rejected')
    else:
        raise AssertionError('unknown old selector accepted')
    inputs = RUN / 'API36-reader-rebind-inputs-0001.json'
    put(inputs, {'files': [rows[key] for key in sorted(rows)], 'authority_effect': 'none'})
    report = {'schema_version': 'lab-offline-successor-rebind-check/v1-candidate',
              'result': 'PASS', 'checks_run': len(checks), 'checks': checks,
              'input_binding': bind(inputs), 'inherited_methods': total,
              'method_files': method_rows, 'source_frozen': False, 'runtime_qualified': False,
              'host_imports': 0, 'public_calls': 0, 'authority_effect': 'none', 'actual_owner_outcome': None}
    put(RUN / 'API36-reader-rebind-checks-0001.json', report)
    print(json.dumps({key: report[key] for key in ['result', 'checks_run', 'inherited_methods', 'source_frozen', 'runtime_qualified']}))


if __name__ == '__main__':
    main()
