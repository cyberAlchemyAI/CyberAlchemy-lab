#!/usr/bin/env python3
"""Use the unchanged frozen runtime with the separate confirmation schedule."""
import argparse, hashlib, importlib.util, json
from pathlib import Path
R = Path(__file__).resolve().parents[1]

def read(path): return json.loads(path.read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def runtime():
    manifest = read(R / 'confirmation-tool-manifest.json')
    for entry in manifest['files']:
        assert sha(R / entry['path']) == entry['sha256'], 'Confirmation binding changed'
    schedule = read(R / 'confirmation-schedule.json')
    freeze = read(R / 'finalist-freeze.json')
    assert schedule['finalist_freeze_sha256'] == sha(R / 'finalist-freeze.json')
    assert schedule['selection_sha256'] == sha(R / 'reports/finalist-selection.json')
    assert schedule['finalists'] == freeze['finalists']
    spec = importlib.util.spec_from_file_location('frozen_generation_runtime', R / 'tools/runtime.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original_lookup = module.unit
    units = {u['unit_id']: u for u in schedule['units']}
    assert len(units) == len(schedule['units']) == freeze['confirmation_units']
    def lookup(uid):
        return units[uid] if uid in units else original_lookup(uid)
    module.unit = lookup
    return module, schedule

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['prepare', 'validate', 'spawn', 'join', 'status'])
    parser.add_argument('unit', nargs='?')
    parser.add_argument('role', nargs='?')
    parser.add_argument('agent', nargs='?')
    args = parser.parse_args()
    module, schedule = runtime()
    if args.command == 'prepare': result = module.make(args.unit, args.role)
    elif args.command == 'validate': result = module.validate(args.unit, args.role)
    elif args.command in ['spawn', 'join']: result = module.record(args.unit, args.role, args.agent, args.command)
    else:
        rows = []
        for unit in schedule['units']:
            states = {role: module.validate(unit['unit_id'], role) for role in unit['roles']}
            rows.append({'unit_id': unit['unit_id'], 'case_id': unit['case_id'],
                         'condition': unit['condition'], 'repetition': unit['repetition'],
                         'valid_complete': all(v['valid'] for v in states.values())})
        result = {'units': rows, 'completed': sum(r['valid_complete'] for r in rows), 'total': len(rows)}
    print(json.dumps(result, indent=2))
