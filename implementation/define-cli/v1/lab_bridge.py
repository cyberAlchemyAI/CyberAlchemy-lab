#!/usr/bin/env python3
"""Read-only adapter to the existing Lab runtime; never authorizes or applies."""
import copy
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[2]
sys.path.insert(0, str(REPO / 'implementation/lab-runtime/v2'))
from lab_runtime.cli import read_data
from lab_runtime.common import RuntimeFault, digest, encoded, require
from lab_runtime.graph import query, posture
from lab_session import Session
from lab_runtime.sources import resolve, freshness
from lab_runtime.store import Store


class RepositoryReader:
    """Uses the selected Lab foundation without provisioning a signing store."""
    def __init__(self, repo, data):
        self.repo, self.data = repo, data
    def replay(self, *, require_current=False):
        current = freshness(self.repo, self.data['baseline'])
        require(current['status'] == 'current', 'stale Lab source context')
        return self.data


def execute(req):
    repo = Path(req.get('repo', REPO)).resolve()
    require(repo == REPO, 'Define bridge requires this Lab checkout')
    if req['operation'] == 'validate-result':
        from jsonschema import Draft202012Validator, FormatChecker
        schema = json.loads((PACKAGE / 'schemas/lab-define-result.schema.json').read_text())
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(req['result']))
        require(not errors, 'invalid Lab Define result: ' + '; '.join(e.message for e in errors[:5]))
        return {'valid': True, 'authority_effect': 'none'}
    store_path = Path(req['store']).resolve() if req.get('store') else repo / '.local/lab-runtime/v2/store'
    store = Store(store_path, repo)
    data = read_data(repo, store)
    require(data['freshness']['status'] == 'current', 'stale Lab branch or source profile')
    op = req['operation']
    if op == 'review':
        require(store.path.exists(), 'review requires an explicitly initialized Lab store')
        return store.review(req['proposal'])
    if op == 'ontology':
        return query(data, req.get('subject', 'Lifecycle'), depth=req.get('depth', 2), max_nodes=60, max_edges=100)
    if op == 'inspect':
        row = resolve(data['projection']['subjects'], req['subject'])
        return {**posture(row), 'record': row['record'], 'authority_effect': 'none'}
    require(op == 'context', 'unsupported Define bridge operation')
    projection = data['projection']
    subject = req.get('subject') or projection['state']['node_id']
    if store.path.exists():
        reader = store
    else:
        # These are source owner/scope/policy labels for a read projection, not
        # authentication or permission to write a new branch.
        data['config'].update(owner_ref=projection['state']['owner_ref'],
            scope_ref=projection['state']['scope_ref'], policy_ref=data['baseline']['profile']['policy_ref'])
        reader = RepositoryReader(repo, data)
    session = Session(reader, subject, ttl=req.get('ttl', 900))
    try:
        packet = session.context()
        definitions = [dict(posture(row), record=row['record']) for row in projection['subjects'].values()
            if row['category'] == 'definition' and row['effective_state'] in ('admitted-current', 'local-admitted-current')]
        selected = list(dict.fromkeys(req.get('definition_refs', [])))
        if selected:
            definitions = []
            for ref in selected:
                row = resolve(projection['subjects'], ref)
                require(row['category'] == 'definition', 'selected reference is not a Definition')
                require(row['effective_state'] in ('admitted-current', 'local-admitted-current'), 'selected Definition is not current')
                definitions.append(dict(posture(row), record=row['record']))
        else:
            # A bounded common-language selection. No synthesized required edge.
            wanted = {'Definition', 'Authority', 'Context', 'Ontology', 'Intent', 'Goal', 'Project', 'Work', 'Agent'}
            definitions = [row for row in definitions if row['record'].get('term') in wanted or row['record'].get('name') in wanted]
        return {'ok': True, 'packet': packet, 'definitions': sorted(definitions, key=lambda row: row['version_ref']),
            'source_snapshot_digest': data['baseline']['snapshot_digest'], 'head': data['head']['transaction_digest'],
            'freshness': data['freshness'], 'authority_effect': 'none', 'projection_owner_from_provisioned_store': store.path.exists()}
    finally:
        session.close()


if __name__ == '__main__':
    try:
        req = json.load(sys.stdin)
        print(encoded(execute(req)).decode(), end='')
    except (RuntimeFault, OSError, ValueError, KeyError) as exc:
        print(json.dumps({'ok': False, 'result': 'BLOCKED', 'error': str(exc), 'authority_effect': 'none'}))
        sys.exit(2)
