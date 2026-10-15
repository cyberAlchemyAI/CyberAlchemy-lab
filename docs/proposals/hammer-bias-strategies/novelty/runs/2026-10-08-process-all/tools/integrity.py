#!/usr/bin/env python3
"""Prospective byte freeze and read-only verification, not outcome assessment."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root=R):
    root = Path(root)
    frozen = json.loads((root / 'freeze-manifest.json').read_text())
    errors = []
    for relative, expected in frozen['hashes'].items():
        path = root / relative
        if not path.is_file() or digest(path) != expected:
            errors.append(relative + ': missing or changed frozen bytes')
    if frozen['schedule_sha256'] != digest(root / 'schedule.json'):
        errors.append('schedule digest mismatch')
    return {'valid': not errors, 'errors': errors,
            'checked': len(frozen['hashes']), 'frozen_at': frozen['frozen_at_utc']}


def freeze(root=R):
    root = Path(root)
    if (root / 'freeze-manifest.json').exists():
        raise ValueError('Freeze exists; verify instead of replacing it')
    events = [json.loads(line) for line in (root / 'receipts/events.jsonl').read_text().splitlines()]
    if any(e.get('event') == 'spawn' and e.get('stage') != 'preflight' for e in events):
        raise ValueError('A scored role has already spawned; a prospective freeze is no longer possible')
    required = ['PROTOCOL.md', 'criteria.json', 'strategy-contracts.json',
                'review-contract.json', 'schedule.json', 'conditions.json',
                'STRATEGIES.md', 'reports/preparation-code-check.json',
                'reports/preflight-review-coverage.json', 'reports/preflight-complete-source.json',
                'reports/review-matrix.json', 'reports/preflight.json',
                'design/round3-balancer.json', 'design/dispatch-validation.json',
                'design/reconciliation.json']
    if json.loads((root / 'design/round3-balancer.json').read_text()).get('status') == 'block':
        raise ValueError('Final launch review blocks freeze')
    if json.loads((root / 'reports/preflight.json').read_text()).get('status') != 'pass':
        raise ValueError('Unscored preflight has not passed')
    paths = {root / name for name in required}
    for folder in ['tools', 'inputs', 'cases', 'archives', 'fixtures', 'dispatches', 'design']:
        paths.update(p for p in (root / folder).rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
    paths.update(p for p in (root / 'prompts').glob('*.txt'))
    for name in ['runtime-code-check.json', 'ranking-code-check.json', 'evaluation-code-check.json']:
        paths.add(root / 'reports' / name)
    hashes = {str(p.relative_to(root)): digest(p) for p in sorted(paths)}
    document = {'version': 1, 'status': 'prospective_frozen',
                'frozen_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'schedule_sha256': digest(root / 'schedule.json'), 'hashes': hashes,
                'scored_roles_spawned_before_freeze': 0,
                'claim_ceiling': 'Frozen experiment mechanics, not successful reasoning or field effects'}
    with (root / 'freeze-manifest.json').open('x') as stream:
        json.dump(document, stream, indent=2)
        stream.write('\n')
    return verify(root)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['freeze', 'verify'])
    args = parser.parse_args()
    result = freeze() if args.command == 'freeze' else verify()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['valid'] else 1)
