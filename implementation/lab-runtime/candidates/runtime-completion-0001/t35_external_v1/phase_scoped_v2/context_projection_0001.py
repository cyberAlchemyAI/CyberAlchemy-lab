"""Pure phase-late Context role projection; no writes, imports of roles, or effects.

The caller supplies held predecessor bytes through a read-only callback. A
binding match is necessary but not proof of filesystem custody; the future
controller must hold and recheck the underlying descriptors independently.
"""
from __future__ import annotations

import hashlib
from pathlib import PurePosixPath

from .. import phase_rebind, role_stage
from ..path_contract import bind_output, require
from .plan import StagePlan


def context_rows(plan: StagePlan, predecessor: dict[str, dict], read_held):
    """Return all eleven selected Context bytes and bindings in role order."""
    require(type(plan) is StagePlan and callable(read_held),
            'selected plan and held-byte reader required')
    plan.value()  # Revalidate the immutable 27-role selection before projection.
    require(type(predecessor) is dict and
            set(predecessor) == phase_rebind.PHASE_PREDECESSORS['context'],
            'exact four Context predecessors required')
    for name in sorted(predecessor):
        row = predecessor[name]
        require(type(row) is dict and set(row) == {'path', 'sha256'} and
                row['path'] == str(plan.layout.family / phase_rebind.PIN_PATHS[name]),
                'held predecessor path differs')
        raw = read_held(row['path'])
        require(type(raw) is bytes and hashlib.sha256(raw).hexdigest() == row['sha256'],
                'held predecessor bytes differ')
    root = plan.layout.family / 'context'
    by_name = {}
    for role, path, raw in plan.templates:
        if role != 'context':
            continue
        rel = PurePosixPath(path).relative_to(root).as_posix()
        require(rel in role_stage.ROLE_FILES['context'] and rel not in by_name and
                type(raw) is bytes, 'Context template path or bytes differ')
        by_name[rel] = raw
    require(set(by_name) == set(role_stage.ROLE_FILES['context']),
            'exact eleven Context template leaves required')
    changed = phase_rebind.rebind(
        plan.layout, 'context',
        {name: by_name[name] for name in phase_rebind.PHASE_FILES['context']},
        predecessor)
    require(set(changed) == set(phase_rebind.PHASE_FILES['context']) and
            all(changed[name] != by_name[name] for name in changed),
            'Context predecessor rewrite did not change three code leaves')
    by_name.update(changed)
    rows = []
    for name in role_stage.ROLE_FILES['context']:
        path = root / name
        raw = by_name[name]
        if type(plan.layout) is role_stage.ProductionLayout:
            binding = bind_output(path, raw, family=plan.layout.family)
        else:
            binding = {'path': str(path), 'sha256': hashlib.sha256(raw).hexdigest()}
        rows.append({'name': name, 'path': str(path), 'bytes': raw, 'binding': binding})
    require(len(rows) == 11 and len({row['path'] for row in rows}) == 11,
            'exact eleven Context output paths required')
    return tuple(rows)


def context_bindings(plan: StagePlan, predecessor: dict[str, dict], read_held):
    """Project eleven prospective no-replace bindings without materializing."""
    return {row['path']: row['binding']
            for row in context_rows(plan, predecessor, read_held)}
