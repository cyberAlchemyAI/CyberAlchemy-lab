"""Unrun candidate T06 raw-dispatch qualifier derived from preserved driver3.

Fresh owned preparation and each startup cohort are separate commands. The
unchanged SDK selects a real new child Action lease; no Session RAM is restored.
This module never qualifies all345 or all34 effect operation sequences.
"""
import argparse
import base64
import copy
from datetime import datetime, timezone
import fcntl
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import select
import stat
import subprocess
import sys
import time
import uuid

HERE = Path(__file__).resolve().parent
ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
ACTION_FILES = ('source.json', 'source.signature', 'grant.json', 'status.json', 'ledger-pins.json')


def need(value, message):
    if not value:
        raise ValueError(message)


def compact(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def parse(raw):
    def pairs(items):
        value = {}
        for key, item in items:
            need(key not in value, 'duplicate selected field')
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: need(False, 'nonfinite JSON'))


def identity(value):
    return [value.st_dev, value.st_ino, value.st_uid, stat.S_IMODE(value.st_mode)]


def stamp(value):
    return [*identity(value), value.st_size, value.st_mtime_ns, value.st_ctime_ns]


def directory(path, expected):
    path = Path(path)
    need(path.is_absolute() and str(path) == os.path.normpath(str(path)), 'canonical absolute locator required')
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:]:
            nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd); fd = nxt
        need(identity(os.fstat(fd)) == expected and expected[2:] == [os.getuid(), 0o700], 'private root changed')
        return fd
    except BaseException:
        os.close(fd)
        raise


def protected(selector, root, root_identity, limit=16 * 1024 * 1024):
    need(set(selector) == {'path', 'identity', 'sha256'}, 'closed protected selector required')
    path = Path(selector['path']); root = Path(root)
    need(path.is_absolute() and str(path) == os.path.normpath(str(path)) and path.is_relative_to(root), 'owned private path required')
    parent = directory(root, root_identity); descriptors = [parent]
    try:
        parts = path.relative_to(root).parts
        need(parts, 'private leaf required')
        for part in parts[:-1]:
            parent = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            descriptors.append(parent)
            value = os.fstat(parent)
            need(value.st_uid == os.getuid() and stat.S_IMODE(value.st_mode) == 0o700, 'private parent changed')
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        try:
            before = os.fstat(fd)
            need(stat.S_ISREG(before.st_mode) and identity(before) == selector['identity']
                 and selector['identity'][2:] == [os.getuid(), 0o600] and before.st_size <= limit, 'private leaf changed')
            with os.fdopen(fd, 'rb', closefd=False) as stream:
                raw = stream.read(limit + 1)
            need(len(raw) <= limit and stamp(before) == stamp(os.fstat(fd))
                 == stamp(os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)), 'private input changed during capture')
            need(sha256(raw).hexdigest() == selector['sha256'], 'private digest changed')
        finally:
            os.close(fd)
        # Reopen every ancestor against its retained descriptor before returning.
        fresh = directory(root, root_identity)
        try:
            for index, part in enumerate(parts[:-1], 1):
                nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fresh)
                os.close(fresh); fresh = nxt
                need(identity(os.fstat(fresh)) == identity(os.fstat(descriptors[index])), 'private parent detached')
            need(stamp(os.stat(parts[-1], dir_fd=fresh, follow_symlinks=False)) == stamp(before), 'private leaf detached')
        finally:
            os.close(fresh)
        return raw
    finally:
        for fd in reversed(descriptors):
            os.close(fd)


def selector(path):
    path = Path(path)
    value = path.lstat()
    need(stat.S_ISREG(value.st_mode) and stat.S_IMODE(value.st_mode) == 0o600, 'private regular file required')
    parent = directory(path.parent, identity(path.parent.lstat()))
    try:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        try:
            before = os.fstat(fd)
            need(stamp(before) == stamp(value) and before.st_size <= 16 * 1024 * 1024, 'private selector capture changed')
            with os.fdopen(fd, 'rb', closefd=False) as stream:
                raw = stream.read(16 * 1024 * 1024 + 1)
            need(len(raw) <= 16 * 1024 * 1024 and stamp(os.fstat(fd)) == stamp(value)
                 == stamp(os.stat(path.name, dir_fd=parent, follow_symlinks=False)), 'private selector bytes changed')
        finally:
            os.close(fd)
        later = directory(path.parent, identity(os.fstat(parent))); os.close(later)
        return {'path': str(path), 'identity': identity(value), 'sha256': sha256(raw).hexdigest()}
    finally:
        os.close(parent)


def read_record(path, pin):
    path = Path(path); root = path.parent; expected_root = identity(root.lstat())
    need(root.name.startswith('cal-T06-branch-fixtures-') and root.parent == Path('/tmp'), 'owned fixture root required')
    row = selector(path); need(row['sha256'] == pin, 'independent private selection pin differs')
    value = parse(protected(row, root, expected_root))
    need(value['root'] == str(root) and value['root_identity'] == expected_root, 'private selection root differs')
    return value


def load_key(row, record):
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    key = load_pem_private_key(protected(row, record['root'], record['root_identity'], 16384), password=None)
    need(isinstance(key, Ed25519PrivateKey), 'Ed25519 private credential required')
    return key


