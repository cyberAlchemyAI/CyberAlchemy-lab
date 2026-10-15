"""Owned actual branch preparation; private selection stays outside Git.

Only stage_keys runs before the coordinator releases the runtime lease slot.
Actual constructors require independently selected true code/profile origins.
"""
import argparse
import base64
import copy
import fcntl
from hashlib import sha256
import importlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[6]
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
KINDS = ('custody', 'grant', 'policy')


def need(value, reason):
    if not value:
        raise ValueError(reason)


def compact(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def parse(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate selected JSON field'); result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: need(False, 'nonfinite selected JSON'))


def identity(path):
    value = Path(path).lstat()
    return [value.st_dev, value.st_ino, value.st_uid, stat.S_IMODE(value.st_mode)]


def private(path):
    path = Path(path)
    need(path.is_absolute() and path.is_relative_to('/tmp') and path.resolve() == path
         and not any(p.is_symlink() for p in (path, *path.parents)), 'owned external locator required')
    value = path.lstat()
    need(stat.S_ISREG(value.st_mode) and value.st_uid == os.getuid()
         and stat.S_IMODE(value.st_mode) == 0o600, 'private selected file required')
    return path.read_bytes()


def put(path, raw):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as handle:
        handle.write(raw); handle.flush(); os.fsync(handle.fileno())


def selector(path):
    return {'path': str(path), 'identity': identity(path), 'sha256': sha256(private(path)).hexdigest()}


def guard_selection(path, independent_pin):
    raw = Path(path).read_bytes(); need(sha256(raw).hexdigest() == independent_pin, 'independent producer selection mismatch')
    selected = parse(raw)
    for row in selected['files']:
        source = Path(row['path']); source = source if source.is_absolute() else ROOT / source
        need(source.is_file() and not any(p.is_symlink() for p in (source, *source.parents))
             and sha256(source.read_bytes()).hexdigest() == row['sha256'], 'selected producer bytes unavailable/changed')
    return selected


def key_bytes(key):
    from cryptography.hazmat.primitives import serialization
    return key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())


def public_key(key):
    from cryptography.hazmat.primitives import serialization
    return base64.b64encode(key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode()


def stage_keys(selection_path, selection_pin):
    guard_selection(selection_path, selection_pin)
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    root = Path(tempfile.mkdtemp(prefix='cal-T06-branch-fixtures-')); root.chmod(0o700)
    issuers = root / 'issuers'; issuers.mkdir(mode=0o700)
    rows = {}
    for kind in KINDS:
        key = Ed25519PrivateKey.generate(); path = issuers / (kind + '.pem'); put(path, key_bytes(key))
        # Public declaration describes candidate authority only; key material and
        # all physical custody selectors remain in the private external record.
        declaration = HERE / ('issuer-' + kind + '-authorization-0001.json')
        body = {'schema_version': 'lab-T06-technical-issuer-selection/v1-candidate',
                'issuer_kind': kind, 'purpose': 'candidate-technical-current-selection',
                'authority_effect': 'none', 'actual_owner_outcome': None,
                'permitted_delta': ['Actual fresh lease attribution', 'Corresponding source/grant policy byte bindings'],
                'preserve': ['original records', 'roles', 'scope', 'period', 'permissions', 'budgets', 'revocation and stop state'],
                'genuine_governing_authority': False}
        with declaration.open('xb') as handle:
            handle.write(json.dumps(body, sort_keys=True, indent=2).encode() + b'\n')
        rows[kind] = {'private_key': selector(path), 'public_key': public_key(key),
                      'authorization_binding': {'path': declaration.relative_to(ROOT).as_posix(),
                                                'sha256': sha256(declaration.read_bytes()).hexdigest()},
                      'posture': 'independently-selected-candidate-technical-issuer'}
    record = {'schema_version': 'lab-T06-owned-branch-key-custody/v1-candidate',
              'root': str(root), 'root_identity': identity(root), 'issuers': rows,
              'producer_selection_sha256': selection_pin, 'authority_effect': 'none', 'actual_owner_outcome': None}
    put(root / 'private-key-selection.json', compact(record))
    guard_selection(selection_path, selection_pin)
    return root


def prepare(root, selection_path, selection_pin, source_pin, profile_pin, lock_path):
    selected = guard_selection(selection_path, selection_pin)
    custody = parse(private(root / 'private-key-selection.json'))
    need(identity(root) == custody['root_identity'], 'original own custody root changed')
    need(not (root / 'private-branch-selection.json').exists(), 'fresh independent fixture attempt required')
    lock = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        # Never start a constructor while Root74 or another owned runtime holds
        # the shared lease-sensitive slot. There is no waiting/autorestart loop.
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        sys.path.insert(0, str(INTERFACE))
        P = importlib.import_module('api-integration-v17.protocol')
        G = importlib.import_module('api-integration-v17.guard')
        F = importlib.import_module('api-integration-v17.fixtures')
        L = importlib.import_module('api-integration-v17.legacy_fixture_selection')
        G.verify(source_pin); schemas = P.Schemas(profile_pin)
        members = parse((INTERFACE / 'api-integration-v17/integration-members.json').read_bytes())['members']
        base = root / 'base'; base.mkdir(mode=0o700)
        key, policy_path, policy_pin = F.provision(base, P.source.CURRENT_LEGACY_NAME, principal=L.EXPECTED_PRINCIPAL)
        original = base / 'workspace/workspace.json'
        bootstrap = base / 'workspace.json'; put(bootstrap, private(original))
        base_policy = parse(private(policy_path))
        need(selector(original)['sha256'] == selector(bootstrap)['sha256'] == base_policy['workspace']['manifest_sha256'],
             'transparent Base bootstrap reproduction differs')
        base_branch = {'workspace_root': str(base), 'root_identity': identity(base),
                       'policy': selector(policy_path), 'public_key': public_key(key),
                       'files': {'workspace.json': selector(bootstrap)}}
        # Load the declared successor producer at its true RUN origin, inside the
        # original Action package for unchanged relative runtime imports. Do not
        # rewrite __file__, the original module, keygen, clock or callback.
        actions_name = members['actions']['directory']
        importlib.import_module(actions_name)
        name = actions_name + '.t06_signer_retained_fixture_v1'
        spec = importlib.util.spec_from_file_location(name, HERE / 'action_fixture_signer_retained_v1.py')
        actor_module = importlib.util.module_from_spec(spec); sys.modules[name] = actor_module; spec.loader.exec_module(actor_module)
        actor = actor_module.OwnedActor.__new__(actor_module.OwnedActor)
        try:
            actor_module.OwnedActor.__init__(actor, root / 'actions', schemas,
                                             integration_profile_binding=schemas.profile_binding)
            put(actor.root / 'reader.pem', key_bytes(actor.key))
            put(actor.root / 'source-signer.pem', key_bytes(actor.source_signer))
            action_branch = {'workspace_root': str(actor.root), 'root_identity': identity(actor.root),
                             'policy': selector(actor.root / 'channel-policy.json'), 'public_key': public_key(actor.key),
                             'source_public_key': actor.source_public_key, 'lease_ttl': 900,
                             'files': {n: selector(actor.root / n) for n in ('source.json', 'source.signature', 'grant.json', 'status.json', 'ledger-pins.json')}}
            # Original bytes and fixed periods are retained privately for the
            # same-process future handoff. No Session RAM or nonce is exported.
            original_inputs = {n: base64.b64encode(private(actor.root / n)).decode()
                               for n in ('source.json', 'source.signature', 'grant.json', 'status.json', 'channel-policy.json', 'ledger-pins.json')}
            put(actor.root / 'initial-handoff-inputs.json', compact(original_inputs))
            actor_runtime_closed = False
        finally:
            if hasattr(actor, 'channel'):
                actor.channel.close()
            elif hasattr(actor, 'runtime'):
                actor.runtime.close()
            elif hasattr(actor, 'session'):
                actor.session.close()
            actor_runtime_closed = getattr(getattr(actor, 'session', None), 'closed', False)
        gov = root / 'governance'; gov.mkdir(mode=0o700)
        gov_module = importlib.import_module(members['governance']['directory'] + '.fixture')
        governance = gov_module.Fixture.__new__(gov_module.Fixture)
        try:
            gov_module.Fixture.__init__(governance, gov, schemas)
            put(gov / 'reader.pem', key_bytes(governance.reader))
            governance_branch = {'workspace_root': str(gov), 'root_identity': identity(gov),
                                 'policy': selector(gov / 'operator-policy.json'), 'public_key': public_key(governance.reader),
                                 'files': {n: selector(gov / n) for n in ('native-store/config.json', 'native-store/baseline.json', 'native-store/HEAD.json')}}
        finally:
            if hasattr(governance, 'service'):
                governance.service.close()
            elif hasattr(governance, 'channel'):
                governance.channel.close()
        branches = {'base': base_branch, 'actions': action_branch, 'governance': governance_branch}
        record = {'schema_version': 'lab-T06-private-actual-branch-fixtures/v1-candidate', 'branches': branches,
                  'issuers': custody['issuers'], 'root': str(root), 'root_identity': identity(root),
                  'base_actual_inner_workspace': {'root': str(original.parent), 'root_identity': identity(original.parent),
                                                  'manifest': selector(original), 'bootstrap_manifest': selector(bootstrap),
                                                  'byte_equal': True, 'sdk_early_inner_inode_pinned': False},
                  'source_sha256': source_pin, 'profile_sha256': profile_pin,
                  'same_preparation_Schemas_instance': True, 'original_Action_producer_lease_closed': actor_runtime_closed,
                  'fixture_technical_only': True, 'authority_effect': 'none', 'actual_owner_outcome': None}
        put(root / 'private-branch-selection.json', compact(record))
        G.verify(source_pin); schemas.guard(); guard_selection(selection_path, selection_pin)
        return record
    finally:
        os.close(lock)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['stage-keys', 'prepare'])
    parser.add_argument('--selection', required=True); parser.add_argument('--selection-sha256', required=True)
    parser.add_argument('--root'); parser.add_argument('--source-sha256'); parser.add_argument('--profile-sha256')
    parser.add_argument('--lease-lock')
    args = parser.parse_args()
    if args.phase == 'stage-keys':
        root = stage_keys(args.selection, args.selection_sha256)
        # Locator only: never print any key, policy, grant, source or nonce body.
        print(str(root)); return 0
    need(all((args.root, args.source_sha256, args.profile_sha256, args.lease_lock)), 'independently selected constructor inputs required')
    prepare(Path(args.root), args.selection, args.selection_sha256, args.source_sha256, args.profile_sha256, args.lease_lock)
    print('Actual technical branch fixtures prepared in selected external root; no admission.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
