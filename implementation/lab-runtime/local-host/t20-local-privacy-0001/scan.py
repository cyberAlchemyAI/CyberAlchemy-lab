"""Exact T07 local package privacy conformance, without content export."""
import hashlib
import json
from pathlib import Path
import re
import stat
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
T07 = ROOT / 'implementation/lab-runtime/local-host'
EVIDENCE = T07 / 'working/t07-contained-package-20261022'
PINS = {
    T07 / 'source-manifest.json': '1e00e6fd7f1baf7f8cfcd0c0ae7c11ab66649e05cc9575705bee968117ae0346',
    T07 / 'package-release.json': 'a8cfacd9e15b65184c1b87a284a699475850b8a783a354102301f50ccbe9cb3e',
    EVIDENCE / 'RELEASE-v3.json': '3d60368f74bdb940229e67931fecbb526248cb81a6519b2f830bf8599b03378d',
    EVIDENCE / 'RUN-v3.log': '16164883d708e054b85aa4fcef48648e638151116681c701d12b8007952e4118',
    EVIDENCE / 'INSPECT-v3-chain.json': '4e4efc1b2a22abf64e10881c046ffe64bc15a1cb65dd191a078ba89ce4277020',
    EVIDENCE / 'INSPECT-v3-work.json': '46e8f131e9b303bf7e1ebbb7d8d67205631d5ff53579cde1efd0e2610c5bfac6',
}
PRIVATE_SEGMENT = re.compile(r'(?:private[_-]?key|(?:^|[_-])private(?:$|[_-])|secret|credential|password|token)|\.(?:pem|key|p12|pfx|sqlite|db)$', re.I)
PRIVATE_BLOCK = re.compile(rb'-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----|-----BEGIN PGP PRIVATE KEY BLOCK-----')
SECRET_ASSIGNMENT = re.compile(rb'\b(?:password|secret|api[_-]?key|access[_-]?token|refresh[_-]?token)\s*[:=]\s*\S+', re.I)
SENSITIVE_KEYS = frozenset({'private_key','private_key_pem','private_credentials','password','secret','secret_key','client_secret','api_key','access_token','refresh_token','bearer_token','token','credential','credentials','auth_token','signing_key','key_material'})
SENSITIVE_KEY_TOKENS = frozenset(re.sub(r'[^a-z0-9]', '', key.lower()) for key in SENSITIVE_KEYS)
PRIVATE_LOCATOR = re.compile(rb'/(?:tmp|run|home)/cal-[A-Za-z0-9_./-]+', re.I)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

def pinned(path):
    require(path.is_file() and not path.is_symlink(), 'selected evidence unavailable')
    raw = path.read_bytes()
    require(sha(raw) == PINS[path], 'selected evidence changed')
    return raw

def no_duplicates(items):
    value = {}
    for key, item in items:
        require(key not in value, 'duplicate JSON key')
        value[key] = item
    return value

def strict_json(raw):
    return json.loads(raw, object_pairs_hook=no_duplicates,
                      parse_constant=lambda _: require(False, 'nonfinite JSON'))

def scan_json(value):
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = re.sub(r'[^a-z0-9]', '', str(key).lower())
            empty = (item is None or item is False or
                     (type(item) is str and item == '') or
                     (type(item) is list and not item) or
                     (type(item) is dict and not item))
            require(normalized not in SENSITIVE_KEY_TOKENS or empty,
                    'sensitive credential field populated')
            scan_json(item)
    elif isinstance(value, list):
        for item in value:
            scan_json(item)

def scan_member(name, raw, *, json_body=False):
    require(not any(PRIVATE_SEGMENT.search(part) for part in name.split('/')),
            'private-state package path selected')
    require(not PRIVATE_BLOCK.search(raw), 'private key block in public bytes')
    if json_body:
        scan_json(strict_json(raw))

def scan_runtime_log(raw):
    require(not PRIVATE_BLOCK.search(raw), 'private key block in public runtime log')
    require(not SECRET_ASSIGNMENT.search(raw), 'credential assignment in public runtime log')
    require(not PRIVATE_LOCATOR.search(raw), 'private owned locator disclosed in runtime log')
    require(b'fixture key: removed' in raw.lower(), 'fixture key cleanup marker absent')

def inspect_boundary(raw):
    record = strict_json(raw)
    scan_json(record)
    require(set(record) == {'cap_drop','container_id','image','image_id','memory_bytes','mounts',
                            'name','nano_cpus','network_mode','pids_limit','readonly_rootfs',
                            'security_opt','user'}, 'unexpected container inspection field')
    require(record['mounts'] == [] and record['network_mode'] == 'none'
            and record['readonly_rootfs'] is True and record['user'] == '20001:20001'
            and record['cap_drop'] == ['ALL'] and record['security_opt'] == ['no-new-privileges:true'],
            'actual container privacy boundary differs')
    return record['image_id']

