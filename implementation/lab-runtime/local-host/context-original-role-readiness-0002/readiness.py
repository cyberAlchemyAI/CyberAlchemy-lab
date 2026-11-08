"""Inert, public-only closure check for the original Context role.

This module never imports a generated role or opens a Source archive. Its result
is a readiness boundary, not a source manifest or permission to run Context.
"""
from __future__ import annotations

import hashlib
import json
import os
import stat
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAX_PUBLIC_LEAF = 16 * 1024 * 1024
MAX_METADATA = 2 * 1024 * 1024
OWN_SELECTION_SHA = '8f4b5a31c6286caaf3de5ac59197ebbcf2e41ad6671994f5ced1120d31b89dc0'
PREDECESSOR_FREEZE_SHA = '3315f131cce284bd95273ce6f6e2e3c58b3672540c350e9dc718f5c2920bab17'
PREDECESSOR_HOLD_SHA = 'fbde6363b9def7d51b2bce00f655abd32ef21b21dfe80be766c5504a09076a46'
EXPECTED_COUNTS = {'api': 34, 'fact_scope': 4, 'native_package': 55,
                   'context_query_schema': 1, 'current_context_role': 7,
                   'source_period': 1}
EXPECTED_PREFIXES = {
    'api': 'product/lab/release-candidates/v1/interface/api-v25/',
    'fact_scope': 'product/lab/release-candidates/v1/interface/fact-read-scope-v1/',
    'native_package': 'product/lab/release-candidates/v1/interface/docker-mapped-20261020-0002/packages/0001/',
    'current_context_role': 'product/lab/release-candidates/v1/interface/docker-context-20261020-0002/',
}


class Refused(ValueError):
    pass


def need(test, message):
    if not test:
        raise Refused(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def held_regular(path, expected, maximum=MAX_METADATA, expected_mode=None):
    """Bounded no-follow, nonblocking read through held directory descriptors."""
    path = Path(path)
    need(path.is_absolute() and all(p not in ('', '.', '..') for p in path.parts[1:])
         and type(maximum) is int and 0 < maximum <= MAX_PUBLIC_LEAF,
         'noncanonical held path or cap')
    handles = []
    error = None
    raw = None
    try:
        parent = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
        handles.append(parent)
        for part in path.parts[1:-1]:
            parent = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW |
                             os.O_CLOEXEC, dir_fd=parent)
            handles.append(parent)
        leaf = os.open(path.parts[-1], os.O_RDONLY | os.O_NOFOLLOW |
                       os.O_NONBLOCK | os.O_CLOEXEC, dir_fd=parent)
        handles.append(leaf)
        before = os.fstat(leaf)
        need(stat.S_ISREG(before.st_mode) and before.st_size <= maximum,
             'held file type/size changed')
        if expected_mode is not None:
            need(f'{stat.S_IMODE(before.st_mode):04o}' == expected_mode,
                 'held file mode changed')
        remaining = before.st_size
        chunks = []
        while remaining:
            chunk = os.read(leaf, min(remaining, 65536))
            need(bool(chunk), 'short held file')
            chunks.append(chunk)
            remaining -= len(chunk)
        need(os.read(leaf, 1) == b'', 'held file grew')
        after = os.fstat(leaf)
        named = os.stat(path.parts[-1], dir_fd=parent, follow_symlinks=False)
        identity = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_uid, s.st_gid,
                              s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        need(identity(before) == identity(after) == identity(named),
             'held file identity changed')
        raw = b''.join(chunks)
        need(sha(raw) == expected, 'held file digest changed')
    except BaseException as exc:
        error = exc
    finally:
        for fd in reversed(handles):
            try:
                os.close(fd)
            except OSError as exc:
                if error is None:
                    error = exc
    if error is not None:
        if isinstance(error, OSError):
            raise Refused('held file open/read/close failed') from error
        raise error
    return raw


def checked_json(path, expected):
    return json.loads(held_regular(path, expected))


