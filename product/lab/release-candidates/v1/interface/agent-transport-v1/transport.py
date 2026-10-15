"""Use an actual selected host resource; never authenticate caller Actor fields."""
import base64
import copy
import hashlib
import importlib
import secrets
import sys
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
READ_OPERATIONS = ('lab.status', 'catalog.get', 'artifact.inspect', 'artifact.query',
                   'context.get', 'session.inspect', 'operation.inspect')


def require(value, reason):
    if not value:
        raise ValueError(reason)


def select(owner, session_ref, parent_source_binding):
    require(type(parent_source_binding) is dict and set(parent_source_binding) == {'path', 'sha256'},
            'independently selected parent source binding required')
    module = sys.modules.get(type(owner).__module__)
    require(module is not None and getattr(module, 'Service', None) is type(owner),
            'actual selected Service instance required')
    path = Path(module.__file__)
    require(path.is_relative_to(HERE.parent) and path.name == 'service.py', 'unselected parent Service module')
    source = path.parent / 'source-manifest.json'
    require(parent_source_binding == {'path': source.relative_to(ROOT).as_posix(),
                                      'sha256': hashlib.sha256(source.read_bytes()).hexdigest()},
            'parent source selection differs')
    package = type(owner).__module__.rsplit('.', 1)[0]
    guard = importlib.import_module(package + '.guard')
    guard.verify(parent_source_binding['sha256'])
    auth = importlib.import_module(package + '.auth')
    require(type(owner.channel) is auth.ReaderChannel, 'only the original authenticated host may select a Machine peer')
    context = owner.channel.guard()
    require(context['role_assignment_bindings'] == [], 'reader peer cannot inherit governing roles')
    sessions = owner.sessions
    require(sessions is not None and session_ref in sessions.live, 'actual live host Session required')
    runtime = importlib.import_module(package + '.custody_context_sessions')
    resource = sessions.live[session_ref]
    require(type(resource) is runtime.LiveReader and resource.source is sessions.source
            and resource.bridge is sessions.bridge and resource.bridge.channel is owner.channel,
            'foreign or reconstructed resource refused')
    resource.guard()
    row = sessions.selected(session_ref)
    require(row['posture'] == 'active' and row['agent_record'] == resource.agent
            and row['session_ref'] == resource.session['node_id']
            and row['agent_instance_ref'] == resource.agent['node_id'], 'actual Agent/Session binding differs')
    handlers = importlib.import_module(package + '.handlers')
    require(row['source_cut'] == handlers.cut(owner.handlers.view), 'Machine belongs to another current source cut')
    require(resource.agent['owner_ref'] == context['principal_ref'], 'accountable Principal differs')
    require(callable(getattr(resource, 'register_disposal_hook', None)),
            'selected resource lacks the explicit transport disposal contract')
    require(not getattr(resource, 'machine_peer_ever_created', False), 'old resource cannot create or restore another peer')
    return MachinePeer(owner, resource, row, package)


class MachinePeer:
    """Host-selected signer/channel; all memory belongs to its live Session."""
    def __init__(self, owner, resource, row, package):
        self.owner = owner
        self.resource = resource
        self.row = copy.deepcopy(row)
        self.P = importlib.import_module(package + '.protocol')
        self.A = importlib.import_module(package + '.auth')
        self.Service = importlib.import_module(package + '.service').Service
        self._private_key = Ed25519PrivateKey.generate()
        self.public_key = self._private_key.public_key()
        self.public_key_bytes = self.public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
        self.closed = False
        self.used = False
        self.context = None
        self.bound_termination_call = False
        self.path = owner.channel.path
        self.expected_sha = owner.channel.expected_sha
        self.schemas = owner.schemas
        self.host = owner.channel.host
        self.connection = 'connection:Machine:' + secrets.token_hex(16)
        self.expires = min(resource.expires, self.A.instant(owner.channel.context['expires_at']))
        self.policy = self.narrow_policy()
        self.challenge = {'schema_version': 'lab-local-reader-challenge/v1-candidate',
                          'host_instance_ref': self.host, 'connection_ref': self.connection,
                          'nonce': secrets.token_hex(32), 'policy_sha256': self.expected_sha,
                          'expires_at': self.expires.isoformat(), 'authority_effect': 'none'}
        require(self.schemas.valid('reader-authentication', self.challenge), 'Machine challenge contract differs')
        resource.register_disposal_hook(self.close)
        resource.machine_peer_ever_created = True
        self.service = None

    def narrow_policy(self):
        policy = copy.deepcopy(self.owner.channel.policy_guard())
        policy['allowed_operations'] = [operation for operation in READ_OPERATIONS
                                        if operation in policy['allowed_operations']]
        require(bool(policy['allowed_operations']), 'parent has no selected Machine read operation')
        return policy

    def live(self):
        require(not self.closed and not self.resource.closed, 'Machine peer or Session is closed')
        try:
            self.resource.guard()
            self.owner.channel.guard()
            require(self.A.now() < self.expires, 'Machine peer expired')
            require(self.narrow_policy() == self.policy, 'current Machine operation subset differs')
        except BaseException:
            self.close()
            raise

    def proof(self):
        self.live()
        require(self._private_key is not None and not self.used, 'Machine signer is closed or challenge consumed')
        value = {'schema_version': 'lab-local-reader-proof/v1-candidate',
                 'challenge': copy.deepcopy(self.challenge),
                 'signature': base64.b64encode(self._private_key.sign(self.P.compact(self.challenge))).decode()}
        return self.P.compact(value)

    def authenticate(self, raw):
        self.live()
        require(not self.used and self.context is None, 'Machine challenge already consumed')
        self.used = True
        proof = self.P.frame_parse(raw)
        require(type(proof) is dict and set(proof) == {'schema_version', 'challenge', 'signature'}
                and proof['schema_version'] == 'lab-local-reader-proof/v1-candidate'
                and self.schemas.valid('reader-authentication', proof) and proof['challenge'] == self.challenge,
                'Machine proof names another host, connection or challenge')
        self.public_key.verify(base64.b64decode(proof['signature'], validate=True), self.P.compact(self.challenge))
        context = copy.deepcopy(self.owner.channel.context)
        context.update(context_ref='context:Machine:' + secrets.token_hex(16), connection_ref=self.connection,
                       agent_instance_ref=self.row['agent_instance_ref'], session_ref=self.row['session_ref'],
                       assignment_ref=self.row['assignment']['version_ref'], expires_at=self.expires.isoformat(),
                       authentication_evidence_binding=self.P.binding('authentication:' + self.connection, raw))
        context['limits']['max_actions'] = 0
        context['limits']['deadline'] = self.expires.isoformat()
        context['policy_bindings'].append(copy.deepcopy(self.row['session_state_binding']))
        require(self.schemas.valid('trusted-call-context', context), 'bound Machine context contract differs')
        self.context = context
        self.live()
        try:
            self.service = self.Service(self.owner.handlers.view, self, self.schemas)
            self.live()
            return copy.deepcopy(context)
        except BaseException:
            self.close()
            raise

    def guard(self):
        require(self.context is not None, 'Machine peer unauthenticated')
        self.live()
        return copy.deepcopy(self.context)

    def policy_guard(self, **kwargs):
        self.live()
        return copy.deepcopy(self.policy)

    def call(self, raw):
        self.guard()
        require(self.service is not None, 'Machine dispatcher unavailable')
        return self.service.call(raw)

    def note(self, raw):
        self.guard()
        self.resource.note(raw)

    def close(self):
        self.closed = True
        self._private_key = None
        self.context = None
        self.challenge = None
        self.service = None
        self.used = True
