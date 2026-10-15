"""Account for each flagged historical Session carrier and propose exclusion.

Field presence is not evidence of leaked RAM. Preserve all original bytes and
scanner findings; select none of these bodies for a public release.
"""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
RUN = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
spec = importlib.util.spec_from_file_location('_cal_R06_session_review', HERE.parent / '0002/review.py')
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)

def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': R.sha(R.read(path))}

def put(path, value):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')
    path.chmod(0o600)

def freeze():
    assert not (HERE / 'source-manifest.json').exists()
    parent = HERE.parent / '0004/receipts/proof-0002.json'
    proof = R.parse(R.read(parent))
    assert proof['result'] == 'PASS' and proof['task_complete'] is False
    rows = {r['path']: r for r in proof['files']}
    controls = [parent, Path(__file__), RUN / 'authorization.json',
                HERE.parent / '0002/review.py', HERE.parent / '0003/inventory.json']
    context = RUN / 'context-R06-session-exclusions-0005.json'
    put(context, {'schema_version': 'lab-bounded-context/v1-candidate',
                  'task': 'R06 review exact historical Session field findings',
                  'strict_coverage': 'PASS', 'blockers': [],
                  'source_bindings': [bind(p) for p in controls],
                  'constraints': ['Read all61flagged originals with the unchanged scanner.',
                                  'Account for all94selectors; disclose no field values.',
                                  'Propose exact body exclusions; change no original, permission or release selection.',
                                  'Field presence does not prove persisted working memory or a credential leak.',
                                  'Final selected integrated release bytes still require review.'],
                  'authority_effect': 'none', 'actual_owner_outcome': None})
    for p in controls + [context]:
        row = bind(p)
        assert rows.get(row['path'], row) == row
        rows[row['path']] = row
    for row in rows.values():
        assert bind(ROOT / row['path']) == row, row['path']
    put(HERE / 'source-manifest.json',
        {'schema_version': 'lab-R06-session-field-review-source/v1-candidate',
         'files': [rows[k] for k in sorted(rows)],
         'parent_partial_binding': bind(parent), 'context_binding': bind(context),
         'frozen_before_observations': True, 'authority_effect': 'none',
         'actual_owner_outcome': None})
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(HERE / 'source-manifest.json')}), flush=True)

def guard(pin):
    path = HERE / 'source-manifest.json'
    assert bind(path)['sha256'] == pin
    manifest = R.parse(R.read(path))
    for row in manifest['files']:
        assert bind(ROOT / row['path']) == row, row['path']
    return manifest

def review(pin):
    source = guard(pin)
    inventory = R.parse(R.read(HERE.parent / '0003/inventory.json'))
    flagged = [r for r in inventory['rows'] if r['private_field_findings']]
    assert len(flagged) == 61
    rows = []
    for old in flagged:
        raw = R.read(ROOT / old['path'])
        assert R.sha(raw) == old['sha256'] and len(raw) == old['size_bytes']
        # The original parser verifies embedded archive digests as it descends.
        actual = R.scan(raw, old['path'])
        assert actual == old['private_field_findings']
        assert all(r['reason'] == 'actual-private-or-session-field'
                   and r['selector'].endswith('/session_memory') for r in actual)
        rows.append({'path': old['path'], 'sha256': old['sha256'], 'size_bytes': len(raw),
                     'original_findings': actual, 'actual_reinspection': 'PASS',
                     'disposition': 'candidate-historical-Session-body-exclusion',
                     'body_kind': 'original-custody-archive' if Path(old['path']).suffix == '.snapshot'
                                  else 'historical-record-or-evidence-carrier',
                     'public_body_export_allowed': False,
                     'private_values_disclosed': False,
                     'working_RAM_persistence_claimed': False,
                     'rationale': 'Exact historical Session metadata or enclosing provenance. Preserve privately; exclude this original body from the proposed public code release. This disposition does not authorize public export or infer a credential leak.'})
    assert sum(len(r['original_findings']) for r in rows) == 94
    guard(pin)
    output = HERE / 'session-exclusions.json'
    put(output, {'schema_version': 'lab-R06-historical-Session-exclusions/v1-candidate',
                 'result': 'PASS-scoped-review', 'checked_at': datetime.now(timezone.utc).isoformat(),
                 'source_binding': bind(HERE / 'source-manifest.json'),
                 'actual_original_files_reinspected': 61, 'actual_selectors_accounted': 94,
                 'original_custody_archives': 27, 'record_or_evidence_carriers': 34,
                 'exclusion_proposals': rows, 'prior_findings_retained': True,
                 'originals_or_permissions_changed': False, 'private_values_disclosed': False,
                 'public_release_selection_changed': False, 'final_public_selection_complete': False,
                 'publication_authorized': False, 'R06_complete': False, 'task_complete': False,
                 'goal_complete': False, 'authority_effect': 'none', 'actual_owner_outcome': None})
    closure = {r['path']: r for r in source['files']}
    for p in [HERE / 'source-manifest.json', output]:
        row = bind(p)
        closure[row['path']] = row
    proof = HERE / 'receipts/proof-0001.json'
    put(proof, {'schema_version': 'lab-R06-Session-exclusion-partial-proof/v1-candidate',
                'result': 'PASS', 'files': [closure[k] for k in sorted(closure)],
                'review_binding': bind(output), 'actual_original_files_reinspected': 61,
                'actual_selectors_accounted': 94, 'exact_original_exclusion_proposals': 61,
                'publication_authorized': False,
                'remaining_obligations': ['Select exact final API/workflow/ontology/schema/release bytes.',
                                          'Reconcile exclusion proposals against final selected package dependencies.',
                                          'Complete R07/S02 privacy reconciliation before actual R08.'],
                'authority_effect': 'none', 'actual_owner_outcome': None,
                'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'PASS-scoped-review', 'files_reinspected': 61,
                      'selectors_accounted': 94, 'proof_binding': bind(proof)}), flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['freeze', 'review'])
    parser.add_argument('--source-sha256')
    args = parser.parse_args()
    if args.command == 'freeze':
        freeze()
    else:
        assert args.source_sha256
        review(args.source_sha256)
