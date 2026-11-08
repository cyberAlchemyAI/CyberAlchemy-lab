"""Build a disjoint API candidate over the signed Agent-contest Source family.

This recuts the already selected API42 code. It changes only family-specific
source pins; challenge authority and handler behavior remain unchanged and
must be exercised separately before this candidate can be selected.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v42-r03-0005-current-0001'
NEW = BASE / 'api-integration-v55-t22-agent-contest-persistent-0001'
OLD_SOURCE = '41aab1ef39fd93c33e2313a19466f4755a8ea14389c1d6abcfdb4ce461be3f50'
OLD_PROFILE = '043138382a4f3bc94e7c5ad00c957e6b1f91d0dd80cbb335941ade05ef942e4d'
OLD_ID = 'legacy-local-710362c855a8a11c'
NEW_ID = 'legacy-local-d3537e8c3cb77a71'
FAMILY = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances' / NEW_ID
CHAIN = ROOT / 'implementation/lab-runtime/local-host/t22-native-agent-contest-0001/CHAIN-0001.json'
CHAIN_SHA = '9463f2cc57a3a7f0ec644e25ce434ba6493dc7e14f431fa53b7b6e71b9eff5cb'
OLD_FAMILY = f'implementation/lab-runtime/local-host/source8-current-fixture/instances/{OLD_ID}/'
NEW_FAMILY = f'implementation/lab-runtime/local-host/source8-current-fixture/instances/{NEW_ID}/'
OLD_SELECTION = f'implementation/lab-runtime/local-host/source8-current-fixture/selections/{OLD_ID}.json'
NEW_SELECTION = f'implementation/lab-runtime/local-host/source8-current-fixture/selections/{NEW_ID}.json'
FAMILY_FILES = {
    'family_source_manifest_binding': 'source/source-manifest.json',
    'family_source_package_binding': 'source/packages/0001/manifest.json',
    'family_reader_manifest_binding': 'reader/source-manifest.json',
    'family_mapped_package_binding': 'mapped/packages/0001/manifest.json',
    'family_mapping_binding': 'mapped/packages/0001/mapping.json',
    'family_context_manifest_binding': 'context/source-manifest.json',
    'family_context_package_binding': 'context/packages/0001/manifest.json',
}
PIN_REPLACEMENTS = {
    '614b14c45370e0d8b500a2dd7c9d57a38394ca404c09414ad3ad80f10db55839':
        '821daa0cea96b240aa3d1b735fdefbc69ccff2d67206aa8f26b52cbb55fe312f',
    '43a4bdbd63485f976d2ffe79026a85711e5e05989d0c38ba6110590410a9c6b3':
        '57ef57d26e3f1ce56d84ed129b00f34485fb859a168008d6940375112762c2e6',
    '2a5179b97aacf9e6e87d2ee6c41d1692a5f9806511203d53c0d7db96e3598539':
        'ef4803d75eedf7f9289642833b2e852daa034754df66c9a967da7b7a0aad97ec',
    '9acba0286ce20363422a60825357ffc1735f8dd975271d57a7020018374d5edc':
        '89059dcbd7b55c972a3f02248c538f1dee4a957a7dd9335003b4495944c9b70a',
}
OLD_PERIOD = '2026-10-23T04:52:49.044239+00:00'
OLD_EXPIRY = '2026-10-24T04:52:49.044239+00:00'
NEW_PERIOD = '2026-10-23T17:54:44.262511+00:00'
NEW_EXPIRY = '2026-10-24T17:54:44.262511+00:00'
CLAIM = ('T22 signed Agent-contest family API candidate. Source rebind only; '
         'live Agent Session, native challenge submit/response/resolve, outcome, '
         'owner Decision and authority effect remain unproved.')


def sha(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f'missing or linked selected file: {path}')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def binding(path: Path) -> dict:
    return {'path': rel(path), 'sha256': sha(path)}


def save(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def preflight() -> None:
    if sha(OLD / 'source-manifest.json') != OLD_SOURCE or sha(OLD / 'contract-profile.json') != OLD_PROFILE:
        raise ValueError('selected API42 predecessor changed')
    if sha(CHAIN) != CHAIN_SHA:
        raise ValueError('selected signed Agent-contest chain changed')
    chain = json.loads(CHAIN.read_bytes())
    if (chain['family'] != rel(FAMILY) or chain['cold_replays'] != 2
            or chain['original_byte_parity'] is not True or chain['authority_effect'] != 'none'
            or chain['challenge_submitted'] is not False or chain['challenge_resolved'] is not False):
        raise ValueError('signed Agent-contest family is not the selected construction')
    for suffix in FAMILY_FILES.values():
        sha(FAMILY / suffix)
    period = json.loads((FAMILY / 'source/packages/0001/period.json').read_bytes())
    if period['not_before'] != NEW_PERIOD or period['expires_at'] != NEW_EXPIRY:
        raise ValueError('selected signed Agent-contest period differs')
    mapping = json.loads((FAMILY / 'mapped/packages/0001/mapping.json').read_bytes())
    if (mapping['source_cut']['store_ref'] != 'completion-legacy-local-d3537e8c3cb77a71'
            or mapping['source_closure']['accounted_subjects'] != 607
            or len(mapping['projection_dispositions']) != 607):
        raise ValueError('selected Agent-contest source cut or mapping differs')
    old = json.loads((OLD / 'source-manifest.json').read_bytes())
    prefix = rel(OLD) + '/'
    own = {row['path'][len(prefix):] for row in old['files'] if row['path'].startswith(prefix)}
    actual = {p.relative_to(OLD).as_posix() for p in OLD.rglob('*') if p.is_file()
              and p.name not in ('source-manifest.json', 'rebind-receipt.json')
              and '__pycache__' not in p.parts and 'receipts' not in p.parts and p.suffix != '.pyc'}
    if len(own) != 201 or len(old['files']) != 207 or own != actual:
        raise ValueError('selected API42 local inventory differs')


def main() -> None:
    preflight()
    if NEW.exists():
        raise ValueError('disjoint API54 candidate already exists')
    old_manifest = json.loads((OLD / 'source-manifest.json').read_bytes())
    old_profile = json.loads((OLD / 'contract-profile.json').read_bytes())
    old_prefix = rel(OLD) + '/'
    stage = NEW.with_name(NEW.name + '.stage')
    if stage.exists():
        raise ValueError('API54 build stage already exists')
    stage.mkdir(mode=0o700)
    try:
        for row in old_manifest['files']:
            if not row['path'].startswith(old_prefix):
                continue
            leaf = row['path'][len(old_prefix):]
            source = OLD / leaf
            if sha(source) != row['sha256']:
                raise ValueError(f'API42 source row changed: {leaf}')
            target = stage / leaf
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target, follow_symlinks=False)
            if OLD_ID in target.read_text(errors='ignore') or any(pin in target.read_text(errors='ignore') for pin in PIN_REPLACEMENTS):
                raw = target.read_text()
                raw = raw.replace(OLD_ID, NEW_ID)
                for old_pin, new_pin in PIN_REPLACEMENTS.items():
                    raw = raw.replace(old_pin, new_pin)
                if leaf == 'legacy_fixture_selection.py':
                    raw = raw.replace(OLD_PERIOD, NEW_PERIOD).replace(OLD_EXPIRY, NEW_EXPIRY)
                if leaf == 'native_dispositions.py':
                    raw = raw.replace('len(rows) == 604', 'len(rows) == 607')
                    raw = raw.replace("len({row['version_ref'] for row in rows}) == 604", "len({row['version_ref'] for row in rows}) == 607")
                    raw = raw.replace("data['source_closure']['accounted_subjects'] == 604", "data['source_closure']['accounted_subjects'] == 607")
                if leaf == 'source_bridge.py':
                    raw = raw.replace('_cal_api42_current_legacy_local_20261023_0001', '_cal_api55_current_legacy_local_20261023_0001')
                    raw = raw.replace('_cal_api42_current_source8_local_20261023_0001', '_cal_api55_current_source8_local_20261023_0001')
                target.write_text(raw)
        def new_row(row):
            path = row['path']
            if path.startswith(old_prefix):
                leaf = path[len(old_prefix):]
                return {'path': rel(NEW / leaf), 'sha256': sha(stage / leaf)}
            if path.startswith(OLD_FAMILY):
                return binding(ROOT / (NEW_FAMILY + path[len(OLD_FAMILY):]))
            if path == OLD_SELECTION:
                return binding(ROOT / NEW_SELECTION)
            return row
        old_profile['files'] = sorted((new_row(row) for row in old_profile['files']), key=lambda r: r['path'])
        old_profile['integration_members_binding'] = {'path': rel(NEW / 'integration-members.json'),
                                                      'sha256': sha(stage / 'integration-members.json')}
        old_profile['claim_ceiling'] = CLAIM
        if len({row['path'] for row in old_profile['files']}) != len(old_profile['files']):
            raise ValueError('API54 profile path collision')
        save(stage / 'contract-profile.json', old_profile)
        old_manifest['files'] = sorted((new_row(row) for row in old_manifest['files']), key=lambda r: r['path'])
        old_manifest['profile_binding'] = {'path': rel(NEW / 'contract-profile.json'),
                                           'sha256': sha(stage / 'contract-profile.json')}
        for row in old_manifest['files']:
            if row['path'] == old_manifest['profile_binding']['path']:
                row['sha256'] = old_manifest['profile_binding']['sha256']
        for key, suffix in FAMILY_FILES.items():
            old_manifest[key] = binding(FAMILY / suffix)
        old_manifest['predecessor_source_manifest_binding'] = binding(OLD / 'source-manifest.json')
        old_manifest['claim_ceiling'] = CLAIM
        save(stage / 'source-manifest.json', old_manifest)
        receipt = {'schema_version': 'lab-T22-Agent-contest-API55-source-rebind/v1-candidate',
                   'successor_package': rel(NEW),
                   'successor_manifest_sha256': sha(stage / 'source-manifest.json'),
                   'predecessor_source_manifest_binding': binding(OLD / 'source-manifest.json'),
                   'successor_source_manifest_binding': {'path': rel(NEW / 'source-manifest.json'),
                                                         'sha256': sha(stage / 'source-manifest.json')},
                   'successor_profile_binding': {'path': rel(NEW / 'contract-profile.json'),
                                                 'sha256': sha(stage / 'contract-profile.json')},
                   'signed_family_chain_binding': binding(CHAIN), 'source_files': len(old_manifest['files']),
                   'profile_files': len(old_profile['files']), 'authority_effect': 'none',
                   'challenge_submitted': False, 'challenge_resolved': False, 'claim_ceiling': CLAIM}
        save(stage / 'rebind-receipt.json', receipt)
        stage.rename(NEW)
    except BaseException:
        shutil.rmtree(stage)
        raise
    print(json.dumps({'source_sha256': sha(NEW / 'source-manifest.json'),
                      'profile_sha256': sha(NEW / 'contract-profile.json'),
                      'source_files': len(old_manifest['files']), 'profile_files': len(old_profile['files'])}, sort_keys=True))


if __name__ == '__main__':
    main()