def run():
    sys.path.insert(0, str(T07))
    import package_runtime as package
    import verify_package as verifier
    manifest_raw = pinned(T07 / 'source-manifest.json')
    pinned(T07 / 'package-release.json')
    manifest = package.load_manifest(T07 / 'source-manifest.json')
    package.verify_release_pin(manifest)
    require(manifest_raw == package.canonical(manifest), 'manifest canonical bytes differ')
    require((len(manifest['materials']), len(manifest['runtime_code']), len(manifest['build_inputs']), len(manifest['namespace_only'])) == (698, 3, 4, 78),
            'selected T07 package membership differs')
    release = strict_json(pinned(EVIDENCE / 'RELEASE-v3.json'))
    scan_json(release)
    log = pinned(EVIDENCE / 'RUN-v3.log')
    chain = pinned(EVIDENCE / 'INSPECT-v3-chain.json')
    work = pinned(EVIDENCE / 'INSPECT-v3-work.json')
    require(release['source_manifest_sha256'] == PINS[T07 / 'source-manifest.json']
            and release['package_release_sha256'] == PINS[T07 / 'package-release.json']
            and release['run_log_sha256'] == sha(log)
            and release['chain_inspect_sha256'] == sha(chain)
            and release['work_inspect_sha256'] == sha(work)
            and release['both_journeys_passed'] is True
            and release['cleanup'] == {'exact_image_tag_remaining': False,
                                       'project_containers_remaining': 0,
                                       'temporary_build_context_remaining': False},
            'selected T07 runtime receipt differs')
    scan_runtime_log(log)
    chain_id = inspect_boundary(chain)
    work_id = inspect_boundary(work)
    require(chain_id == work_id == release['image_id'], 'contained image identity differs')
    counts = {'material_bytes_scanned': 0, 'runtime_code_bytes_scanned': 0,
              'build_input_bytes_scanned': 0, 'namespace_placeholder_count': 0}
    with tempfile.TemporaryDirectory(prefix='cal-T20-public-scan-') as name:
        context = Path(name)
        require(stat.S_IMODE(context.stat().st_mode) == 0o700, 'private scanner scratch required')
        package.stage(ROOT, context, manifest)
        verifier.verify(context / 'workspace', context / 'package-manifest.json', context)
        for kind in ('materials', 'runtime_code'):
            for path, expected in manifest[kind].items():
                raw = (context / 'workspace' / package.safe_relative(path)).read_bytes()
                require(sha(raw) == expected, 'staged selected byte differs')
                scan_member(path, raw, json_body=path.endswith('.json'))
                counts['material_bytes_scanned' if kind == 'materials' else 'runtime_code_bytes_scanned'] += len(raw)
        registry = 'authority/definitions/registry.json'
        public = package.PUBLIC_REGISTRY
        require((context / 'workspace' / registry).read_bytes() ==
                (context / 'workspace' / public).read_bytes(),
                'owner-only registry was not replaced by exact public postimage')
        for path in manifest['namespace_only']:
            raw = (context / 'workspace' / package.safe_relative(path)).read_bytes()
            require(raw == b'', 'name-only historical path carried data')
            scan_member(path, raw)
            counts['namespace_placeholder_count'] += 1
        for path, expected in manifest['build_inputs'].items():
            raw = (context / path).read_bytes()
            require(sha(raw) == expected, 'staged build input differs')
            scan_member(path, raw)
            counts['build_input_bytes_scanned'] += len(raw)
    result = {'schema_version': 'lab-T20-T07-local-privacy-scan/v1',
              'source_manifest_sha256': PINS[T07 / 'source-manifest.json'],
              'package_release_sha256': PINS[T07 / 'package-release.json'],
              'runtime_release_sha256': PINS[EVIDENCE / 'RELEASE-v3.json'],
              'material_count': 698, 'runtime_code_count': 3,
              'build_input_count': 4, 'name_only_count': 78,
              'counts': counts, 'private_path_count': 0, 'private_key_block_count': 0,
              'populated_credential_field_count': 0, 'runtime_private_locator_count': 0,
              'container_inspections_checked': 2, 'status': 'PASS-LOCAL-TECHNICAL',
              'authority_effect': 'none', 'final_family_privacy_qualified': False,
              'claim_ceiling': 'Exact T07 disposable public package and its pinned local runtime outputs only; no final family, protected Source8, pilot, or T25 closure.'}
    (HERE / 'RESULT.json').write_bytes((json.dumps(result, sort_keys=True, indent=2) + '\n').encode())
    print(json.dumps({'status': result['status'], 'selected_members': 783,
                      'runtime_inspections': 2}, sort_keys=True))
    return result

if __name__ == '__main__':
    run()
