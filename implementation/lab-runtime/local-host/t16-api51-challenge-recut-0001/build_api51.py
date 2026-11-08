"""No-replace API51: select current signed challenge fixture and scoped policy."""
import hashlib
import json
import os
from pathlib import Path
import stat

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v50-t16-fixtures-current-0001'
NEW = BASE / 'api-integration-v51-t16-challenge-current-0001'
OLD_ADAPTER = ROOT / 'implementation/lab-runtime/local-host/t16-api50-bootstrap-0001/bootstrap.py'
NEW_ADAPTER = ROOT / 'implementation/lab-runtime/local-host/t16-api51-bootstrap-0001/bootstrap.py'
OLD_SOURCE = '4e7f12a88ba818512f23bc86d4d7adf76035fcf1a9041d2fb07575d82d9a6b2a'
OLD_PROFILE = 'ad74732bff0492b5691e17178a746c15d06b4c0ee5903583c94df91963dc5713'
OLD_ADAPTER_SHA = '7bf17df82207d4f390102af40a1e7a83ebe292552febfcfa1763dcc1ca680fc5'
CURRENT_NAME = 'completion-legacy:legacy-local-ce4d53a6479188a5'
CURRENT_STORE = 'completion-legacy-local-ce4d53a6479188a5'
SESSION = 'agent-session:first-governed-agent-episode:2026-10-06@candidate.1'
CLAIM = ('Selected current T31 Source with focused inherited challenge fixture recut; '
         'no full 345-method T16 or final T15 qualification, no owner effect.')


def sha(raw): return hashlib.sha256(raw).hexdigest()


def exact(path):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('absolute closed path required')
    handles = []
    try:
        parent = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        handles.append(parent)
        for part in path.parts[1:-1]:
            parent = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            handles.append(parent)
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
        try:
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode):
                raise ValueError('selected regular input required')
            chunks = []
            while block := os.read(fd, 1024 * 1024):
                chunks.append(block)
            after = os.fstat(fd)
            named = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
            stamp = lambda v: (v.st_dev, v.st_ino, v.st_size, v.st_mtime_ns, v.st_ctime_ns)
            if stamp(before) != stamp(after) or stamp(after) != stamp(named):
                raise ValueError('selected input changed during read')
            return b''.join(chunks)
        finally:
            os.close(fd)
    finally:
        for handle in reversed(handles):
            os.close(handle)


def digest(path): return sha(exact(path))


def row(path):
    return {'path': Path(path).relative_to(ROOT).as_posix(), 'sha256': digest(path)}


def new_file(path, raw):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def save(path, value):
    new_file(path, (json.dumps(value, sort_keys=True, indent=2) + '\n').encode())


def replace_exact(raw, old, new, count):
    if raw.count(old) != count:
        raise ValueError('exact API49 edit anchor differs: ' + old[:80])
    return raw.replace(old, new)


def recut_challenge(raw):
    raw = replace_exact(raw,
        "        cls.manager=P.source.replay_source('custody-participation');cls.view=cls.manager.__enter__()\n"
        "        cls.projection=P.compact(cls.view.data['projection']);cls.witnesses=[]",
        "        if P.source.CURRENT_LEGACY_NAME!='" + CURRENT_NAME + "':\n"
        "            raise ValueError('current challenge family differs')\n"
        "        cls.manager=P.source.replay_source(P.source.CURRENT_LEGACY_NAME);cls.view=cls.manager.__enter__()\n"
        "        try:\n"
        "            if not P.source.current_legacy_view(cls.view) or cls.view.legacy_signed_sources.source_cut['store_ref']!='" + CURRENT_STORE + "':\n"
        "                raise ValueError('exact current challenge signed cut differs')\n"
        "            cls.projection=P.compact(cls.view.data['projection']);cls.witnesses=[]\n"
        "        except BaseException:\n"
        "            cls.manager.__exit__(None,None,None);raise", 1)
    raw = replace_exact(raw,
        "        assert P.compact(cls.view.data['projection'])==cls.projection\n"
        "        cls.manager.__exit__(None,None,None);verify(SOURCE)",
        "        try:\n"
        "            if P.compact(cls.view.data['projection'])!=cls.projection:\n"
        "                raise ValueError('current challenge projection changed')\n"
        "        finally:\n"
        "            cls.manager.__exit__(None,None,None);verify(SOURCE)", 1)
    compile(raw, str(NEW / 'test_challenge_api.py'), 'exec')
    return raw