def replace_owned(path, expected, raw, root, root_identity):
    # Only the six declared files inside the newly owned Action root are replaced.
    protected(expected, root, root_identity)
    path = Path(path); need(path.parent == Path(root), 'owned direct Action leaf required')
    parent = directory(root, root_identity); temporary = '.handoff-' + uuid.uuid4().hex
    try:
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        need(identity(os.stat(path.name, dir_fd=parent, follow_symlinks=False)) == expected['identity'], 'Action preimage detached')
        fresh = directory(root, root_identity); os.close(fresh)
        os.replace(temporary, path.name, src_dir_fd=parent, dst_dir_fd=parent); os.fsync(parent)
    finally:
        os.close(parent)
    row = selector(path); protected(row, root, root_identity)
    return row


def handoff_materials(initial, fresh, signer):
    source = parse(initial['source.json']); status = parse(initial['status.json'])
    grant = parse(initial['grant.json']); policy = parse(initial['channel-policy.json'])
    need(set(fresh) == {'instance', 'session'} and all(type(x) is str and x for x in fresh.values()), 'fresh public lease attribution required')
    source = copy.deepcopy(source); source['runtime_bindings'] = copy.deepcopy(fresh)
    refs = source['refs']; handles = {refs['agent-instance']: fresh['instance'], refs['agent-session']: fresh['session']}
    need(set(source['initial_status']['runtime_handle_bindings']) == set(handles)
         and set(status['runtime_handle_bindings']) == set(handles), 'original attribution shape differs')
    source['initial_status']['runtime_handle_bindings'] = handles
    status = copy.deepcopy(status); status['runtime_handle_bindings'] = handles
    source_raw = compact(source); grant = copy.deepcopy(grant); grant['source_sha256'] = sha256(source_raw).hexdigest()
    grant_raw = compact(grant); policy = copy.deepcopy(policy)
    policy['source_binding'] = {'ref': 'action-source:' + sha256(source_raw).hexdigest(), 'sha256': sha256(source_raw).hexdigest()}
    policy['grant_binding'] = {'ref': 'action-grant:' + sha256(grant_raw).hexdigest(), 'sha256': sha256(grant_raw).hexdigest()}
    return {'source.json': source_raw, 'source.signature': base64.b64encode(signer.sign(source_raw)),
            'status.json': compact(status), 'grant.json': grant_raw, 'operator-policy.json': compact(policy),
            'ledger-pins.json': initial['ledger-pins.json']}


def make_handoff(record, config, config_pin, request):
    need(request['schema_version'] == 'lab-composite-fresh-session-request/v1-candidate'
         and request['configuration_sha256'] == config_pin and request['authority_effect'] == 'none', 'wrong live child handoff request')
    action = record['branches']['actions']; signer = load_key(record['source_signer'], record)
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    need(base64.b64encode(signer.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)).decode()
         == action['source_public_key'], 'original source signer credential differs')
    original = parse(protected(record['initial_inputs'], record['root'], record['root_identity']))
    initial = {name: base64.b64decode(raw, validate=True) for name, raw in original.items()}
    grant = parse(initial['grant.json']); end = grant['expires_at']
    need(grant['not_before'] <= time.time() < end and time.time() < request['lease_expires_at'] <= end, 'fixed original grant period cannot support actual lease')
    materials = handoff_materials(initial, request['fresh_lease'], signer)
    files = {}
    for name in ACTION_FILES:
        if name == 'ledger-pins.json':
            files[name] = action['files'][name]
            protected(files[name], action['workspace_root'], action['root_identity'])
        else:
            files[name] = replace_owned(Path(action['workspace_root']) / name, action['files'][name],
                                        materials[name], action['workspace_root'], action['root_identity'])
    policy_path = Path(action['workspace_root']) / 'operator-policy.json'
    need(not policy_path.exists(), 'new owned handoff policy leaf required')
    parent=directory(action['workspace_root'],action['root_identity'])
    try:
        fd=os.open(policy_path.name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=parent)
        with os.fdopen(fd,'wb') as stream:
            stream.write(materials['operator-policy.json']);stream.flush();os.fsync(stream.fileno())
        later=directory(action['workspace_root'],action['root_identity']);os.close(later);os.fsync(parent)
    finally:os.close(parent)
    files['operator-policy.json'] = selector(policy_path)
    protected(files['operator-policy.json'], action['workspace_root'], action['root_identity'])
    packet = {'schema_version': 'lab-composite-current-handoff/v1-candidate', 'configuration_sha256': config_pin,
              'fresh_lease': copy.deepcopy(request['fresh_lease']), 'files': files}
    authorizations = {}
    for kind in ('custody', 'grant', 'policy'):
        issuer = config['handoff']['issuers'][kind]
        key = load_key(record['issuers'][kind]['private_key'], record)
        need(base64.b64encode(key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)).decode()
             == issuer['public_key'], 'independent issuer credential differs')
        signed = {'schema_version': 'lab-composite-current-selection-authorization/v1-candidate',
                  'selection_kind': kind, 'purpose': 'candidate-technical-current-selection', 'authority_effect': 'none',
                  'issuer_authorization_binding': issuer['authorization_binding'], 'handoff': packet}
        authorizations[kind] = {'signature_base64': base64.b64encode(key.sign(compact(signed))).decode()}
    return {**packet, 'authorizations': authorizations}


