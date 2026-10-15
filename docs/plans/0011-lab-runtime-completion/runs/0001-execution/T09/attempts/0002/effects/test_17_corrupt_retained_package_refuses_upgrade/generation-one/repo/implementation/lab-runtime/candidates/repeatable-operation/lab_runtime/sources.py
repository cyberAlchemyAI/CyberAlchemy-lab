"""Independent source captures with exact original bytes and second-read rejection."""
from __future__ import annotations

import base64
import copy
from pathlib import Path

from .common import byte_digest, digest, loads, require, under
from .profiles import Selection, checked_read
from ._legacy import v1_sources, v2_sources


def capture(selection: Selection, *, after_read=None):
    repo, profile, policy = selection.repo, selection.profile, selection.policy
    materials, contents, documents = {}, {}, {}
    total = 0
    for index, ref in enumerate(selection.content_manifest['materials']):
        raw = checked_read(repo, ref)
        total += len(raw)
        require(total <= policy['max_source_bytes'], 'actual capture byte budget exceeded')
        name = ref['path']
        materials[name] = byte_digest(raw)
        contents[name] = base64.b64encode(raw).decode('ascii')
        if name.endswith('.json'):
            documents[name] = loads(raw)
        if after_read:
            after_read(index, name)
    config = policy['capture_config']
    require(config['path'] in materials and config['sha256'] == materials[config['path']], 'capture configuration outside exact closure')
    legacy_profile = documents.get(config['path'])
    require(isinstance(legacy_profile, dict), 'capture config must be JSON')
    provider = policy['capture_provider']
    if provider == 'native-byte-manifest':
        require(profile['domain_posture'] == 'isolated-candidate', 'native bindings cannot claim admitted source authority')
        closed = set(legacy_profile) == {'schema_version', 'authority_effect', 'subject_bindings'}
        require(closed and legacy_profile['schema_version'] == 'lab-native-source-bindings/v1-candidate'
                and legacy_profile['authority_effect'] == 'none', 'invalid native source bindings')
        subjects = {}
        for b in legacy_profile['subject_bindings']:
            require(set(b) == {'version_ref', 'identity_ref', 'identity_selector', 'path', 'sha256', 'semantic_kind', 'carrier_ref'}, 'unclosed native subject binding')
            require(b['path'] in documents and materials[b['path']] == b['sha256'], 'native subject outside exact closure')
            from .common import pointer
            require(pointer(documents[b['path']], b['identity_selector']) == b['identity_ref'], 'native identity mismatch')
            require(b['version_ref'] not in subjects, 'duplicate native version')
            subjects[b['version_ref']] = {'identity': b['identity_ref'], 'version_ref': b['version_ref'],
                'kind': b['semantic_kind'], 'category': 'artifact-instance', 'carrier_ref': b['carrier_ref'],
                'effective_state': 'candidate-unadmitted', 'record': documents[b['path']],
                'source': {'path': b['path'], 'sha256': b['sha256']}, 'decision_ref': None}
        semantic = {'subjects': subjects, 'contracts': {}, 'relation_contracts': {}, 'state': None, 'histories': {},
                    'profile': legacy_profile, 'admission_as_of': None}
    else:
        adapter = v1_sources if provider == 'frozen-lab-v1' else v2_sources
        semantic = adapter.capture(repo, legacy_profile)
        require(semantic['admission_as_of'] == profile['expected_cut'], 'semantic provider selected a different cut')
        require(semantic['materials'] == materials, 'semantic capture and original-byte manifest disagree')
        require(semantic['documents'] == documents, 'semantic capture and original-byte JSON disagree')
    result = copy.deepcopy({k: semantic[k] for k in ['subjects', 'contracts', 'relation_contracts', 'state', 'histories', 'profile', 'admission_as_of']})
    result.update(schema_version='lab-independent-source-snapshot/v1-candidate', authority_effect='none',
        source_profile=profile, source_profile_sha256=selection.profile_sha256,
        materials=materials, documents=documents, byte_contents=contents,
        controls=selection.controls, executable_materials=selection.executable_manifest['files'],
        control_bytes={name: base64.b64encode(checked_read(repo, ref)).decode('ascii') for name, ref in selection.controls.items()},
        executable_byte_contents={ref['path']: base64.b64encode(checked_read(repo, ref)).decode('ascii') for ref in selection.executable_manifest['files']},
        expected_cut=profile['expected_cut'], domain_posture=profile['domain_posture'],
        effective_state_scope='selected profile cut; not proof of latest repository authority',
        selection_scope='candidate-read-selection-only', repository_runtime_activation='not-observed',
        epoch_inventory=v2_sources.epoch_inventory(repo))
    result['snapshot_digest'] = digest(result)
    require(freshness(repo, result)['status'] == 'current', 'source drift during capture')
    return result


