"""One separate job per invocation; terminal evidence never substitutes launcher success."""
from pathlib import Path
import datetime, json, os, subprocess, sys
root, prepared = Path.cwd(), Path(__file__).resolve().parent
unit = root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.capability-instance'
job = sys.argv[1]
assert job in ['dependency', 'inventory']
fresh = '--fresh' in sys.argv
stem = ('fresh-' if fresh else '')+job
script = 'verify_dependencies.py' if job == 'dependency' else 'verify_current_inventory.py'
argv = [sys.executable, '-B', str(unit/script)] + ([] if fresh else ['--write'])
for folder in [prepared, unit]:
    for suffix in ['stdout.txt', 'stderr.txt', 'command-result.json']:
        assert not (folder/(stem+'-'+suffix)).exists(), 'Already captured job; inspect state before attempting another run'
assert not (prepared/(stem+'-live-observation.json')).exists(), 'A prior process observation needs explicit reconciliation'
child = subprocess.Popen(argv, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
def identity(pid):
    path = Path('/proc')/str(pid)
    return {'pid': pid, 'cmdline': (path/'cmdline').read_bytes().replace(b'\0', b' ').decode(),
            'start_ticks': (path/'stat').read_text().rsplit(')', 1)[1].split()[19]}
observation = {'schema_version': 'CI-single-job-process-observation/v1-candidate', 'job': job,
               'fresh': fresh, 'argv': argv, 'capture_process': identity(os.getpid()),
               'child_process': identity(child.pid), 'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'actual_terminal_result': None, 'authority_effect': 'none'}
with (prepared/(stem+'-live-observation.json')).open('x') as stream:
    json.dump(observation, stream, indent=2); stream.write('\n')
stdout, stderr = child.communicate()
record = {'check': job, 'argv': argv, 'exit_code': child.returncode,
          'stdout': stem+'-stdout.txt', 'stderr': stem+'-stderr.txt'}
for folder in [prepared, unit]:
    for suffix, content in [('stdout.txt', stdout), ('stderr.txt', stderr),
                            ('command-result.json', (json.dumps(record, indent=2)+'\n').encode())]:
        with (folder/(stem+'-'+suffix)).open('xb') as stream: stream.write(content)
print(stdout.decode(), end=''); print(stderr.decode(), end='', file=sys.stderr)
if child.returncode or stderr:
    raise SystemExit(child.returncode or 1)
if fresh:
    assert stdout == (unit/(job+'-stdout.txt')).read_bytes(), 'Fresh terminal stdout differs from initial producer'
