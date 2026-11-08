#!/usr/bin/env python3
"""Retain a real command-by-command local exercise; never retry unknown effects."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

PACKAGE = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--home', required=True);p.add_argument('--run-root', required=True)
    p.add_argument('--principal', required=True);p.add_argument('--store-id', required=True)
    p.add_argument('--authorize-local', action='store_true', help='Explicitly select signed local native admission for this exercise.')
    args = p.parse_args()
    root = Path(args.run_root).absolute();root.mkdir(mode=0o700)
    def write(name, value):
        with (root / name).open('x') as stream:json.dump(value, stream, sort_keys=True, indent=2);stream.write('\n')
    index = []
    def command(label, *arguments):
        proc = subprocess.run([sys.executable, '-I', '-B', str(PACKAGE / 'define.py'), *arguments], capture_output=True, timeout=180)
        result = json.loads(proc.stdout)
        write(label + '.json', {'exit_code': proc.returncode, 'response': result})
        index.append({'phase': label, 'exit_code': proc.returncode})
        if proc.returncode:raise RuntimeError('phase refused: ' + label)
        return result['result']
    try:
        command('01-doctor', 'doctor')
        command('02-setup', 'setup', '--home', args.home, '--principal', args.principal, '--store-id', args.store_id)
        command('03-example', 'example', '--home', args.home, '--output', str(root / 'input'))
        command('04-prepare', 'prepare', '--home', args.home, '--input', str(root / 'input'), '--permit-retention', '--output', str(root / 'package'))
        review = command('05-review', 'review', '--home', args.home, '--package', str(root / 'package'),
                         '--id', 'user-journey-0001', '--output', str(root / 'review'))
        if not args.authorize_local:
            write('RESULT.json', {'result': 'PREPARED-awaiting-explicit-local-authorization', 'phases': index, 'canonical_admission': False})
            return 0
        command('06-authorize', 'authorize', '--home', args.home, '--proposal', str(root / 'review/proposal.json'), '--output', str(root / 'approval'))
        applied = command('07-apply', 'apply', '--home', args.home, '--proposal', str(root / 'review/proposal.json'), '--approval', str(root / 'approval/approval.json'))
        repeated = command('08-idempotent-retry', 'apply', '--home', args.home, '--proposal', str(root / 'review/proposal.json'), '--approval', str(root / 'approval/approval.json'))
        if not repeated['idempotent'] or repeated['transaction_digest'] != applied['transaction_digest']:
            raise RuntimeError('idempotent native commit mismatch')
        restored = command('09-fresh-reconstruct', 'reconstruct', '--home', args.home, '--work', review['work_ref'], '--output', str(root / 'restored'))
        def members(directory):
            return {str(f.relative_to(directory)): hashlib.sha256(f.read_bytes()).hexdigest() for f in directory.rglob('*') if f.is_file()}
        before, after = members(root / 'package'), members(root / 'restored')
        if before != after:raise RuntimeError('original/restored member mismatch')
        command('10-fresh-definition-context', 'context', '--home', args.home, '--definition', 'cal.definition.user-journey', '--output', str(root / 'new-context'))
        status = command('11-status', 'status', '--home', args.home)
        result = {'result': 'PASS-real-local-native-integration', 'completed_at': datetime.now(timezone.utc).isoformat(),
                  'principal_ref': status['principal_ref'], 'scope_ref': status['scope_ref'], 'project_ref': status['project_ref'],
                  'work_ref': review['work_ref'], 'native_head': status['head'], 'root_sha256': restored['root_sha256'],
                  'member_hashes': before, 'exact_reconstruction': True, 'idempotent_commit': True,
                  'fresh_process_definition_resolution': True, 'session_memory_restored': False,
                  'canonical_admission': False, 'independent_semantic_acceptance': False, 'phases': index}
        write('RESULT.json', result)
        print(json.dumps({'result': result['result'], 'run_root': str(root), 'member_count': len(before), 'canonical_admission': False}))
        return 0
    except BaseException as exc:
        write('FAILED-RETAINED.json', {'result': 'RECONCILIATION-REQUIRED', 'failed_type': type(exc).__name__,
                                     'completed_phases': index, 'continuation': 'Inspect retained phase responses and native head; no effect was retried.'})
        raise


if __name__ == '__main__':raise SystemExit(main())
