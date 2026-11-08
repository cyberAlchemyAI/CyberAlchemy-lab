"""Direct current API33 mixed graph import; no whole host/owner claim."""

import base64
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import time

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
API = 'product/lab/release-candidates/v1/interface/api-integration-v33-current-0001'
SOURCE_SHA = 'e400703a2ace9ea1899d7abf15023632a83235e1e15f5459970b1ed8d12a37dd'
PROFILE_SHA = 'c86a04159a99d607f15f42078ae64b108ef5007e121f830d54174f0167b8813a'
ORIGINAL = 'product/lab/release-candidates/v1/interface/release-proof-inputs-v2-completion-0001'
TEST_SHA = 'f95ab964e9a7d8d12a905c625e574f979fbd656b5b6d64555298b6624ed214a9'
P_SHA = '7a51fed6ecf0842bc3b6711e02a0b480ca9eed666405643c4e6577f938da703f'
G_SHA = '64bfc7c45792ac67caf947d805b6881869496de7740b0de4d28e77c5b55d14b1'
BRIDGE = API + '/protected_bridge.py'
BRIDGE_SHA = 'd4c69fbbdc3dac2325adf76bcf54b98c23f6434370a4b1decc58fce65ce60634'
CONTENT = 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T08/current-standing-host-integration-preparation-0001/private_content.py'
CONTENT_SHA = 'be08149f6a1be6a17f61afda725807bc0f72d388626de77c745859796b82fa2b'
NODE = 'authority/artifact-types/ontology-node/v2/fixtures/valid/record.json'
CUT = 'authority/artifact-types/ontology-cut/v1/fixtures/valid/record.json'
EDGE = {'source': 'ontology-cut:artifact-governance:842',
        'dependency': 'ontology-node:artifact-type-definition'}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def selected(name, digest):
    path = ROOT / name
    need(not path.is_symlink() and path.is_file(), 'selected original path absent/unsafe: ' + name)
    raw = path.read_bytes()
    need(sha(raw) == digest, 'selected original bytes differ: ' + name)
    return raw


def metadata(info):
    return {'device': info.st_dev, 'inode': info.st_ino,
            'uid': info.st_uid, 'mode': stat.S_IMODE(info.st_mode)}


def private_write(path, raw):
    with path.open('xb') as out:
        out.write(raw)
        out.flush()
        os.fsync(out.fileno())
    path.chmod(0o600)


