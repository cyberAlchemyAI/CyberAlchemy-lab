"""Rebind one disjoint API33 successor with preclaim Session contract validation."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v33-t35-current-reader-0001'
NEW = BASE / 'api-integration-v33-t35-session-preflight-0002'
OLD_SOURCE_SHA = 'b7fe1be6e05c48856791fe010b0ba007c38424d552b3007c33b59e8729eda827'
OLD_PROFILE_SHA = '1000942922f152ba03561086664eedc1004fb1dc1f292f322182d903723f90f8'
OLD_MEMBERS_SHA = '64931c417e6738d82c1c4cb819bb660237aab038bf6474594d421d8991f6d7d1'
OLD_SERVICE_SHA = '6c6cd97c1735e162758bb9c6d2df745db782ac4b3dd051d95192acfc569f0e60'
NEW_SERVICE_SHA = '2a20953d458aa5da61ac8d2ad76c2ad6445895153ebbc4665082925152133fa1'


def sha(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('missing or linked selected file: ' + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def row(path):
    return {'path': rel(path), 'sha256': sha(path)}


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def verify_service_edit(old_service, new_service):
    old = b"if name=='session.open':session_plan=self.sessions.open_plan(message,call['expected_source_cut'])"
    new = b"""if name=='session.open':
                        session_plan=self.sessions.open_plan(message,call['expected_source_cut'])
                        if source.current_source8_view(self.handlers.view):
                            carrier='cal.artifact-type.typed-relation/v4'
                            contract=self.handlers.view.data['projection']['contracts'].get(carrier)
                            if not (type(contract) is dict and contract.get('semantic_kind')=='typed-relation'
                                    and contract.get('lifecycle_state') in ('admitted-current','local-admitted-current')
                                    and contract.get('schema_selector') is None):
                                raise ApplicationError('unresolved-reference','Current native typed-relation/v4 contract unavailable before claim.')
                            from .native_schema import original_schema
                            original_schema(self.sessions.source,carrier)"""
    if old_service.count(old) != 1 or old_service.replace(old, new) != new_service:
        raise ValueError('preclaim Session contract check is not the sole service change')


def main():
    if (sha(OLD / 'source-manifest.json') != OLD_SOURCE_SHA or
            sha(OLD / 'contract-profile.json') != OLD_PROFILE_SHA or
            sha(OLD / 'integration-members.json') != OLD_MEMBERS_SHA):
        raise ValueError('frozen API33 predecessor changed')
    if (sha(NEW / 'source-manifest.json') != OLD_SOURCE_SHA or
            sha(NEW / 'contract-profile.json') != OLD_PROFILE_SHA or
            sha(NEW / 'integration-members.json') != OLD_MEMBERS_SHA):
        raise ValueError('successor is not an otherwise untouched copy')
    old_prefix = rel(OLD) + '/'
    source = json.loads((OLD / 'source-manifest.json').read_bytes())
    own = {item['path'][len(old_prefix):]: item['sha256'] for item in source['files']
           if item['path'].startswith(old_prefix)}
    actual = {p.relative_to(NEW).as_posix() for p in NEW.rglob('*')
              if p.is_file() and p.name not in ('source-manifest.json', 'rebind-receipt.json')
              and '__pycache__' not in p.parts and 'receipts' not in p.parts and p.suffix != '.pyc'}
    if set(own) != actual or len(own) == 0:
        raise ValueError('copied successor closure differs')
    for filename, digest in own.items():
        if filename != 'contract-profile.json' and filename != 'service.py' and sha(NEW / filename) != digest:
            raise ValueError('unexpected copied file changed: ' + filename)
    old_service = (OLD / 'service.py').read_bytes()
    new_service = (NEW / 'service.py').read_bytes()
    if sha(OLD / 'service.py') != OLD_SERVICE_SHA or sha(NEW / 'service.py') != NEW_SERVICE_SHA:
        raise ValueError('Session service pin changed')
    verify_service_edit(old_service, new_service)
    profile = json.loads((OLD / 'contract-profile.json').read_bytes())
    profile['files'] = [row(NEW / item['path'][len(old_prefix):])
                        if item['path'].startswith(old_prefix) else item for item in profile['files']]
    profile['integration_members_binding'] = row(NEW / 'integration-members.json')
    profile['claim_ceiling'] = 'T35 current Source8 Session preclaim contract refusal successor; positive Session and complete T35 unqualified.'
    write(NEW / 'contract-profile.json', profile)
    source['files'] = sorted((row(NEW / item['path'][len(old_prefix):])
                              if item['path'].startswith(old_prefix) else item for item in source['files']),
                             key=lambda item: item['path'])
    source['profile_binding'] = row(NEW / 'contract-profile.json')
    source['predecessor_source_manifest_binding'] = {'path': rel(OLD / 'source-manifest.json'), 'sha256': OLD_SOURCE_SHA}
    source['claim_ceiling'] = profile['claim_ceiling']
    write(NEW / 'source-manifest.json', source)
    write(NEW / 'rebind-receipt.json', {
        'schema_version': 'lab-T35-api33-session-preclaim-rebind/v1-candidate',
        'successor_package': rel(NEW),
        'successor_manifest_sha256': sha(NEW / 'source-manifest.json'),
        'predecessor_source_manifest_binding': source['predecessor_source_manifest_binding'],
        'successor_source_manifest_binding': row(NEW / 'source-manifest.json'),
        'successor_profile_binding': source['profile_binding'],
        'service_binding': row(NEW / 'service.py'),
        'authority_effect': 'none',
        'claim_ceiling': source['claim_ceiling'], 'current_session_preclaim_tested': False})
    print(json.dumps({'source_manifest_sha256': sha(NEW / 'source-manifest.json'),
                      'profile_sha256': sha(NEW / 'contract-profile.json'),
                      'service_sha256': sha(NEW / 'service.py'),
                      'source_files': len(source['files']), 'profile_files': len(profile['files'])}, sort_keys=True))


if __name__ == '__main__':
    main()
