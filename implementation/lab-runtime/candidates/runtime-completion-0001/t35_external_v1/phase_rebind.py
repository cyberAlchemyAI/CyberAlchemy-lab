"""Pure, inactive predecessor-pin rewrite for later mapper/Context phases.

The frozen constructor rewrites these exact constants after each predecessor
produces a new signed manifest. This module performs that calculation only; it
does not accept a phase receipt, import a role, write a file, or grant effects.
"""
from __future__ import annotations

import hashlib
from pathlib import PurePosixPath

from .path_contract import bind_output, check_binding, require
from .role_stage import DisposableLayout, ProductionLayout

ORIGINAL_PINS = {
    'source': 'f3cbec21c32dce3938460a1203e6e3f3575608f463aa3f3fffae9f9338a798f2',
    'source_package': '8e7b675666308e0e73fb23962b310ea3a89baa48ad6bf2c9cf1c5c9ce9e96964',
    'reader': '0ad1c974a5725d7bf0c23cc08b27c9e4e6c2b4fba512ddc0009aef337e81c0a5',
    'mapped': '04a22ae3cd37ee70f2e2eb4dcf9a6b2d164fd08382a90c50e2d6a26be8f3f73c',
    'mapped_package': 'ba99b0023708613af17196ff4d5ed3ef9f2e9ddb68de06ab14d374182f5a5b94',
}
PIN_PATHS = {
    'source': 'source/source-manifest.json',
    'source_package': 'source/packages/0001/manifest.json',
    'reader': 'reader/source-manifest.json',
    'mapped': 'mapped/source-manifest.json',
    'mapped_package': 'mapped/packages/0001/manifest.json',
}
PHASE_FILES = {
    'mapped': ('base.py', 'build.py'),
    'context': ('base.py', 'build.py', 'generation.py'),
}
PHASE_PREDECESSORS = {
    'mapped': frozenset(('source', 'source_package', 'reader')),
    'context': frozenset(('source', 'source_package', 'mapped', 'mapped_package')),
}
EXPECTED_COUNTS = {
    ('mapped', 'base.py'): {'source': 1, 'source_package': 1, 'reader': 1},
    ('mapped', 'build.py'): {'source': 1, 'source_package': 1},
    ('context', 'base.py'): {'mapped': 1, 'mapped_package': 1},
    ('context', 'build.py'): {'source': 1, 'source_package': 1},
    ('context', 'generation.py'): {'mapped': 1},
}


def rebind(layout: ProductionLayout | DisposableLayout, role: str,
           rendered: dict[str, bytes], predecessor: dict[str, dict]) -> dict[str, bytes]:
    """Return exact transformed code bytes, with no claim of signed custody."""
    require(type(layout) in (ProductionLayout, DisposableLayout) and role in PHASE_FILES and
            type(rendered) is dict and set(rendered) == set(PHASE_FILES[role]) and
            all(type(raw) is bytes for raw in rendered.values()) and
            type(predecessor) is dict and set(predecessor) == PHASE_PREDECESSORS[role],
            'closed phase code and predecessor set required')
    for name, row in predecessor.items():
        if type(layout) is ProductionLayout:
            check_binding(row, kind='output', family=layout.family)
        else:
            require(type(row) is dict and set(row) == {'path', 'sha256'},
                    'closed disposable predecessor binding required')
        require(row['path'] == str(layout.family / PIN_PATHS[name]) and
                type(row['sha256']) is str and len(row['sha256']) == 64 and
                all(c in '0123456789abcdef' for c in row['sha256']),
                'predecessor path or digest differs')
    result = {}
    for filename, raw in rendered.items():
        text = raw.decode('utf-8')
        counts = {name: text.count(ORIGINAL_PINS[name]) for name in predecessor}
        require(counts == {name: EXPECTED_COUNTS[(role, filename)].get(name, 0)
                           for name in predecessor},
                'exact frozen predecessor selector occurrence vector differs')
        for name, row in predecessor.items():
            old = ORIGINAL_PINS[name]
            text = text.replace(old, row['sha256'])
        require(all(ORIGINAL_PINS[name] not in text for name in predecessor),
                'historical predecessor pin remains')
        generated = (text if text.endswith('\n') else text + '\n').encode()
        compile(generated, str(layout.family / role / filename), 'exec', optimize=0)
        compile(generated, str(layout.family / role / filename), 'exec', optimize=2)
        result[filename] = generated
    return result


def projected_bindings(layout: ProductionLayout | DisposableLayout,
                       role: str, rendered: dict[str, bytes], predecessor: dict[str, dict]) -> dict[str, dict]:
    """Describe post-rewrite outputs; caller still lacks a signed phase receipt."""
    changed = rebind(layout, role, rendered, predecessor)
    if type(layout) is ProductionLayout:
        return {name: bind_output(layout.family / role / name, raw, family=layout.family)
                for name, raw in changed.items()}
    return {name: {'path': str(layout.family / role / name),
                   'sha256': hashlib.sha256(raw).hexdigest()}
            for name, raw in changed.items()}
