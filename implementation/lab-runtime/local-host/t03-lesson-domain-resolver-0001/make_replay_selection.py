"""Pin one fresh installed T03 replay selection before any native phase."""
import argparse
import hashlib
import json
import os
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--installation-repository', required=True)
    parser.add_argument('--api-dir', required=True, help='installed API76 path relative to repository')
    parser.add_argument('--evidence-root', required=True)
    parser.add_argument('--selection-output', required=True)
    args = parser.parse_args()
    repo = Path(args.installation_repository).resolve()
    api = Path(args.api_dir)
    base = Path(args.evidence_root)
    out = Path(args.selection_output)
    if (not repo.is_dir() or not base.is_absolute() or base.exists()
            or not out.is_absolute() or out.exists() or not out.parent.is_dir()
            or api.is_absolute() or '..' in api.parts or not api.name.startswith('api-integration-v76-')
            or 'final-local-product-20261026-0003' in str(repo)):
        raise ValueError('fresh installed API76, absent evidence root and new selection output required')
    caller = repo / 'implementation/lab-runtime/local-host/t03-installed-learning-caller-0005'
    emitter = repo / 'implementation/lab-runtime/local-host/t31-native-first-emitter-0002/native_first_emitter.py'
    if not caller.is_dir() or not emitter.is_file() or emitter.is_symlink():
        raise ValueError('installed caller and native first-emitter source required')
    files = {p.name: sha(p) for p in sorted(caller.glob('*.py'))}
    if not files or any(p.is_symlink() for p in caller.glob('*.py')):
        raise ValueError('current T03 caller files unavailable')
    source_ref = str(api / 'source-manifest.json')
    profile_ref = str(api / 'contract-profile.json')
    package_path = repo / '.cal-package-manifest.json'
    package = json.loads(package_path.read_bytes())
    if (package['entrypoint']['api_directory'] != str(api)
            or package['binding_paths']['api.source'] != source_ref
            or package['binding_paths']['api.profile'] != profile_ref
            or source_ref not in package['generated_metadata_paths']
            or profile_ref not in package['generated_metadata_paths']):
        raise ValueError('installed package does not select exact API76 source/profile')
    members = {row['path']: row['sha256'] for row in package['members']}
    for path in [emitter, *sorted(caller.glob('*.py'))]:
        rel = str(path.relative_to(repo))
        if path.is_symlink() or members.get(rel) != sha(path):
            raise ValueError('installed first-emitter/caller bytes outside package selection')
    value = {'schema_version': 'lab-t03-fresh-installed-replay-selection/v1',
             'installation_repository': str(repo), 'evidence_root': str(base),
             'api_source_ref': source_ref,
             'api_source_sha256': sha(repo / source_ref),
             'profile_ref': profile_ref,
             'profile_sha256': sha(repo / profile_ref),
             'package_manifest_sha256': sha(package_path),
             'first_emitter_code': str(emitter),
             'first_emitter_sha256': sha(emitter),
             'caller_dir': str(caller), 'caller_bindings': files}
    fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write((json.dumps(value, sort_keys=True, indent=2) + '\n').encode())
        stream.flush(); os.fsync(stream.fileno())
    print(json.dumps({'selection': str(out), 'selection_sha256': sha(out),
                      'source_sha256': value['api_source_sha256'],
                      'profile_sha256': value['profile_sha256']}, sort_keys=True))


if __name__ == '__main__':
    main()
