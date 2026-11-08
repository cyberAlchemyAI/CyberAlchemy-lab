"""Use an actual selected host resource; never authenticate caller Actor fields."""
import base64
import copy
import hashlib
import importlib
import secrets
import sys
import threading
import time
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
READ_OPERATIONS = ('lab.status', 'catalog.get', 'artifact.inspect', 'artifact.query',
                   'context.get', 'session.inspect', 'operation.inspect')
LESSON_READ_OPERATIONS = READ_OPERATIONS + ('lesson.select',)


def require(value, reason):
    if not value:
        raise ValueError(reason)


def fresh_selected_source(selected, expected_family=None):
    """Recheck every selected physical source byte without native replay.

    The original producer capture checks no-follow path custody and exact
    digests. Its archive-handle read also rehashes the owner-only archive.
    The full signed source proof is still required at call entry.
    """
    reader = selected.view.integrated_reader
    require(reader is not None and selected.view.custody_signed_sources is selected,
            'selected source/view identity changed')
    producer = reader.adapter.source
    context = selected.view.legacy_context_producer
    from . import source_bridge
    require(context.reader is reader and context.MAPPED.reader is reader,
            'selected Context/Mapper/Reader family changed')
    basis = selected.selected['candidate_selection_basis']
    context_source = context.HERE / 'source-manifest.json'
    context_pin = source_bridge.CURRENT_LEGACY_DELIVERY_PIN
    context_body = producer.parse(producer.original({
        'path': context_source.relative_to(ROOT).as_posix(), 'sha256': context_pin}))
    mapper_source = context.MAPPED.HERE / 'source-manifest.json'
    mapper_package = context.MAPPED.HERE / 'packages/0001/manifest.json'
    mapper_source_pin = context_body['qualified_mapper_source_binding']['sha256']
    mapper_package_pin = context_body['qualified_mapper_package_binding']['sha256']
    require(context_body['qualified_mapper_source_binding']['path'] == mapper_source.relative_to(ROOT).as_posix()
            and context_body['qualified_mapper_package_binding']['path'] == mapper_package.relative_to(ROOT).as_posix(),
            'Context selected Mapper source/package paths differ')
    manifests = (
        (reader.HERE / 'source-manifest.json', basis['source_manifest_sha256']),
        (reader.adapter.HERE / 'source-manifest.json', basis['adapter_source_sha256']),
        (mapper_source, mapper_source_pin),
        (context_source, context_pin),
    )
    closure = {}
    family = {}
    for path, digest in manifests:
        ref = path.relative_to(ROOT).as_posix()
        raw = producer.original({'path': ref, 'sha256': digest})
        family[ref] = digest
        body = producer.parse(raw)
        require(type(body.get('files')) is list and len(body['files']) <= 4096,
                'selected family source manifest inventory differs')
        for row in body['files']:
            previous = closure.setdefault(row['path'], row['sha256'])
            require(previous == row['sha256'], 'signed family member pins conflict')
    packages = (
        (reader.HERE / 'packages/0001/manifest.json', basis['manifest_sha256']),
        (mapper_package, mapper_package_pin),
        (context.HERE / 'packages/0001/manifest.json', None),
    )
    for path, pin in packages:
        ref = path.relative_to(ROOT).as_posix()
        if pin is None:
            raw = path.read_bytes()
            pin = hashlib.sha256(raw).hexdigest()
        raw = producer.original({'path': ref, 'sha256': pin})
        body = producer.parse(raw)
        require(type(body.get('files')) is list and len(body['files']) <= 4096,
                'selected family package inventory differs')
        family[ref] = pin
        if path.parent.parent.parent == context.HERE:
            require(body['source_manifest_binding'] == {'path': (context.HERE / 'source-manifest.json').relative_to(ROOT).as_posix(),
                                                       'sha256': source_bridge.CURRENT_LEGACY_DELIVERY_PIN},
                    'Context package is not bound to selected source manifest')
        for row in body['files']:
            previous = closure.setdefault(row['path'], row['sha256'])
            require(previous == row['sha256'], 'signed family package member pins conflict')
    producer.original(selected.selected['archive_binding'])
    producer.original(selected.selected['expected_replay_binding'])
    materials = selected.view.data['baseline']['materials']
    require(type(materials) is dict and 0 < len(materials) <= 2048,
            'selected baseline material closure differs')
    for path, digest in materials.items():
        previous = closure.setdefault(path, digest)
        require(previous == digest, 'baseline and signed family pins conflict')
    producer.B.verify_inputs([{'path': path, 'sha256': digest}
                              for path, digest in sorted(closure.items())])
    if expected_family is not None:
        require(family == expected_family, 'selected signed family package bindings changed')
    return family


