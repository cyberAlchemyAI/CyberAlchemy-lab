"""Record qualified fresh source components and explicit pending integration."""
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v75'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def load(path):
    return json.loads(path.read_bytes())


def main():
    parent_path = API / 'receipts/R03-0111.json'
    parent = load(parent_path)
    rows = {row['path']: row for row in parent['files']}
    proofs = [RUN / name for name in ['current-participation-source-proof-0005.json',
              'current-participation-audit-proof-0005.json', 'current-source-adapter-checks-proof-0005.json',
              'current-source-adapter-audit-proof-0005.json']]
    proofs += [BASE / 'current-source-adapter-v4/qualification-0002.json',
               BASE / 'current-mapped-context-v4/qualification-0001.json']
    for path in proofs:
        document = load(path)
        assert document['result'] == 'PASS'
        for row in document['files']:
            assert rows.get(row['path'], row) == row, row['path']
            rows[row['path']] = row
    selected = BASE / 'current-context-delivery-v9'
    source = selected / 'source-manifest.json'
    for row in load(source)['files']:
        assert rows.get(row['path'], row) == row, row['path']
        rows[row['path']] = row
    paths = [*proofs, parent_path, source, RUN / 'author-API76-fresh-context-selection-0001.py',
             RUN / 'API76-fresh-binding-revision-0001.json', Path(__file__).resolve(),
             RUN / 'current-source-mapping-audit-terminal-0005.json',
             RUN / 'current-source-mapping-audit-terminal-0006.json',
             RUN / 'current-context-code-audit-source-0009.json']
    # Only immutable API draft bytes are selected; active logs are never bound.
    paths += [path for folder in [BASE / 'api-v76', BASE / 'lesson-host-composition-v26']
              for path in folder.rglob('*') if path.is_file() and '__pycache__' not in path.parts]
    for path in paths:
        row = bind(path)
        assert rows.get(row['path'], row) == row, row['path']
        rows[row['path']] = row
    for row in rows.values():
        assert bind(ROOT / row['path']) == row, row['path']
    value = {**parent, 'files': [rows[key] for key in sorted(rows)], 'result': 'PASS',
             'parent_progress_binding': bind(parent_path),
             'fresh_participation_source_built': True,
             'fresh_participation_source_qualified': True,
             'fresh_participation_source_binding': bind(BASE / 'current-participation-v5/source-manifest.json'),
             'fresh_participation_package_binding': bind(BASE / 'current-participation-v5/packages/0001/manifest.json'),
             'fresh_source_reader_qualification_binding': bind(proofs[-2]),
             'fresh_mapper_qualification_binding': bind(proofs[-1]),
             'fresh_source_tests': 20, 'fresh_reader_tests': 20, 'fresh_mapper_tests': 29,
             'source_independent_audit_checks': 94, 'reader_independent_audit_checks': 137,
             'mapper_independent_audit_checks': 251,
             'fresh_Context_candidate_source_binding': bind(source),
             'fresh_Context_component_qualified': False,
             'fresh_API76_candidate_binding_revision': bind(RUN / 'API76-fresh-binding-revision-0001.json'),
             'current_API_version': 75, 'current_Machine_qualified': False,
             'Machine_fixture_successor_required': False,
             'fresh_Machine_API_selection_and_qualification_required': True,
             'existing_periods_or_grants_extended': False,
             'remaining_obligations': [
                 'Complete Context9 full50/code execution/independent audit and API76 original Machine/termination qualification under exact fresh component bindings.',
                 'Finish thirteen missing public handlers, original R05/R06/R07 acceptance and full S02 package before the sole R08 owner decision; retain A01-A04 effect boundaries.',
                 *parent['remaining_obligations']],
             'change': 'Fresh signed Source5, Reader4 and Mapper4 qualified: 20/20/29 tests and 94/137/251 independent checks. All23 original bodies retained,15nodes10edges mapped. Failed mapper audit5 retained; successor6 corrected only the stale declared reader expectation. Context9 frozen, build/full50 qualification pending; API76 drafted with323 methods,316 unchanged and7 exact path/identity revisions.',
             'whole_API_qualified': False, 'task_complete': False, 'goal_complete': False,
             'claim_ceiling': 'Exact fresh source/reader/mapper component evidence and frozen Context/API drafts. Current Agent, complete API, owner outcome, canonical admission and activation remain unqualified.'}
    output = API / 'receipts/R03-0112.json'
    with output.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'PASS', 'progress_binding': bind(output), 'bound_files': len(rows),
                      'task_complete': False, 'goal_complete': False}), flush=True)


if __name__ == '__main__':
    main()
