"""Exact historical 363-member reconciliation; no successor or owner effect."""

import hashlib
import json
import os
from pathlib import Path
from collections import Counter
import stat


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
ORIGINAL = ('docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/final-review-0247/inventory.json',
            '2cd9850f8da1dfbf5c6a4a531f2ad0730956956c57d26003d0456196b5862f1d')
OWNER_MATRIX = ('docs/plans/0011-lab-runtime-completion/runs/0001-execution/T12/owner-prerequisites-0001/candidate-owner-effect-matrix.json',
                '24bd05bee504f53806638bd8d443d36135cf0d7319a289fd912b1513c150c94b')
CANDIDATE = ('implementation/lab-runtime/local-host/t25-local-candidate-0001/INVENTORY.json',
             '268e54ebce2674006b327f1a1d5c45ff64ac7031465eaa3d9b35e4845306b8e9')
INPUTS = ('product/lab/release-candidates/v1/release-validation/0001/final-member-inputs-0276.json',
          'a099221682af6d061cad24f4759ec225541f203882627fa74361285b54b25987')
EXPECTED_ROUTES = {'role:repository-owner': 354, 'role:identity-graph-owner': 4,
                   'role:definition-owner': 3, 'role:artifact-type-owner': 2}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode()


def parse(raw):
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError('duplicate JSON key')
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def selected(binding, root=ROOT):
    relative, digest = binding
    path = root / relative
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise ValueError('linked selected source')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        raw = os.read(fd, os.fstat(fd).st_size + 1)
    finally:
        os.close(fd)
    if sha(raw) != digest or sha(path.read_bytes()) != digest:
        raise ValueError('selected source changed: ' + relative)
    return parse(raw)


def derive(original, matrix, candidate, inputs):
    original_rows = original['members']
    matrix_rows = matrix['members']
    ids = [row.get('member_id', row.get('member_ref')) for row in original_rows]
    if (original['member_count'] != 363 or matrix['original_member_count'] != 363 or
            inputs['original_members'] != 363 or candidate['original_member_dispositions_complete'] is not False or
            len(original_rows) != 363 or len(matrix_rows) != 363 or len(set(ids)) != 363 or
            ids != candidate['original_member_ids'] or
            candidate['archive_sha256'] != '020f2755bd2687003f15d93a49a1e3bd6a49d838e3efe1398d6731881edce448'):
        raise ValueError('exact original member selection differs')
    routes = Counter()
    rows = []
    for position, (old, owner, identity) in enumerate(zip(original_rows, matrix_rows, ids)):
        required = owner['required_roles']
        if (owner['member_ref'] != identity or owner['member_class'] != old['member_class'] or
                required != old['proposed_owner_roles'] or len(required) != 1 or
                old['selected_outcome'] is not None or old['current_owner_authority_verified'] is not False or
                owner['actual_owner_outcome'] is not None or owner['current_owner_authority_verified'] is not False or
                owner['status'] != 'BLOCKED-owner-bootstrap-or-current-assignment-prerequisite'):
            raise ValueError('historical member/owner metadata differs at ' + str(position))
        routes[required[0]] += 1
        rows.append({'position': position, 'original_member_ref': identity,
                     'member_class': old['member_class'],
                     'original_preparation_member_sha256': old['original_preparation_member_sha256'],
                     'historical_required_role_ref': required[0],
                     'historical_requested_effect': old['requested_effect'],
                     'historical_effect_proposal_sha256': sha(canonical(owner['effect_selection'])),
                     'disposition_state': 'unresolved-current-successor-selection',
                     'selected_successor_effect': None, 'owner_outcome': None,
                     'current_authority_evidence': None})
    if dict(routes) != EXPECTED_ROUTES:
        raise ValueError('historical route counts differ')
    return {'schema_version': 'lab-t25-original-member-reconciliation/v1',
            'source_bindings': [{'path': path, 'sha256': digest}
                                for path, digest in (ORIGINAL, OWNER_MATRIX, CANDIDATE, INPUTS)],
            'original_member_count': 363, 'unresolved_member_count': 363,
            'observed_historical_role_routes': dict(sorted(routes.items())),
            'original_member_dispositions_complete': False, 'authority_effect': 'none',
            'members': rows}


def expected():
    return derive(selected(ORIGINAL), selected(OWNER_MATRIX), selected(CANDIDATE), selected(INPUTS))


def verify(raw):
    actual = parse(raw)
    if type(actual) is not dict or canonical(actual) != raw or actual != expected():
        raise ValueError('reconciliation differs from selected exact members')
    return {'schema_version': 'lab-t25-original-member-reconciliation-result/v1',
            'reconciliation_sha256': sha(raw), 'original_member_count': 363,
            'unresolved_member_count': 363, 'observed_historical_role_routes': EXPECTED_ROUTES,
            'original_member_dispositions_complete': False,
            'candidate_archive_sha256': '020f2755bd2687003f15d93a49a1e3bd6a49d838e3efe1398d6731881edce448',
            'installed_api40_replay': False, 'authority_effect': 'none', 'task_complete': False}


def read_frozen(path):
    path = Path(path)
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise ValueError('linked frozen evidence')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        state = os.fstat(fd)
        if not stat.S_ISREG(state.st_mode):
            raise ValueError('frozen evidence is not a regular file')
        raw = os.read(fd, state.st_size + 1)
    finally:
        os.close(fd)
    return raw


def cold_verify():
    result = verify(read_frozen(HERE / 'RECONCILIATION.json'))
    if canonical(result) != read_frozen(HERE / 'RESULT.json'):
        raise ValueError('retained result differs')
    return result


if __name__ == '__main__':
    import sys
    if sys.argv[1:] == ['--verify']:
        print(json.dumps(cold_verify(), sort_keys=True, indent=2))
    else:
        raise SystemExit('usage: reconcile.py --verify (frozen evidence is read-only)')
