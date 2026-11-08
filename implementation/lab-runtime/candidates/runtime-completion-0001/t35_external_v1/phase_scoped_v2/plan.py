"""Immutable full-template plan with a smaller Source/Reader materialization.

The 30-path plan is prospective. Only the Source and Reader roles and three
controls enter the early family. Mapper and Context paths remain absent until
their predecessor bindings exist; this module never writes or imports them.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import PurePosixPath

from .. import constructor_paths, phase_rebind, role_stage
from ..held_paths import _parse_closed
from ..path_contract import bind_output, check_binding, require

ACTIVE_ROLES = frozenset(('source', 'reader'))
DEFERRED_ROLES = frozenset(('mapped', 'context'))
PLAN_SUFFIX = 'construction-selection.json'
CONTROL_SUFFIXES = {
    'episode_contract': 'source/episode-contract.json',
    'context_native_role': 'source/context-native-role.json',
}


def _bind(layout, path: PurePosixPath, raw: bytes) -> dict:
    if type(layout) is role_stage.ProductionLayout:
        return bind_output(path, raw, family=layout.family)
    return {'path': str(path), 'sha256': hashlib.sha256(raw).hexdigest()}


def _json(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=False, allow_nan=False) + '\n').encode()


@dataclass(frozen=True)
class StagePlan:
    layout: role_stage.ProductionLayout | role_stage.DisposableLayout
    plan_leaf_bytes: bytes
    templates: tuple[tuple[str, str, bytes], ...]
    episode_raw: bytes
    role_raw: bytes

    def value(self) -> dict:
        selected = _parse_closed(self.plan_leaf_bytes)
        require(type(selected) is dict and
                set(selected) == {'schema_version', 'instance', 'output_family_path',
                                  'template_rows', 'initial_role_bindings',
                                  'deferred_template_bindings', 'episode_binding',
                                  'current_role_binding', 'status', 'authority_effect',
                                  'actual_owner_outcome'} and
                selected['schema_version'] == 'lab-T35-phase-scoped-template-plan/v2-inactive' and
                selected['authority_effect'] == 'none' and
                selected['actual_owner_outcome'] is None and
                selected['status'] == 'planned-unmaterialized' and
                selected['instance'] == self.layout.instance and
                selected['output_family_path'] == str(self.layout.family),
                'closed immutable phase-scoped plan differs')
        require(len(selected['initial_role_bindings']) == 12 and
                len(selected['deferred_template_bindings']) == 15 and
                len(selected['template_rows']) == 27,
                'phase plan partition differs')
        template = selected['template_rows']
        require(all(type(row) is dict and set(row) == {'role', 'input', 'output'}
                    for row in template) and
                [(row['role'], row['output']['path'], row['output']['sha256'])
                 for row in template] ==
                [(role, path, hashlib.sha256(raw).hexdigest())
                 for role, path, raw in self.templates],
                'phase template bytes or role mapping changed')
        require(selected['initial_role_bindings'] == sorted(
                    [row['output'] for row in template if row['role'] in ACTIVE_ROLES],
                    key=lambda row: row['path']) and
                selected['deferred_template_bindings'] == sorted(
                    [row['output'] for row in template if row['role'] in DEFERRED_ROLES],
                    key=lambda row: row['path']) and
                selected['episode_binding'] == _bind(
                    self.layout, self.layout.family / CONTROL_SUFFIXES['episode_contract'],
                    self.episode_raw) and
                selected['current_role_binding'] == _bind(
                    self.layout, self.layout.family / CONTROL_SUFFIXES['context_native_role'],
                    self.role_raw),
                'phase role partition or control bytes changed')
        return selected

    def template_rows(self) -> tuple[dict, ...]:
        return tuple(self.value()['template_rows'])

    def initial_bindings(self) -> tuple[dict, ...]:
        value = self.value()
        plan_binding = _bind(self.layout, self.layout.family / PLAN_SUFFIX,
                             self.plan_leaf_bytes)
        result = sorted([*value['initial_role_bindings'], value['episode_binding'],
                         value['current_role_binding'], plan_binding],
                        key=lambda row: row['path'])
        require(len(result) == 15 and len({row['path'] for row in result}) == 15,
                'exact 15 early materialization bindings required')
        return tuple(result)

    def deferred_bindings(self) -> tuple[dict, ...]:
        return tuple(self.value()['deferred_template_bindings'])

    def initial_inventory(self) -> dict[str, str]:
        return {row['path']: row['sha256'] for row in self.initial_bindings()}

    def check_initial_inventory(self, actual: dict[str, str]) -> None:
        require(type(actual) is dict and actual == self.initial_inventory(),
                'Source/Reader early family contains a future or changed leaf')

    def source_rows(self, repository_rows: list[dict]) -> list[dict]:
        """Select only immutable early family leaves and exact Source/API rows."""
        require(type(repository_rows) is list, 'selected repository rows required')
        selected = {}
        for row in repository_rows:
            check_binding(row, kind='source_api')
            require(row['path'] not in selected, 'duplicate Source/API input')
            selected[row['path']] = dict(row)
        require(bool(selected), 'Source/API snapshot cannot be empty')
        for row in self.initial_bindings():
            check_binding(row, kind='output', family=self.layout.family)
            require(row['path'] not in selected, 'early stage input conflict')
            selected[row['path']] = dict(row)
        require(set(selected).isdisjoint(row['path'] for row in self.deferred_bindings()),
                'future role entered early Source manifest')
        return [selected[name] for name in sorted(selected)]

    def mapper_bindings(self, predecessor: dict[str, dict]) -> dict[str, dict]:
        """Project O_EXCL Mapper outputs after fresh predecessor pins exist."""
        by_name = {PurePosixPath(path).name: raw for role, path, raw in self.templates
                   if role == 'mapped'}
        require(set(by_name) == set(role_stage.ROLE_FILES['mapped']),
                'exact four Mapper template leaves required')
        changed = phase_rebind.rebind(self.layout, 'mapped',
                                     {key: by_name[key] for key in ('base.py', 'build.py')},
                                     predecessor)
        require(all(changed[name] != by_name[name] for name in changed),
                'Mapper predecessor pins did not change template bytes')
        by_name.update(changed)
        bindings = {str(self.layout.family / 'mapped' / name):
                    _bind(self.layout, self.layout.family / 'mapped' / name, raw)
                    for name, raw in by_name.items()}
        require(set(bindings) == {str(self.layout.family / 'mapped' / name)
                                  for name in role_stage.ROLE_FILES['mapped']},
                'exact four phase-materialized Mapper paths required')
        return bindings


def plan(layout: role_stage.ProductionLayout | role_stage.DisposableLayout,
         rows: list[dict], *, episode_raw: bytes, role_raw: bytes) -> StagePlan:
    require(type(layout) in (role_stage.ProductionLayout, role_stage.DisposableLayout) and
            type(rows) is list and type(episode_raw) is bytes and type(role_raw) is bytes and
            bool(episode_raw) and bool(role_raw),
            'selected 27-role inputs and two controls required')
    selected = constructor_paths.stage_output_membership(layout, rows)
    require(len(selected) == 27, 'exact full prospective 27-role plan required')
    templates = tuple((row['role'], row['output']['path'], bytes(row['bytes'])) for row in rows)
    initial = [row['output'] for row in rows if row['role'] in ACTIVE_ROLES]
    deferred = [row['output'] for row in rows if row['role'] in DEFERRED_ROLES]
    require(len(initial) == 12 and len(deferred) == 15 and
            {row['path'] for row in initial + deferred} == set(selected),
            'Source/Reader and future role partition differs')
    controls = {
        'episode_contract': _bind(layout, layout.family / CONTROL_SUFFIXES['episode_contract'],
                                  episode_raw),
        'context_native_role': _bind(layout, layout.family / CONTROL_SUFFIXES['context_native_role'],
                                     role_raw),
    }
    value = {
        'schema_version': 'lab-T35-phase-scoped-template-plan/v2-inactive',
        'instance': layout.instance,
        'output_family_path': str(layout.family),
        'template_rows': [{key: row[key] for key in ('role', 'input', 'output')} for row in rows],
        'initial_role_bindings': sorted(initial, key=lambda row: row['path']),
        'deferred_template_bindings': sorted(deferred, key=lambda row: row['path']),
        'episode_binding': controls['episode_contract'],
        'current_role_binding': controls['context_native_role'],
        'status': 'planned-unmaterialized',
        'authority_effect': 'none',
        'actual_owner_outcome': None,
    }
    # The leaf cannot include its own digest. Its binding is derived from these
    # exact bytes when forming the 15-leaf early inventory.
    raw = _json(value)
    return StagePlan(layout, raw, templates,
                     bytes(episode_raw), bytes(role_raw))