class Frames:
    def __init__(self, stream):
        self.stream = stream; self.buffer = b''

    def receive(self, deadline):
        while b'\n' not in self.buffer:
            remaining = deadline - time.monotonic()
            need(remaining > 0 and select.select([self.stream.fileno()], [], [], remaining)[0], 'actual child observation deadline exceeded')
            raw = os.read(self.stream.fileno(), 65536)
            need(raw, 'actual child ended before expected frame'); self.buffer += raw
            need(len(self.buffer) <= 2 * 1024 * 1024, 'child output frame budget exceeded')
        raw, self.buffer = self.buffer.split(b'\n', 1)
        need(len(raw) <= 1024 * 1024, 'child output frame too large')
        return parse(raw)


def send(stream, value):
    stream.write(compact(value) + b'\n'); stream.flush()


def configure(record, args):
    sdk = Path(args.sdk_directory)
    need(sdk == INTERFACE / 'composite-operator-v1-completion-0001/revision-0003', 'independently selected revision-0003 SDK required')
    manifest_raw = public_exact(args.chosen['SDK_binding'])
    need(sha256(manifest_raw).hexdigest() == args.sdk_source_sha256, 'SDK source manifest differs')
    api = INTERFACE / 'api-integration-v17'
    chosen = args.chosen
    bootstrap = chosen['bootstrap_bindings']
    for row in bootstrap:
        public_exact(row)
    need(record['source_sha256'] == chosen['source_binding']['sha256']
         and record['profile_sha256'] == chosen['profile_binding']['sha256'], 'private branches were not prepared for independently selected current API')
    config = {'schema_version': 'lab-composite-operator-config/v2-candidate', 'purpose': 'owned-candidate-rehearsal', 'authority_effect': 'none',
              'provisioning_binding': {'path': args.provisioning_path, 'sha256': args.provisioning_sha256},
              'source': {'directory': str(api), 'source_sha256': record['source_sha256'], 'profile_sha256': record['profile_sha256'],
                         'members_sha256': chosen['members_binding']['sha256'], 'bootstrap_bindings': bootstrap},
              'dependencies': {'selection': {'path': 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json',
                                            'sha256': '2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'},
                               'installation': str(INTERFACE / 'runtime-dependencies-v2-completion-0001/installations/0004')},
              'branches': record['branches'],
              'handoff': {'contract': 'fresh-session-current-source-handoff/v1-candidate', 'startup_seconds': 300,
                          'issuers': {kind: {key: value for key, value in row.items() if key != 'private_key'} for kind, row in record['issuers'].items()}},
              'transport': {'max_frames': 128, 'max_wire_bytes': 16 * 1024 * 1024, 'max_frame_bytes': 1024 * 1024, 'max_response_bytes': 1024 * 1024}}
    # The independently selected original constructors produced these pinned
    # branches. The launcher repeats its own complete semantic preflight.
    if args.scenario == 'missing-governance-policy':
        missing = Path(record['root']) / chosen['missing_policy_leaf']
        need(not missing.exists() and not missing.is_symlink(), 'negative must select an actually absent owned leaf')
        config['branches'] = copy.deepcopy(config['branches'])
        config['branches']['governance']['policy']['path'] = str(missing)
    raw = compact(config); path = Path(record['root']) / ('operator-' + args.scenario + '.json')
    parent = directory(record['root'],record['root_identity'])
    try:
        fd = os.open(path.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600,dir_fd=parent)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        later=directory(record['root'],record['root_identity']);os.close(later);os.fsync(parent)
    finally:os.close(parent)
    return config, path, sha256(raw).hexdigest()


def public_exact(row):
    need(type(row) is dict and set(row) == {'path', 'sha256'}, 'closed independent public binding')
    relative = Path(row['path'])
    need(not relative.is_absolute() and '..' not in relative.parts and relative.as_posix() == row['path'], 'true public origin required')
    path = ROOT / relative
    fds = [os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)]
    try:
        for part in path.parts[1:-1]:fds.append(os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fds[-1]))
        fds.append(os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fds[-1]))
        before = os.fstat(fds[-1]);need(stat.S_ISREG(before.st_mode) and before.st_size <= 32 * 1024 * 1024, 'bounded public input')
        parts = []
        while block := os.read(fds[-1], 1024 * 1024):parts.append(block)
        raw = b''.join(parts)
        need(stamp(before) == stamp(os.fstat(fds[-1])) and sha256(raw).hexdigest() == row['sha256'], 'independently selected public bytes changed')
        for index, part in enumerate(path.parts[1:]):
            a = os.stat(part, dir_fd=fds[index], follow_symlinks=False);b = os.fstat(fds[index + 1])
            need((a.st_dev,a.st_ino,a.st_mode,a.st_uid,a.st_gid) == (b.st_dev,b.st_ino,b.st_mode,b.st_uid,b.st_gid), 'public input detached')
        return raw
    finally:
        for fd in reversed(fds):os.close(fd)


