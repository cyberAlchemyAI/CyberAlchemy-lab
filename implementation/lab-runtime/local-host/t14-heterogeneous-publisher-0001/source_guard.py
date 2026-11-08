"""Exact local T14 component and seven public example input selection."""

import hashlib
import json
from pathlib import Path


ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
COMPONENT = 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T14/mixed-target-publisher-0002'
COMPONENT_ROWS = {
    COMPONENT + '/__init__.py': '5185fd914cc299322c92bc778b9e7c238c41512fb6e6d1c9520a98618020cb09',
    COMPONENT + '/publisher.py': '8a1992b3c1a05ea2c1f5be951d06788904e38d81f5b1605b50488ebabb7365b8',
    COMPONENT + '/typed_targets.py': 'f238f586d04b62e526eac55d9dc48ae82219d85f66b7eb32a0ad3ec941ee13f3',
}
SELECTION = COMPONENT + '/public-schema-example-selection.json'
SELECTION_SHA256 = '7b6204120c79f69fff01b5d66f27dbeae278402a007c31f55e7cf740af24657f'


def capture(name, expected):
    path = ROOT / name
    if path.is_symlink() or not path.is_file():
        raise ValueError('selected T14 input absent/unsafe: ' + name)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('selected T14 input bytes differ: ' + name)
    return raw


def verify():
    for name, digest in COMPONENT_ROWS.items():
        capture(name, digest)
    selection = json.loads(capture(SELECTION, SELECTION_SHA256))
    if (selection['authority_effect'] != 'none' or selection['actual_protected_bodies_read'] is not False
            or len(selection['rows']) != 7):
        raise ValueError('selected T14 local example scope differs')
    rows = {}
    for row in selection['rows']:
        for key in ('public_original_fixture', 'schema', 'carrier_binding'):
            binding = row[key]
            name, digest = binding['path'], binding['sha256']
            if name in rows and rows[name] != digest:
                raise ValueError('conflicting selected T14 path')
            rows[name] = digest
    for name, digest in rows.items():
        capture(name, digest)
    return {'component_files': len(COMPONENT_ROWS), 'selection_files': 1,
            'selected_input_files': len(rows), 'public_target_families': len(selection['rows'])}
