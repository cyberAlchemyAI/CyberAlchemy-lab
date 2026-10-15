from pathlib import Path
import json, subprocess, sys
prepared = Path(__file__).resolve().parent
argv = [sys.executable, '-B', str(prepared/'audit_consumer_closeout.py')]
result = subprocess.run(argv, cwd=Path.cwd(), capture_output=True)
for kind, content in [('stdout', result.stdout), ('stderr', result.stderr)]:
    with (prepared/('consumer-profile-audit-'+kind+'.txt')).open('xb') as stream: stream.write(content)
with (prepared/'consumer-profile-audit-command-result.json').open('x') as stream:
    json.dump({'argv': argv, 'exit_code': result.returncode, 'stdout': 'consumer-profile-audit-stdout.txt', 'stderr': 'consumer-profile-audit-stderr.txt'}, stream, indent=2); stream.write('\n')
print(result.stdout.decode(), end=''); print(result.stderr.decode(), end='', file=sys.stderr)
raise SystemExit(result.returncode)