def selection_check(value):
    fields = {'schema_version','status','authority_effect','source_binding','profile_binding','members_binding',
              'SDK_binding','provisioning_binding','dependency_selection_binding','dependency_installation',
              'bootstrap_bindings','handler_bindings','caller_boundary_binding','registry_operations','missing_policy_leaf',
              'probe_seconds','observation_seconds'}
    need(type(value) is dict and set(value) == fields and value['schema_version'] == 'lab-T06-development-operator-selection/v1-candidate'
         and value['status'] == 'Root-selected-for-T06-development' and value['authority_effect'] == 'none', 'unresolved independent Root selection')
    need(value['source_binding']['sha256']=='ee969cc8c6b539aa3247d81c82322cb9e7aefd42188d63db0195e381cdad4cb1'
         and value['profile_binding']['sha256']=='9c8c3018226abb9077c6a99ee3cbc9dd0174c148b332b9488fd4a3a9cd30418b','this version selects exact finalcapture5; successor required after drift')
    need(value['source_binding']['path'] == 'product/lab/release-candidates/v1/interface/api-integration-v17/source-manifest.json'
         and value['profile_binding']['path'] == 'product/lab/release-candidates/v1/interface/api-integration-v17/contract-profile.json', 'exact current API origins required')
    need(value['SDK_binding']['sha256']=='15cd8e4e863d110c0da025091220f6efdc7fee8509b001c5bbee816307cfdabd'
         and value['provisioning_binding']['sha256']=='81920701206b6e8556b973c975c0c6dd00fb83c2f21a3bea42b472d834cb117d','selected reviewed SDK3 and T34 technical receipt required')
    need(value['SDK_binding']['path'] == 'product/lab/release-candidates/v1/interface/composite-operator-v1-completion-0001/revision-0003/source-manifest.json', 'true maintained SDK3 required')
    need(value['dependency_selection_binding'] == {'path':'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json','sha256':'2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'}, 'selected0004 dependency closure required')
    need(value['members_binding']['path']=='product/lab/release-candidates/v1/interface/api-integration-v17/integration-members.json'
         and value['caller_boundary_binding']=={'path':'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T04/revision-0002/caller_adapter.py','sha256':'b2b171a48754ffcff9cda8dbac889b06bd0b2e0d32d3c75ad49c4d63aeaab7f8'}
         and value['provisioning_binding']['path']=='docs/plans/0011-lab-runtime-completion/runs/0001-execution/T34/task-session-result-v4.json','independent original boundary/member/provisioning origins')
    installation = INTERFACE / 'runtime-dependencies-v2-completion-0001/installations/0004'
    need(value['dependency_installation'] == str(installation) and Path(sys.executable) == installation/'bin/python', 'exact selected interpreter required')
    need(type(value['missing_policy_leaf']) is str and value['missing_policy_leaf'].startswith('missing-governance-')
         and Path(value['missing_policy_leaf']).name == value['missing_policy_leaf'], 'flat independently selected negative leaf')
    need(type(value['registry_operations']) is list and len(value['registry_operations']) == len(set(value['registry_operations'])) == 34, 'full34 registry required')
    need(type(value['probe_seconds']) is int and 1 <= value['probe_seconds'] <= 300
         and type(value['observation_seconds']) is int and 1 <= value['observation_seconds'] <= 900, 'independently selected bounded observation windows')
    need(set(value['handler_bindings']) == {'base_catalog','base_inspect','actions','governance'}, 'four exact callback handler origins required')
    for key in ['source_binding','profile_binding','members_binding','SDK_binding','provisioning_binding','dependency_selection_binding','caller_boundary_binding']:
        public_exact(value[key])
    profile = parse(public_exact(value['profile_binding']))
    need(profile['implemented_operations'] == value['registry_operations'], 'independent registry/profile differs')
    members=parse(public_exact(value['members_binding']))['members']
    handler_paths={'base_catalog':'product/lab/release-candidates/v1/interface/api-integration-v17/handlers.py',
                   'base_inspect':'product/lab/release-candidates/v1/interface/api-integration-v17/candidate.py',
                   **{k:'product/lab/release-candidates/v1/interface/'+members[k]['directory']+'/service.py' for k in ['actions','governance']}}
    for kind,row in value['handler_bindings'].items():
        need(row['path']==handler_paths[kind],'exact original branch handler origin');public_exact(row)
    sdk=INTERFACE/'composite-operator-v1-completion-0001/revision-0003'
    needed={str(p.relative_to(ROOT)) for p in sdk.glob('*.py')}|{str((INTERFACE/'api-integration-v17'/n).relative_to(ROOT)) for n in ['guard.py','__init__.py','source-manifest.json','contract-profile.json','integration-members.json']}
    need(type(value['bootstrap_bindings']) is list and {r['path'] for r in value['bootstrap_bindings']}==needed
         and len(value['bootstrap_bindings'])==len(needed),'complete independently selected bootstrap inputs')
    for row in value['bootstrap_bindings']:public_exact(row)
    boot={r['path']:r for r in value['bootstrap_bindings']}
    for key in ['source_binding','profile_binding','members_binding']:
        need(boot[value[key]['path']]==value[key],'bootstrap/public selection mismatch')
    return value


