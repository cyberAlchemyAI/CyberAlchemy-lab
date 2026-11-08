"""Owned O03 current/historical query replay over the disjoint T12 engine cut."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys

import probe

ROOT = probe.ROOT
HERE = Path(__file__).resolve().parent
CONTROLS = HERE / 'query-control-selection.json'
CONTROLS_SHA = '559ca5e90bc1d0e90d1724a2d2b8ecc1427e2694469bfb4d89c6c7a208fc6b6d'
SCOPES = ('current-specialist-owner', 'historical-d73-slice', 'O05-source-interpretation')
QUESTION_NAMES = {'current-specialist-owner': {'lifecycle-current-specialist'},
                  'historical-d73-slice': {'lifecycle', 'authority', 'provenance'},
                  'O05-source-interpretation': {'native-source-lineage'}}
QUESTION_IDS = {'lifecycle-current-specialist': 'lifecycle-slice', 'lifecycle': 'lifecycle-slice',
                'authority': 'authority-explanation', 'provenance': 'capability-provenance',
                'native-source-lineage': 'capability-provenance'}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def selected(path, expected):
    rel = Path(path)
    if rel.is_absolute() or '..' in rel.parts or rel.as_posix() != path:
        raise ValueError('noncanonical selected path')
    target = ROOT / rel
    if not target.resolve().is_relative_to(ROOT) or not target.is_file() or any(p.is_symlink() for p in (target, *target.parents)):
        raise ValueError('unsafe selected path')
    raw = target.read_bytes()
    if digest(raw) != expected:
        raise ValueError('selected bytes changed: ' + path)
    return raw


def verify_controls():
    probe.verify_successor()
    manifest_path = CONTROLS.relative_to(ROOT).as_posix()
    manifest = json.loads(selected(manifest_path, CONTROLS_SHA))
    if manifest['schema_version'] != 'lab-T10-O03-current-query-control-selection/v1':
        raise ValueError('wrong query control selector')
    expected = {p.relative_to(ROOT).as_posix() for p in (HERE / 'query-successor').rglob('*')
                if p.is_file() and '__pycache__' not in p.parts}
    listed = [row['path'] for row in manifest['files']]
    if len(listed) != len(set(listed)) or set(listed) != expected:
        raise ValueError('query control closure changed')
    for row in manifest['files']:
        if set(row) != {'path', 'sha256'}:
            raise ValueError('query control row malformed')
        selected(row['path'], row['sha256'])
    return manifest


def query_modules(manifest):
    path = HERE / 'query-successor'
    sys.path.insert(0, str(path))
    names = ('common', 'contract', 'scope', 'model', 'materialize')
    modules = {name: importlib.import_module(name) for name in names}
    rows = {row['path']: row['sha256'] for row in manifest['files']}
    for name, module in modules.items():
        source = Path(module.__file__).resolve()
        expected = path / (name + '.py')
        if source != expected or digest(source.read_bytes()) != rows[expected.relative_to(ROOT).as_posix()]:
            raise ValueError('loaded query code differs: ' + name)
    return modules


def execute(scope_name):
    if scope_name not in SCOPES:
        raise ValueError('undeclared query scope')
    manifest = verify_controls()
    modules = query_modules(manifest)
    common, scope, model, materialize = (modules[k] for k in ('common', 'scope', 'model', 'materialize'))
    factory = scope.native_source_scope() if scope_name == 'O05-source-interpretation' else scope.governed_scope(scope_name)
    answers = {}
    with factory as selected_scope:
        graph = model.Model(selected_scope)
        for name, request in materialize.cases(scope_name, graph).items():
            answer = graph.query(request)
            repeated = graph.query(json.loads(json.dumps(request)))
            if common.encoded(answer) != common.encoded(repeated):
                raise ValueError('same-cut query nondeterminism')
            if answer['query'] != request or answer['source_snapshot']['admission_epoch'] != request['admission_as_of']:
                raise ValueError('query/epoch binding differs')
            if answer['freshness']['state'] not in ('current', 'historical'):
                raise ValueError('stale/unknown source accepted')
            rows = answer['coverage']['subject_rows']
            if len(rows) != len(graph.p['subjects']) or len({r['version_ref'] for r in rows}) != len(rows):
                raise ValueError('query source subject partition differs')
            if sum(answer['coverage']['partition'].values()) != len(rows):
                raise ValueError('query partition incomplete')
            answers[name] = answer
        if selected_scope.guard()['state'] != 'current':
            raise ValueError('source changed before query closure')
    if not selected_scope.closed:
        raise ValueError('query scope not closed')
    verify_controls()
    return answers


def record(scope_name, output):
    answers = execute(scope_name)
    output = Path(output).resolve()
    if not output.resolve().is_relative_to(HERE) or output.exists():
        raise ValueError('query output must be a new task-local directory')
    output.mkdir(parents=True)
    rows = {}
    for name, answer in sorted(answers.items()):
        target = output / (name + '.json')
        raw = (json.dumps(answer, sort_keys=True, indent=2, ensure_ascii=False) + '\n').encode()
        target.write_bytes(raw)
        rows[name] = {'path': target.relative_to(ROOT).as_posix(), 'sha256': digest(raw),
                      'response_digest': digest(canonical(answer)), 'status': answer['result_status'],
                      'admission_epoch': answer['source_snapshot']['admission_epoch'],
                      'subjects': answer['coverage']['selected_subjects'], 'gaps': len(answer['gaps'])}
    result = {'schema_version': 'lab-T10-O03-T12-disjoint-query-run/v1', 'scope': scope_name,
              'engine_manifest_sha256': probe.NEW_MANIFEST_SHA, 'query_controls_sha256': CONTROLS_SHA,
              'source_sha256': probe.NEW_SOURCE_SHA, 'queries': rows, 'closed_scope': True,
              'authority_effect': 'none', 'selected_governed_models': 0,
              'claim_ceiling': 'Local exact-source candidate query; partial answers are not completed semantics or authority.'}
    (output / 'RESULT.json').write_bytes((json.dumps(result, sort_keys=True, indent=2) + '\n').encode())
    return result


def verify_result(directory):
    """Cold-replay exact owned response bytes and bounded receipt semantics."""
    verify_controls()
    requested = Path(directory).absolute()
    if any(path.is_symlink() for path in (requested, *requested.parents)) or (requested / 'RESULT.json').is_symlink():
        raise ValueError('linked run path')
    directory = requested.resolve()
    if not directory.is_relative_to(HERE):
        raise ValueError('run outside task-local root')
    raw = (directory / 'RESULT.json').read_bytes()
    result = json.loads(raw)
    scope_name = result['scope']
    if (result['schema_version'] != 'lab-T10-O03-T12-disjoint-query-run/v1' or
            scope_name not in SCOPES or result['engine_manifest_sha256'] != probe.NEW_MANIFEST_SHA or
            result['query_controls_sha256'] != CONTROLS_SHA or result['source_sha256'] != probe.NEW_SOURCE_SHA or
            result['authority_effect'] != 'none' or result['selected_governed_models'] != 0 or
            result['closed_scope'] is not True or set(result['queries']) != QUESTION_NAMES[scope_name]):
        raise ValueError('query result control/claim set differs')
    from_epoch = {'current-specialist-owner': 'decision:lab-specialist-owner-bootstrap-0003',
                  'historical-d73-slice': 'decision:0073',
                  'O05-source-interpretation': 'candidate:O05'}[scope_name]
    for name, row in result['queries'].items():
        path = (directory / (name + '.json')).relative_to(ROOT).as_posix()
        if row['path'] != path:
            raise ValueError('query response path differs')
        answer = json.loads(selected(path, row['sha256']))
        if (digest(canonical(answer)) != row['response_digest'] or
                answer['query']['scope_ref'] != scope_name or
                answer['query']['query_id'] != QUESTION_IDS[name] or
                answer['query']['admission_as_of'] != from_epoch or
                answer['source_snapshot']['admission_epoch'] != from_epoch or
                answer['result_status'] != row['status'] or
                answer['authority_effect'] != 'none' or answer['replay_source'] is not False or
                answer['coverage']['selected_subjects'] != row['subjects'] or
                len(answer['gaps']) != row['gaps']):
            raise ValueError('query response content/claim differs')
        if answer['freshness']['state'] != ('historical' if scope_name == 'historical-d73-slice' else 'current'):
            raise ValueError('query source posture differs')
        histories = answer['source_snapshot']['histories']
        if scope_name == 'historical-d73-slice':
            if (histories['project-semantic-event-history']['cursor'] != 2 or
                    histories['project-governance-event-history']['cursor'] != 2 or
                    histories['ontology-semantic'] is not None or histories['ontology-governance'] is not None or
                    row['status'] != {'lifecycle': 'partial', 'authority': 'complete',
                                      'provenance': 'complete'}[name]):
                raise ValueError('historical D73 scope semantics differ')
        if scope_name == 'current-specialist-owner':
            if (histories['project-semantic-event-history']['cursor'] != 7 or
                    histories['project-governance-event-history']['cursor'] != 7 or
                    answer['coverage']['required_obligations']['current-state'] is not True or
                    answer['coverage']['required_obligations']['separate-project-histories'] is not True):
                raise ValueError('current specialist State/history semantics differ')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('scope', choices=SCOPES)
    parser.add_argument('output')
    args = parser.parse_args()
    print(json.dumps(record(args.scope, args.output), sort_keys=True))
