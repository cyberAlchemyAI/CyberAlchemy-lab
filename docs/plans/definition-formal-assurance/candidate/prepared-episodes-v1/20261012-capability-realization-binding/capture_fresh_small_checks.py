"""Fresh contract/model/source/profile checks; heavy checks have separate processes."""
from pathlib import Path
import json, subprocess, sys
root, prepared = Path.cwd(), Path(__file__).resolve().parent
unit = root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.capability-realization-binding'
impl = root/'craft/formalization/candidates/definition-assurance-v1'
jobs = [('contract', impl/'contracts.py', ['validate', '--kind', 'interpretation', '--input', str(unit/'t.json')]),
        ('model', unit/'verify_candidate.py', []), ('source', unit/'verify_source_checks.py', []),
        ('profile', unit/'verify_authority_profile.py', [])]
rows = []
for name, script, arguments in jobs:
    stem = 'fresh-'+name
    for folder in [unit, prepared]:
        for suffix in ['stdout.txt', 'stderr.txt', 'command-result.json']:
            assert not (folder/(stem+'-'+suffix)).exists(), 'Retain or resume a prior result before rerunning'
    argv = [sys.executable, '-B', str(script)] + arguments
    result = subprocess.run(argv, cwd=root, capture_output=True)
    row = {'check': name, 'argv': argv, 'exit_code': result.returncode,
           'stdout': stem+'-stdout.txt', 'stderr': stem+'-stderr.txt'}
    for folder in [unit, prepared]:
        for suffix, content in [('stdout.txt', result.stdout), ('stderr.txt', result.stderr),
                                ('command-result.json', (json.dumps(row, indent=2)+'\n').encode())]:
            with (folder/(stem+'-'+suffix)).open('xb') as stream: stream.write(content)
    assert result.returncode == 0 and not result.stderr, (name, result.returncode, result.stderr.decode())
    original = 'fresh-types-contract-stdout.txt' if name == 'contract' else name+'-stdout.txt'
    assert result.stdout == (unit/original).read_bytes(), 'Fresh small-check stdout differs: '+name
    rows.append(row)
    print(json.dumps({'check': name, 'actual_exit_code': result.returncode, 'stdout_matches_initial': True}), flush=True)
with (prepared/'fresh-small-check-results.json').open('x') as stream:
    json.dump(rows, stream, indent=2); stream.write('\n')
