"""Disjoint O03 post-D75 source-capture successor probe; no query or authority effect."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASE = ROOT / 'product/lab/release-candidates/v1/interface/coupling'
QUERY = ROOT / 'implementation/lab-ontology/candidates/v1/queries/successors/0009'
OLD_PROFILE_SHA = 'cbfe3d7c5f92d0bc547b836a9d84616b9be26cb399a587aab8800f93fd96ed58'
OLD_MANIFEST_SHA = '53e2f74c53f123b42d60d3cc3b4c66e75f3fa0c4c9a3142bf3f11e7500bd9677'
NEW_PROFILE_SHA = '16fbff5992cf8006219f7a33aee75642e3d6dd8a9624dc03058dc04703627f67'
NEW_MANIFEST_SHA = 'adc284c0c25ad6389c05c22c8652d218b119341accca300592d842402a66c276'
NEW_SOURCES_SHA = '0c3d4bf662060f4e6aff2038e48ec053af5a98ff7429b6138a438358b66d5db3'
SOURCE_PATH = 'authority/project-state-transitions/current.json'
OLD_SOURCE_SHA = '8ba8ee25ccbf12721d800c693120a3452ddf1ec4427c6fdf1e0655beae31bc12'
NEW_SOURCE_SHA = '12937950af2a00ef329deb1a922275250c61ad199b8f6216eab448e06bf49984'
QUERY_SELECTION = {'path': 'implementation/lab-ontology/candidates/v1/queries/successors/0009/packages/0001/selection.json',
                   'sha256': '5dce634a00ac7ff99f4319332d36ca77ee2c5850244d016b4bf778b705db9cf3'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_successor(expected_current=NEW_SOURCE_SHA):
    if sha(ROOT / SOURCE_PATH) != expected_current:
        raise ValueError('current authority source differs from selected successor')
    old = BASE / 'engine/profile.json'
    predecessor = BASE / 'engine-manifest.json'
    new = HERE / 'profile.json'
    successor = HERE / 'engine-manifest.json'
    if (sha(old), sha(predecessor), sha(new), sha(successor)) != (
            OLD_PROFILE_SHA, OLD_MANIFEST_SHA, NEW_PROFILE_SHA, NEW_MANIFEST_SHA):
        raise ValueError('engine predecessor or successor bytes differ')
    before, after = json.loads(old.read_bytes()), json.loads(new.read_bytes())
    expected = json.loads(old.read_bytes())
    if before['current_selection']['lookup'] != {'path': SOURCE_PATH, 'sha256': OLD_SOURCE_SHA}:
        raise ValueError('unexpected engine predecessor lookup')
    expected['operational_roots'] += [
        {'path': 'authority/admissions/lab-repository-owner-bootstrap-v1-0005/bundle.json',
         'sha256': '49ece9676ddbbaaedfec1f1245777de311d409075d2483da4c6be7e4950d445d'},
        {'path': 'authority/admissions/lab-specialist-owner-bootstrap-v1-0003/bundle.json',
         'sha256': '8eb940493460ea2c10f50f677d5cbfbd5b898625868af036fb0e594ec9b1b220'}]
    expected['admission_as_of'] = 'decision:lab-specialist-owner-bootstrap-0003'
    expected['current_selection'] = {
        'bundle_path': 'authority/admissions/lab-specialist-owner-bootstrap-v1-0003/bundle.json',
        'history_base': 'authority/admissions/lab-specialist-owner-bootstrap-v1-0003/instances',
        'history_cursor': 7, 'lookup': {'path': SOURCE_PATH, 'sha256': NEW_SOURCE_SHA},
        'state_path': 'authority/admissions/lab-specialist-owner-bootstrap-v1-0003/instances/project-state.json',
        'state_version_ref': 'project-state:cyberalchemy-v2-to-lab-migration:specialist-owner-bootstrap-0003@sha256.cccf18d2966cf0dd494f7d88b054243bb635a91bc84fdcbf5c70709b7b6f8793'}
    expected['successor_application_receipts'] = [
        {'path': 'authority/admissions/lab-repository-owner-bootstrap-v1-0005/receipts/application.json',
         'sha256': 'cbe13d1a9f2628c2150ed4700a7b3037a79e0abbef3b32233206d9a5cd2eaead'},
        {'path': 'authority/admissions/lab-specialist-owner-bootstrap-v1-0003/receipts/application.json',
         'sha256': 'ef78b537748071df158d7ca06ef91e56b8868deade6876891ad3186d0203d310'}]
    if after != expected:
        raise ValueError('successor profile changes more than exact T12 current selection')
    old_manifest, new_manifest = json.loads(predecessor.read_bytes()), json.loads(successor.read_bytes())
    expected_manifest = json.loads(predecessor.read_bytes())
    old_engine = (BASE / 'engine').relative_to(ROOT).as_posix()
    new_engine = (HERE / 'engine').relative_to(ROOT).as_posix()
    def successor_binding(binding):
        if binding['path'].startswith(old_engine + '/'):
            binding['path'] = new_engine + binding['path'][len(old_engine):]
            if binding['path'].endswith('/profile.json'):
                binding['sha256'] = NEW_PROFILE_SHA
            if binding['path'].endswith('/lab_runtime/sources.py'):
                binding['sha256'] = NEW_SOURCES_SHA
    for binding in expected_manifest['files']:
        successor_binding(binding)
    successor_binding(expected_manifest['mapping_binding'])
    successor_binding(expected_manifest['profile_binding'])
    for row in expected_manifest['changed_files']:
        successor_binding(row['candidate_binding'])
    if new_manifest != expected_manifest or old_manifest['profile_binding']['sha256'] != OLD_PROFILE_SHA:
        raise ValueError('successor manifest differs from exact copied engine/source/profile rebind')
    if {binding['path'] for binding in new_manifest['files']} != {
            path.relative_to(ROOT).as_posix() for path in (HERE / 'engine').rglob('*')
            if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc'}:
        raise ValueError('successor engine file closure differs')
    for binding in new_manifest['files']:
        if sha(ROOT / binding['path']) != binding['sha256']:
            raise ValueError('successor engine member changed')
    if sha(ROOT / QUERY_SELECTION['path']) != QUERY_SELECTION['sha256']:
        raise ValueError('historical query selection differs')
    return new_manifest


def attempt():
    manifest = verify_successor()
    sys.path.insert(0, str(QUERY))
    from selection import verify
    import scope
    verify(QUERY_SELECTION)
    pins = scope.loader.EnginePins(NEW_MANIFEST_SHA, scope.PINS.engine_id,
                                   scope.PINS.mapping_sha256, NEW_PROFILE_SHA)
    scope.loader.MANIFEST = HERE / 'engine-manifest.json'
    scope.loader.ENGINE = HERE / 'engine'
    scope.PINS = pins
    scope.loader.verify_engine(pins)
    result = {'schema_version': 'lab-T10-O03-T12-source-capture-successor-probe/v2',
              'predecessor_profile_sha256': OLD_PROFILE_SHA,
              'successor_profile_sha256': NEW_PROFILE_SHA,
              'successor_manifest_sha256': NEW_MANIFEST_SHA,
              'current_source_sha256': NEW_SOURCE_SHA,
              'engine_manifest_selected': True,
              'queries_executed': 0,
              'selected_governed_model_representations': 0,
              'authority_effect': 'none'}
    try:
        with scope.governed_scope('d75-selected-source') as selected:
            result['scope_state'] = selected.guard()['state']
            data = selected.data
            result['captured_subject_count'] = len(data['projection']['subjects'])
            result['selected_state_ref'] = data['projection']['state']['node_id']
            result['selected_state_cursor'] = data['projection']['state']['payload']['cursor']
            result['project_history_cursors'] = {
                name: len(history['payload']['events']) for name, history in data['projection']['histories'].items()}
            result['query_contract_status'] = 'NOT_SELECTED-original-O03-scope-still-names-D75'
    except Exception as error:
        result['scope_state'] = 'REFUSED'
        result['exception_class'] = type(error).__name__
        result['exception_message'] = str(error)[:300]
    return result


if __name__ == '__main__':
    print(json.dumps(attempt(), sort_keys=True, indent=2))