def select(owner, session_ref, parent_source_binding, *, agent_challenge=None):
    from .machine_auth_scope import source_facts, peer_current
    peer = None
    try:
        with source_facts(owner):
            peer = _select_original(owner, session_ref, parent_source_binding, agent_challenge)
            peer_current(peer)
        peer_current(peer)
        return peer
    except BaseException:
        if peer is not None:
            peer.close()
        raise


def _select_original(owner, session_ref, parent_source_binding, agent_challenge):
    require(type(parent_source_binding) is dict and set(parent_source_binding) == {'path', 'sha256'},
            'independently selected parent source binding required')
    module = sys.modules.get(type(owner).__module__)
    require(module is not None and getattr(module, 'Service', None) is type(owner),
            'actual selected Service instance required')
    path = Path(module.__file__)
    require(path.parent == HERE and path.name == 'service.py', 'unselected parent Service module')
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
    runtime = importlib.import_module(type(sessions).__module__)
    runtime_path=Path(runtime.__file__).resolve()
    require(runtime_path.parent==HERE and runtime_path.name in ('custody_context_sessions.py','source8_context_sessions.py','fixture_context_sessions.py','legacy_context_sessions.py','current_context_sessions.py','current_legacy_context_sessions.py') and type(sessions) is runtime.ContextSessions,'actual selected parent runtime required')
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
    require(resource.agent['payload']['accountable_principal_ref'] == context['principal_ref'],
            'actual Machine accountability differs')
    require(callable(getattr(resource, 'register_disposal_hook', None)),
            'selected resource lacks the explicit transport disposal contract')
    require(not getattr(resource, 'machine_peer_ever_created', False), 'old resource cannot create or restore another peer')
    return MachinePeer(owner, resource, row, package, agent_challenge)