def read_public_at(root, row):
    """Read a selected public stage leaf; never open a private archive body."""
    rel = row['path']
    pieces = rel.split('/')
    need(all(p not in ('', '.', '..') for p in pieces) and
         not rel.startswith('/') and '\\' not in rel,
         'noncanonical public stage row')
    return held_regular(Path(root) / rel, row['sha256'], MAX_PUBLIC_LEAF,
                        row['mode'])


def validate_selection(selected, final, stage_review, roles, components):
    need(selected['schema'] == 'lab-context-original-role-readiness/v2-effect-disabled' and
         selected['predecessor_freeze_sha256'] == PREDECESSOR_FREEZE_SHA and
         selected['predecessor_hold_review_sha256'] == PREDECESSOR_HOLD_SHA and
         selected['effect_enabled'] is False and
         selected['status'] == 'PUBLIC_CLOSURE_SELECTED_REAL_ROLE_HELD',
         'readiness effect boundary changed')
    need(final['bound_file_count'] == 1570 and len(final['bound_rows']) == 1570 and
         len({r['path'] for r in final['bound_rows']}) == 1570,
         'stage selection is not exact 1570-row set')
    need(final['authorization'] == 'UNMINTED' and
         final['auth_placeholder'] == selected['auth_placeholder'] and
         final['auth_placeholder']['sha256'] == 'UNMINTED_UNSELECTED',
         'AUTH placeholder unexpectedly changed')
    need(final['topology']['stage_root'] == selected['stage_root'] and
         final['topology']['context_attempt'] == selected['stage_attempt'] and
         final['topology']['context_family_ref'] == selected['current_role_path'],
         'stage topology changed')
    need(final['pins'] == selected['source_pins'] and
         final['source_period_sha256'] == selected['selected_source_period_sha256'],
         'current Source/Reader/Mapper pins changed')
    need(stage_review['verdict'] == selected['stage_review_verdict'] ==
         'PASS_BOUNDED_DISPOSABLE_CONTEXT_STAGE_ONLY' and
         type(stage_review['external_os_exit']) is int and
         stage_review['external_os_exit'] == 0 and
         stage_review['files_verified'] == 1570 and
         stage_review['directories_verified'] == 1021 and
         stage_review['auth'] == 'UNMINTED_UNSELECTED' and
         stage_review['all_selected_file_hashes_verified'] is True and
         stage_review['all_selected_modes_verified'] is True and
         stage_review['unknown_absent'] is True and
         stage_review['context_executed'] is False and
         stage_review['retry_allowed'] is False and
         stage_review['continuous_cross_time_inode_custody_proven'] is False,
         'stage effect review ceiling changed')
    need(selected['public_closure_counts'] == EXPECTED_COUNTS and
         {k: len(v) for k, v in selected['public_closure'].items()} == EXPECTED_COUNTS,
         'public closure counts changed')
    bound = {r['path']: r for r in final['bound_rows']}
    all_rows = [r for rows in selected['public_closure'].values() for r in rows]
    need(len(all_rows) == len({r['path'] for r in all_rows}) == 102,
         'public closure path collision')
    for kind, rows in selected['public_closure'].items():
        for row in rows:
            need(type(row) is dict and set(row) == {'path', 'mode', 'sha256', 'source'} and
                 bound.get(row['path']) == row,
                 'public closure row does not match actual stage selection')
            if kind in EXPECTED_PREFIXES:
                need(row['path'].startswith(EXPECTED_PREFIXES[kind]),
                     'public closure kind/path mismatch')
            elif kind == 'context_query_schema':
                need(row['path'] == 'docs/proposals/0007-lab-integrated-schema-package/schemas/context-query.schema.json',
                     'Context Query schema path changed')
            else:
                need(row['path'] == 'product/lab/release-candidates/v1/interface/docker-source-20261020-0002/packages/0001/period.json' and
                     row['sha256'] == final['source_period_sha256'],
                     'Source period row changed')
    need(next(r['sha256'] for r in selected['public_closure']['api']
              if r['path'].endswith('/contract-profile.json')) == final['api_profile_sha256'],
         'selected API profile changed')
    need({r['path'].split('/')[-1] for r in selected['public_closure']['current_context_role']} ==
         {'__init__.py', 'base.py', 'build.py', 'control.py', 'generation.py',
          'implementation-binding.json', 'lifetime-policy.json'},
         'current Context role stage subset changed')
    need(any(r['sha256'] == components['validator']['selection']['context_query_schema_sha256']
             for r in selected['public_closure']['context_query_schema']),
         'validator Context Query schema differs')
    need(len(roles['role_rows']) == 11 and
         selected['historical_role_rows'] ==
         [{k: r[k] for k in ('name', 'preimage_sha256', 'render_sha256', 'size')}
          for r in roles['role_rows']] and
         sum(sum(r.get('predecessor_occurrences', {}).values())
             for r in roles['role_rows']) == 5 and
         roles['source_manifest_status'] ==
         'REFUSED_PENDING_FRESH_MAPPER_AND_COMPLETE_CLOSURE',
         'old-family role renderer boundary changed')
    role_prefix = EXPECTED_PREFIXES['current_context_role']
    missing = [role_prefix + r['name'] for r in roles['role_rows']
               if r['name'].startswith('protocols/')]
    missing.append(role_prefix + 'source-manifest.json')
    need(len(missing) == 6 and selected['missing_current_role_paths'] == missing and
         all(path not in bound for path in missing),
         'claimed missing Context inputs are in the selected stage')
    bridge = components['bridge']['selection']
    integration = components['integration']['selection']
    validator = components['validator']['selection']
    need(bridge['effect_enabled'] is False and bridge['wire_requests'] == 42 and
         bridge['leaves'] == 40 and bridge['manifest_rows'] == 39 and
         bridge['private_release_after_leaves'] == 38 and
         bridge['finish_ordinal'] == 41,
         'synthetic bridge contract changed')
    need(integration['effect_enabled'] is False and
         integration['wire_request_count'] == 42 and
         integration['emit_count'] == 40 and
         integration['release_private_ordinal'] == 38 and
         integration['finish_ordinal'] == 41 and
         integration['real_authorization'] == 'UNMINTED' and
         integration['original_context'] == 'NOT_RUN',
         'synthetic integration boundary changed')
    need(validator['effect_enabled'] is False and
         validator['package_leaves'] == 40 and
         validator['manifest_file_bindings'] == 39 and
         sum(validator['carrier_counts'].values()) == 30 and
         validator['real_output'] == 'UNSELECTED',
         'synthetic output validator boundary changed')


