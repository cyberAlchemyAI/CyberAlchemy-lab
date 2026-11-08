#!/usr/bin/env python3
"""Validate the applied import and exact current local qualification inputs."""
from pathlib import Path
import hashlib
import json
import re
from jsonschema import Draft202012Validator

P = Path(__file__).resolve().parent
LAB = P.parents[2]
UPSTREAM = LAB.parent / 'cyberAlchemy-v2'


def load(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    report = load(LAB / 'craft/work/outcomes/current-verification/lab-qualification.json')
    assert report['status'] == 'passed-local-scope' and report['totals'] == dict(tests=10, passed=10, failed=0)
    assert report['authority_effect'] == 'none' and not report['global_consumer_cutover']
    assert not report['runtime_copied'] and not report['publication']
    snapshot = {r['path']: r['sha256'] for r in report['source_inputs']}
    for relative, expected in snapshot.items():
        assert sha(LAB / relative) == expected, 'Qualified source changed: ' + relative
    for row in report['compiled_outputs']:
        assert sha(LAB / row['path']) == row['sha256'], 'Compiled output changed: ' + row['path']
    for relative, expected in report['protected_files'].items():
        assert sha(LAB / relative) == expected, 'Protected original changed: ' + relative
    changes = {r['path']: r for r in load(P / 'LOCAL-CHANGES.json')['changes']}
    rows = load(P / 'IMPORT.json')['payload'] + load(P / 'EVIDENCE-EXPORT.json')['payload']
    for row in rows:
        expected = changes.get(row['target'], {}).get('local_sha256', row['sha256'])
        assert snapshot[row['target']] == expected, 'Unrecorded import change: ' + row['target']
        if 'current_source' in row and row['current_source']['root'] == 'upstream':
            source = row['current_source']
            assert sha(UPSTREAM / source['path']) == source['sha256'], 'Upstream source changed'
    for row in load(P / 'ADDITIONAL-INPUTS.json')['inputs']:
        assert sha(UPSTREAM / row['source']) == row['sha256'] == sha(LAB / row['target'])
    capabilities = bindings = 0
    base = LAB / 'craft/product/capabilities'
    schema = Draft202012Validator(load(LAB / 'authority/artifact-types/product-capability/v1/schema.json'))
    realization = Draft202012Validator(load(LAB / 'authority/artifact-types/capability-realization-binding/v2/schema.json'))
    for family in load(base / 'catalog.json')['families']:
        data = load(base / family['path'])
        records = data[family['record_collection']] if family['record_collection'] else [data]
        for record in records:
            schema.validate(record)
            assert record['evidence_refs'] == record['revision_history'] == record['successor_refs'] == []
            capabilities += 1
        for binding in load(base / family['family'] / 'realizations.json')['bindings']:
            realization.validate(binding)
            assert binding['binding_state'] == 'candidate' and binding['adoption_decision_ref'] is None
            bindings += 1
    assert capabilities == bindings == 37
    native_counts = {}
    for name in ['product-bridge', 'orodi-bridge']:
        home = LAB / 'craft/ontology/packages' / name
        native = load(home / ('schema/ontology-package.schema.json' if name == 'product-bridge' else 'schemas/orodi-ontology.schema.json'))
        source_ids = {row['source_id'] for row in load(home / 'sources.json')['sources']}
        subjects = {row['node_id'] for row in load(home / 'nodes.json')['nodes']}
        checks = [('sources', 'source'), ('nodes', 'node'), ('relations', 'relation'), ('residue', 'residue')]
        if name == 'orodi-bridge':
            checks += [('capabilities', 'capability'), ('implementation-bindings', 'implementationBinding')]
        for filename, kind in checks:
            data = load(home / (filename + '.json'))
            records = data['bindings'] if filename == 'implementation-bindings' else data[filename]
            validator = Draft202012Validator({'$schema': native['$schema'], '$defs': native['$defs'], '$ref': '#/$defs/' + kind})
            for record in records:
                validator.validate(record)
                assert set(record.get('source_refs', [])) <= source_ids
                for refs in record.get('evidence', {}).values():
                    assert set(refs) <= source_ids
                if kind == 'relation':
                    assert record['from'] in subjects and record['to'] in subjects
                if kind == 'implementationBinding':
                    assert not record['runtime_evidence_refs'] and record['conformance_ref'] is None
                    for target in record['target_refs']:
                        assert sha(LAB / target['ref']) == target['digest']
        native_counts[name] = dict(nodes=len(subjects), relations=len(load(home / 'relations.json')['relations']))
    reconciliation = load(LAB / 'craft/ontology/sources/reconciliation.json')
    assert reconciliation['status'] == 'current' and reconciliation['counts'] == dict(current=74, missing=0, drifted=0)
    blockers = load(LAB / 'craft/work/blockers/blockers.json')['items']
    assert {item['id'] for item in blockers} == {'CRAFT-VERIFY-TDE-INPUTS'}
    broader = load(LAB / 'craft/work/outcomes/current-verification/broader-qualification.json')
    assert broader['status'] == 'completed-with-gaps' and broader['authority_effect'] == 'none'
    assert broader['selected_inputs_current'] and broader['inputs_unchanged_during_each_run']
    assert broader['runtime_package_inputs_unchanged_across_runs'] and not broader['historical_evidence_restored']
    encoded = json.dumps(broader['source_inputs'], ensure_ascii=False, separators=(',', ':')).encode()
    assert hashlib.sha256(encoded).hexdigest() == broader['selected_input_set_sha256']
    assert broader['repacked_dependency_files_match_shared_inputs']
    assert not broader['publication'] and not broader['global_consumer_cutover']
    for source in broader['source_inputs']:
        assert sha(Path(source['path'])) == source['sha256'], 'Broader verification input changed: ' + source['path']
    assert broader['evf']['passed'] == 8 and broader['evf']['failed'] == 0 and broader['evf']['exit_code'] == 0
    assert broader['body_war']['aggregate_exit_code'] == 0
    installed = broader['installed']
    assert installed['status'] == 'failed', 'Preserve the original diagnostic matrix result'
    assert installed['focused_retest']['status'] == 'passed'
    assert installed['focused_retest']['counts'] == {'tests': 3, 'pass': 3, 'fail': 0, 'skipped': 0, 'cancelled': 0, 'todo': 0}
    assert installed['portfolio_retest']['status'] == 'passed'
    assert installed['portfolio_retest']['counts'] == {'tests': 6, 'pass': 6, 'fail': 0, 'skipped': 0, 'cancelled': 0, 'todo': 0}
    repair = installed['test_only_repair']
    assert repair['module_unchanged_outside_declared_fragment'] and repair['package_tuple_unchanged']
    assert not repair['runtime_package_changes'] and not repair['full_matrix_repeated_after_test_only_repair']
    current = Path(repair['target']).read_text()
    assert hashlib.sha256(current.replace(repair['new_fragment'], repair['original_fragment']).encode()).hexdigest() == repair['original_sha256']
    assert len(installed['command_aliases']) == 3
    assert broader['body_war']['node'] == dict(tests=33, passed=33, failed=0)
    assert sum(item['tests'] for item in broader['body_war']['python']) == 16
    assert all(item['exit_code'] == 0 for item in broader['body_war']['python'])
    assert broader['body_war']['static_exit_code'] == 0
    assert broader['tde']['total'] == broader['tde']['passed'] + broader['tde']['failed'] + broader['tde']['pending']
    assert broader['tde']['failed'] == len(broader['tde']['failures'])
    for item in load(LAB / 'craft/implementation/verification/input-origins.json')['inputs']:
        assert sha(UPSTREAM / item['source']) == item['source_sha256']
        assert sha(LAB / item['target']) == item['prepared_sha256']
    reference = load(LAB / 'craft/work/experiments/body-war-reference/application.json')
    assert reference['classification'] == 'reference-application' and not reference['production_capability']
    assert reference['runtime_state'] == 'not-qualified'
    links = 0
    docs = [LAB / path for path in snapshot if path.endswith('.md')]
    for file in docs:
        # Frozen/synthetic fixtures are test inputs, not live navigation pages.
        if any(part in {'fixtures', '__fixtures__', '__tests__'} for part in file.parts):
            continue
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', file.read_text()):
            if re.match(r'[A-Za-z][A-Za-z0-9+.-]*:', link) or link.startswith('#'):
                continue
            assert (file.parent / link.split('#')[0]).exists(), 'Broken live reader link: ' + str(file) + ': ' + link
            links += 1
    assert sha(LAB / 'craft/ontology/application/source-manifest.json') == report['native_source_manifest_sha256']
    result = dict(status='pass', functional_and_selected_import_files=len(rows),
                  qualified_source_files=len(snapshot), compiled_files=len(report['compiled_outputs']),
                  capability_schemas=capabilities, candidate_realization_schemas=bindings,
                  reader_links=links, protected_files=len(report['protected_files']),
                  tests=report['totals'], broader_status=broader['status'], original_application_checks=[dict(id=r['id'], status=r['status'], counts=r['counts']) for r in broader['installed']['checks']], preference_retest=broader['installed']['focused_retest']['counts'], portfolio_retest=broader['installed']['portfolio_retest']['counts'], tde=dict(passed=broader['tde']['passed'], failed=broader['tde']['failed'], pending=broader['tde']['pending']), open_verification_gaps=len(blockers), source_reconciliation=report['legacy_semantic_lineage'],
                  native_models=native_counts, reference_application=reference['application_id'],
                  activation=False, publication=False)
    print(json.dumps(result))
    (P / 'LIVE-VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
