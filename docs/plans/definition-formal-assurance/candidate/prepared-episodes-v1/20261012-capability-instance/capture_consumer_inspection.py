"""Capture actual terminal results of the producer or separate read-only replay."""
from pathlib import Path
import json, subprocess, sys
root = Path.cwd()
prepared = Path(__file__).resolve().parent
unit = root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.capability-instance'
replay = '--replay' in sys.argv
argv = [sys.executable, '-B', str(unit/'inspect_carrier_consumers.py')]
if not replay:
    argv.append('--write')
stem = 'consumer-inspection-replay' if replay else 'consumer-inspection'
result = subprocess.run(argv, cwd=root, capture_output=True)
for kind, content in [('stdout', result.stdout), ('stderr', result.stderr)]:
    with (prepared/(stem+'-'+kind+'.txt')).open('xb') as stream:
        stream.write(content)
with (prepared/(stem+'-command-result.json')).open('x') as stream:
    json.dump({'argv': argv, 'exit_code': result.returncode, 'stdout': stem+'-stdout.txt', 'stderr': stem+'-stderr.txt'}, stream, indent=2)
    stream.write('\n')
print(result.stdout.decode(), end='')
print(result.stderr.decode(), end='', file=sys.stderr)
raise SystemExit(result.returncode)