def recut_controls(raw):
    old = """        with tempfile.TemporaryDirectory(prefix='cal-R03-expired-source-refusal-') as tmp:
            root=Path(tmp);root.chmod(0o700)
            key,path,pin=provision(root,'fresh-participation',principal='principal:R03-fresh-reader')
            old=source.parse((HERE.parent/'session-participation-v2/packages/0001/period.json').read_bytes())
            self.assertGreaterEqual(now(),instant(old['expires_at']))
            with self.assertRaisesRegex(Exception,'retained absolute Assignment interval'):ReaderChannel(path,pin,self.schemas)
        self.assertFalse(root.exists())"""
    new = """        period_path=HERE.parent/'session-participation-v2/packages/0001/period.json'
        period_raw=period_path.read_bytes()
        self.assertEqual(source.sha(period_raw),'2c0a79e0a8f471114822cc8aed489edf514c7064942442d2670dfdccb2c0a082')
        old=source.parse(period_raw);self.assertGreaterEqual(now(),instant(old['expires_at']))
        with tempfile.TemporaryDirectory(prefix='cal-T16-expired-original-') as tmp:
            root=Path(tmp);root.chmod(0o700)
            key,path,pin=provision(root,'fresh-participation',principal='principal:R03-fresh-reader')
            with self.assertRaisesRegex(ValueError,'^selected R02 participation environment differs$'):
                ReaderChannel(path,pin,self.schemas)
            selected=object.__new__(ReaderChannel)
            selected.path,selected.expected_sha,selected.schemas=path,pin,self.schemas
            with self.assertRaisesRegex(ValueError,'^historical fresh source host window exceeds retained absolute Assignment interval$'):
                selected.policy_guard(check_source=False)
            key=None
        self.assertFalse(root.exists())"""
    raw = replace_exact(raw, old, new, 1)
    compile(raw, str(NEW / 'test_current_controls.py'), 'exec')
    return raw


def recut_preparation(raw):
    old = """        subjects=[s for s in self.view.subjects.values() if s['kind']=='agent-session' and s['record'].get('payload',{}).get('session_memory')]
        self.assertTrue(subjects,'independent R02 audit source Session memory input remains explicit')
        c=call(self.channel.context,'artifact.inspect',cut(self.view),artifact=artifact_ref(self.view,subjects[0]),include=['body'])
        r=self.service.call(compact(c));self.assertEqual(r['message']['code'],'unauthorized')
        self.assertNotIn('envelope',r['message'])"""
    new = """        from .test_current_controls import scoped_service
        with scoped_service(self.schemas) as (view,channel,service,_):
            subject=_current_protected_session(view)
            c=call(channel.context,'artifact.inspect',cut(view),artifact=artifact_ref(view,subject),include=['body'])
            r=service.call(compact(c));self.assertEqual(r['message']['code'],'unauthorized',r)
            self.assertNotIn('envelope',r['message'])"""
    raw = replace_exact(raw, old, new, 1)
    old = """        s=next(s for s in self.view.subjects.values() if s['kind']=='agent-session')
        c=call(self.channel.context,'artifact.inspect',cut(self.view),artifact=artifact_ref(self.view,s),include=['contract','lifecycle','gaps'])
        r=self.service.call(compact(c));self.assertEqual(r['kind'],'result');self.assertIsNone(r['message']['envelope'])"""
    new = """        from .test_current_controls import scoped_service
        with scoped_service(self.schemas) as (view,channel,service,_):
            subject=_current_protected_session(view)
            c=call(channel.context,'artifact.inspect',cut(view),artifact=artifact_ref(view,subject),include=['contract','lifecycle','gaps'])
            r=service.call(compact(c));self.assertEqual(r['kind'],'result',r)
            self.assertIsNone(r['message']['envelope'])"""
    raw = replace_exact(raw, old, new, 1)
    helper = """

def _current_protected_session(view):
    from .protocol import source
    if not source.current_legacy_view(view) or view.legacy_signed_sources.source_cut['store_ref']!='""" + CURRENT_STORE + """':
        raise ValueError('current protected Session signed cut differs')
    rows=[s for s in view.subjects.values() if s['kind']=='agent-session'
          and s['version_ref']=='""" + SESSION + """'
          and s['record'].get('payload',{}).get('session_memory')]
    if len(rows)!=1:raise ValueError('exact current protected Session witness unavailable')
    return rows[0]
"""
    raw = replace_exact(raw, "if __name__=='__main__':original.unittest.main(verbosity=2)",
                        helper + "\nif __name__=='__main__':original.unittest.main(verbosity=2)", 1)
    compile(raw, str(NEW / 'test_preparation_corrected.py'), 'exec')
    return raw


