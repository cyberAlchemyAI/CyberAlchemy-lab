"""Run remaining whole-class buckets; observe each real child exit separately."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
PLAN = RUN / 'final-api-regression-plan-0274.json'
PLAN_PIN = 'b04c3f6a9953765b807adf4f8ef72b480c6c51985a1b1c563535395f86b8ac40'
PREFIX = 'final-api-regression-0173-0274'
OUTER = RUN / 'final-api-regression-0173-0190.execution.lock'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def execute(bucket):
    label = bucket.replace(':', '-') if bucket.startswith('worker:') else 'sequential-' + hashlib.sha256(bucket.encode()).hexdigest()[:16]
    report = RUN / (PREFIX + '.' + label + '.json')
    command = RUN / (PREFIX + '.' + label + '.command.json')
    if command.exists():
        observed = json.loads(command.read_bytes())
        assert report.is_file() and observed['report_binding']['sha256'] == sha(report)
        return {'bucket': bucket, 'previous_actual_exit': observed['actual_os_exit_code']}
    assert not report.exists() and not report.with_suffix('.events.jsonl').exists()
    data = json.loads(PLAN.read_bytes())
    assert sha(PLAN) == PLAN_PIN
    args = ['flock', '-x' if bucket.startswith('sequential:') else '-s', str(OUTER), sys.executable, '-B',
            str(RUN / 'final-api-regression-0270.py'), '--api-directory', data['api_directory'],
            '--source', data['source_sha256'], '--profile', data['profile_sha256'],
            '--plan', str(PLAN), '--plan-sha256', PLAN_PIN, '--output-prefix', PREFIX, '--worker', bucket]
    started = datetime.now(timezone.utc).isoformat()
    log = RUN / (PREFIX + '.' + label + '.log')
    with log.open('xb') as stream:
        result = subprocess.run(args, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    value = {'schema_version': 'lab-actual-regression-command-observation/v1-candidate',
             'bucket': bucket, 'started_at': started, 'ended_at': datetime.now(timezone.utc).isoformat(),
             'actual_os_exit_code': result.returncode, 'argv': args, 'plan_sha256': PLAN_PIN,
             'log_sha256': sha(log), 'report_binding': None if not report.exists() else
             {'path': str(report.relative_to(ROOT)), 'sha256': sha(report)}, 'authority_effect': 'none'}
    with command.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'bucket': bucket, 'actual_os_exit_code': result.returncode,
                      'report_exists': report.exists()}), flush=True)
    return value

def main():
    assert sha(PLAN) == PLAN_PIN
    plan = json.loads(PLAN.read_bytes())
    # Shared, ordinary buckets can coexist with the other native qualification.
    # Source-corrupting classes acquire the same outer EX lock afterwards.
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        jobs = [executor.submit(execute, 'worker:' + key)
                for key in sorted(plan['workers'], key=int) if key not in ('1','8')]
        for job in jobs:
            job.result()
    for key in plan['sequential_classes']:
        execute('sequential:' + key)
    print(json.dumps({'scheduler_terminal': True, 'all_commands_observed': True,
                      'aggregate_conformance': 'requires-independent-aggregate', 'authority_effect': 'none'}), flush=True)

if __name__ == '__main__':
    main()
