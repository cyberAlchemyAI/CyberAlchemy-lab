from pathlib import Path
import json, subprocess, sys
root, prepared = Path.cwd(), Path(__file__).resolve().parent
unit = root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.capability-instance'
replay = '--replay' in sys.argv
argv = [sys.executable, '-B', str(unit/'verify_authority_profile.py')] + ([] if replay else ['--write'])
stem = 'profile-replay' if replay else 'profile'
result = subprocess.run(argv, cwd=root, capture_output=True)
for kind, content in [('stdout', result.stdout), ('stderr', result.stderr)]:
    with (prepared/(stem+'-'+kind+'.txt')).open('xb') as stream: stream.write(content)
record = {'argv': argv, 'exit_code': result.returncode, 'stdout': stem+'-stdout.txt', 'stderr': stem+'-stderr.txt'}
with (prepared/(stem+'-command-result.json')).open('x') as stream:
    json.dump(record, stream, indent=2); stream.write('\n')
if not replay:
    for kind, content in [('stdout.txt', result.stdout), ('stderr.txt', result.stderr), ('command-result.json', (json.dumps(record, indent=2)+'\n').encode())]:
        with (unit/(stem+'-'+kind)).open('xb') as stream: stream.write(content)
print(result.stdout.decode(), end=''); print(result.stderr.decode(), end='', file=sys.stderr)
raise SystemExit(result.returncode)