class MachinePeer:
    """Host-selected signer/channel; all memory belongs to its live Session."""
    def __init__(self, owner, resource, row, package, agent_challenge):
        self.owner = owner
        self.resource = resource
        self.row = copy.deepcopy(row)
        self.agent_challenge = copy.deepcopy(agent_challenge)
        self.challenge_used = False
        self._challenge_lease_deadline = None
        self.P = importlib.import_module(package + '.protocol')
        self.A = importlib.import_module(package + '.auth')
        self.Service = importlib.import_module(package + '.service').Service
        self._private_key = Ed25519PrivateKey.generate()
        self.public_key = self._private_key.public_key()
        self.public_key_bytes = self.public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
        self.closed = False
        self._state_lock = threading.RLock()
        self._dispatch_scope = False
        self._family_bindings = fresh_selected_source(resource.source)
        self.used = False
        self.context = None
        self.bound_termination_call = False
        self.path = owner.channel.path
        self.expected_sha = owner.channel.expected_sha
        self.schemas = owner.schemas
        self.host = owner.channel.host
        self.connection = 'connection:Machine:' + secrets.token_hex(16)
        self.expires = min(resource.expires, self.A.instant(owner.channel.context['expires_at']))
        from .session_source_freshness import captured_source_basis
        self._source_memory_basis = copy.deepcopy(captured_source_basis(resource.source))
        self._peer_owner = owner
        self._peer_resource = resource
        self._peer_binding_basis = self.P.source.sha(self.P.compact({
            'row': self.row, 'connection': self.connection,
            'public_key': base64.b64encode(self.public_key_bytes).decode()}))
        self._authenticated_context_basis = None
        if self.agent_challenge is not None:
            self.challenge_grant()
        self.policy = self.narrow_policy()
        self.service = None
        self.challenge = {'schema_version': 'lab-local-reader-challenge/v1-candidate',
                          'host_instance_ref': self.host, 'connection_ref': self.connection,
                          'nonce': secrets.token_hex(32), 'policy_sha256': self.expected_sha,
                          'expires_at': self.expires.isoformat(), 'authority_effect': 'none'}
        require(self.schemas.valid('reader-authentication', self.challenge), 'Machine challenge contract differs')
        resource.register_disposal_hook(self.close)

    def narrow_policy(self, *, verified_parent=False, verified_resource=False):
        # A full parent/resource proof at the call entry permits the exact
        # already-selected policy to be transformed without recursively
        # repeating the complete signed-source replay.
        policy = copy.deepcopy(self.owner.channel.policy if verified_parent
                               else self.owner.channel.policy_guard())
        reads = LESSON_READ_OPERATIONS if policy['schema_version']=='lab-local-lesson-read-policy/v1-candidate' else READ_OPERATIONS
        policy['allowed_operations'] = [operation for operation in reads
                                        if operation in policy['allowed_operations']]
        if self.agent_challenge is not None and not self.challenge_used:
            self.challenge_grant(verified_resource=verified_resource)
            policy['allowed_operations'].append('challenge.submit')
            policy['schema_version'] = 'lab-local-challenge-candidate-policy/v1-candidate'
            policy['challenge_control'] = copy.deepcopy(self.agent_challenge['challenge_control'])
        policy['expires_at'] = self.expires.isoformat()
        require(bool(policy['allowed_operations']), 'parent has no selected Machine read operation')
        return policy

    def _peer_basis_guard(self):
        from .session_source_freshness import captured_source_basis
        require(self.owner is self._peer_owner and self.resource is self._peer_resource
                and self.owner.sessions.source is self.resource.source
                and self.owner.sessions.bridge is self.resource.bridge
                and self.owner.sessions.live.get(self.row['session_ref']) is self.resource,
                'Machine peer selected owner or actual Session changed')
        current = self.P.source.sha(self.P.compact({
            'row': self.row, 'connection': self.connection,
            'public_key': base64.b64encode(self.public_key_bytes).decode()}))
        require(current == self._peer_binding_basis,
                'Machine peer Actor, cut, connection or signer changed')
        if self._authenticated_context_basis is None:
            require(self.context is None, 'Machine context predates actual authentication')
        else:
            require(self.context is not None
                    and self.P.source.sha(self.P.compact(self.context)) == self._authenticated_context_basis,
                    'Machine authenticated opaque context changed')
        require(captured_source_basis(self.resource.source) == self._source_memory_basis,
                'Machine captured source facts changed')

    def live(self):
        require(not self.closed and not self.resource.closed, 'Machine peer or Session is closed')
        try:
            self._peer_basis_guard()
            self.schemas.guard()
            # The selected API69 resource guard performs complete physical and
            # captured freshness. Retain an explicit original semantic proof at
            # the outer Machine boundary before the private dispatch scope.
            self.resource.source.guard()
            self.resource.guard()
            require(self.A.now() < self.expires, 'Machine peer expired')
            require(self.narrow_policy(verified_parent=True, verified_resource=True) == self.policy,
                    'current Machine operation subset differs')
        except BaseException:
            self.close()
            raise

    def proof(self):
        from .machine_auth_scope import source_facts, peer_current
        try:
            with source_facts(self.owner):
                value = self._proof_original()
                peer_current(self)
            peer_current(self)
            return value
        except BaseException:
            self.close()
            raise

    def _proof_original(self):
        self.live()
        require(self._private_key is not None and not self.used, 'Machine signer is closed or challenge consumed')
        value = {'schema_version': 'lab-local-reader-proof/v1-candidate',
                 'challenge': copy.deepcopy(self.challenge),
                 'signature': base64.b64encode(self._private_key.sign(self.P.compact(self.challenge))).decode()}
        return self.P.compact(value)

    def authenticate(self, raw):
        from .machine_auth_scope import source_facts, peer_current
        with self._state_lock:
            try:
                with source_facts(self.owner):
                    value = self._authenticate(raw)
                    peer_current(self)
                peer_current(self)
                return value
            except BaseException:
                self.close()
                raise

    def _authenticate(self, raw):
        self.live()
        require(not self.used and self.context is None, 'Machine challenge already consumed')
        self.used = True
        require(type(raw) is bytes and 0 < len(raw) <= 16384, 'bounded original Machine proof bytes required')
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
        if self.agent_challenge is not None:
            context['limits']['max_actions'] = 1
        context['limits']['deadline'] = self.expires.isoformat()
        context['policy_bindings'].append(copy.deepcopy(self.row['session_state_binding']))
        require(self.schemas.valid('trusted-call-context', context), 'bound Machine context contract differs')
        self.context = context
        self._authenticated_context_basis = self.P.source.sha(self.P.compact(context))
        self.live()
        try:
            self.service = self.Service(self.owner.handlers.view, self, self.schemas, parent_host=self.owner)
            self.live()
            return copy.deepcopy(context)
        except BaseException:
            self.close()
            raise

    def guard(self):
        require(self.context is not None, 'Machine peer unauthenticated')
        if self._dispatch_scope:
            self.dispatch_current()
        else:
            self.live()
        return copy.deepcopy(self.context)

    def policy_guard(self, **kwargs):
        if self._dispatch_scope:
            self.dispatch_current()
        else:
            self.live()
        return copy.deepcopy(self.policy)

    def dispatch_current(self):
        """Fresh physical source and live authority checks inside one call.

        The outer call already completed the full source/contract proof. The
        private archive and expected replay are reread by their exact selected
        bindings here, while the original termination guard rereads policy,
        nonce, revocation, period and actual UTC without replaying the archive.
        """
        require(self._dispatch_scope and not self.closed and not self.resource.closed
                and self.owner.sessions.live.get(self.row['session_ref']) is self.resource
                and self.resource.source is self.owner.sessions.source
                and self.resource.bridge is self.owner.sessions.bridge
                and self.A.now() < min(self.expires, self.resource.expires),
                'Machine or actual Session changed during dispatch')
        self._peer_basis_guard()
        fresh_selected_source(self.resource.source, self._family_bindings)
        self.owner.channel.termination_guard()
        require(self.narrow_policy(verified_parent=True, verified_resource=True) == self.policy,
                'current Machine operation subset differs during dispatch')

    def call(self, raw):
        try:
            self.guard()
            # Disposal may finish during an original guard. Capture only the
            # still-live dispatcher under its existing state lock, then release
            # it before any Service/resource callback. Disposal takes the
            # resource lifetime lock before this lock; reversing that order
            # across a callback could deadlock the timer.
            with self._state_lock:
                require(not self.closed and not self.resource.closed
                        and self.context is not None and self.service is not None
                        and self.A.now() < min(self.expires,self.resource.expires),
                        'Machine dispatcher closed or expired before dispatch')
                service = self.service
                self._dispatch_scope = True
        except Exception:
            return importlib.import_module(self.Service.__module__).transport('unauthenticated-channel', raw)
        # The actual Service checks current private authority and selected
        # physical source bytes at every channel boundary. No stale successful
        # guard result crosses an effect boundary.
        try:
            result = service.call(raw)
        finally:
            with self._state_lock:
                self._dispatch_scope = False
        try:
            operation = self.P.frame_parse(raw).get('operation')
        except Exception:
            operation = None
        if operation == 'challenge.submit' and self.agent_challenge is not None:
            # One technical attempt is all this host-selected live grant permits.
            # The current dispatch has already passed the original Service guard.
            self.challenge_used = True
        return result

    def challenge_grant(self, *, verified_resource=False):
        from . import agent_challenge_grant as grant
        selected = self.agent_challenge
        require(type(selected) is dict and set(selected) == {'envelope','issuer_public','challenge_control'},
                'closed Agent challenge selection required')
        public = base64.b64decode(selected['issuer_public'], validate=True)
        payload = selected['envelope']['payload']
        require(grant.verify(selected['envelope'], public, payload, self.A.now()) is True,
                'signed Agent challenge grant refused')
        remaining = (self.A.instant(payload['expires_at']) - self.A.now()).total_seconds()
        require(remaining > 0, 'Agent challenge grant expired on the UTC clock')
        if self._challenge_lease_deadline is None:
            self._challenge_lease_deadline = time.monotonic() + remaining
        require(time.monotonic() < self._challenge_lease_deadline,
                'Agent challenge grant expired on the monotonic clock')
        require(payload['principal_ref'] == self.owner.channel.context['principal_ref']
                and payload['agent_instance_ref'] == self.row['agent_instance_ref']
                and payload['session_ref'] == self.row['session_ref']
                and payload['assignment_ref'] == self.row['assignment']['version_ref']
                and payload['source_cut'] == self.row['source_cut']
                and payload['scope_ref'] == self.owner.channel.policy['scope_refs'][0]
                and (verified_resource or self.resource.guard() is True),
                'Agent grant differs from this actual live Session')
        return payload

    def note(self, raw):
        self.guard()
        self.resource.note(raw)

    def close(self):
        with self._state_lock:
            if self.closed:
                return
            self.closed = True
            self._private_key = None
            self.agent_challenge = None
            self._challenge_lease_deadline = None
            self.context = None
            self._authenticated_context_basis = None
            self._source_memory_basis = None
            self._peer_binding_basis = None
            self._peer_owner = None
            self._peer_resource = None
            self.challenge = None
            service, self.service = self.service, None
            self.used = True
        if service is not None:
            service.close()
