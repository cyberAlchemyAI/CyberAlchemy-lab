"""Actual frozen public snapshot byte fidelity/size probe; no authenticated source claim."""
import base64
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'


def main():
    check = BASE / 'package-publication-v1/checks.py'
    spec = importlib.util.spec_from_file_location('_cal_public_snapshot_checks', check)
    C = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(C)
    own_source = 'f925592eeacb64b74933652fa4223ef62f58e0e2ae7c7b90ceeb620f03b37252'
    C.guard(own_source)
    test_spec = importlib.util.spec_from_file_location('_cal_public_snapshot_fixtures', check.with_name('test_publication.py'))
    fixtures = importlib.util.module_from_spec(test_spec)
    sys.modules[test_spec.name] = fixtures
    test_spec.loader.exec_module(fixtures)
    P = fixtures.P
    api_source = BASE / 'api-v52/source-manifest.json'
    assert C.bind(api_source)['sha256'] == 'b28af91a974d3039aec4dae206d4dc8dc2007835f69adaee66b800e067da4c93'
    manifest = json.loads(api_source.read_bytes())
    snapshot = BASE / 'current-participation-v4/packages/0001/branch.snapshot'
    rows = [r for r in manifest['files'] if r['path'] == snapshot.relative_to(ROOT).as_posix()]
    assert len(rows) == 1 and C.bind(snapshot) == rows[0]
    original = snapshot.read_bytes()
    data = P.T.parse(original, P.T.MAX_MATERIAL_BYTES)
    decoded_checks = []
    for name, row in sorted(data['files'].items()):
        raw = base64.b64decode(row['base64_original_bytes'], validate=True)
        assert base64.b64encode(raw).decode() == row['base64_original_bytes']
        assert P.sha(raw) == row['sha256']
        # Decode/check embedded public JSON too; the envelope's base64 fields alone
        # are not evidence of absence of credential or memory fields.
        P.T.privacy(P.T.parse(raw, P.T.MAX_MATERIAL_BYTES))
        decoded_checks.append({'relative_path': name, 'sha256': P.sha(raw), 'size_bytes': len(raw)})
    F = fixtures.F.Packages('test_export_preserves_whitespace_and_original_bytes')
    F.setUp()
    F.change_dependency(original, 'json-utf8')
    F.contract['maximum_package_bytes'] = P.T.MAX_PACKAGE_BYTES
    F.sync_export_controls()
    package = F.export()
    package_binding = P.pin('package:synthetic-size-probe-with-public-snapshot', package)
    verified = F.engine.verify_archive(package, package_binding)
    snapshot_row = next(r for r in verified['materials'] if r['binding'] == F.dependency_binding)
    assert base64.b64decode(snapshot_row['original_bytes_b64']) == original
    with tempfile.TemporaryDirectory(prefix='cal-package-real-snapshot-') as temporary:
        root = Path(temporary) / 'owned-exports'
        root.mkdir(mode=0o700)
        root_identity = P.identity(root.stat())
        scope = {'schema_version': 'lab-owned-package-root/v1-candidate', 'output_root': str(root),
            'output_root_scope_ref': 'output:synthetic-size-probe', 'principal_ref': 'principal:synthetic-size-probe',
            'output_root_identity': root_identity, 'authority_effect': 'none', 'actual_owner_outcome': None}
        raw = P.encoded(scope)
        fd = os.open(root / '.scope.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
        host = P.Publisher(root, scope['output_root_scope_ref'], root_identity, P.pin('scope:synthetic-size', raw),
            scope['principal_ref'], F.engine, lambda: None, lambda: True, P.T.MAX_PACKAGE_BYTES, 1)
        request = P.pin('request:synthetic-size-probe', P.T.encoded(F.request))
        receipt = host.publish(package, package_binding, request, F.cut)
        dirs = list(root.glob('pkg-*'))
        assert len(dirs) == 1
        assert (dirs[0] / 'package.json').read_bytes() == package
        before = {p.name: (p.stat().st_ino, p.stat().st_mtime_ns, p.stat().st_ctime_ns) for p in dirs[0].iterdir()}
        assert host.publish(package, package_binding, request, F.cut, existing_only=True) == receipt
        after = {p.name: (p.stat().st_ino, p.stat().st_mtime_ns, p.stat().st_ctime_ns) for p in dirs[0].iterdir()}
        assert before == after
    C.guard(own_source)
    assert C.bind(snapshot) == rows[0]
    report = {'schema_version': 'lab-package-public-source-size-probe/v1-candidate', 'result': 'PASS',
        'source_snapshot_binding': rows[0], 'source_snapshot_bytes': len(original),
        'embedded_original_file_checks': decoded_checks, 'package_bytes': len(package),
        'package_sha256': P.sha(package), 'receipt': receipt, 'exact_snapshot_bytes_retained': True,
        'actual_owned_temporary_publication_completed': True, 'readonly_retry_attributes_unchanged': True,
        'temporary_cleanup_completed': True, 'source_guarded_exit_completed': True,
        'fixture_posture': 'synthetic-root-and-controls-with-actual-frozen-public-snapshot-bytes',
        'actual_signed_source_replay_qualified': False, 'actual_authenticated_host_used': False,
        'actual_source_privacy_review_qualified': False, 'actual_public_calls': 0, 'public_handlers_added': 0,
        'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False, 'goal_complete': False,
        'claim_ceiling': 'Size and exact-byte filesystem probe for the bound 23.5 MB public snapshot and its six original embedded files. Synthetic root/cut/control/permission values are explicit fixtures; no authenticated source replay, genuine privacy review, public operation or semantic import is qualified.',
        'files': [C.bind(Path(__file__).resolve()), C.bind(api_source), rows[0], C.bind(check.with_name('source-manifest.json'))]}
    path = RUN / 'package-public-source-size-receipt-0001.json'
    with path.open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'PASS', 'source_bytes': len(original), 'package_bytes': len(package),
        'embedded_files': len(decoded_checks), 'report_binding': C.bind(path), 'actual_public_calls': 0}), flush=True)


if __name__ == '__main__':
    main()
