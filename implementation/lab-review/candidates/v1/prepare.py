#!/usr/bin/env python3
"""Materialize a new numbered candidate preparation; never overwrite an old one."""
from review import *

if __name__ == '__main__':
    value = assemble(); registry = registry_candidate(); artifact = runtime_artifact()
    packages = PACKAGE / 'packages'; packages.mkdir(exist_ok=True)
    index = 1
    while (packages / f'{index:04d}').exists(): index += 1
    destination = packages / f'{index:04d}'; destination.mkdir()
    for name, body in [('runtime-implementation.json', artifact), ('registry.json', registry)]:
        (destination / name).write_bytes(encoded(body))
    value['generated_targets'] = [binding((destination / name).relative_to(ROOT).as_posix()) for name in ('runtime-implementation.json', 'registry.json')]
    (destination / 'REGISTRY.md').write_text(REGISTRY_PROJECTION)
    for member in value['members']:
        if member['member_id'] == 'protocol:C10:successor-runtime': member['targets'].append(value['generated_targets'][0])
        if member['member_id'] == 'protocol:C10:method-type': member['targets'].append(value['generated_targets'][1])
    validate_members(value)
    path = destination / 'preparation.json'; path.write_bytes(encoded(value))
    print(json.dumps({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes()), 'members': len(value['members']), 'authority_effect': 'none'}))
