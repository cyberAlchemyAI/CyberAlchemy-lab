"""Pure pinned compatibility check; neither builds a stage nor imports Context."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent


def pinned(path, digest):
    raw = path.read_bytes()
    if len(raw) > 1024*1024 or hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError('topology input changed')
    return json.loads(raw)


def check():
    value = json.loads((HERE / 'compatibility.json').read_bytes())
    stage = pinned(LOCAL / 'context-stage-0001/selection.json',
                   value['predecessor_stage_selection_sha256'])
    pinned(LOCAL / 'context-stage-effect-0001/freeze.json',
           value['predecessor_stage_effect_freeze_sha256'])
    jit = pinned(LOCAL / 'context-jit-effect-0001/required-topology.json',
                 value['jit_required_topology_draft_sha256'])
    replacements = {x['path']: x for x in jit['role_replacements']}
    selected_roles = {x['path']: x['sha256'] for x in stage['projected_context_additions']}
    for path, row in replacements.items():
        if selected_roles.get(path) != row['predecessor_sha256']:
            raise ValueError('projected role predecessor mismatch')
    source = jit['source_role']
    if (stage['future_root_file_count_if_protected_copied_under_separate_effect'] != 1570
        or stage['context_output_mount_mode'] != 'rw'
        or stage['root_mount_mode'] != 'ro'
        or stage['native_mount_mode'] != 'ro'
        or value['stage_root_file_count_after_auth'] != 1571
        or jit['proposed_file_count_after_exact_auth_leaf'] != 1571
        or source['path'] != value['source_role_mode_projection']['path']
        or source['required_mode'] != value['source_role_mode_projection']['to_mode']
        or jit['authorization_directory']['path'] != value['authorization_directory']['path']
        or jit['authorization_leaf']['path'] != value['authorization_leaf']['path']
        or replacements[next(p for p in replacements if p.endswith('/build.py'))]['projected_sha256']
            != value['context_build_projected_sha256']
        or replacements[next(p for p in replacements if p.endswith('/control.py'))]['projected_sha256']
            != value['context_control_projected_sha256']
        or value['context_output_mount_required_for_child'] != 'ro'
        or value['effect'] != 'NOT_RUN'
        or value['context_launch'] != 'REFUSED'):
        raise ValueError('topology compatibility requirement mismatch')
    return {'status': 'COMPATIBILITY_ONLY', 'prior_files': 1570,
            'required_files_after_auth': 1571, 'role_replacements': len(replacements),
            'child_output_mount': 'ro', 'effect': 'NOT_RUN'}


if __name__ == '__main__':
    print(json.dumps(check(), sort_keys=True))