def prepare_dependencies(args):
    # Capture the selected original SDK control helper before importing any
    # dependency package. Its installed-byte callback is executed unchanged.
    import types
    row=next(r for r in args.chosen['bootstrap_bindings'] if r['path'].endswith('/revision-0003/control.py'))
    name='_cal_T06_dependency_control_'+uuid.uuid4().hex
    module=types.ModuleType(name);module.__file__=str(ROOT/row['path']);sys.modules[name]=module
    try:exec(compile(public_exact(row),module.__file__,'exec'),module.__dict__)
    except BaseException:
        if sys.modules.get(name) is module:del sys.modules[name]
        raise
    value=parse(public_exact(args.chosen['dependency_selection_binding']))
    need(len(value['original_bindings'])==5 and len(value['inputs'])==720,'full original selected dependency provenance')
    expected={r['destination']:{'sha256':r['sha256'],'size_bytes':r['size_bytes'],'mode':0o755 if r['kind'] in {'interpreter','native-executable'} else 0o644} for r in value['inputs']}
    expected.update(value['wheel_members']);expected['lib/abi/ld-linux-x86-64.so.2']['mode']=0o755
    need(len(expected)==1010,'complete original installed closure')
    installation=Path(args.chosen['dependency_installation'])
    module.installed(installation,expected)
    sys.path.insert(0,str(installation/'deps'))
    return module,installation,expected


class QualificationRefusal(ValueError):
    def __init__(self, envelope, code):self.envelope=envelope;self.code=code


def reply_check(reply, raw, call, branch, context, schemas, chosen, expect, boundary):
    # Classify before reading domain payload. Original response schema and
    # exact raw request/actual handler bind the real callback route.
    need(type(reply) is dict, 'reply object required')
    classification = boundary.classify(reply)
    if classification.envelope == 'transport-error':
        need(schemas.valid('transport-error',reply), 'original transport refusal schema differs')
        raise QualificationRefusal(classification.envelope,classification.code)
    need(schemas.valid('api-reply', reply), 'selected original reply schema refusal')
    need(reply.get('kind') in ('result','error') and reply['call_id'] == call['call_id']
         and reply['operation'] == call['operation'] and reply['contract_profile_binding'] == schemas.profile_binding,
         'reply classification or held pre-call selection differs')
    handler_key = ('base_catalog' if call['operation']=='catalog.get' else 'base_inspect') if branch=='base' else branch
    need(reply['trusted_context_binding'] == {'ref':context['context_ref'],'sha256':sha256(compact(context)).hexdigest()}, 'actual independent branch context differs')
    need(reply['request_binding']['sha256'] == sha256(raw).hexdigest()
         and reply['handler_binding'] == {'ref':chosen['handler_bindings'][handler_key]['path'], 'sha256':chosen['handler_bindings'][handler_key]['sha256']},
         'actual raw bytes or branch handler binding differs')
    message = reply['message']
    if expect == 'not-found':
        if reply['kind'] == 'error' and message.get('code') != 'not-found':
            raise QualificationRefusal(classification.envelope,classification.code)
        need(reply['kind'] == 'error' and message.get('schema_version') == 'lab-error-result/v1-candidate'
             and message.get('code') == 'not-found' and message.get('retry_policy') == 'no-retry', 'actual inspector did not return exact causal absence')
    else:
        if reply['kind'] != 'result':raise QualificationRefusal(classification.envelope,classification.code)
        need(reply['kind'] == 'result' and message.get('authority_effect') == 'none', 'actual catalog result unavailable')
    return {'branch':branch,'operation':call['operation'],'reply_kind':reply['kind'],
            'code':message.get('code'),'request_byte_sha256':sha256(raw).hexdigest(),
            'handler_binding':reply['handler_binding'],'trusted_context_binding':reply['trusted_context_binding'],'caller_classification':classification.envelope,'retry_allowed':False,'authority_effect':'none'}