def main():
    if digest(OLD / 'source-manifest.json') != OLD_SOURCE or digest(OLD / 'contract-profile.json') != OLD_PROFILE:
        raise ValueError('frozen API49 source/profile differs')
    if digest(OLD_ADAPTER) != OLD_ADAPTER_SHA:
        raise ValueError('frozen API49 assembler differs')
    if NEW.exists() or NEW_ADAPTER.exists():
        raise ValueError('versioned API49 output already exists')
    manifest = json.loads(exact(OLD / 'source-manifest.json'))
    profile = json.loads(exact(OLD / 'contract-profile.json'))
    old_prefix = OLD.relative_to(ROOT).as_posix() + '/'
    new_prefix = NEW.relative_to(ROOT).as_posix() + '/'
    own = [r for r in manifest['files'] if r['path'].startswith(old_prefix)]
    if len(manifest['files']) != 208 or len(own) != 201 or len(profile['files']) != 33425:
        raise ValueError('API49 selected inventory differs')
    physical = {p.relative_to(OLD).as_posix() for p in OLD.rglob('*') if p.is_file()
                and p.name not in ('source-manifest.json', 'rebind-receipt.json')
                and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    selected_names = {r['path'][len(old_prefix):] for r in own}
    unselected_receipts = physical - selected_names
    if selected_names - physical or unselected_receipts:
        raise ValueError('API49 physical/source closure differs')
    for selected in own:
        if digest(OLD / selected['path'][len(old_prefix):]) != selected['sha256']:
            raise ValueError('frozen API49 selected byte differs')

    schema = exact(OLD / 'workflow-output-plan.schema.json').decode()
    old_service = old_prefix + 'service.py'
    new_service = new_prefix + 'service.py'
    schema = replace_exact(schema, old_service, new_service, 2)
    registry = exact(OLD / 'workflow_output_registry.py').decode()
    registry = replace_exact(registry, old_prefix + 'workflow_', new_prefix + 'workflow_', 7)
    bridge = exact(OLD / 'source_bridge.py').decode()
    bridge = replace_exact(bridge, '_cal_api50_t16_legacy_local_20261023_0001',
                           '_cal_api51_t16_legacy_local_20261023_0001', 1)
    bridge = replace_exact(bridge, '_cal_api50_t16_source8_local_20261023_0001',
                           '_cal_api51_t16_source8_local_20261023_0001', 1)
    guard = exact(OLD / 'guard.py').decode()
    guard = replace_exact(guard, OLD_ADAPTER.relative_to(ROOT).as_posix(),
                          NEW_ADAPTER.relative_to(ROOT).as_posix(), 1)
    adapter = exact(OLD_ADAPTER).decode()
    adapter = replace_exact(adapter, OLD.name, NEW.name, 1)
    challenge_fixture = exact(OLD / 'challenge_fixture.py').decode()
    challenge_fixture = replace_exact(challenge_fixture,
        "def example(view,schemas,*,grant_challenge=True):\n",
        "def example(view,schemas,*,grant_challenge=True):\n"
        "    P.source.require(P.source.current_legacy_view(view) and "
        "view.legacy_signed_sources.source_cut['store_ref']=='" + CURRENT_STORE + "',\n"
        "        'exact current signed challenge fixture view differs')\n", 1)
    challenge_fixture = replace_exact(challenge_fixture,
        "            source_name='custody-participation',allowed_operations=",
        "            source_name=P.source.CURRENT_LEGACY_NAME,allowed_operations=", 1)
    auth = exact(OLD / 'auth.py').decode()
    auth = replace_exact(auth,
        "or (transition and value['source_name']==source.CURRENT_LEGACY_NAME)) and control is None",
        "or ((transition or challenge) and value['source_name']==source.CURRENT_LEGACY_NAME)) and control is None", 1)
    authentication = json.loads(exact(OLD / 'authentication.schema.json'))
    branches = {'lab-local-metadata-candidate-policy/v1-candidate',
                'lab-local-challenge-candidate-policy/v1-candidate',
                'lab-local-challenge-review-policy/v1-candidate',
                'lab-local-reference-closed-review-policy/v1-candidate'}
    changed_branches = []
    for branch in authentication['oneOf']:
        version = branch.get('properties', {}).get('schema_version', {}).get('const')
        if version in branches:
            if branch['properties']['source_name'] != {'const': 'custody-participation'}:
                raise ValueError('frozen challenge policy source contract differs')
            branch['properties']['source_name'] = {'enum': ['custody-participation', CURRENT_NAME]}
            changed_branches.append(version)
    if set(changed_branches) != branches or len(changed_branches) != 4:
        raise ValueError('four exact challenge policy branches required')
    authentication_raw = (json.dumps(authentication, indent=2) + '\n').encode()
    compile(auth, str(NEW / 'auth.py'), 'exec')
    compile(challenge_fixture, str(NEW / 'challenge_fixture.py'), 'exec')
    changed = {'workflow-output-plan.schema.json': schema.encode(),
               'workflow_output_registry.py': registry.encode(),
               'source_bridge.py': bridge.encode(),
               'guard.py': guard.encode(),
               'auth.py': auth.encode(),
               'authentication.schema.json': authentication_raw,
               'challenge_fixture.py': challenge_fixture.encode()}
    NEW_ADAPTER.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    new_file(NEW_ADAPTER, adapter.encode())
    NEW.mkdir(mode=0o700)
    for selected in own:
        name = selected['path'][len(old_prefix):]
        if name == 'contract-profile.json':
            continue
        target = NEW / name
        target.parent.mkdir(parents=True, exist_ok=True)
        new_file(target, changed.get(name, exact(OLD / name)))
    old_adapter_path = OLD_ADAPTER.relative_to(ROOT).as_posix()
    new_adapter_path = NEW_ADAPTER.relative_to(ROOT).as_posix()
    new_profile_rows = []
    for selected in profile['files']:
        path = selected['path']
        if path.startswith(old_prefix):
            new_profile_rows.append(row(NEW / path[len(old_prefix):]))
        elif path == old_adapter_path:
            new_profile_rows.append(row(NEW_ADAPTER))
        else:
            new_profile_rows.append(selected)
    if len(new_profile_rows) != 33425 or len({r['path'] for r in new_profile_rows}) != 33425:
        raise ValueError('API49 v2 profile inventory differs')
    profile['files'] = sorted(new_profile_rows, key=lambda r: r['path'])
    profile['integration_members_binding'] = row(NEW / 'integration-members.json')
    profile['claim_ceiling'] = CLAIM
    save(NEW / 'contract-profile.json', profile)

    new_source_rows = []
    for selected in manifest['files']:
        path = selected['path']
        if path.startswith(old_prefix):
            new_source_rows.append(row(NEW / path[len(old_prefix):]))
        elif path == old_adapter_path:
            new_source_rows.append(row(NEW_ADAPTER))
        else:
            new_source_rows.append(selected)
    if len(new_source_rows) != 208 or len({r['path'] for r in new_source_rows}) != 208:
        raise ValueError('API49 v2 source inventory differs')
    manifest['files'] = sorted(new_source_rows, key=lambda r: r['path'])
    manifest['profile_binding'] = row(NEW / 'contract-profile.json')
    manifest['predecessor_source_manifest_binding'] = row(OLD / 'source-manifest.json')
    manifest['claim_ceiling'] = CLAIM
    save(NEW / 'source-manifest.json', manifest)
    receipt = {'schema_version': 'lab-T16-API51-current-challenge-rebind/v1-candidate',
               'predecessor_source_binding': row(OLD / 'source-manifest.json'),
               'successor_source_binding': row(NEW / 'source-manifest.json'),
               'successor_profile_binding': row(NEW / 'contract-profile.json'),
               'adapter_binding': row(NEW_ADAPTER),
               'successor_package': NEW.relative_to(ROOT).as_posix(),
               'successor_manifest_sha256': digest(NEW / 'source-manifest.json'),
               'source_files': len(new_source_rows), 'profile_files': len(new_profile_rows),
               'schema_service_path_replacements': 2, 'staged_origin_replacements': 7,
               'challenge_policy_schema_versions': sorted(changed_branches),
               'challenge_fixture_current_source': CURRENT_NAME,
               'authority_effect': 'none', 'actual_workflow_transitions': 0,
               'claim_ceiling': CLAIM}
    save(NEW / 'rebind-receipt.json', receipt)
    print(json.dumps({'source_sha256': digest(NEW / 'source-manifest.json'),
                      'profile_sha256': digest(NEW / 'contract-profile.json'),
                      'adapter_sha256': digest(NEW_ADAPTER),
                      'source_files': len(new_source_rows), 'profile_files': len(new_profile_rows)},
                     sort_keys=True))


if __name__ == '__main__': main()
