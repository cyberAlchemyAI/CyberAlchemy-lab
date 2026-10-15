"""Fresh-process original-byte and partial-effect observations for the export kernel."""
import argparse
import base64
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
PACKAGE = ROOT / 'product/lab/release-candidates/v1/interface/file-materialization-v1'
SOURCE = RUN / 'file-materialization-audit-source-0001.json'
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path), 'sha256': sha(path.read_bytes())}
def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    args = parser.parse_args()
    assert sha(SOURCE.read_bytes()) == args.source_sha256
    source = json.loads(SOURCE.read_bytes())
    checks = []
    def need(condition, name):
        assert condition, name
        checks.append(name)
    for row in source['files']:
        assert bind(ROOT / row['path']) == row
    name = '_cal_file_export_independent'
    spec = importlib.util.spec_from_file_location(name, PACKAGE / '__init__.py', submodule_search_locations=[str(PACKAGE)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    B = __import__(name + '.base', fromlist=['*'])
    K = __import__(name + '.kernel', fromlist=['*'])
    schemas = B.guard()
    observations = []
    roots = []
    with B.P.source.replay_source('custody-participation') as view:
        cut = B.H.cut(view)
        actual = []
        with B.M.model_read_batch(view):
            for subject in view.subjects.values():
                if subject['carrier_ref'] not in ('cal.artifact-type.intent/v1', 'cal.artifact-type.goal/v1') or subject['source'].get('encoding') != view.handle.custody.ENCODING:
                    continue
                header = B.M.artifact_ref(view, subject)
                raw, locator, encoding, enclosing = B.M.record_bytes(view, subject)
                tx_raw = view.originals[subject['source']['path']]
                target = view.handle.common.pointer(json.loads(tx_raw), subject['source']['record_selector'].removesuffix('/record'))
                independent = base64.b64decode(target['content']['data'], validate=True)
                need(raw == independent and sha(raw) == header['byte_sha256'], 'independent original transaction body extraction ' + header['version_ref'])
                need(raw != view.handle.common.encoded(subject['record']) and enclosing == sha(tx_raw), 'body versus serialized value versus enclosing transaction ' + header['version_ref'])
                actual.append(K.Material(K.encoded(header), raw, locator, encoding))
        need(len(actual) == 2, 'complete independently selected two-artifact export closure')
        review = {'selection_ref': 'selection:independent-intent-goal-export', 'source_cut': cut, 'artifact_refs': [m.artifact for m in actual], 'include_session_memory': False, 'authority_effect': 'none'}
        selection = K.Selection(review['selection_ref'], K.encoded(cut), tuple(actual), K.encoded(review))
        actor = {'principal_ref': 'principal:owned-independent-export-fixture', 'agent_instance_ref': None, 'assignment_ref': None, 'session_ref': None, 'role_assignment_refs': []}
        request = {'schema_version': 'lab-file-materialization-request/v1-candidate', 'request_ref': 'request:independent-managed-export', 'actor': actor, 'source_cut': cut, 'selection_ref': selection.ref, 'artifact_refs': review['artifact_refs'], 'output_root_scope_ref': 'owned:independent-file-export', 'mode': 'byte-exact', 'renderer_binding': None, 'managed_relative_paths': ['selected/00.json', 'selected/01.json'], 'overwrite_unmanaged_files': False, 'include_session_memory': False, 'privacy_review_binding': selection.privacy_binding, 'authority_effect': 'none'}
        for interrupted in (False, True):
            with tempfile.TemporaryDirectory(prefix='cal-R03-independent-file-export-') as temporary:
                root = Path(temporary)
                root.chmod(0o700)
                roots.append(str(root))
                (root / 'unmanaged.txt').write_bytes(b'preserve this independent file')
                state = {'calls': 0, 'revoked': False}
                def permission():
                    state['calls'] += 1
                    if interrupted and state['calls'] >= 5:
                        state['revoked'] = True
                    return not state['revoked']
                host = K.ExportHost(root, request['output_root_scope_ref'], actor, selection, schemas, view.custody_signed_sources.guard, permission)
                result = host.materialize(request)
                need(schemas.protocol_valid('urn:cyberalchemy-lab:protocol:file-materialization-receipt:v1-candidate', result), 'actual receipt conforms to unchanged schema ' + str(interrupted))
                generation = root / sha(K.encoded(request))
                if interrupted:
                    need(result['posture'] == 'indeterminate' and result['recovery_required'] and (generation / 'CLAIM.json').is_file(), 'real permission loss after durable claim retains uncertainty')
                    need(not (generation / 'PUBLISHED.json').exists(), 'partial generation is not published')
                    state['revoked'] = False
                    # A fresh current host permission permits inspection only;
                    # the existing pending generation still cannot redispatch.
                    retry = K.ExportHost(root, request['output_root_scope_ref'], actor, selection, schemas, view.custody_signed_sources.guard, lambda: True)
                    before = sorted(p.relative_to(root).as_posix() for p in root.rglob('*'))
                    refused = False
                    try:
                        retry.materialize(request)
                    except ValueError:
                        refused = True
                    need(refused and before == sorted(p.relative_to(root).as_posix() for p in root.rglob('*')), 'current permission does not redispatch retained pending generation')
                    observations.append({'interrupted_after_claim': True, 'receipt': result, 'pending_claim': json.loads((generation / 'CLAIM.json').read_bytes())})
                else:
                    need(result['posture'] == 'published' and not result['recovery_required'], 'actual independent managed generation published')
                    manifest_raw = (generation / 'manifest.json').read_bytes()
                    receipt_raw = (generation / 'receipt.json').read_bytes()
                    marker = json.loads((generation / 'PUBLISHED.json').read_bytes())
                    need(marker == {'manifest_sha256': sha(manifest_raw), 'receipt_sha256': sha(receipt_raw)}, 'publication marker binds actual flushed manifest and receipt')
                    manifest = json.loads(manifest_raw)
                    for path, material, row in zip(request['managed_relative_paths'], actual, manifest['files'], strict=True):
                        output = (generation / 'files' / path).read_bytes()
                        need(output == material.original_bytes and row['artifact'] == material.artifact and row['output_sha256'] == sha(output) and row['source_locator'] == material.source_locator, 'actual independent output original bytes and provenance ' + path)
                    before = {p.relative_to(root).as_posix(): (p.stat().st_ino, sha(p.read_bytes())) for p in root.rglob('*') if p.is_file()}
                    need(host.materialize(request) == result, 'independent exact retry returns recorded receipt')
                    need(before == {p.relative_to(root).as_posix(): (p.stat().st_ino, sha(p.read_bytes())) for p in root.rglob('*') if p.is_file()}, 'independent retry does not rewrite managed files')
                    observations.append({'interrupted_after_claim': False, 'receipt': result, 'manifest': manifest, 'marker': marker})
                need((root / 'unmanaged.txt').read_bytes() == b'preserve this independent file', 'independent unmanaged bytes preserved ' + str(interrupted))
            need(not root.exists(), 'actual independently owned output root removed ' + str(interrupted))
        view.custody_signed_sources.guard()
    for row in source['files']:
        assert bind(ROOT / row['path']) == row
    out = RUN / 'file-materialization-independent-observations-0001.json'
    put(out, {'schema_version': 'lab-file-materialization-independent-observation/v1-candidate', 'result': 'PASS', 'checks': len(checks), 'check_names': checks, 'source_binding': bind(SOURCE), 'observations': observations, 'owned_output_roots_removed': roots, 'fixture_permission_only': True, 'public_api_qualification': False, 'observed_at': datetime.now(timezone.utc).isoformat(), 'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'PASS', 'checks': len(checks), 'observation_binding': bind(out)}), flush=True)
if __name__ == '__main__':
    main()
