"""Separate seal or audit, with captures outside the sealed file set."""
from pathlib import Path
import json, subprocess, sys
root, prepared = Path.cwd(), Path(__file__).resolve().parent
unit = root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.capability-realization-binding'
boundary = sys.argv[1]
assert boundary in ['seal', 'audit']
script = 'finalize.py' if boundary == 'seal' else 'check_delivery.py'
argv = [sys.executable, '-B', str(unit/script)]
result = subprocess.run(argv, cwd=root, capture_output=True)
stem = 'full-delivery-'+boundary
for kind, content in [('stdout', result.stdout), ('stderr', result.stderr)]:
    with (prepared/(stem+'-'+kind+'.txt')).open('xb') as stream: stream.write(content)
with (prepared/(stem+'-command-result.json')).open('x') as stream:
    json.dump({'argv': argv, 'exit_code': result.returncode, 'stdout': stem+'-stdout.txt', 'stderr': stem+'-stderr.txt'}, stream, indent=2); stream.write('\n')
print(result.stdout.decode(), end=''); print(result.stderr.decode(), end='', file=sys.stderr)
raise SystemExit(result.returncode)