def probe_calls(child, frames, ready, record, schemas, chosen, deadline, lease_expires, boundary, event):
    from datetime import timedelta
    contexts = ready.get('contexts')
    need(type(contexts) is dict and set(contexts) == {'base','actions','governance'}, 'actual independent contexts required')
    need(len({contexts[k]['context_ref'] for k in contexts})==3,'independent branch channels required')
    observations = []
    for branch, operation in [('base','catalog.get'),('base','operation.inspect'),('actions','operation.inspect'),('governance','operation.inspect')]:
        context = contexts[branch]
        policy = parse(protected(record['branches'][branch]['policy'], record['branches'][branch]['workspace_root'], record['branches'][branch]['root_identity']))
        need(context['principal_ref']==policy['principal_ref'],'actual authenticated principal differs from its independently selected branch policy')
        # Cap this new read by unchanged policy and original selected local
        # maximum. No lease/grant/policy expiry is extended or predicted.
        policy_end = datetime.fromisoformat(policy['expires_at'].replace('Z','+00:00'))
        until = min(datetime.now(timezone.utc) + timedelta(seconds=chosen['probe_seconds']), policy_end,
                    datetime.fromtimestamp(lease_expires,timezone.utc),
                    datetime.fromisoformat(context['expires_at'].replace('Z','+00:00')))
        need(until > datetime.now(timezone.utc), 'original branch period ended')
        actor = {k:context[k] for k in ['principal_ref','agent_instance_ref','assignment_ref','session_ref']}
        actor['role_assignment_refs'] = context['role_assignment_bindings']
        budget = {'max_actions':0,'max_input_bytes':min(65536,policy['max_request_bytes']),
                  'max_output_bytes':min(262144,policy['max_response_bytes']),'deadline':until.isoformat()}
        need(budget['max_output_bytes'] >= 32768, 'original inspection budget unavailable')
        message = {'schema_version':'lab-catalog-request/v1-candidate' if operation == 'catalog.get' else 'lab-operation-inspect-request/v1-candidate',
                   'request_ref':'request:T06:'+uuid.uuid4().hex,'actor':actor,'budget':budget,'authority_effect':'none'}
        if operation == 'catalog.get':message.update(source_cut=None,carrier_refs=[],include_relations=True,limit=20,page_cursor=None)
        else:message['lookup'] = {'operation':{'base':'change.prepare','actions':'action.dispatch','governance':'admission.apply'}[branch],
                                 'idempotency_key':'T06-absent:'+uuid.uuid4().hex}
        call = {'schema_version':'lab-api-call/v2-candidate','call_id':'call:T06:'+uuid.uuid4().hex,'operation':operation,
                'caller_context_ref':context['context_ref'],'expected_source_cut':None,'deadline':until.isoformat(),
                'max_response_bytes':budget['max_output_bytes'],'idempotency_key':None,'message':message,
                'expected_contract_profile_binding':schemas.profile_binding}
        need(schemas.valid('api-call',call), 'original request schema refused qualification read')
        raw = b' \t' + json.dumps(call,ensure_ascii=False,allow_nan=False,separators=(', ', ': ')).encode() + b' \r'
        need(b'\n' not in raw and len(raw) <= policy['max_request_bytes'], 'bounded original LF-frame bytes required')
        event({'phase':'call-start','branch':branch,'operation':operation,'request_byte_sha256':sha256(raw).hexdigest(),
               'actual_call_deadline':until.isoformat()})
        child.stdin.write(raw + b'\n');child.stdin.flush()
        reply = frames.receive(min(deadline,time.monotonic()+chosen['probe_seconds']))
        observed = reply_check(reply,raw,call,branch,context,schemas,chosen,'result' if operation=='catalog.get' else 'not-found',boundary)
        observations.append(observed);event({'phase':'call-result',**observed})
    return observations




