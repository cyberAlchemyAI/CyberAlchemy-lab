"""Explicit exact selection of independently versioned, read-only source profiles."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from jsonschema import Draft202012Validator

from .common import RuntimeFault, byte_digest, load, loads, require, under

PACKAGE = Path(__file__).resolve().parents[1]
PROFILE_SCHEMA = PACKAGE / 'schemas/source-profile.schema.json'


def closed(value, required):
    require(isinstance(value, dict) and set(value) == set(required), 'closed envelope fields differ: ' + ','.join(required))


def checked_read(repo, ref):
    require(isinstance(ref, dict) and {'path', 'sha256'} <= set(ref), 'invalid exact file binding')
    require(not any(part in ['.local', '.env'] or part.startswith('.env.') for part in Path(ref['path']).parts)
            and not ref['path'].endswith(('.pem', '.key')), 'private control/source material forbidden')
    path = under(repo, ref['path'])
    require(path.is_file(), 'missing selected material: ' + ref['path'])
    raw = path.read_bytes()
    require(byte_digest(raw) == ref['sha256'], 'selected material digest mismatch: ' + ref['path'])
    if 'size_bytes' in ref:
        require(type(ref['size_bytes']) is int and len(raw) == ref['size_bytes'], 'material length mismatch')
    return raw


@dataclass(frozen=True)
class Selection:
    repo: Path
    profile: dict
    policy: dict
    content_manifest: dict
    executable_manifest: dict
    controls: dict
    selection_ref: str
    selection_sha256: str

    @property
    def profile_sha256(self):
        return self.controls['profile']['sha256']


def select(repo, *, profile_path, profile_sha256, policy_path, executable_manifest_path,
           review_path, review_sha256):
    """Pins are independent inputs from the bounded caller, never accepted from body claims.

    Selection reviews prove candidate read selection only. No method here grants
    repository admission, local action authority, operator identity or release.
    """
    repo = Path(repo).resolve()
    profile_ref = {'path': profile_path, 'sha256': profile_sha256}
    profile_raw = checked_read(repo, profile_ref)
    profile = loads(profile_raw)
    require(profile.get('protocol_version') == 1, 'unsupported source profile protocol')
    try:
        Draft202012Validator(load(PROFILE_SCHEMA)).validate(profile)
    except Exception as exc:
        raise RuntimeFault('invalid source profile: ' + str(exc)) from exc
    policy_ref = {'path': policy_path, 'sha256': profile['policy_core_sha256']}
    policy = loads(checked_read(repo, policy_ref))
    closed(policy, ['schema_version', 'authority_effect', 'policy_id', 'allowed_source_roots', 'max_files',
                    'max_source_bytes', 'capture_provider', 'capture_config', 'code_roots', 'compatibility_binding'])
    require(policy['schema_version'] == 'lab-source-capture-policy/v1-candidate' and policy['authority_effect'] == 'none', 'unsupported capture policy')
    require(policy['capture_provider'] in ['frozen-lab-v1', 'frozen-lab-v2', 'native-byte-manifest'], 'unsupported capture provider')
    require(type(policy['max_files']) is int and 0 < policy['max_files'] <= 100000, 'invalid file budget')
    require(type(policy['max_source_bytes']) is int and 0 < policy['max_source_bytes'] <= 1024**3, 'invalid byte budget')
    for name in policy['allowed_source_roots'] + policy['code_roots']:
        under(repo, name)
    executable_ref = {'path': executable_manifest_path, 'sha256': profile['executable_manifest_sha256']}
    executable = loads(checked_read(repo, executable_ref))
    closed(executable, ['schema_version', 'authority_effect', 'files'])
    require(executable['schema_version'] == 'lab-executable-manifest/v1-candidate' and executable['authority_effect'] == 'none', 'invalid executable manifest')
    expected_code = set()
    for ref in executable['files']:
        checked_read(repo, ref)
        require(ref['path'] not in expected_code, 'duplicate executable path')
        expected_code.add(ref['path'])
    actual_code = set()
    for name in policy['code_roots']:
        path = under(repo, name)
        require(path.exists(), 'missing code root')
        files = path.rglob('*.py') if path.is_dir() else [path]
        for file in files:
            require(not file.is_symlink(), 'code symlink forbidden')
            if '__pycache__' not in file.parts:
                actual_code.add(file.relative_to(repo).as_posix())
    require(expected_code == actual_code, 'executable closure differs from declared code roots')
    # Verify the executable actually running, not just arbitrary files named by a policy.
    prefix = PACKAGE.relative_to(PACKAGE.parents[3]).as_posix()
    running = [p for p in (PACKAGE / 'lab_runtime').rglob('*.py') if '__pycache__' not in p.parts] + [PACKAGE / 'lab.py']
    expected_refs = {r['path']: r for r in executable['files']}
    for path in running:
        name = prefix + '/' + path.relative_to(PACKAGE).as_posix()
        require(name in expected_refs and expected_refs[name]['sha256'] == byte_digest(path.read_bytes()), 'selection does not bind the running executable')
    manifest_ref = profile['content_manifest']
    manifest = loads(checked_read(repo, manifest_ref))
    closed(manifest, ['schema_version', 'authority_effect', 'source_cut', 'materials'])
    require(manifest['schema_version'] == 'lab-source-content-manifest/v1-candidate' and manifest['authority_effect'] == 'none', 'unsupported content manifest')
    require(manifest['source_cut'] == profile['expected_cut'], 'manifest cut differs from profile')
    require(0 < len(manifest['materials']) <= policy['max_files'], 'capture file budget exceeded')
    total = 0
    seen = set()
    for ref in manifest['materials']:
        closed(ref, ['path', 'sha256', 'size_bytes'])
        name = ref['path']
        under(repo, name)
        require(name not in seen, 'duplicate capture path')
        seen.add(name)
        require(any(name == root.rstrip('/') or name.startswith(root.rstrip('/') + '/') for root in policy['allowed_source_roots']), 'source outside selected roots')
        require(not any(part in ['.local', '.env', 'node_modules'] or part.startswith('.env.') for part in Path(name).parts), 'private source forbidden')
        require(not name.endswith(('.pem', '.key')), 'private key source forbidden')
        require(type(ref['size_bytes']) is int and ref['size_bytes'] >= 0, 'invalid source length')
        total += ref['size_bytes']
    require(total <= policy['max_source_bytes'], 'capture byte budget exceeded')
    review_ref = {'path': review_path, 'sha256': review_sha256}
    review = loads(checked_read(repo, review_ref))
    closed(review, ['schema_version', 'authority_effect', 'purpose', 'profile_sha256', 'policy_sha256',
                    'executable_manifest_sha256', 'content_manifest_sha256', 'expected_cut', 'domain_posture', 'scope_ref', 'provenance_ref'])
    require(review['schema_version'] == 'lab-profile-selection-review/v1-candidate' and review['authority_effect'] == 'none'
            and review['purpose'] == 'candidate-read-selection-only', 'selection review cannot grant operational authority')
    for key, expected in [('profile_sha256', profile_sha256), ('policy_sha256', policy_ref['sha256']),
                          ('executable_manifest_sha256', executable_ref['sha256']), ('content_manifest_sha256', manifest_ref['sha256']),
                          ('expected_cut', profile['expected_cut']), ('domain_posture', profile['domain_posture'])]:
        require(review[key] == expected, 'selection review mismatch: ' + key)
    require(bool(review['scope_ref']) and bool(review['provenance_ref']), 'selection scope/provenance missing')
    controls = {'profile': profile_ref, 'policy': policy_ref, 'executable_manifest': executable_ref,
                'content_manifest': manifest_ref, 'selection_review': review_ref,
                'compatibility_binding': policy['compatibility_binding']}
    checked_read(repo, policy['compatibility_binding'])
    for ref in profile['authority_basis'] + profile['registries'] + profile['transition_basis']['basis_refs']:
        checked_read(repo, ref)
        require(ref['path'] in seen, 'authority/registry/transition evidence outside captured closure')
    return Selection(repo, profile, policy, manifest, executable, controls, review_path, review_sha256)
