"""Verify every preserved preparation member before final admission composition."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
INPUTS = (
    'implementation/lab-review/candidates/v1/packages/0001/preparation.json',
    'implementation/lab-workflows/candidates/v1/review/W08/packages/0001/preparation.json',
    'implementation/lab-ontology/candidates/v1/review/O06/packages/0001/preparation.json',
)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}

def main():
    output = HERE / 'inventory.json'
    assert not output.exists(), 'exclusive evidence required'
    members, problems, inputs, seen, paths = [], [], [], set(), {}
    for name in INPUTS:
        path = ROOT / name
        data = json.loads(path.read_bytes())
        assert data['authority_effect'] == 'none' and data['actual_owner_outcome'] is None
        inputs.append(binding(path))
        for member in data['members']:
            identity = member.get('member_id', member.get('member_ref'))
            assert identity and identity not in seen
            seen.add(identity)
            assert member['selected_outcome'] is None and not member['current_owner_authority_verified']
            assert member['actual_answering_principal_ref'] is None
            local = []
            def verify_rows(value, pointer=''):
                if isinstance(value, dict):
                    if set(value) == {'path', 'sha256'}:
                        relative = Path(value['path'])
                        target = ROOT / relative
                        reason = None
                        if relative.is_absolute() or '..' in relative.parts:
                            reason = 'invalid-repository-path'
                        elif not target.is_file() or target.is_symlink():
                            reason = 'missing-or-nonregular'
                        elif sha(target.read_bytes()) != value['sha256']:
                            reason = 'bound-bytes-changed'
                        old = paths.get(value['path'])
                        if old is not None and old != value['sha256']:
                            local.append({'pointer': pointer, 'binding': value, 'reason': 'different-members-select-different-bytes'})
                        paths[value['path']] = value['sha256']
                        if reason:
                            local.append({'pointer': pointer, 'binding': value, 'reason': reason})
                    for key, item in value.items():
                        verify_rows(item, pointer + '/' + key.replace('~', '~0').replace('/', '~1'))
                elif isinstance(value, list):
                    for index, item in enumerate(value):
                        verify_rows(item, pointer + '/' + str(index))
            verify_rows(member)
            copied = dict(member)
            copied['preparation_input_binding'] = inputs[-1]
            copied['original_preparation_member_sha256'] = sha(json.dumps(member, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode())
            copied['current_binding_problems'] = local
            copied['final_decision_core_binding'] = None
            copied['final_target_operation_selection'] = None
            members.append(copied)
            problems.extend({'member_ref': identity, **problem} for problem in local)
    graph = {m.get('member_id', m.get('member_ref')): m.get('dependencies', []) for m in members}
    def visit(node, stack):
        if node in stack:
            raise ValueError('member dependency cycle: ' + node)
        for dep in graph[node]:
            if dep not in graph:
                problems.append({'member_ref': node, 'reason': 'unresolved-preparation-dependency', 'dependency': dep})
            else:
                visit(dep, stack | {node})
    for node in graph:
        visit(node, set())
    value = {
        'schema_version': 'lab-final-preserved-member-inventory/v1-candidate',
        'result': 'PASS' if not problems else 'FAIL',
        'input_bindings': inputs, 'generator_binding': binding(Path(__file__)),
        'member_count': len(members), 'distinct_bound_paths': len(paths),
        'members': members, 'problems': problems,
        'final_package_complete': False, 'ready_for_R08': False,
        'remaining_assembly_obligations': [
            'Choose exact materialized final target operations and independent stable cores for every member',
            'Reconcile final API/runtime/schema/registry/implementation and additional custody members',
            'Bind genuine human three-journey pilot and exact final qualification evidence',
            'Resolve actual owner-role authority, base State and all-member effects',
            'Prove final mixed-target publisher, recovery, carrier fit and acyclic digest closure',
        ],
        'authority_effect': 'none', 'actual_owner_outcome': None,
        'claim_ceiling': 'Exact preserved preparation inventory and current binding checks only; no stable Decision core, final admission package, pilot, owner authority or task completion.',
    }
    with output.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': value['result'], 'members': len(members), 'problems': len(problems), 'output_binding': binding(output)}))
    return 0 if not problems else 1

if __name__ == '__main__':
    raise SystemExit(main())