def run(record, args):
    lock = args.runtime_lock
    child = None; rows = []; started = time.monotonic(); exit_code = None
    try:
        config, path, config_pin = configure(record, args)
        sdk = Path(args.sdk_directory)
        stderr_path = Path(record['root']) / 'operator-stderr.bin'
        parent=directory(record['root'],record['root_identity'])
        try:
            errfd=os.open(stderr_path.name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=parent)
            later=directory(record['root'],record['root_identity']);os.close(later)
        except BaseException:
            if 'errfd' in locals():os.close(errfd)
            raise
        finally:os.close(parent)
        with os.fdopen(errfd, 'wb') as errors:
            installation = Path(config['dependencies']['installation'])
            child = subprocess.Popen([str(installation / 'lib/abi/ld-linux-x86-64.so.2'), '--inhibit-cache',
                                      '--library-path', str(installation / 'lib/abi'), str(installation / 'bin/python'),
                                      '-I', '-X', 'utf8', '-B', '-S', str(sdk / 'launch.py'), '--launcher-source-sha256', args.sdk_source_sha256,
                                      '--config', str(path), '--config-sha256', config_pin], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=errors, pass_fds=(lock,), env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'})
            frames = Frames(child.stdout); observation_deadline = time.monotonic() + args.chosen['observation_seconds']
            request = frames.receive(observation_deadline)
            if args.scenario == 'missing-governance-policy':
                need(request == {'schema_version':'lab-composite-startup-error/v1-candidate','code':'startup-or-channel-refused','authority_effect':'none'}, 'missing credential emitted a challenge or unexpected output')
                child.stdin.close(); exit_code=child.wait(timeout=120)
                need(exit_code == 2, 'missing credential did not refuse startup')
                return {'schema_version':'lab-T06-development-operator-result/v1-candidate','result':'PASS-refusal-before-challenge-on-missing-policy-cohort','dispatch_operations_executed':0,'process_exit_code':exit_code,'exact_inner_refusal_cause_claimed':False,'authority_effect':'none','task_complete':False}
            need(request.get('schema_version') == 'lab-composite-fresh-session-request/v1-candidate', 'actual full34 launch did not request fresh lease')
            rows.append({'event': request['schema_version'], 'elapsed_seconds': time.monotonic() - started});args.event({'phase':'fresh-child-lease-request','child_pid':child.pid,'lease_expires_at':request['lease_expires_at']})
            send(child.stdin, make_handoff(record, config, config_pin, request))
            challenges = frames.receive(observation_deadline)
            need(challenges.get('schema_version') == 'lab-composite-challenges/v1-candidate'
                 and set(challenges['challenges']) == {'base', 'actions', 'governance'}, 'actual independent branch challenges absent')
            for kind in ('base', 'actions', 'governance'):
                challenge = challenges['challenges'][kind]; key = load_key(record['reader_keys'][kind], record)
                if kind == 'governance':
                    # Selected Governance-v4 dependencies.encoded is P.compact.
                    encoded = compact(challenge)
                    proof = {'challenge': challenge, 'signature_base64': base64.b64encode(key.sign(encoded)).decode()}
                else:
                    proof = {'schema_version': 'lab-local-reader-proof/v1-candidate' if kind == 'base' else 'lab-local-action-proof/v1-candidate',
                             'challenge': challenge, 'signature': base64.b64encode(key.sign(compact(challenge))).decode()}
                send(child.stdin, {'schema_version': 'lab-composite-branch-proof/v1-candidate', 'branch': kind,
                                   'proof_base64': base64.b64encode(compact(proof)).decode()})
            ready = frames.receive(observation_deadline)
            need(ready.get('schema_version') == 'lab-composite-ready/v1-candidate' and ready['catalog_operation_count'] == 34
                 and ready['composition'] == 'Base28+Action3+Governance3' and ready['authority_effect'] == 'none', 'actual common full34 dispatcher readiness absent')
            rows.append({'event': ready['schema_version'], 'elapsed_seconds': time.monotonic() - started,
                         'composition': ready['composition'], 'catalog_operation_count': 34})
            args.event({'phase':'ready','catalog_operation_count':34,'composition':ready['composition']})
            observations = probe_calls(child,frames,ready,record,args.schemas,args.chosen,observation_deadline,request['lease_expires_at'],args.boundary,args.event)
            args.event({'phase':'all-four-raw-probes-returned','operations':len(observations)})
            # EOF requires actual owned channel/service cleanup and source exit
            # guards. These four read requests perform no admission/checkpoint effect.
            child.stdin.close(); exit_code = child.wait(timeout=120)
            need(exit_code == 0, 'actual full34 owned shutdown refused')
        return {'schema_version': 'lab-T06-development-operator-result/v1-candidate', 'status': 'PASS-development-raw-dispatch-only', 'authority_effect': 'none',
                'actual_owner_outcome': None, 'process_exit_code': exit_code, 'events': rows,
                'elapsed_seconds': time.monotonic() - started, 'configuration_sha256': config_pin,
                'dispatch_operations_executed': len(observations), 'observations': observations, 'inspector_absent_keys_not_completed_recovery': True, 'whole_API_qualified': False, 'actual_admitted_provisioning': False,
                'private_credentials_public_exported': False}
    finally:
        args.cleanup = {'child_pid':child.pid if child is not None else None,'child_exit':None,'live':False,'errors':[]}
        if child is not None:
            try:
                if child.stdin is not None and not child.stdin.closed:child.stdin.close()
                child.wait(timeout=120)
            except BaseException as error:args.cleanup['errors'].append(type(error).__name__)
            args.cleanup['child_exit']=child.poll();args.cleanup['live']=child.poll() is None
        # The parent outer scope retains this same lock across exit guards.


def negative_state(record):
    # Only explicitly selected freshly owned fixture bytes; no private bodies
    # enter public evidence. Unknown roots and old historical stores are absent.
    result = {}
    for kind, branch in record['branches'].items():
        for label,row in {'policy':branch['policy'],**branch['files']}.items():
            raw=protected(row,branch['workspace_root'],branch['root_identity'])
            result[kind+':'+label]=sha256(raw).hexdigest()
    return result


class Output:
    """New public sanitized evidence only, held no-follow output directory."""
    def __init__(self, parent, prefix):
        self.parent = Path(parent);self.fds=[];self.event_fd=None;self.prefix=prefix
        try:
            path=self.parent
            self.fds=[os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)]
            for part in path.parts[1:]:self.fds.append(os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=self.fds[-1]))
            try:os.mkdir('observations',0o700,dir_fd=self.fds[-1])
            except FileExistsError:pass
            self.fds.append(os.open('observations',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=self.fds[-1]))
            st=os.fstat(self.fds[-1]);need(st.st_uid==os.getuid() and stat.S_IMODE(st.st_mode)==0o700,'owned output custody')
            self.check()
            self.event_fd=os.open(prefix+'.events.jsonl',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=self.fds[-1])
            self.check()
        except BaseException:self.close();raise
    def check(self):
        for index,part in enumerate((*self.parent.parts[1:],'observations')):
            a=os.stat(part,dir_fd=self.fds[index],follow_symlinks=False);b=os.fstat(self.fds[index+1])
            need((a.st_dev,a.st_ino,a.st_mode,a.st_uid,a.st_gid)==(b.st_dev,b.st_ino,b.st_mode,b.st_uid,b.st_gid),'owned output ancestor detached')
    def write(self,fd,raw,label):
        self.check();before=os.fstat(fd);attached=os.stat(label,dir_fd=self.fds[-1],follow_symlinks=False)
        need(identity(before)==identity(attached) and stat.S_ISREG(before.st_mode) and identity(before)[2:]==[os.getuid(),0o600],'owned evidence leaf detached')
        offset=0
        while offset<len(raw):
            size=os.write(fd,raw[offset:]);need(size>0,'output write stalled');offset+=size
        os.fsync(fd);self.check()
        need(stamp(os.fstat(fd))==stamp(os.stat(label,dir_fd=self.fds[-1],follow_symlinks=False)),'owned evidence leaf replaced')
    def append(self,value):self.write(self.event_fd,compact(value)+b'\n',self.prefix+'.events.jsonl')
    def report(self,value):
        self.check();fd=os.open(self.prefix+'.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=self.fds[-1])
        try:self.write(fd,compact(value)+b'\n',self.prefix+'.json');os.fsync(self.fds[-1])
        finally:os.close(fd)
    def close(self):
        if self.event_fd is not None:os.close(self.event_fd);self.event_fd=None
        for fd in reversed(self.fds):os.close(fd)
        self.fds=[]


def main(argv=None):
    parser=argparse.ArgumentParser()
    for key in ['selection','selection-sha256','branch-selection','branch-selection-sha256','lease-lock','output-prefix']:
        parser.add_argument('--'+key,required=True)
    parser.add_argument('--scenario',required=True,choices=['positive-raw-reads','missing-governance-policy'])
    args=parser.parse_args(argv)
    need(args.output_prefix.replace('-','').isalnum(),'new owned output prefix')
    path=Path(args.selection);need(path.is_absolute() and path.is_relative_to(ROOT),'public Root selection at exact repo origin required')
    args.chosen=selection_check(parse(public_exact({'path':str(path.relative_to(ROOT)),'sha256':args.selection_sha256})))
    args.sdk_directory=str(INTERFACE/'composite-operator-v1-completion-0001/revision-0003')
    args.sdk_source_sha256=args.chosen['SDK_binding']['sha256']
    args.provisioning_path=args.chosen['provisioning_binding']['path'];args.provisioning_sha256=args.chosen['provisioning_binding']['sha256']
    expected_lock=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/lease-sensitive-runtime.lock'
    need(Path(args.lease_lock)==expected_lock,'exact existing shared runtime slot required')
    lock=os.open(expected_lock,os.O_RDWR|os.O_NOFOLLOW)
    try:
        before=os.fstat(lock)
        need(stat.S_ISREG(before.st_mode) and before.st_uid==os.getuid() and stat.S_IMODE(before.st_mode)==0o600
             and identity(before)==identity(expected_lock.lstat()),'runtime lock custody changed')
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);args.runtime_lock=lock
        dependency=prepare_dependencies(args);args.dependency=dependency;args.dependency_exit_checked=False
        try:return execute(args)
        finally:
            if not args.dependency_exit_checked:dependency[0].installed(dependency[1],dependency[2])
    finally:os.close(lock)


