"""Closed external-family role and runtime path selection, without dispatch."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath

from .path_contract import bind_output, check_binding, require
from .role_stage import DisposableLayout, ProductionLayout, entries

NINE_ROLES = {
    'source': 'source/source-manifest.json',
    'source_package': 'source/packages/0001/manifest.json',
    'reader': 'reader/source-manifest.json',
    'mapper': 'mapped/source-manifest.json',
    'mapper_package': 'mapped/packages/0001/manifest.json',
    'context': 'context/source-manifest.json',
    'context_package': 'context/packages/0001/manifest.json',
    'implementation': 'context/implementation-binding.json',
    'period': 'source/packages/0001/period.json',
}
STAGE_CONTROLS = {
    'episode_contract': 'source/episode-contract.json',
    'context_native_role': 'source/context-native-role.json',
    'construction_selection': 'construction-selection.json',
}
ORIGINAL_EPISODE = {
    'path': 'product/lab/release-candidates/v1/interface/legacy-session-fixture-source-v1-action-0148/episode-contract.json',
    'sha256': 'bc6acaa6022791ea102ced5b1dfc8621403f8e5e557a937765e187a90d887055',
}


def stage_output_membership(layout: ProductionLayout | DisposableLayout,
                            rows: list[dict]) -> dict[str, dict]:
    """Require the exact 27 selected role outputs, with no alias or extra."""
    require(type(layout) in (ProductionLayout, DisposableLayout) and type(rows) is list,
            'typed 27-role construction selection required')
    expected = {(role, source, target) for role, source, target in entries(layout)}
    actual = set()
    by_path = {}
    for row in rows:
        require(type(row) is dict and set(row) == {'role', 'input', 'output', 'bytes'} and
                type(row['bytes']) is bytes, 'closed role row required')
        output = row['output']
        check_binding(row['input'], kind='source_api')
        if type(layout) is ProductionLayout:
            check_binding(output, kind='output', family=layout.family)
        else:
            require(type(output) is dict and set(output) == {'path', 'sha256'},
                    'closed disposable output row required')
            require(layout.family in PurePosixPath(output['path']).parents,
                    'disposable output outside synthetic family')
        require(hashlib.sha256(row['bytes']).hexdigest() == output['sha256'],
                'rendered output digest differs')
        identity = (row['role'], row['input']['path'], output['path'])
        require(identity in expected and identity not in actual,
                'unknown or duplicate generated role binding')
        actual.add(identity)
        by_path[output['path']] = output
    require(actual == expected and len(actual) == 27,
            'complete exact 27-role stage selection required')
    return by_path


def stage_30_membership(layout: ProductionLayout | DisposableLayout,
                        rows: list[dict], controls: dict[str, bytes]) -> dict[str, dict]:
    """Bind all 30 stage leaves, including the exact 27-role selection control."""
    selected = stage_output_membership(layout, rows)
    require(type(controls) is dict and set(controls) == set(STAGE_CONTROLS) and
            all(type(raw) is bytes for raw in controls.values()),
            'exact three stage control leaves required')
    expected = {name: str(layout.family / suffix) for name, suffix in STAGE_CONTROLS.items()}
    for name, path in expected.items():
        raw = controls[name]
        selected[path] = bind_output(path, raw, family=layout.family) if type(layout) is ProductionLayout else {
            'path': path, 'sha256': hashlib.sha256(raw).hexdigest()}
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate construction selection key')
            result[key] = value
        return result
    try:
        construction = json.loads(controls['construction_selection'], object_pairs_hook=pairs,
                                  parse_constant=lambda _: require(False, 'nonfinite construction selection'))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError('invalid stage selection bytes') from error
    require(type(construction) is dict and
            set(construction) == {'schema_version', 'authority_effect', 'instance',
                                  'output_family_path', 'template_rows',
                                  'episode_binding', 'current_role_binding', 'status'} and
            construction['schema_version'] == 'lab-T35-external-root-stage-selection/v1-inactive' and
            construction['authority_effect'] == 'none' and
            construction['status'] == 'staged-unqualified' and
            construction['instance'] == layout.instance and
            construction['output_family_path'] == str(layout.family) and
            construction['episode_binding'] == selected[expected['episode_contract']] and
            construction['current_role_binding'] == selected[expected['context_native_role']],
            'closed stage selection control differs')
    expected_rows = [{key: item[key] for key in ('role', 'input', 'output')} for item in rows]
    require(construction['template_rows'] == expected_rows,
            'stage selection does not bind exact 27-role output mapping')
    require(len(selected) == 30, 'closed 30-leaf stage closure differs')
    return selected


def selected_stage_30(selection, rows: list[dict]) -> tuple[dict[str, dict], dict[str, bytes]]:
    """Close all 30 outputs from selected inputs and deterministic control bytes.

    The two payload controls must be exact Root-selected snapshot rows. This is
    a read-only construction calculation, not proof that any output was written.
    """
    from .held_paths import SelectedSnapshot
    require(type(selection) is SelectedSnapshot, 'selected snapshot required for stage controls')
    layout = ProductionLayout(selection.intent)
    code = selection.intent['code_bindings']
    controls = {}
    for name, key in (('episode_contract', 'stage_episode_contract'),
                      ('context_native_role', 'stage_context_native_role')):
        require(key in code and selection.rows.get(code[key]['path']) == code[key],
                'Root-selected stage control input absent')
        controls[name] = selection.read(code[key])
    require(code['stage_episode_contract'] == ORIGINAL_EPISODE,
            'exact frozen original episode binding required')
    from .held_paths import _parse_closed
    original_episode = _parse_closed(controls['episode_contract'])
    require(type(original_episode) is dict and
            original_episode.get('schema_version') == 'lab-new-candidate-episode-contract/v1-candidate' and
            original_episode.get('authority_effect') == 'none' and
            original_episode.get('actual_owner_outcome') is None,
            'selected original episode contract differs')
    prefix = 'completion-' + layout.instance
    episode_value = {key: value.replace('R03-legacy-session-fixture-0257', prefix)
                     if type(value) is str else value
                     for key, value in original_episode.items()}
    episode_value.update(not_before=selection.intent['not_before'],
                         expires_at=selection.intent['expires_at'],
                         purpose='Distinct independently signed legacy diagnostic family; no old identity, Assignment or grant renewal.')
    controls['episode_contract'] = (json.dumps(episode_value, sort_keys=True,
                                              indent=2, allow_nan=False) + '\n').encode()
    episode = bind_output(layout.family / STAGE_CONTROLS['episode_contract'],
                          controls['episode_contract'], family=layout.family)
    current_role = bind_output(layout.family / STAGE_CONTROLS['context_native_role'],
                               controls['context_native_role'], family=layout.family)
    construction = {
        'schema_version': 'lab-T35-external-root-stage-selection/v1-inactive',
        'authority_effect': 'none', 'instance': layout.instance,
        'output_family_path': str(layout.family),
        'template_rows': [{key: item[key] for key in ('role', 'input', 'output')}
                          for item in rows],
        'episode_binding': episode, 'current_role_binding': current_role,
        'status': 'staged-unqualified',
    }
    controls['construction_selection'] = (json.dumps(construction, sort_keys=True,
                                                      separators=(',', ':'), allow_nan=False) + '\n').encode()
    return stage_30_membership(layout, rows, controls), controls


def runtime_role_paths(layout: ProductionLayout | DisposableLayout) -> dict[str, str]:
    require(type(layout) in (ProductionLayout, DisposableLayout),
            'typed family required for runtime role selection')
    return {name: str(layout.family / suffix) for name, suffix in NINE_ROLES.items()}


def bind_nine_roles(layout: ProductionLayout | DisposableLayout, read_output) -> dict:
    """Bind the nine known role paths after construction; no role is invoked."""
    require(type(layout) in (ProductionLayout, DisposableLayout) and callable(read_output),
            'typed family and exact output reader required')
    paths = runtime_role_paths(layout)
    bindings = {}
    for role, path in paths.items():
        raw = read_output(path)
        require(type(raw) is bytes, 'exact role bytes required')
        bindings[role] = bind_output(path, raw, family=layout.family) if type(layout) is ProductionLayout else {
            'path': path, 'sha256': hashlib.sha256(raw).hexdigest()}
    reader_path = str(layout.family / 'reader' / 'reader.py')
    reader_raw = read_output(reader_path)
    require(type(reader_raw) is bytes, 'selected reader entrypoint bytes required')
    return {'schema_version': 'lab-T35-external-root-nine-role-selection/v1-inactive',
            'status': 'construction-bound-unqualified', 'authority_effect': 'none',
            'instance': layout.instance, 'output_family_path': str(layout.family),
            'role_bindings': bindings, 'source_period_binding': bindings['period'],
            'reader_entrypoint_ref': reader_path + '#SelectedReader.open_signed',
            'reader_entrypoint_sha256': hashlib.sha256(reader_raw).hexdigest(),
            'shared_api_qualified': False, 'runtime_executed': False}


def write_effect(*_args, **_kwargs):
    raise RuntimeError('No external-root constructor write capability is installed')
