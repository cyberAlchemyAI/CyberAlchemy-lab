#!/usr/bin/env python3
"""Prepare exact read-only candidate selections for real D74/D75 source cuts."""
from __future__ import annotations

import json
from pathlib import Path

from lab_runtime.common import binding, byte_digest, encoded, load
from lab_runtime._legacy import v1_sources, v2_sources

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[3]
OUT = PACKAGE / 'profiles'


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded(value))


def main():
    code_roots = [(PACKAGE / 'lab_runtime').relative_to(REPO).as_posix(),
                  (PACKAGE / 'lab.py').relative_to(REPO).as_posix()]
    files = sorted([p for p in (PACKAGE / 'lab_runtime').rglob('*.py') if '__pycache__' not in p.parts] + [PACKAGE / 'lab.py'])
    executable_path = OUT / 'executable-manifest.json'
    put(executable_path, {'schema_version': 'lab-executable-manifest/v1-candidate', 'authority_effect': 'none',
                          'files': [binding(REPO, p.relative_to(REPO).as_posix()) for p in files]})
    executable_ref = binding(REPO, executable_path.relative_to(REPO).as_posix())
    selections = []
    for name, adapter, version in [('d74', v1_sources, 'v1'), ('d75', v2_sources, 'v2')]:
        legacy_path = f'implementation/lab-runtime/{version}/profile.json'
        legacy_profile = load(REPO / legacy_path)
        semantic = adapter.capture(REPO, legacy_profile)
        refs = [binding(REPO, path) for path in sorted(semantic['materials'])]
        manifest_path = OUT / name / 'content-manifest.json'
        put(manifest_path, {'schema_version': 'lab-source-content-manifest/v1-candidate', 'authority_effect': 'none',
                           'source_cut': semantic['admission_as_of'], 'materials': refs})
        policy_path = OUT / name / 'policy.json'
        put(policy_path, {'schema_version': 'lab-source-capture-policy/v1-candidate', 'authority_effect': 'none',
            'policy_id': 'policy:independent-read-capture:' + name,
            'allowed_source_roots': sorted({path.split('/')[0] for path in semantic['materials']}),
            'max_files': 5000, 'max_source_bytes': 128 * 1024**2,
            'capture_provider': 'frozen-lab-' + version, 'capture_config': binding(REPO, legacy_path),
            'code_roots': code_roots, 'compatibility_binding': binding(REPO, 'docs/proposals/0007-lab-integrated-schema-package/schema-dependencies.json')})
        policy_ref = binding(REPO, policy_path.relative_to(REPO).as_posix())
        registry = 'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json'
        root_bindings = [{'path': b['path'], 'sha256': b['sha256']} for b in legacy_profile['roots']]
        profile = {'schema_version': 'lab-independent-source-profile/v1-candidate', 'authority_effect': 'none',
            'profile_id': 'source-profile:lab-read:' + name, 'protocol_version': 1,
            'executable_manifest_sha256': executable_ref['sha256'], 'policy_core_sha256': policy_ref['sha256'],
            'authority_basis': root_bindings, 'registries': [{'path': registry, 'sha256': binding(REPO, registry)['sha256']}],
            'content_manifest': {k: v for k, v in binding(REPO, manifest_path.relative_to(REPO).as_posix()).items() if k != 'size_bytes'},
            'expected_cut': semantic['admission_as_of'], 'domain_posture': 'admitted-source',
            'transition_basis': {'mode': 'initial', 'basis_refs': root_bindings}}
        profile_path = OUT / name / 'profile.json'
        put(profile_path, profile)
        profile_ref = binding(REPO, profile_path.relative_to(REPO).as_posix())
        review_path = OUT / name / 'selection-review.json'
        put(review_path, {'schema_version': 'lab-profile-selection-review/v1-candidate', 'authority_effect': 'none',
            'purpose': 'candidate-read-selection-only', 'profile_sha256': profile_ref['sha256'],
            'policy_sha256': policy_ref['sha256'], 'executable_manifest_sha256': executable_ref['sha256'],
            'content_manifest_sha256': profile['content_manifest']['sha256'], 'expected_cut': profile['expected_cut'],
            'domain_posture': profile['domain_posture'], 'scope_ref': 'scope:lab-integrated-candidate-development',
            'provenance_ref': 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'})
        selections.append({'name': name, 'profile_path': profile_ref['path'], 'profile_sha256': profile_ref['sha256'],
            'policy_path': policy_ref['path'], 'executable_manifest_path': executable_ref['path'],
            'review_path': review_path.relative_to(REPO).as_posix(), 'review_sha256': byte_digest(review_path.read_bytes()),
            'source_materials': len(refs), 'source_bytes': sum(r['size_bytes'] for r in refs)})
    put(OUT / 'selections.json', {'authority_effect': 'none', 'purpose': 'candidate-read-selection-only', 'selections': selections})
    print(json.dumps({'profiles': [{k: s[k] for k in ['name', 'source_materials', 'source_bytes']} for s in selections],
                      'authority_effect': 'none'}))


if __name__ == '__main__':
    main()