def execute(args):
    # API and T04 bodies retain true origins. No class/function/clock callback
    # is replaced. The original API verifies the complete current Source.
    api=INTERFACE/'api-integration-v17';name='_cal_T06_qualification_API_'+uuid.uuid4().hex
    spec=importlib.util.spec_from_file_location(name,api/'__init__.py',submodule_search_locations=[str(api)])
    package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
    guard=__import__(name+'.guard',fromlist=['verify']);guard.verify(args.chosen['source_binding']['sha256'])
    protocol=__import__(name+'.protocol',fromlist=['Schemas']);args.schemas=protocol.Schemas(args.chosen['profile_binding']['sha256'])
    import types
    row=args.chosen['caller_boundary_binding'];boundary=types.ModuleType('_cal_T06_boundary_'+uuid.uuid4().hex)
    boundary.__file__=str(ROOT/row['path']);sys.modules[boundary.__name__]=boundary
    exec(compile(public_exact(row),boundary.__file__,'exec'),boundary.__dict__);args.boundary=boundary
    output = Output(HERE, args.output_prefix)
    def event(value):output.append({'at':datetime.now(timezone.utc).isoformat(),**value})
    args.event=event;args.cleanup={};primary=None;result=None;exit_error=None;negative_unchanged=None
    try:
        before=None;record=None
        try:
            record=read_record(args.branch_selection,args.branch_selection_sha256)
            before=negative_state(record) if args.scenario=='missing-governance-policy' else None
            event({'phase':'selected-entry','scenario':args.scenario,'source':args.chosen['source_binding'],'profile':args.chosen['profile_binding']})
            result=run(record,args)
        except BaseException as error:
            primary={'class':type(error).__name__,'envelope':getattr(error,'envelope',None),'code':getattr(error,'code',None)}
        finally:
            try:
                if before is not None:negative_unchanged=before==negative_state(record)
                guard.verify(args.chosen['source_binding']['sha256']);args.schemas.guard()
                public_exact(args.chosen['profile_binding'])
                args.dependency[0].installed(args.dependency[1],args.dependency[2]);args.dependency_exit_checked=True
            except BaseException as error:exit_error=type(error).__name__
        passed=primary is None and exit_error is None and not args.cleanup.get('live',True) and not args.cleanup.get('errors')
        if args.scenario=='missing-governance-policy':passed=passed and negative_unchanged is True
        report={'schema_version':'lab-T06-development-operator-qualification/v1-candidate','result':'PASS' if passed else 'FAIL',
                'scenario':args.scenario,'primary_refusal':primary,'exit_guard_error_class':exit_error,'cleanup':args.cleanup,
                'negative_selected_fixture_bytes_unchanged':negative_unchanged,'execution':result,
                'selection_sha256':args.selection_sha256,'source_binding':args.chosen['source_binding'],'profile_binding':args.chosen['profile_binding'],
                'selected_registry_operations':args.chosen['registry_operations'],
                'old_zero_dispatch_evidence_preserved':True,'complete345_or_all34_qualification':False,
                'authority_effect':'none','task_complete':False}
        event({'phase':'terminal','result':report['result'],'primary_refusal':primary,'cleanup':args.cleanup})
        output.report(report)
        print(compact({'result':report['result'],'scenario':args.scenario,'authority_effect':'none','task_complete':False}).decode())
        return 0 if passed else 1
    finally:output.close()


