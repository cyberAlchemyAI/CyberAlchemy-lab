"""Resolve admitted migration contracts without activating their domain effects."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = Path('authority/decisions/migration-contracts/v1/registry.json')


def load_registry(root=ROOT):
    def read(path):
        return json.loads((root / path).read_text())

    def verify(ref):
        path = (root / ref['path']).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError('Binding outside repository')
        if hashlib.sha256(path.read_bytes()).hexdigest() != ref['sha256']:
            raise ValueError('Binding drift: ' + ref['path'])

    registry = read(REGISTRY)
    decision = read(registry['decision_path'])
    verify(decision['registry'])
    if decision['registry']['path'] != str(REGISTRY):
        raise ValueError('Wrong registry selected by decision')
    if decision['status'] != 'owner-admitted-within-migration':
        raise ValueError('Missing admission')
    for key in ('approval', 'snapshot', 'dependency_inventory'):
        verify(registry[key])
    approval = read(registry['approval']['path'])
    if approval['status'] != 'approved':
        raise ValueError('Missing approval')
    for ref in approval['subject'].values():
        verify(ref)
    approved = {entry['target_id']: entry for entry in approval['targets']}
    entries = registry['entries']
    if len(entries) != 83 or len(approved) != 83 or {e['target_id'] for e in entries} != set(approved):
        raise ValueError('Approved membership mismatch')
    for ref in read(registry['snapshot']['path'])['materials']:
        verify(ref)
    deps = read(registry['dependency_inventory']['path'])
    for ref in deps['definitions'] + deps['admitted_definitions']:
        verify(ref)
    for entry in entries:
        if entry['status'] != 'admitted-migration-contract' or entry['scope'] != registry['scope']:
            raise ValueError('Admission scope mismatch')
        if entry['decision_ref'] != decision['decision_id'] or entry['action_authorized'] is not False:
            raise ValueError('Invalid admission effect')
        for key in ('binding', 'contract'):
            if entry[key] != approved[entry['target_id']][key]:
                raise ValueError('Unapproved contract substitution')
            verify(entry[key])
        contract = read(entry['contract']['path'])
        if entry['semantic_definition_bindings'] != contract['semantic_definition_bindings']:
            raise ValueError('Dependency posture changed')
    return registry


def resolve(target_id, scope, root=ROOT):
    registry = load_registry(root)
    if scope != registry['scope']:
        raise ValueError('Contract is not admitted in the requested scope')
    for entry in registry['entries']:
        if entry['target_id'] == target_id:
            return entry
    raise ValueError('Target is not admitted by this registry: ' + target_id)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target', nargs='?')
    parser.add_argument('--scope', default='cyberAlchemy-v2-to-CyberAlchemy-lab-migration')
    args = parser.parse_args()
    try:
        result = resolve(args.target, args.scope) if args.target else {
            'result': 'PASS', 'contracts': len(load_registry()['entries']), 'action_authorized': False,
        }
    except (ValueError, KeyError, OSError) as exc:
        print(json.dumps({'result': 'BLOCK', 'error': str(exc)}))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