def inspect(selected=None, read_public=True):
    own = checked_json(HERE / 'selection.json', OWN_SELECTION_SHA)
    if selected is None:
        selected = own
    else:
        need(selected == own, 'caller selection is not frozen own selection')
    local = HERE.parent
    predecessor = checked_json(local / 'context-original-role-readiness-0001/freeze.json',
                               PREDECESSOR_FREEZE_SHA)
    hold = checked_json(local / 'context-original-role-readiness-independent-review-0001/review.json',
                        PREDECESSOR_HOLD_SHA)
    need(predecessor['effect_enabled'] is False and
         hold['verdict'] == 'HOLD' and
         hold['candidate_freeze_sha256'] == PREDECESSOR_FREEZE_SHA and
         {r['id'] for r in hold['findings']} == {'R01', 'R02'},
         'predecessor HOLD identity changed')
    final = checked_json(selected['selection_path'], selected['selection_sha256'])
    stage = checked_json(selected['stage_review_path'], selected['stage_review_sha256'])
    roles = checked_json(selected['historical_role_selection_path'],
                         selected['historical_role_selection_sha256'])
    components = {}
    for key, pin in selected['components'].items():
        freeze = checked_json(pin['freeze_path'], pin['freeze_sha256'])
        checked_json(pin['review_path'], pin['review_sha256']) if pin['review_path'].endswith('.json') else _check_raw(pin['review_path'], pin['review_sha256'])
        components[key] = {'freeze': freeze,
                           'selection': _frozen_selection(pin, freeze)}
        if key in ('bridge', 'integration', 'validator'):
            module_name = {'bridge': 'bridge.py', 'integration': 'integration.py',
                           'validator': 'validator.py'}[key]
            _frozen_module(pin, freeze, module_name)
    render_dir = Path(selected['historical_role_selection_path']).with_name('rendered')
    for row in selected['historical_role_rows']:
        _check_raw(render_dir / row['name'], row['render_sha256'])
    validate_selection(selected, final, stage, roles, components)
    period = None
    if read_public:
        for rows in selected['public_closure'].values():
            for row in rows:
                raw = read_public_at(selected['stage_root'], row)
                if row['path'] == selected['public_closure']['source_period'][0]['path']:
                    period = json.loads(raw)
        need(period['authority_effect'] == 'none' and
             period['schema_version'] == 'lab-owned-absolute-participation-period/v1-candidate',
             'Source period semantics changed')
    role_root = Path(selected['current_role_path'])
    need(role_root.is_dir() and not role_root.is_symlink() and
         set(os.listdir(role_root)) ==
         {Path(r['path']).name for r in selected['public_closure']['current_context_role']} and
         all(not os.path.lexists(Path(selected['stage_root']) / p)
             for p in selected['missing_current_role_paths']),
         'current Context role subset appeared with unselected closure')
    auth = Path(selected['stage_root']) / selected['auth_placeholder']['path']
    need(not os.path.lexists(auth), 'AUTH appeared without a new selected stage')
    return {
        'schema': 'lab-context-original-role-readiness-result/v1',
        'status': 'WAIT_AUTH_CURRENT_ROLE_AND_REAL_TRANSPORT',
        'public_closure_rows_checked': 102 if read_public else 0,
        'public_closure_counts': EXPECTED_COUNTS,
        'source_period': ({'not_before': period['not_before'],
                           'expires_at': period['expires_at'],
                           'current_at_inspection':
                           datetime.fromisoformat(period['not_before']) <=
                           datetime.now(timezone.utc) <
                           datetime.fromisoformat(period['expires_at'])}
                          if period else 'NOT_RECHECKED'),
        'historical_role_preimages': 11,
        'current_role_source_manifest': 'MISSING',
        'current_role_staged_rows': 7,
        'current_role_local_protocols': 'FIVE_MISSING',
        'exact_missing_stage_paths': selected['missing_current_role_paths'],
        'bridge_contract': selected['bridge_contract'],
        'bridge_proof': 'SYNTHETIC_ONLY',
        'output_validator_proof': 'SYNTHETIC_ONLY',
        'missing': [
            'independently reviewed real signed-scope attestation',
            'local issuer/grant and signed current AUTH',
            'new disjoint stage with AUTH and six missing current-role files; existing attempt consumed',
            'complete current-family source manifest and any additional dependency rows',
            'real checked 42-frame transport and 40-leaf parent writer',
            'actual output, OS receipts and independent effect review',
        ],
        'effect': 'NONE',
        'original_context': 'NOT_RUN',
    }


def _check_raw(path, expected):
    held_regular(path, expected)


def _frozen_selection(pin, freeze):
    rows = freeze.get('files', freeze.get('file_bindings'))
    need(type(rows) is list, 'component freeze has no file bindings')
    matches = [r for r in rows if r['path'].endswith('/selection.json') or
               r['path'] == 'selection.json']
    need(len(matches) == 1, 'component selection is not frozen exactly once')
    candidate = Path(pin['freeze_path']).with_name('selection.json')
    return checked_json(candidate, matches[0]['sha256'])


def _frozen_module(pin, freeze, module_name):
    rows = freeze.get('files', freeze.get('file_bindings'))
    matches = [r for r in rows if r['path'].endswith('/' + module_name) or
               r['path'] == module_name]
    need(len(matches) == 1, 'component module is not frozen exactly once')
    _check_raw(Path(pin['freeze_path']).with_name(module_name),
               matches[0]['sha256'])


def launch(*_args, **_kwargs):
    raise Refused('original Context effect disabled: no AUTH/current role/real transport')


if __name__ == '__main__':
    print(json.dumps(inspect(), sort_keys=True))
