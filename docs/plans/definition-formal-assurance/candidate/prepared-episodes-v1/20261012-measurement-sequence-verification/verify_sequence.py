"""Read-only verification of existing measurement formalization candidates.

New evidence is written only alongside this verifier, outside all sealed packets.
Historical exact-file-set audits are not rerun after subsequent packet additions.
"""
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[6]
OUT = pathlib.Path(__file__).resolve().parent
BASE = ROOT / 'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions'
IDS = ['cal.definition.measurement-method', 'cal.definition.measurement-result', 'cal.definition.provenance']

def put(name, data):
    with (OUT / name).open('x') as stream:
        json.dump(data, stream, indent=2, sort_keys=True)
        stream.write('\n')

def main():
    cache = {}
    rows = []
    for identity in IDS:
        unit = BASE / identity
        manifest = json.loads((unit / 'delivery-manifest.json').read_bytes())
        mismatches = []
        for binding in manifest['files']:
            path = ROOT / binding['path']
            if path not in cache:
                cache[path] = hashlib.sha256(path.read_bytes()).hexdigest()
            if cache[path] != binding['sha256']:
                mismatches.append(binding['path'])
        recorded = json.loads((unit / 'fresh-command-results.json').read_bytes())
        history = []
        for check in recorded:
            history.append({'check': check['check'], 'exit_code': check['exit_code'],
                            'stderr_empty': not (unit / check['stderr']).read_bytes()})
        row = {'definition': identity, 'manifest_files_verified': len(manifest['files']),
               'hash_mismatches': mismatches, 'recorded_six_terminal_checks': history,
               'current_replays': [], 'counts': json.loads((unit / 'receipt.json').read_bytes())['validation']}
        rows.append(row)
        assert not mismatches, mismatches
        assert len(history) == 6 and all(c['exit_code'] == 0 and c['stderr_empty'] for c in history)
        for check in recorded:
            if check['check'] not in ['contract', 'model', 'source', 'profile']:
                continue
            argv = list(check['argv'])
            argv.insert(1, '-B')
            result = subprocess.run(argv, cwd=ROOT, capture_output=True)
            stem = identity.rsplit('.', 1)[-1] + '-' + check['check']
            for suffix, data in [('stdout.txt', result.stdout), ('stderr.txt', result.stderr)]:
                with (OUT / (stem + '-' + suffix)).open('xb') as stream:
                    stream.write(data)
            observation = {'check': check['check'], 'argv': argv, 'exit_code': result.returncode,
                           'stdout': stem + '-stdout.txt', 'stderr': stem + '-stderr.txt',
                           'stdout_matches_sealed_capture': result.stdout == (unit / check['stdout']).read_bytes(),
                           'stderr_empty': not result.stderr}
            put(stem + '-command-result.json', observation)
            row['current_replays'].append(observation)
            print(identity, check['check'], result.returncode, flush=True)
            assert result.returncode == 0 and not result.stderr and observation['stdout_matches_sealed_capture'], observation
    for path, before in cache.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == before, str(path)
    report = {'schema_version': 'measurement-sequence-current-verification/v1-candidate',
              'result': 'PASS-for-existing-candidate-deliveries', 'definitions': rows,
              'unique_sealed_files_verified_before_and_after': len(cache),
              'requested_order_preserved': IDS, 'fresh_current_commands': 12,
              'historical_exact_file_set_audits_rerun': False,
              'dependency_and_inventory_replays_this_verification': False,
              'source_owner_accepted_whole_translations': 0, 'whole_definition_proofs': 0,
              'source_fidelity': 'pending', 'semantic_ready': False,
              'authority_effect': 'none', 'goal_status': 'active',
              'original_episode_completion': 'not-established'}
    put('verification.json', report)
    print(json.dumps({'result': report['result'], 'unique_files': len(cache), 'current_commands': 12}), flush=True)

if __name__ == '__main__':
    main()
