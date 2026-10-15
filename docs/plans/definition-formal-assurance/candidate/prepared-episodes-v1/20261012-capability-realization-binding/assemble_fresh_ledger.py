"""Assemble only six actual successful terminal records; no observation is a result."""
from pathlib import Path
import json, sys
root, prepared = Path.cwd(), Path(__file__).resolve().parent
unit = root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.capability-realization-binding'
impl = root/'craft/formalization/candidates/definition-assurance-v1'
rows = []
scripts = {'model': 'verify_candidate.py', 'source': 'verify_source_checks.py', 'profile': 'verify_authority_profile.py',
           'dependency': 'verify_dependencies.py', 'inventory': 'verify_current_inventory.py'}
for name in ['contract', 'model', 'source', 'profile', 'dependency', 'inventory']:
    path = unit/('fresh-'+name+'-command-result.json')
    row = json.loads(path.read_bytes())
    assert row['check'] == name and row['exit_code'] == 0 and not (unit/row['stderr']).read_bytes()
    assert row == json.loads((prepared/path.name).read_bytes())
    expected = [sys.executable, '-B', str(impl/'contracts.py'), 'validate', '--kind', 'interpretation', '--input', str(unit/'t.json')] if name == 'contract' else [sys.executable, '-B', str(unit/scripts[name])]
    assert row['argv'] == expected
    original = 'fresh-types-contract-stdout.txt' if name == 'contract' else name+'-stdout.txt'
    assert (unit/row['stdout']).read_bytes() == (unit/original).read_bytes()
    rows.append(row)
for folder in [unit, prepared]:
    with (folder/'fresh-command-results.json').open('x') as stream:
        json.dump(rows, stream, indent=2); stream.write('\n')
print(json.dumps({'result': 'PASS-six-actual-independent-delivery-checks', 'checks': [x['check'] for x in rows], 'authority_effect': 'none'}, indent=2))
