"""Current API33 full technical Reader/content/graph bridge boundary."""

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
import types

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
CONTENT = 'implementation/lab-runtime/local-host/t08-current-mixed-boundary-0001/current_content.py'
CONTENT_SHA = '47180629c3179d1a349b24c659d5fbbfe13adc8beb3859cf7738c729c6f4acaf'
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


def full_content_reader(p, content, reader, selector, roots, semantic, source_binding,
                        profile_binding, cut, private):
    """Extend the signed current selector before full proof; no original writes."""
    original = {}
    documents = {}
    for name, digest in content.TABLE_PINS.items():
        documents[name] = p.parse(selected(name, digest))
    for table, key in content.TABLES:
        rows = [documents[table][key]] if key == 'host_native_binding' else documents[table][key]
        for row in rows:
            binding = content.byte_pair(row)
            need(original.get(binding['path'], binding['sha256']) == binding['sha256'],
                 'conflicting original historical declaration')
            original[binding['path']] = binding['sha256']
    for key in content.CLASSIFICATION_TABLES:
        rows = ([documents[content.CLASSIFICATION][key]] if key == 'host_native_binding'
                else documents[content.CLASSIFICATION][key])
        for row in rows:
            binding = content.byte_pair({k: row[k] for k in ('path', 'sha256')})
            need(original.get(binding['path'], binding['sha256']) == binding['sha256'],
                 'conflicting original classification declaration')
            original[binding['path']] = binding['sha256']
    original.update(content.TABLE_PINS)
    need(len(original) == 24503, 'complete historical metadata domain differs')
    selected_rows = {row['logical_path']: row for row in selector['files']}

    def add(logical, digest, kind, *, private_name=None):
        row = selected_rows.get(logical)
        if row is not None:
            need(row['sha256'] == digest, 'existing selected path digest conflicts')
            if kind in ('history-proof', 'execution-selection'):
                need(row['kind'] in ('host-dependency', kind), 'typed selected path conflicts')
                row['kind'] = kind
            return row['id']
        physical = private / private_name if private_name is not None else (
            Path(logical) if Path(logical).is_absolute() else ROOT / logical)
        info = physical.lstat()
        need(stat.S_ISREG(info.st_mode), 'selected historical physical file absent')
        if private_name is not None:
            root_id, relative = 'private', private_name
        elif Path(logical).is_absolute():
            parent = physical.parent
            root_id = 'absolute:' + sha(str(parent).encode())[:20]
            if root_id not in roots:
                roots[root_id] = {'id': root_id, 'path': str(parent), **metadata(parent.lstat())}
            relative = physical.name
        else:
            root_id, relative = 'repo', logical
        ident = 'historic:' + sha(logical.encode())[:32]
        row = {'id': ident, 'root_id': root_id, 'path': relative,
               'logical_path': logical, 'kind': kind, 'sha256': digest,
               'size': info.st_size, **metadata(info)}
        selected_rows[logical] = row
        selector['files'].append(row)
        return ident

    table_rows = []
    for name, digest in content.TABLE_PINS.items():
        ident = add(name, digest, 'history-proof')
        table_rows.append({'binding': {'path': name, 'sha256': digest}, 'file_id': ident})
    history25 = content.HISTORICAL25
    history_id = add(history25[0], history25[1], 'history-proof')
    coverage = []
    for original_name, digest in original.items():
        alternative = content.EXTRA_ALTERNATES.get(original_name)
        if alternative is not None:
            current = alternative['path']
            need(alternative['sha256'] == digest, 'successor alternate digest differs')
            standing = 'content-only-current-locator'
        elif original_name in content._base.CONTENT_ALTERNATES:
            current, alternate_digest = content._base.CONTENT_ALTERNATES[original_name]
            need(alternate_digest == digest, 'retained alternate digest differs')
            current = (Path(current).relative_to(ROOT).as_posix()
                       if Path(current).is_relative_to(ROOT) else current)
            standing = 'content-only-current-locator'
        else:
            current, standing = original_name, 'exact-original-locator'
        preferred = 'governed-record' if original_name in content.GRAPH_RECORDS else 'host-dependency'
        ident = add(current, digest, preferred)
        coverage.append({'original_binding': {'path': original_name, 'sha256': digest},
                         'file_id': ident, 'kind': selected_rows[current]['kind'],
                         'standing': standing})
    account_id = add(content.ACCOUNT_PATH, content.ACCOUNT_SHA, 'execution-selection')
    native = content._base.ACCOUNTING_FIXED['native_reprovision']
    native_binding = native['installed_binding']
    installed_id = add(native_binding['path'], native_binding['sha256'], 'host-dependency')
    deployment_binding = native['deployment_terminal_binding']
    add(deployment_binding['path'], deployment_binding['sha256'], 'history-proof')
    scope_ref = 'technical:T08-mixed/scope-full'
    scope_id = 'historic:' + sha(scope_ref.encode())[:32]
    scope = {'schema_version': 'lab-private-historical-content-scope/v3-candidate',
             'current_source_binding': source_binding, 'current_profile_binding': profile_binding,
             'current_source_cut': cut, 'scope_file_id': scope_id,
             'historical_tables': table_rows, 'historical25_file_id': history_id,
             'coverage': coverage, 'semantic_selection': semantic,
             'body_export_allowed': False, 'authority_effect': 'none',
             'current_accounting_file_id': account_id,
             'installed_native_file_id': installed_id}
    scope_raw = p.canonical(scope)
    private_write(private / 'scope-full.json', scope_raw)
    scope_binding = {'ref': scope_ref, 'sha256': sha(scope_raw)}
    need(add(scope_binding['ref'], scope_binding['sha256'], 'history-proof',
             private_name='scope-full.json') == scope_id,
         'scope file identity differs')
    selector_raw = p.canonical(selector)
    private_write(private / 'selector-full.json', selector_raw)
    selector_binding = {'ref': 'technical:T08-mixed/selector-full', 'sha256': sha(selector_raw)}
    signer = Ed25519PrivateKey.generate()
    public = base64.b64encode(signer.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode()
    now = datetime.now(timezone.utc)
    payload = {'schema_version': 'lab-protected-input-custody-grant/v1-candidate',
               'selector_binding': selector_binding, 'source_binding': source_binding,
               'profile_binding': profile_binding, 'source_cut': cut,
               'principal_ref': 'technical-principal:T08-mixed-current',
               'operation': 'release.prepare',
               'not_before': (now - timedelta(seconds=5)).isoformat(),
               'expires_at': (now + timedelta(minutes=30)).isoformat(),
               'authority_effect': 'none'}
    grant_raw = p.canonical({'payload': payload,
                             'signature_b64': base64.b64encode(
                                 signer.sign(p.canonical(payload))).decode()})
    private_write(private / 'grant-full.json', grant_raw)
    grant_binding = {'ref': 'technical:T08-mixed/grant-full', 'sha256': sha(grant_raw)}

    def locator(name):
        info = (private / name).lstat()
        return {'root_id': 'private', 'path': name, 'size': info.st_size,
                **metadata(info)}

    anchor = p.CustodyAnchor(payload['principal_ref'], public,
                             source_binding, profile_binding, cut, payload['operation'],
                             selector_binding, grant_binding,
                             locator('selector-full.json'), locator('grant-full.json'))
    reader = p.ProtectedReader(selector_raw, grant_raw, anchor)
    return reader, anchor, scope_binding, scope, selector


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
        reader, anchor, full_scope_binding, full_scope, selector = full_content_reader(
            p, content, reader, selector, roots, selection['semantic_selection'],
            source_binding, profile_binding, technical_cut, private)
        selection['custody_anchor'] = {key: getattr(anchor, key) for key in host.ANCHOR_FIELDS}
        selection['control_roots'] = list(roots.values())
        selection['historical_content'] = {
            'scope_binding': full_scope_binding, 'scope_file_id': full_scope['scope_file_id']}
        phase('signed-full-historical-selector-constructed')
        guard_path = API + '/guard.py'
        guard_digest = next(row['sha256'] for row in source['files'] if row['path'] == guard_path)
        guard_raw = selected(guard_path, guard_digest)
        guard_module = types.ModuleType('_cal_t08_current_source_guard')
        guard_module.__file__ = str(ROOT / guard_path)
        exec(compile(guard_raw, guard_module.__file__, 'exec'), guard_module.__dict__)
        guard_module.verify(SOURCE_SHA)
        phase('actual-current-source-host-guard-preflight')
        bridge = host.ProtectedHostBridge(selection, p, g, module_bindings, ROOT,
                                          private_content_module=content)
        bridge.builder = types.SimpleNamespace(guard=lambda: guard_module.verify(SOURCE_SHA))
        phase('actual-host-bridge-constructed')
        with bridge.verified_boundary(semantics=True) as (verified_reader, historical):
            need(verified_reader is not None and
                 historical['content_identity_closure'] == 'PASS' and
                 historical['original_locator_physical_closure'] == 'REFUSED' and
                 historical['declared_unique_inputs'] == 24503 and
                 historical['current_standing']['content_only_total'] == 5,
                 'actual full historical content result differs')
        phase('actual-full-verified-boundary-closed')
        # verified_boundary itself executed original semantic_graph.verify_graph.
        # Its return is deliberately not exposed; the separate prior graph
        # receipt retains the observed counts for this exact graph selection.
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
            'schema_version': 'lab-T08-current-mixed-full-boundary/v1-candidate',
            'result': 'PASS-bounded-technical-full-boundary',
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
            'actual_semantic_graph_executed': True,
            'separate_prior_graph_receipt_sha256':
                '138b14f3d32dc6f6c90e5903a15647479c4f8f0362860a1f9618bc4689c0c24d',
            'wrong_host_module_origin_refused': module_refused,
            'proof_and_byte_substitution_controls': 'small-selector-tests-only',
            'full_reader_entry_exit_verified_this_run': True,
            'historical_content_verified_this_run': True,
            'historical_content': historical,
            'current_source_host_guard_entry_exit_verified_this_run': True,
            'full_installation_release_builder_guard_verified_this_run': False,
            'private_body_exported': False,
            'original_full_proof_status': 'REFUSED',
            'authority_effect': 'none', 'T08_complete': False}


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, indent=2))
