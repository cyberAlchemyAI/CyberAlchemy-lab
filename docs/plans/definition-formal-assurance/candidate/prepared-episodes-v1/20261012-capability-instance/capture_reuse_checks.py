from pathlib import Path
import json, subprocess, sys
root, prepared = Path.cwd(), Path(__file__).resolve().parent
unit = root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.capability-instance'
argv = [sys.executable, '-B', str(unit/'verify_static_snapshot_reuse.py')]
result = subprocess.run(argv, cwd=root, capture_output=True)
record = {'argv': argv, 'exit_code': result.returncode, 'stdout': 'reuse-stdout.txt', 'stderr': 'reuse-stderr.txt'}
for folder in [prepared, unit]:
    for kind, content in [('stdout.txt', result.stdout), ('stderr.txt', result.stderr), ('command-result.json', (json.dumps(record, indent=2)+'\n').encode())]:
        with (folder/('reuse-'+kind)).open('xb') as stream: stream.write(content)
print(result.stdout.decode(), end=''); print(result.stderr.decode(), end='', file=sys.stderr)
raise SystemExit(result.returncode)
