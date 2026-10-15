"""Capture the candidate engine closure; never alter frozen parent files."""
from loader import *


def freeze():
    require(not MANIFEST.exists(), 'candidate engine manifest already captured')
    parent_binding = bind(HERE / 'upstream-bindings.json'); parent = parse(original(parent_binding))
    delta = []
    for row in parent['files']:
        original(row)
        path = ENGINE / Path(row['path']).relative_to('implementation/lab-runtime/v2')
        if sha(path.read_bytes()) != row['sha256']:
            delta.append({'parent_binding': row, 'candidate_binding': bind(path)})
    from importlib.util import spec_from_file_location
    require({d['candidate_binding']['path'].split('/engine/')[1] for d in delta}
        == {'lab_runtime/operations.py', 'lab_runtime/protocols.py', 'lab_runtime/store.py',
            'lab_runtime/sources.py', 'lab_runtime/graph.py'}, 'unselected candidate parent delta')
    manifest = {'schema_version': 'lab-R03-candidate-engine-manifest/v1-candidate',
        'authority_effect': 'none', 'actual_owner_outcome': None,
        'engine_id': 'lab-operator-signed-coupling/v1-candidate', 'parent_binding': parent_binding,
        'files': [bind(p) for p in sorted(ENGINE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts],
        'changed_files': delta, 'profile_binding': bind(ENGINE / 'profile.json'),
        'mapping_binding': bind(ENGINE / 'endpoint-mapping.json')}
    with MANIFEST.open('xb') as stream:
        stream.write(encoded(manifest))
    pins = selected_pins(); verify_engine(pins)
    print(json.dumps({'result':'PASS','authority_effect':'none','pins':pins.__dict__,
        'parent_files_changed':0,'candidate_parent_deltas':len(delta),'files':len(manifest['files'])},sort_keys=True))


if __name__ == '__main__':
    freeze()
