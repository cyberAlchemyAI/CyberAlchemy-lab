"""Resolve known formats and stage exact diagnostic exclusions, with no publication."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import tomllib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
RUN = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
PARENT = HERE.parent / '0003'
spec = importlib.util.spec_from_file_location('_cal_R06_format_scanner', HERE.parent / '0002/review.py')
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)

def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(R.read(path)).hexdigest()}

def put(path, value):
    path.parent.mkdir(mode=0o700, exist_ok=True, parents=True)
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')
    path.chmod(0o600)

def freeze():
    output = HERE / 'source-manifest.json'
    assert not output.exists()
    parent = PARENT / 'receipts/proof-0002.json'
    selected = json.loads(R.read(parent))
    assert selected['result'] == 'PASS'
    rows = {row['path']: row for row in selected['files']}
    context = RUN / 'context-R06-format-resolution-0004.json'
    scoped = json.loads(R.read(context))
    assert scoped['strict_coverage'] == 'PASS' and scoped['blockers'] == []
    for row in scoped['source_bindings']:
        assert rows.get(row['path'], row) == row
        rows[row['path']] = row
    for path in [parent, context, Path(__file__)]:
        rows[bind(path)['path']] = bind(path)
    for row in rows.values():
        assert bind(ROOT / row['path']) == row, row['path']
    put(output, {'schema_version': 'lab-R06-format-resolution-source/v1-candidate',
                 'files': [rows[key] for key in sorted(rows)],
                 'parent_partial_binding': bind(parent), 'context_binding': bind(context),
                 'frozen_before_format_observations': True,
                 'authority_effect': 'none', 'actual_owner_outcome': None})
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(output), 'files': len(rows)}), flush=True)

def guard(pin):
    source = HERE / 'source-manifest.json'
    assert bind(source)['sha256'] == pin
    selected = json.loads(R.read(source))
    for row in selected['files']:
        assert bind(ROOT / row['path']) == row, row['path']
    return selected

def resolve(pin):
    source = guard(pin)
    parent_inventory = PARENT / 'inventory.json'
    inventory = json.loads(R.read(parent_inventory))
    original = [row for row in inventory['rows'] if row['inspection'] == 'refused']
    assert len(original) == 34
    toml, excluded = [], []
    for row in original:
        path = ROOT / row['path']
        raw = R.read(path)
        assert R.sha(raw) == row['sha256']
        if path.suffix == '.toml':
            parsed = tomllib.loads(raw.decode('utf-8'))
            assert isinstance(parsed, dict)
            findings = R.scan(json.dumps(parsed, sort_keys=True, default=lambda v: v.isoformat()).encode(), row['path'])
            assert not findings, 'selected TOML input needs private-field review'
            toml.append({'path': row['path'], 'sha256': row['sha256'], 'size_bytes': len(raw),
                         'parser': 'python-stdlib-tomllib', 'parser_result': 'PASS',
                         'private_field_findings': [], 'original_json_scanner_refusal_retained': True,
                         'public_body_export_allowed': False,
                         'disposition': 'inspected-source-awaiting-final-release-selection'})
        else:
            assert path.suffix in {'.log', '.stdout', '.wire'} or path.name.endswith(('.stdout', '.stdout.log'))
            excluded.append({'path': row['path'], 'sha256': row['sha256'], 'size_bytes': len(raw),
                             'original_json_scanner_refusal_retained': True,
                             'content_privacy_qualification_claimed': False,
                             'disposition': 'candidate-diagnostic-exclusion-proposal',
                             'public_body_export_allowed': False,
                             'rationale': 'Diagnostic stdout, logs and wire captures are retained evidence; their raw bodies are excluded from this proposed public code release. This proposal changes no file or prior classification.'})
    assert len(toml) == 5 and len(excluded) == 29
    assert {row['path'] for row in toml + excluded} == {row['path'] for row in original}
    guard(pin)
    output = HERE / 'format-resolution.json'
    put(output, {'schema_version': 'lab-R06-format-resolution/v1-candidate', 'result': 'PASS-scoped-resolution',
                 'checked_at': datetime.now(timezone.utc).isoformat(),
                 'parent_inventory_binding': bind(parent_inventory), 'source_binding': bind(HERE / 'source-manifest.json'),
                 'original_scanner_refusals': 34, 'actual_TOML_files_parsed': 5,
                 'diagnostic_exclusion_proposals': 29, 'TOML_observations': toml,
                 'diagnostic_exclusions': excluded, 'private_field_files_still_require_review': 61,
                 'originals_or_permissions_changed': False, 'prior_classifications_changed': False,
                 'final_public_selection_complete': False, 'publication_authorized': False,
                 'authority_effect': 'none', 'actual_owner_outcome': None,
                 'R06_complete': False, 'task_complete': False, 'goal_complete': False})
    rows = {row['path']: row for row in source['files']}
    for path in [HERE / 'source-manifest.json', output]:
        rows[bind(path)['path']] = bind(path)
    proof = HERE / 'receipts/proof-0001.json'
    put(proof, {'schema_version': 'lab-R06-format-resolution-partial-proof/v1-candidate', 'result': 'PASS',
                'files': [rows[key] for key in sorted(rows)], 'format_resolution_binding': bind(output),
                'actual_TOML_files_parsed': 5, 'diagnostic_exclusion_proposals': 29,
                'private_field_files_still_require_review': 61,
                'remaining_obligations': ['Resolve61private-field reviews under exact final release selection.',
                                          'Include and inspect final API/workflow/ontology/schema/evidence bytes.',
                                          'Reconcile candidate release privacy at R07/S02 before actual R08.'],
                'authority_effect': 'none', 'actual_owner_outcome': None,
                'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'PASS-scoped-resolution', 'TOML_files_parsed': 5,
                      'diagnostic_exclusion_proposals': 29, 'proof_binding': bind(proof)}), flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['freeze', 'resolve'])
    parser.add_argument('--source-sha256')
    args = parser.parse_args()
    if args.command == 'freeze':
        freeze()
    else:
        assert args.source_sha256
        resolve(args.source_sha256)
