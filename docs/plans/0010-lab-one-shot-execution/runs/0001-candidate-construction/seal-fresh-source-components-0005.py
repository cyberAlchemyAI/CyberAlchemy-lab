"""Bind actual fresh source, reader and mapper component outcomes."""
import ast
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def load(path):
    return json.loads(path.read_bytes())


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def closure(documents, paths):
    rows = {}
    for document in documents:
        for row in document.get('files', []):
            assert rows.get(row['path'], row) == row, row['path']
            rows[row['path']] = row
    for path in paths:
        row = bind(path)
        assert rows.get(row['path'], row) == row, row['path']
        rows[row['path']] = row
    for row in rows.values():
        assert bind(ROOT / row['path']) == row, row['path']
    return [rows[key] for key in sorted(rows)]


def main():
    common = {'result': 'PASS', 'authority_effect': 'none',
              'actual_owner_outcome': None, 'current_Agent_qualified': False,
              'whole_API_qualified': False, 'task_complete': False, 'goal_complete': False}
    proofs = [RUN / name for name in [
        'current-participation-source-proof-0005.json',
        'current-participation-audit-proof-0005.json',
        'current-source-adapter-checks-proof-0005.json',
        'current-source-adapter-audit-proof-0005.json']]
    documents = [load(path) for path in proofs]
    assert all(doc['result'] == 'PASS' for doc in documents)
    reader = BASE / 'current-source-adapter-v4'
    reader_out = reader / 'qualification-0002.json'
    emit(reader_out, {**common, 'schema_version': 'lab-current-source-reader-component-qualification/v4-candidate',
                     'files': closure(documents, [*proofs, Path(__file__).resolve(), reader / 'source-manifest.json']),
                     'tests_run': 20, 'independent_source_audit_checks': 94,
                     'independent_reader_audit_checks': 137,
                     'source_binding': bind(reader / 'source-manifest.json'),
                     'participation_source_binding': bind(BASE / 'current-participation-v5/source-manifest.json'),
                     'historical_copied_result_used_as_current_proof': False})
    mapped = BASE / 'current-mapped-context-v4'
    source = mapped / 'source-manifest.json'
    package = mapped / 'packages/0001/manifest.json'
    checks = mapped / 'receipts/checks.json'
    audit = RUN / 'current-mapping-independent-observations-0006.json'
    audit_source = RUN / 'current-mapping-audit-source-0006.json'
    terminals = [RUN / name for name in ['current-mapping-build-terminal-0004.json',
                 'current-mapping-checks-terminal-0004.json', 'current-source-mapping-audit-terminal-0006.json']]
    reports = [mapped / 'packages/0001/build-result.json', checks, audit]
    for terminal_path, report_path in zip(terminals, reports):
        terminal = load(terminal_path)
        assert terminal['actual_exit_code'] == 0
        assert terminal.get('report_binding', terminal.get('observation_binding')) == bind(report_path)
        for key in ['log_binding', 'producer_binding']:
            assert bind(ROOT / terminal[key]['path']) == terminal[key]
    check_result = load(checks)
    audit_result = load(audit)
    assert check_result['result'] == audit_result['result'] == 'PASS'
    assert check_result['tests_run'] == 29 and audit_result['checks'] == 251
    assert check_result['source_sha256'] == bind(source)['sha256']
    assert check_result['package_sha256'] == bind(package)['sha256']
    assert audit_result['source_binding'] == bind(audit_source)
    assert audit_result['original_body_count'] == 23 and audit_result['captured_subject_count'] == 582
    def methods(path):
        return {n.name: ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(path.read_bytes()))
                if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}
    for name in ['test_original_mapping.py', 'test_raw_mapping.py']:
        assert methods(mapped / name) == methods(BASE / 'current-mapped-context-v3' / name)
    paths = [source, package, audit_source, *terminals, *reports, reader_out, Path(__file__).resolve()]
    for terminal_path in terminals:
        for key in ['log_binding', 'producer_binding']:
            paths.append(ROOT / load(terminal_path)[key]['path'])
    result = {**common, 'schema_version': 'lab-current-mapped-context-component-qualification/v4-candidate',
              'files': closure([load(source), load(package), load(audit_source), load(reader_out)], paths),
              'source_binding': bind(source), 'package_binding': bind(package),
              'qualified_source_reader_binding': bind(reader_out),
              'full_tests': 29, 'all29_original_test_methods_unchanged': True,
              'independent_audit_checks': 251, 'original_bodies': 23,
              'captured_subjects': 582, 'nodes': 15, 'edges': 10,
              'actual_build_exit_code': 0, 'actual_check_exit_code': 0, 'actual_audit_exit_code': 0,
              'failed_predecessor_audit_preserved': True}
    out = mapped / 'qualification-0001.json'
    emit(out, result)
    print(json.dumps({'result': 'PASS', 'reader': bind(reader_out), 'mapper': bind(out), 'bound_files': len(result['files'])}), flush=True)


if __name__ == '__main__':
    main()