def verify_snapshot(snapshot, *, expected_profile_sha256=None):
    require(snapshot['snapshot_digest'] == digest({k: v for k, v in snapshot.items() if k != 'snapshot_digest'}), 'capture envelope digest mismatch')
    require(set(snapshot['materials']) == set(snapshot['byte_contents']), 'capture byte closure mismatch')
    require(set(snapshot['documents']) <= set(snapshot['materials']), 'parsed body outside capture closure')
    controls = {}
    require(set(snapshot['control_bytes']) == set(snapshot['controls']), 'control byte closure mismatch')
    for name, ref in snapshot['controls'].items():
        raw = base64.b64decode(snapshot['control_bytes'][name], validate=True)
        require(byte_digest(raw) == ref['sha256'], 'control bytes changed: ' + name)
        controls[name] = loads(raw)
    require(controls['profile'] == snapshot['source_profile']
            and byte_digest(base64.b64decode(snapshot['control_bytes']['profile'])) == snapshot['source_profile_sha256'], 'source profile differs from exact reviewed bytes')
    profile = controls['profile']
    if expected_profile_sha256 is not None:
        require(snapshot['source_profile_sha256'] == expected_profile_sha256, 'wrong independently selected profile')
    require(profile['content_manifest']['sha256'] == snapshot['controls']['content_manifest']['sha256']
            and profile['policy_core_sha256'] == snapshot['controls']['policy']['sha256']
            and profile['executable_manifest_sha256'] == snapshot['controls']['executable_manifest']['sha256'], 'profile/control reference mismatch')
    expected_materials = {ref['path']: ref['sha256'] for ref in controls['content_manifest']['materials']}
    require(expected_materials == snapshot['materials'] and controls['content_manifest']['source_cut'] == snapshot['expected_cut'], 'original materials differ from reviewed manifest')
    require(controls['executable_manifest']['files'] == snapshot['executable_materials'], 'executable manifest mismatch')
    require(set(snapshot['executable_byte_contents']) == {ref['path'] for ref in snapshot['executable_materials']}, 'executable byte closure mismatch')
    for ref in snapshot['executable_materials']:
        raw = base64.b64decode(snapshot['executable_byte_contents'][ref['path']], validate=True)
        require(byte_digest(raw) == ref['sha256'], 'captured executable bytes changed')
    for name, expected in snapshot['materials'].items():
        try:
            raw = base64.b64decode(snapshot['byte_contents'][name], validate=True)
        except (ValueError, TypeError) as exc:
            raise ValueError('invalid captured byte encoding') from exc
        require(byte_digest(raw) == expected, 'captured original bytes changed: ' + name)
        if name in snapshot['documents']:
            require(loads(raw) == snapshot['documents'][name], 'captured parsed body differs from original bytes')
    require(snapshot['selection_scope'] == 'candidate-read-selection-only', 'capture cannot grant effect authority')
    return True


def freshness(repo, snapshot):
    verify_snapshot(snapshot)
    repo = Path(repo).resolve()
    changed = []
    refs = [{'path': path, 'sha256': sha} for path, sha in snapshot['materials'].items()]
    refs += list(snapshot['controls'].values()) + snapshot['executable_materials']
    for ref in refs:
        path = under(repo, ref['path'])
        if not path.is_file() or byte_digest(path.read_bytes()) != ref['sha256']:
            changed.append(ref['path'])
    policy = loads(base64.b64decode(snapshot['control_bytes']['policy'], validate=True))
    actual_code = set()
    for name in policy['code_roots']:
        path = under(repo, name)
        files = path.rglob('*.py') if path.is_dir() else [path]
        for file in files:
            if '__pycache__' not in file.parts:
                if file.is_symlink():
                    changed.append('executable-symlink')
                actual_code.add(file.relative_to(repo).as_posix())
    if actual_code != {ref['path'] for ref in snapshot['executable_materials']}:
        changed.append('executable-closure-changed')
    if v2_sources.epoch_inventory(repo) != snapshot['epoch_inventory']:
        changed.append('repository-admission-epoch-inventory')
    return {'status': 'stale' if changed else 'current', 'changed': sorted(set(changed)),
            'checked_count': len(refs), 'snapshot_digest': snapshot['snapshot_digest']}


def original_bytes(snapshot, path):
    verify_snapshot(snapshot)
    require(path in snapshot['byte_contents'], 'original bytes outside capture')
    return base64.b64decode(snapshot['byte_contents'][path], validate=True)


resolve = v2_sources.resolve
validate_histories = v2_sources.validate_histories
make_record = v2_sources.make_record
validate_schema = v2_sources.validate_schema
