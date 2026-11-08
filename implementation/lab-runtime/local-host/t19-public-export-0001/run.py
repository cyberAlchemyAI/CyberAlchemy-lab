"""Bounded public-file export through the unchanged selected API36 kernel."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import time
from contextlib import nullcontext

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v36-current-t06-0001'
PACKAGE = '_t19_selected_api36'
PINS = {
    'source-manifest.json': '5990d980ae1df2fe59c90eabfc9de806ea8ab7abbf90bb123063f5ad83ff592f',
    'contract-profile.json': 'c5bc36e213979199fdd947bdb7309a4e32534305fd93eca6366aff9e19f01e78',
    'export_kernel.py': '385e0ba2417631c335dcaa5ad4362b743e2785ddf7dece61eeb24202eb74f464',
    'protocol.py': 'f3f24585ac712732c297ef04b4a7f31f6cd70745b60f6dd0bc5df92b40d7bcde',
}
FIXTURES = (
    ('authority/artifact-types/intent/v1/fixtures/valid/record.json',
     'edfe2f79412c823d8ec45f7e97a8e6f1031ca523aecba7ac39712484c7f9e078',
     'cal.artifact-type.intent/v1', 'intent/body.json'),
    ('authority/artifact-types/goal/v1/fixtures/valid/goal.json',
     '5e2899448cd647884decc23e4874f199080080633dcdd287fe99422159e211bd',
     'cal.artifact-type.goal/v1', 'goal/body.json'),
)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def check(condition, message):
    if not condition:
        raise ValueError(message)

def api():
    spec = importlib.util.spec_from_file_location(PACKAGE, API / '__init__.py', submodule_search_locations=[str(API)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[PACKAGE] = module
    spec.loader.exec_module(module)
    return module

def fixture_bytes(profile):
    rows = {row['path']: row['sha256'] for row in profile['files']}
    out = []
    for relative, expected, carrier, output in FIXTURES:
        check(rows.get(relative) == expected, 'fixture absent from exact selected API36 profile')
        path = ROOT / relative
        check(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(ROOT), 'unsafe fixture path')
        raw = path.read_bytes()
        check(sha(raw) == expected, 'selected public fixture changed')
        out.append((relative, raw, carrier, output))
    return out

def selected():
    for name, expected in PINS.items():
        check(sha((API / name).read_bytes()) == expected, 'selected API36 file changed: ' + name)
    profile = json.loads((API / 'contract-profile.json').read_bytes())
    return profile, fixture_bytes(profile)

def construct(pkg, schema, selected_profile, fixture):
    from importlib import import_module
    K = import_module(PACKAGE + '.export_kernel')
    G = import_module(PACKAGE + '.guard')
    P = import_module(PACKAGE + '.protocol')
    bindings = [{'path': path, 'sha256': sha(raw)} for path, raw, _, _ in fixture]
    cut = {'store_ref': 'technical:T19-public-profile-pinned-files',
           'branch_ref': 'branch:technical:T19-public-profile-pinned-files',
           'commit_sequence': 0, 'commit_sha256': sha(K.encoded(bindings)),
           'source_profile_sha256': PINS['contract-profile.json'], 'streams': []}
    materials = []
    for path, raw, carrier, _ in fixture:
        body = json.loads(raw)
        identity = body.get('node_id', body.get('goal_id'))
        check(type(identity) is str and identity, 'public fixture identity missing')
        artifact = {'scope_ref': body.get('scope_ref', 'scope:technical-T19-public-fixture'),
                    'identity_ref': identity, 'version_ref': body.get('version', 'fixture:v1'),
                    'carrier_ref': carrier, 'byte_sha256': sha(raw)}
        materials.append(K.Material(K.encoded(artifact), raw, path, 'public-profile-pinned-json/v1'))
    actor = {'principal_ref': 'principal:technical-T19-public-export', 'agent_instance_ref': None,
             'assignment_ref': None, 'session_ref': None, 'role_assignment_refs': []}
    review = {'selection_ref': 'selection:technical-T19-public-intent-goal', 'source_cut': cut,
              'artifact_refs': [m.artifact for m in materials], 'include_session_memory': False,
              'authority_effect': 'none'}
    selection = K.Selection(review['selection_ref'], K.encoded(cut), tuple(materials), K.encoded(review))
    def source_guard():
        G.verify(PINS['source-manifest.json'])
        # Selection remains fresh across each entry/exit, including after the
        # schema and API guards. No cached acceptance of changed fixture bytes.
        check(fixture_bytes(selected_profile) == fixture, 'public fixture changed across export boundary')
    return K, actor, selection, source_guard

def request(K, actor, selection, *, mode='byte-exact', paths=None):
    return {'schema_version': 'lab-file-materialization-request/v1-candidate',
            'request_ref': 'request:technical-T19-public-export', 'actor': actor,
            'source_cut': selection.cut, 'selection_ref': selection.ref,
            'artifact_refs': [m.artifact for m in selection.materials],
            'output_root_scope_ref': 'owned:technical-T19-public-export', 'mode': mode,
            'renderer_binding': K.renderer_binding() if mode == 'rendered' else None,
            'managed_relative_paths': paths or [row[3] for row in FIXTURES],
            'overwrite_unmanaged_files': False, 'include_session_memory': False,
            'privacy_review_binding': selection.privacy_binding, 'authority_effect': 'none'}

def run():
    started = time.monotonic()
    profile, fixture = selected()
    api()
    from importlib import import_module
    G = import_module(PACKAGE + '.guard')
    P = import_module(PACKAGE + '.protocol')
    G.verify(PINS['source-manifest.json'])
    schema = P.Schemas(PINS['contract-profile.json'])
    K, actor, selection, source_guard = construct(PACKAGE, schema, profile, fixture)
    observations = []
    base = HERE / 'working' / 'owned-export-0001'
    base.mkdir(parents=True, mode=0o700, exist_ok=True)
    check(stat.S_IMODE(base.stat().st_mode) == 0o700 and base.stat().st_uid == os.getuid(),
          'owned private export base required')
    with nullcontext(base):
        for mode in ('byte-exact', 'rendered'):
            root = base / mode
            root.mkdir(mode=0o700, exist_ok=True)
            host = K.ExportHost(root, 'owned:technical-T19-public-export', actor, selection,
                                schema, source_guard, lambda: True)
            req = request(K, actor, selection, mode=mode)
            receipt = host.materialize(req)
            check(receipt['posture'] == 'published', 'export did not publish')
            generation = root / sha(K.encoded(req))
            manifest_raw = (generation / 'manifest.json').read_bytes()
            receipt_raw = (generation / 'receipt.json').read_bytes()
            marker_raw = (generation / 'PUBLISHED.json').read_bytes()
            check(receipt_raw == K.encoded(receipt), 'receipt bytes differ')
            check(json.loads(marker_raw) == {'manifest_sha256': sha(manifest_raw),
                                              'receipt_sha256': sha(receipt_raw)}, 'publication marker differs')
            for path, raw, _, output in fixture:
                got = (generation / 'files' / output).read_bytes()
                expected = raw if mode == 'byte-exact' else (json.dumps(json.loads(raw), indent=2,
                    sort_keys=True, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')
                check(got == expected, 'physical output differs')
            check(host.materialize(copy.deepcopy(req)) == receipt, 'exact replay differs')
            observations.append({'case': mode, 'posture': 'published', 'request_sha256': sha(K.encoded(req)),
                                 'manifest_sha256': sha(manifest_raw), 'receipt_sha256': sha(receipt_raw),
                                 'marker_sha256': sha(marker_raw),
                                 'output_sha256': [sha((generation / 'files' / row[3]).read_bytes()) for row in fixture],
                                 'exact_replay': True})
        root = base / 'negative'
        root.mkdir(mode=0o700, exist_ok=True)
        foreign = root / 'foreign.txt'
        if not foreign.exists():
            foreign.write_bytes(b'foreign-untouched')
        check(foreign.read_bytes() == b'foreign-untouched', 'foreign file changed before run')
        host = K.ExportHost(root, 'owned:technical-T19-public-export', actor, selection,
                            schema, source_guard, lambda: True)
        for label, change in (
            ('parent-traversal', lambda r: r.update(managed_relative_paths=['../escape.json','goal/body.json'])),
            ('absolute-path', lambda r: r.update(managed_relative_paths=['/tmp/escape.json','goal/body.json'])),
            ('unmanaged-overwrite', lambda r: r.update(overwrite_unmanaged_files=True)),
        ):
            req = request(K, actor, selection)
            change(req)
            try:
                host.materialize(req)
            except ValueError as error:
                check(not (root / sha(K.encoded(req))).exists(), label + ' created a generation')
                check(foreign.read_bytes() == b'foreign-untouched', label + ' changed foreign bytes')
                observations.append({'case': label, 'posture': 'refused', 'error': str(error)})
            else:
                raise ValueError(label + ' unexpectedly published')
    result = {'schema_version': 'lab-T19-public-export-technical-run/v1',
              'api_source_manifest_sha256': PINS['source-manifest.json'],
              'api_profile_sha256': PINS['contract-profile.json'],
              'selected_public_fixture_bindings': [{'path': p, 'sha256': sha(raw)} for p, raw, _, _ in fixture],
              'cases': observations, 'elapsed_seconds': round(time.monotonic()-started, 3),
              'authority_effect': 'none', 'historical_custody_fixture_replayed': False,
              'claim_ceiling': 'Local technical file export over public profile-pinned fixtures only; no current Source8, owner decision, or canonical publication.'}
    (HERE / 'RESULT.json').write_bytes(json.dumps(result, indent=2, sort_keys=True).encode() + b'\n')
    print(json.dumps({'cases': [(x['case'], x['posture']) for x in observations],
                      'elapsed_seconds': result['elapsed_seconds']}))

if __name__ == '__main__':
    run()