def modules():
    selected(ORIGINAL + '/protected_inputs.py', P_SHA)
    selected(ORIGINAL + '/semantic_graph.py', G_SHA)
    selected(ORIGINAL + '/test_inputs.py', TEST_SHA)
    selected(BRIDGE, BRIDGE_SHA)
    selected(CONTENT, CONTENT_SHA)
    name = '_cal_t08_mixed_selected_original_0001'
    spec = importlib.util.spec_from_file_location(
        name, ROOT / ORIGINAL / '__init__.py',
        submodule_search_locations=[str(ROOT / ORIGINAL)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    p = sys.modules[name + '.protected_inputs']
    g = sys.modules[name + '.semantic_graph']
    # The original technical fixture provides only schema/role policy generation.
    # Its synthetic Reader is discarded before constructing the current selector.
    test_spec = importlib.util.spec_from_file_location(name + '.test_inputs', ROOT / ORIGINAL / 'test_inputs.py')
    tests = importlib.util.module_from_spec(test_spec)
    sys.modules[name + '.test_inputs'] = tests
    test_spec.loader.exec_module(tests)
    api_name = '_cal_t08_mixed_current_api_0001'
    api_spec = importlib.util.spec_from_file_location(
        api_name, ROOT / API / '__init__.py',
        submodule_search_locations=[str(ROOT / API)])
    api_package = importlib.util.module_from_spec(api_spec)
    sys.modules[api_name] = api_package
    api_spec.loader.exec_module(api_package)
    bridge_spec = importlib.util.spec_from_file_location(
        api_name + '.protected_bridge', ROOT / BRIDGE)
    bridge = importlib.util.module_from_spec(bridge_spec)
    sys.modules[api_name + '.protected_bridge'] = bridge
    bridge_spec.loader.exec_module(bridge)
    content_spec = importlib.util.spec_from_file_location('_cal_t08_mixed_content_0001', ROOT / CONTENT)
    content = importlib.util.module_from_spec(content_spec)
    content_spec.loader.exec_module(content)
    return p, g, tests, bridge, content


def policy_material(tests, parent, source_binding, profile_binding, cut):
    f = tests.VariedFixture(parent)
    f.original('node', NODE, 'cal.artifact-type.ontology-node/v2')
    f.original('cut', CUT, 'cal.artifact-type.ontology-cut/v1')
    for profile in f.profiles:
        if profile['carrier_ref'] == 'cal.artifact-type.ontology-cut/v1':
            fields = [v for v in profile['fields'] if v['instance_pointer'] == '/payload/node_refs/*']
            need(len(fields) == 1, 'original cut node reference slot changed')
            fields[0]['disposition'] = 'semantic-node'
    f.edges = [EDGE]
    f.finish()
    policy = json.loads(f.payloads['policy'])
    eligibility = json.loads(f.payloads['eligibility'])
    eligibility['source_binding'] = source_binding
    eligibility['profile_binding'] = profile_binding
    eligibility['source_cut'] = cut
    for name, path in [('node', NODE), ('cut', CUT)]:
        row = next(v for v in policy['nodes'] if v['file_id'] == name)
        eligibility['subjects'][row['version_ref']]['source'] = {
            'path': path, 'sha256': sha(f.payloads[name])}
    physical = {
        'registry': tests.REGISTRY, 'catalog': tests.CATALOG,
        'kernel-identity': tests.KERNEL + 'common.py',
        'kernel-operations': tests.KERNEL + 'operations.py',
        'relation-registry': tests.RELATIONS,
        'foundation-declarations': 'authority/artifact-types/artifact-type/v1/artifact.json',
        'node': NODE, 'cut': CUT,
    }
    for row in policy['schemas']:
        physical[row['file_id']] = row['path']
    for row in policy['profiles']:
        contract = tests.G.pointer(f.registry, row['registry_pointer'])
        physical[row['descriptor_file_id']] = contract['artifact_path']
    need(set(physical) | {'source', 'profile', 'state', 'policy', 'eligibility'} == set(f.payloads),
         'original generated graph input set changed')
    for file_id, path in physical.items():
        need(selected(path, sha(f.payloads[file_id])) == f.payloads[file_id],
             'actual original graph bytes differ')
    return policy, eligibility, physical


def make_reader(p, source_raw, profile_raw, source_binding, profile_binding,
                cut, policy, eligibility, physical, private):
    selected_rows = {}
    roots = {'repo': {'id': 'repo', 'path': str(ROOT), **metadata(ROOT.lstat())},
             'private': {'id': 'private', 'path': str(private), **metadata(private.lstat())}}
    kinds = {'registry': 'history-proof', 'catalog': 'history-proof',
             'relation-registry': 'history-proof', 'foundation-declarations': 'governed-descriptor',
             'kernel-identity': 'host-dependency', 'kernel-operations': 'host-dependency',
             'node': 'governed-record', 'cut': 'governed-record'}
    for row in policy['schemas']:
        kinds[row['file_id']] = 'governed-schema'
    for row in policy['profiles']:
        kinds[row['descriptor_file_id']] = 'governed-descriptor'
    by_path = {path: (file_id, kinds[file_id]) for file_id, path in physical.items()}
    need(len(by_path) == len(physical), 'graph physical origin aliased')

    def select(name, digest, default_kind, *, root_id=None, relative=None, file_id=None):
        if name in selected_rows:
            need(selected_rows[name]['sha256'] == digest, 'conflicting selected graph/proof digest')
            return selected_rows[name]['id']
        physical_path = (private / relative if root_id == 'private' else
                         Path(name) if Path(name).is_absolute() else ROOT / name)
        if root_id is None:
            if physical_path.is_absolute() and Path(name).is_absolute():
                parent = physical_path.parent
                root_id = 'absolute:' + sha(str(parent).encode())[:20]
                roots[root_id] = {'id': root_id, 'path': str(parent), **metadata(parent.lstat())}
                relative = physical_path.name
            else:
                root_id, relative = 'repo', name
        info = physical_path.lstat()
        need(stat.S_ISREG(info.st_mode), 'selected graph/proof file absent/unsafe: ' + name)
        chosen_id, kind = by_path.get(name, (file_id or 'proof:' + sha(name.encode()), default_kind))
        row = {'id': chosen_id, 'root_id': root_id, 'path': relative,
               'logical_path': name, 'kind': kind, 'sha256': digest,
               'size': info.st_size, **metadata(info)}
        selected_rows[name] = row
        return chosen_id

    source_id = select(source_binding['ref'], source_binding['sha256'], 'source-manifest', file_id='source')
    profile_id = select(profile_binding['ref'], profile_binding['sha256'], 'contract-profile', file_id='profile')
    source = p.parse(source_raw)
    profile = p.parse(profile_raw)
    source_ids = [select(v['path'], v['sha256'], 'host-dependency') for v in source['files']]
    profile_ids = [select(v['path'], v['sha256'], 'host-dependency') for v in profile['files']]
    external_ids = [select(v['path'], v['sha256'], 'host-dependency')
                    for v in profile['external_execution_dependency_bindings']]
    for file_id, path in physical.items():
        select(path, sha((ROOT / path).read_bytes()), kinds[file_id], file_id=file_id)
        need(selected_rows[path]['id'] == file_id and selected_rows[path]['kind'] == kinds[file_id],
             'graph row kind/id differs from physical origin')
    policy_raw = p.canonical(policy)
    eligibility_raw = p.canonical(eligibility)
    for file_id, kind, raw in [('policy', 'semantic-policy', policy_raw),
                               ('eligibility', 'history-proof', eligibility_raw)]:
        path = private / (file_id + '.json')
        private_write(path, raw)
        select('technical:T08-mixed/' + file_id, sha(raw), kind,
               root_id='private', relative=path.name, file_id=file_id)
    state_raw = p.canonical({'schema_version': 'lab-protected-input-custody-state/v1-candidate',
                             'principal_ref': 'technical-principal:T08-mixed-current',
                             'revoked': False, 'authority_effect': 'none'})
    state_path = private / 'state.json'
    private_write(state_path, state_raw)
    select('technical:T08-mixed/state', sha(state_raw), 'custody-state',
           root_id='private', relative=state_path.name, file_id='state')
    scope_raw = p.canonical({'schema_version': 'technical-T08-mixed-content-scope/v1',
                             'authority_effect': 'none',
                             'whole_historical_content_verified': False})
    scope_path = private / 'scope.json'
    private_write(scope_path, scope_raw)
    select('technical:T08-mixed/scope', sha(scope_raw), 'history-proof',
           root_id='private', relative=scope_path.name, file_id='scope')
    principal = 'technical-principal:T08-mixed-current'
    selector = {
        'schema_version': 'lab-protected-input-selector/v1-candidate',
        'source_binding': source_binding, 'profile_binding': profile_binding,
        'source_cut': cut, 'principal_ref': principal,
        'operation': 'release.prepare', 'roots': list(roots.values()),
        'files': list(selected_rows.values()),
        'proof_tables': [
            {'file_id': source_id, 'row_selector': '/files', 'coverage_file_ids': source_ids},
            {'file_id': profile_id, 'row_selector': '/files', 'coverage_file_ids': profile_ids},
            {'file_id': profile_id, 'row_selector': '/external_execution_dependency_bindings',
             'coverage_file_ids': external_ids}],
        'custody_state_file_id': 'state', 'authority_effect': 'none'}
    selector_raw = p.canonical(selector)
    selector_path = private / 'selector.json'
    private_write(selector_path, selector_raw)
    selector_binding = {'ref': 'technical:T08-mixed/selector', 'sha256': sha(selector_raw)}
    signer = Ed25519PrivateKey.generate()
    public = base64.b64encode(signer.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode()
    now = datetime.now(timezone.utc)
    grant_payload = {
        'schema_version': 'lab-protected-input-custody-grant/v1-candidate',
        'selector_binding': selector_binding, 'source_binding': source_binding,
        'profile_binding': profile_binding, 'source_cut': cut,
        'principal_ref': principal, 'operation': 'release.prepare',
        'not_before': (now - timedelta(seconds=5)).isoformat(),
        'expires_at': (now + timedelta(minutes=30)).isoformat(),
        'authority_effect': 'none'}
    grant_raw = p.canonical({'payload': grant_payload,
                             'signature_b64': base64.b64encode(
                                 signer.sign(p.canonical(grant_payload))).decode()})
    grant_path = private / 'grant.json'
    private_write(grant_path, grant_raw)
    grant_binding = {'ref': 'technical:T08-mixed/grant', 'sha256': sha(grant_raw)}

    def locator(path):
        info = path.lstat()
        return {'root_id': 'private', 'path': path.name, 'size': info.st_size,
                **metadata(info)}

    anchor = p.CustodyAnchor(principal, public, source_binding, profile_binding,
                             cut, 'release.prepare', selector_binding, grant_binding,
                             locator(selector_path), locator(grant_path))
    reader = p.ProtectedReader(selector_raw, grant_raw, anchor)
    return reader, anchor, selector, roots, policy_raw, eligibility_raw, scope_raw


def run():
    started = time.monotonic()
    def phase(name):
        print(json.dumps({'phase': name, 'elapsed_seconds': round(time.monotonic() - started, 3)}),
              file=sys.stderr, flush=True)
    p, g, tests, host, content = modules()
    phase('selected-module-origins')
    source_path = API + '/source-manifest.json'
    profile_path = API + '/contract-profile.json'
    source_raw = selected(source_path, SOURCE_SHA)
    profile_raw = selected(profile_path, PROFILE_SHA)
    source_binding = {'ref': source_path, 'sha256': SOURCE_SHA}
    profile_binding = {'ref': profile_path, 'sha256': PROFILE_SHA}
    source = p.parse(source_raw)
    need(source['profile_binding'] == {'path': profile_path, 'sha256': PROFILE_SHA},
         'selected current API33 source/profile correspondence differs')
    technical_cut = {
        'branch_ref': 'technical:T08-current-mixed/branch',
        'store_ref': 'technical:T08-current-mixed/store',
        'commit_sequence': 0,
        'commit_sha256': sha(b'T08-current-mixed-technical-branch'),
        'source_profile_sha256': PROFILE_SHA, 'streams': []}
    with tempfile.TemporaryDirectory(prefix='cal-t08-mixed-current-', dir='/tmp') as location:
        parent = Path(location)
        parent.chmod(0o700)
        template = parent / 'template'
        template.mkdir(mode=0o700)
        private = parent / 'private'
        private.mkdir(mode=0o700)
        policy, eligibility, physical = policy_material(
            tests, template, source_binding, profile_binding, technical_cut)
        current_rows = {(r['path'], r['sha256'])
                        for r in source['files'] + p.parse(profile_raw)['files']}
        need(all((path, sha((ROOT / path).read_bytes())) in current_rows
                 for path in physical.values()),
             'original graph file absent from exact seventh selection')
        phase('original-public-records-and-graph-policy')
        reader, anchor, selector, roots, policy_raw, eligibility_raw, scope_raw = make_reader(
            p, source_raw, profile_raw, source_binding, profile_binding,
            technical_cut, policy, eligibility, physical, private)
        phase('signed-seventh-selector-constructed')
        module_bindings = {
            'protected_inputs': {'path': ORIGINAL + '/protected_inputs.py', 'sha256': P_SHA},
            'semantic_graph': {'path': ORIGINAL + '/semantic_graph.py', 'sha256': G_SHA},
            'private_content': {'path': CONTENT, 'sha256': CONTENT_SHA}}
        schema_path = API + '/typed-review-observation.schema.json'
        schema_raw = (ROOT / schema_path).read_bytes()
        selection = {
            'custody_anchor': {key: getattr(anchor, key) for key in host.ANCHOR_FIELDS},
            'control_roots': list(roots.values()), 'binding_routes': [],
            'semantic_selection': {
                'anchor': {
                    'policy_binding': {'ref': 'technical:T08-mixed/policy', 'sha256': sha(policy_raw)},
                    'eligibility_binding': {'ref': 'technical:T08-mixed/eligibility',
                                            'sha256': sha(eligibility_raw)},
                    'source_binding': source_binding, 'profile_binding': profile_binding,
                    'source_cut': technical_cut, 'allowed_states': ['candidate-current']},
                'policy_file_id': 'policy', 'declared_edges': [EDGE],
                'root_refs': [EDGE['source']]},
            'readiness_version': host.REVIEW_VERSION,
            'observation_schema_binding': {'path': schema_path, 'sha256': sha(schema_raw)},
            'historical_original_proof': {
                'status': 'REFUSED',
                'unavailable_binding': {
                    'path': 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/accounting-0001/unavailable-original-inputs.json',
                    'sha256': '4408c5433d41119a92660f86f856d6847be24171ddb1dab368e22c63ee294e7a'},
                'unavailable_count': 25},
            'historical_content': {
                'scope_binding': {'ref': 'technical:T08-mixed/scope', 'sha256': sha(scope_raw)},
                'scope_file_id': 'scope'}}
        bridge = host.ProtectedHostBridge(selection, p, g, module_bindings, ROOT,
                                          private_content_module=content)
        phase('actual-host-bridge-constructed')
        actual = bridge.verify_semantics(reader)
        phase('actual-mixed-graph-verified')
        need(actual['nodes'] == 2 and actual['edges'] == 1
             and actual['declarations'] == 7 and actual['profiles'] == 2
             and actual['admission_or_owner_authority'] is False,
             'actual original mixed graph result differs')
        wrong = dict(module_bindings)
        wrong['protected_inputs'] = {'path': module_bindings['protected_inputs']['path'],
                                     'sha256': '0' * 64}
        try:
            host.ProtectedHostBridge(selection, p, g, wrong, ROOT,
                                     private_content_module=content)
        except ValueError:
            module_refused = True
        else:
            raise ValueError('wrong protected host module origin accepted')
        # Do not multiply 3.3 GiB boundaries for negatives during the live
        # current run. The same original path/kind/byte refusals are exercised
        # in test_small_graph.py with a signed, small technical selector.
        return {
            'schema_version': 'lab-T08-current-mixed-graph-import/v1-candidate',
            'result': 'PASS-bounded-technical-mixed-graph-import',
            'source_sha256': SOURCE_SHA, 'profile_sha256': PROFILE_SHA,
            'technical_cut_only': True,
            'selected_source_rows': len(source['files']),
            'selected_profile_rows': len(p.parse(profile_raw)['files']),
            'selected_proof_occurrences': sum(len(t['coverage_file_ids'])
                                              for t in selector['proof_tables']),
            'selected_files': len(reader.files),
            'original_record_bindings': [
                {'path': name, 'sha256': sha((ROOT / name).read_bytes())}
                for name in (NODE, CUT)],
            'actual_graph': actual,
            'wrong_host_module_origin_refused': module_refused,
            'proof_and_byte_substitution_controls': 'small-selector-tests-only',
            'full_reader_entry_exit_verified_this_run': True,
            'historical_content_verified_this_run': False,
            'current_host_entry_exit_verified_this_run': False,
            'private_body_exported': False,
            'original_full_proof_status': 'REFUSED',
            'authority_effect': 'none', 'T08_complete': False}


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, indent=2))
