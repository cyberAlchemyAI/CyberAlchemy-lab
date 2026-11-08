"""Owner-provisioned local scope, exact source views, custody and native review.

This is not the historical API17 gateway. Its trust boundary is the provisioning
user's private directory and key; it grants no repository admission authority.
"""
import copy
from datetime import datetime, timedelta, timezone
import fcntl
import os
from pathlib import Path
import re
import tempfile

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from define_core import call
from define_core.api import byte_members, encoded_members
from define_core.capture import bindings_in
from define_core.exact import (binding, bound, decode, encode, exclusive, fsync_dir,
                               logical, publish_directory, read, require, sha, write_package)
from define_core.package import inspect_local
from lab_runtime import common
from lab_runtime.sources import resolve
from lab_runtime.store import Store, keygen
from lab_runtime.session import Session

from .bootstrap import PACKAGE, REPO

OPERATIONS = ['context', 'prepare', 'review', 'retain', 'reconstruct', 'authorize', 'apply']


def invoke(operation, **params):
    result = call({'api_version': 'define.api/v1', 'id': 'lab-connector',
                   'operation': operation, 'params': params})
    require(result['outcome'] in ('prepared', 'prepared-with-gaps', 'ready', 'not-evaluable'),
            result['diagnostics'][0]['code'] if result['diagnostics'] else 'define-refused', exit_code=3)
    return result['data']


def package_members(directory):
    raw, _, _, buffers = inspect_local(directory)
    return {**buffers, 'manifest.json': raw}


def sign(value, key):
    return {**value, 'signature': key.sign(encode(value)).hex()}


def verified(value, public):
    require(isinstance(value, dict) and isinstance(value.get('signature'), str), 'signature-required', exit_code=3)
    core = {k: v for k, v in value.items() if k != 'signature'}
    try:Ed25519PublicKey.from_public_bytes(bytes.fromhex(public)).verify(bytes.fromhex(value['signature']), encode(core))
    except (ValueError, __import__('cryptography.exceptions', fromlist=['InvalidSignature']).InvalidSignature):
        require(False, 'signature-invalid', exit_code=3)
    return core


def setup(home, principal, *, store_id='define-lab-local', hours=24):
    home = Path(home).absolute()
    require(not home.is_relative_to(REPO) and home.resolve() == home, 'operator-home-must-be-external', exit_code=3)
    require(not home.exists() and home.parent.is_dir(), 'new-operator-home-required', exit_code=3)
    require(isinstance(principal, str) and principal.startswith(('person:', 'principal:')), 'explicit-principal-required')
    require(type(hours) is int and 1 <= hours <= 168, 'invalid-grant-period')
    staged = Path(tempfile.mkdtemp(prefix='.define-lab-setup-', dir=home.parent))
    try:
        os.chmod(staged, 0o700)
        keys = staged / 'operator';keys.mkdir(mode=0o700)
        keygen(keys / 'owner.pem', keys / 'owner.pub')
        public = (keys / 'owner.pub').read_text().strip()
        os.chmod(keys / 'owner.pub', 0o600)
        store = Store(staged / 'native-store', REPO)
        store.initialize(common.load(REPO / 'implementation/lab-runtime/v2/profile.json'),
                         store_id, 'role:definition-owner', public,
                         allowed_categories=['definition', 'artifact-instance'], allowed_effects=['admit'])
        data = store.replay(require_current=True)
        for directory in ['objects', 'receipts', 'operations']:(staged / directory).mkdir(mode=0o700)
        now = datetime.now(timezone.utc)
        grant = {'schema_version': 'cal.define.local-operator/v1', 'principal_ref': principal,
                 'identity_assurance': 'local-user-declared-at-explicit-provisioning', 'local_uid': os.getuid(),
                 'owner_ref': data['config']['owner_ref'], 'scope_ref': data['config']['scope_ref'],
                 'store_id': store_id, 'public_key': public, 'operations': OPERATIONS,
                 'repository_root': str(REPO), 'project_ref': data['projection']['state']['payload']['project_ref'],
                 'source_snapshot_digest': data['baseline']['snapshot_digest'],
                 'connector_manifest_sha256': sha(read(PACKAGE / 'runtime-manifest.json')),
                 'issued_at': now.isoformat(), 'expires_at': (now + timedelta(hours=hours)).isoformat(),
                 'repository_admission_effect': 'none', 'external_identity_verified': False}
        key = serialization.load_pem_private_key(read(keys / 'owner.pem', private=True), password=None)
        exclusive(staged / 'operator.json', encode(sign(grant, key)))
        fsync_dir(staged)
        publish_directory(staged, home)
    finally:
        if staged.exists():
            import shutil
            shutil.rmtree(staged)
    return Host(home).status()


class Host:
    def __init__(self, home, *, allow_expired=False):
        self.home = Path(home).absolute()
        require(self.home.resolve() == self.home and not self.home.is_symlink(), 'unsafe-operator-home', exit_code=3)
        st = self.home.stat()
        require(st.st_uid == os.getuid() and not st.st_mode & 0o077, 'unsafe-operator-home', exit_code=3)
        self.identity = (st.st_dev, st.st_ino)
        self.public = read(self.home / 'operator/owner.pub', private=True).decode().strip()
        self.grant_raw = read(self.home / 'operator.json', private=True)
        self.grant = verified(decode(self.grant_raw), self.public)
        self.store = Store(self.home / 'native-store', REPO)
        self.guard(allow_expired=allow_expired)

    def guard(self, operation=None, *, allow_expired=False):
        st = self.home.stat()
        require(self.home.resolve() == self.home and (st.st_dev, st.st_ino) == self.identity and
                st.st_uid == os.getuid() and not st.st_mode & 0o077, 'operator-home-changed', exit_code=3)
        require(read(self.home / 'operator.json', private=True) == self.grant_raw, 'operator-grant-changed', exit_code=3)
        g = self.grant
        require(g['repository_root'] == str(REPO) and g['local_uid'] == os.getuid() and
                g['public_key'] == self.public and g['repository_admission_effect'] == 'none', 'operator-binding-mismatch', exit_code=3)
        require(g['connector_manifest_sha256'] == sha(read(PACKAGE / 'runtime-manifest.json')), 'operator-successor-selection-required', exit_code=3)
        require(not (self.home / 'REVOKED').exists(), 'operator-revoked', exit_code=3)
        require(allow_expired or datetime.now(timezone.utc) < datetime.fromisoformat(g['expires_at']), 'operator-expired', exit_code=3)
        if operation:require(operation in g['operations'], 'operation-not-granted', exit_code=3)

    def data(self, operation):
        self.guard(operation)
        d = self.store.replay(require_current=True)
        g = self.grant
        require(d['config']['public_key'] == self.public and d['config']['scope_ref'] == g['scope_ref'] and
                d['config']['owner_ref'] == g['owner_ref'] and d['config']['store_id'] == g['store_id'] and
                d['baseline']['snapshot_digest'] == g['source_snapshot_digest'] and
                d['projection']['state']['payload']['project_ref'] == g['project_ref'], 'native-host-binding-mismatch', exit_code=3)
        return d

    def key(self):
        key = serialization.load_pem_private_key(read(self.home / 'operator/owner.pem', private=True), password=None)
        require(isinstance(key, Ed25519PrivateKey) and
                key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw).hex() == self.public,
                'operator-key-mismatch', exit_code=3)
        return key

    def status(self):
        d = self.data('context')
        return {'project_ref': self.grant['project_ref'], 'principal_ref': self.grant['principal_ref'],
                'scope_ref': self.grant['scope_ref'], 'head': d['head'], 'source_freshness': d['freshness']['status'],
                'operator_expires_at': self.grant['expires_at'], 'native_store': 'initialized',
                'permission_boundary': 'explicitly-provisioned-local-operator', 'repository_admission_effect': 'none',
                'canonical_release_qualified': False, 'authority_effect': 'none'}

    def context(self, definitions=('cal.definition.product',), ttl=900):
        d = self.data('context')
        session = Session(self.store, d['projection']['state']['node_id'], ttl=ttl)
        try:
            packet = session.context()
            selected = []
            for ref in definitions:
                row = resolve(d['projection']['subjects'], ref)
                require(row['category'] == 'definition' and row['effective_state'] in ('admitted-current', 'local-admitted-current'),
                        'definition-not-current', exit_code=3)
                raw = read(REPO / row['source']['path']) if row['effective_state'] == 'admitted-current' else common.encoded(row['record'])
                require(sha(raw) == row['source']['sha256'], 'definition-source-drift', exit_code=3)
                selected.append({'version_ref': row['version_ref'], 'identity': row['identity'],
                                 'effective_state': row['effective_state'], 'raw': raw,
                                 'carrier_ref': row['carrier_ref'] or row['record']['classification']['artifact_type_ref'],
                                 'record': row['record']})
            record = {'schema_version': 'cal.define.local-lab-context/v1', 'project_ref': self.grant['project_ref'],
                      'scope_ref': self.grant['scope_ref'], 'source_snapshot_digest': d['baseline']['snapshot_digest'],
                      'head': d['head']['transaction_digest'], 'state_ref': d['projection']['state']['node_id'],
                      'profile_sha256': sha(read(REPO / 'implementation/lab-runtime/v2/profile.json')),
                      'context_view': packet['context_view'], 'ontology_view': packet['ontology_view'],
                      'definition_bindings': [{'version_ref': s['version_ref'], 'sha256': sha(s['raw'])} for s in selected],
                      'grant_sha256': sha(self.grant_raw), 'expires_at': packet['context_view']['expires_at'],
                      'permission_boundary': 'local-source-read-only', 'authority_effect': 'none'}
            session.context();self.guard('context')
            return sign(record, self.key()), selected
        finally:session.close()

    def check_context(self, raw, *, current=True):
        c = verified(decode(raw), self.public)
        d = self.data('prepare' if current else 'reconstruct')
        require(c['schema_version'] == 'cal.define.local-lab-context/v1' and
                c['project_ref'] == self.grant['project_ref'] and c['scope_ref'] == self.grant['scope_ref'] and
                c['source_snapshot_digest'] == d['baseline']['snapshot_digest'] and
                c['grant_sha256'] == sha(self.grant_raw), 'context-host-mismatch', exit_code=3)
        if current:
            require(c['head'] == d['head']['transaction_digest'], 'stale-context-head', exit_code=3)
            require(datetime.now(timezone.utc) < datetime.fromisoformat(c['expires_at'].replace('Z', '+00:00')), 'context-expired', exit_code=3)
            require(c['state_ref'] == d['projection']['state']['node_id'] and
                    c['profile_sha256'] == sha(read(REPO / 'implementation/lab-runtime/v2/profile.json')),
                    'context-source-selection-mismatch', exit_code=3)
            for selected in c['definition_bindings']:
                row = resolve(d['projection']['subjects'], selected['version_ref'])
                require(row['version_ref'] == selected['version_ref'] and row['category'] == 'definition' and
                        row['effective_state'] in ('admitted-current', 'local-admitted-current') and
                        row['source']['sha256'] == selected['sha256'], 'context-definition-source-mismatch', exit_code=3)
        return c

    def renew(self, hours=24):
        self.guard(allow_expired=True)
        require(type(hours) is int and 1 <= hours <= 168, 'invalid-grant-period')
        data = self.store.replay(require_current=True)
        require(data['config']['public_key'] == self.public and data['config']['scope_ref'] == self.grant['scope_ref'] and
                data['baseline']['snapshot_digest'] == self.grant['source_snapshot_digest'], 'native-host-binding-mismatch', exit_code=3)
        now = datetime.now(timezone.utc)
        grant = {**self.grant, 'issued_at': now.isoformat(), 'expires_at': (now + timedelta(hours=hours)).isoformat()}
        common.atomic(self.home / 'operator.json', encode(sign(grant, self.key())))
        return Host(self.home).status()

    def prepare(self, input_root, output, *, permit_retention=False):
        request_raw = read(Path(input_root) / 'request.json', maximum=1048576)
        request = decode(request_raw)
        members = {}
        for b in bindings_in(request):
            raw = bound(input_root, b)
            require(members.setdefault(b['path'], raw) == raw, 'mixed-source-epochs')
        context = members.get('lab-context.json')
        require(context is not None and any(b['path'] == 'lab-context.json' for b in request['evidence_bindings']),
                'explicit-lab-context-required', exit_code=3)
        selected_context = self.check_context(context)
        expected = {row['version_ref']: row['sha256'] for row in selected_context['definition_bindings']}
        def references(value):
            if isinstance(value, dict):
                if value.get('kind') == 'external':yield value
                for key, item in value.items():
                    if key not in ('bindings', 'value_schema'):yield from references(item)
            elif isinstance(value, list):
                for item in value:yield from references(item)
        for ref in references(request):
            version = ref['identity'] + '@' + ref['revision']
            if version in expected:
                raw = members.get(ref['input_id'])
                require(raw is not None and sha(raw) == expected[version], 'context-definition-source-mismatch', exit_code=3)
        captured = invoke('capture', request_utf8=request_raw.decode(), inputs=encoded_members(members), permit_retention=permit_retention)
        prepared = invoke('prepare', request_utf8=request_raw.decode(), capture_utf8=captured['capture_utf8'], inputs=captured['inputs'])
        self.check_context(context)
        write_package(output, byte_members(prepared['package_members']))
        return {'root_sha256': prepared['root_sha256'], 'readiness': prepared['readiness'],
                'context_verified': True, 'capture_standing': 'standalone-reference-with-signed-local-context-evidence',
                'actual_owner_outcome': None, 'authority_effect': 'none'}

    def retain(self, package):
        d = self.data('retain');members = package_members(package)
        invoke('inspect', package_members=encoded_members(members))
        capture = decode(members['capture.json'])
        require(all(row['retention_posture'] == 'permitted' for row in capture['input_rows']), 'retention-not-permitted', exit_code=3)
        root = sha(members['manifest.json']);destination = self.home / 'objects' / root
        lock = os.open(self.home / '.custody.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(lock, fcntl.LOCK_EX)
            self.guard('retain')
            if not destination.exists():write_package(destination, members)
            require(package_members(destination) == members, 'retained-package-mismatch', exit_code=3)
            receipt_path = self.home / 'receipts' / (root + '.json')
            if receipt_path.exists():
                receipt = decode(read(receipt_path, private=True));verified(receipt, self.public)
            else:
                receipt = sign({'schema_version': 'cal.define.local-retention/v1', 'root_sha256': root,
                                'store_id': self.grant['store_id'], 'scope_ref': self.grant['scope_ref'],
                                'source_head': d['head']['transaction_digest'], 'member_count': len(members),
                                'retained_at': datetime.now(timezone.utc).isoformat(), 'authority_effect': 'none'}, self.key())
                exclusive(receipt_path, encode(receipt));fsync_dir(receipt_path.parent)
            require(receipt['root_sha256'] == root and receipt['scope_ref'] == self.grant['scope_ref'], 'retention-receipt-mismatch', exit_code=3)
            self.guard('retain')
            return {'root_sha256': root, 'locator': 'define-lab-retained:' + self.grant['store_id'] + ':' + root,
                    'receipt_sha256': sha(encode(receipt)), 'member_count': len(members), 'authority_effect': 'none'}
        finally:os.close(lock)

    def review(self, package, output, proposal_id):
        require(re.fullmatch(r'[a-zA-Z0-9-]{1,80}', proposal_id), 'invalid-proposal-id')
        d = self.data('review');members = package_members(package)
        self.check_context(members.get('inputs/lab-context.json', b''))
        materialized = invoke('materialize', package_members=encoded_members(members))
        definitions = byte_members(materialized['members'])
        retention = self.retain(package)
        scope, owner = self.grant['scope_ref'], self.grant['owner_ref']
        targets, mapping, originals = [], [], {}
        for path, raw in sorted(definitions.items()):
            if not path.endswith('/definition.json'):continue
            body = decode(raw)
            require(body['semantic_owner_ref'] == owner, 'definition-owner-route-mismatch', exit_code=3)
            selection = next(s for s in decode(members['pack.json'])['materialization_selection']
                             if s['definition_binding']['sha256'] == sha(raw))
            require(selection['identity_intention'] == 'new-identity' and selection['owner_route'] == owner,
                    'unsupported-owner-or-successor-route', exit_code=4)
            version = body['definition_id'] + '@' + body['version']
            targets.append({'category': 'definition', 'operation': 'admit', 'version_ref': version,
                            'carrier_ref': 'cal.artifact-type.definition/v2', 'record': body,
                            'predecessor_ref': None, 'decision_ref': 'decision:define-lab:' + proposal_id + ':' + str(len(targets)), 'contract': None})
            mapping.append({'version_ref': version, 'original_binding': binding(raw, path),
                            'native_binding': binding(common.encoded(body), 'native-records/' + str(len(targets) - 1) + '.json'),
                            'transformation': 'explicit-original-JSON-to-native-record; original retained unchanged'})
            originals[path] = raw
        require(bool(targets), 'no-materialized-definitions')
        source_id = 'source:define-lab:' + proposal_id
        work_id = 'work:define-lab:' + proposal_id
        def envelope(kind, identity):
            return {'schema_version': 'cyberalchemy-lab-' + kind + '/v1', 'node_id': identity, 'kind': kind,
                    'name': 'Define retained ' + kind + ': ' + proposal_id, 'lifecycle_state': 'candidate',
                    'authority_effect': 'none', 'owner_ref': owner, 'scope_ref': scope, 'challenge_route': d['config']['challenge_route'],
                    'evidence_refs': ['sha256:' + retention['root_sha256']], 'successor_refs': [],
                    'claim_ceiling': 'Explicit local integration record; no canonical repository admission or semantic fidelity acceptance.'}
        source = envelope('source', source_id)
        source['payload'] = {'source_kind': 'define-pack/v3', 'locator': retention['locator'],
                             'content_digest': 'sha256:' + retention['root_sha256'], 'captured_at': datetime.now(timezone.utc).isoformat(),
                             'provenance_refs': ['define-retention-receipt:sha256:' + retention['receipt_sha256']]}
        source['relation_refs'] = [{'counterpart_kind': 'definition', 'counterpart_ref': targets[0]['record']['definition_id'],
                                   'direction': 'target', 'relation_kind_ref': 'relation.originates-from'}]
        work = envelope('work', work_id)
        work['payload'] = {'project_ref': self.grant['project_ref'], 'completion_state': 'candidate-complete',
                           'goal_refs': ['goal:define-lab-integration'], 'input_refs': [d['projection']['state']['node_id']],
                           'output_refs': [source_id + '@candidate.1'],
                           'work_statement': 'Prepare and retain the User Journey candidate for local integration testing; semantic admission is separate.'}
        work['relation_refs'] = [{'counterpart_kind': 'project', 'counterpart_ref': self.grant['project_ref'],
                                 'direction': 'source', 'relation_kind_ref': 'relation.member-of'}]
        for body in [source, work]:
            targets.append({'category': 'artifact-instance', 'operation': 'admit', 'version_ref': body['node_id'] + '@candidate.1',
                            'carrier_ref': 'cal.artifact-type.' + body['kind'] + '/v1', 'record': body, 'predecessor_ref': None,
                            'decision_ref': 'decision:define-lab:' + proposal_id + ':' + str(len(targets)), 'contract': None})
        proposal = {'schema_version': 'lab-runtime-proposal/v1', 'proposal_id': proposal_id,
                    'expected_head': d['head']['transaction_digest'], 'source_snapshot_digest': d['baseline']['snapshot_digest'],
                    'scope_ref': scope, 'policy_ref': d['config']['policy_ref'], 'challenge_route': d['config']['challenge_route'],
                    'targets': targets, 'schemas': {}}
        result = self.store.review(proposal)
        self.check_context(members['inputs/lab-context.json'])
        write_package(output, {'proposal.json': common.encoded(proposal), 'review.json': encode(result),
                               'mapping.json': encode({'schema_version': 'cal.define.native-v3-mapping/v1', 'definitions': mapping,
                                                       'retention': retention, 'work_ref': work_id + '@candidate.1', 'authority_effect': 'none'}),
                               **{'originals/' + path: raw for path, raw in originals.items()},
                               **{'native-records/' + str(i) + '.json': common.encoded(t['record'])
                                  for i, t in enumerate(targets)},
                               **{'materialized/' + path: raw for path, raw in definitions.items()}})
        return {'target_count': result['target_count'], 'proposal_digest': result['proposal_digest'],
                'approval_required': True, 'work_ref': work_id + '@candidate.1', 'retention': retention,
                'actual_owner_outcome': None, 'authority_effect': 'none'}

    def authorize(self, proposal, output):
        self.data('authorize')
        p = decode(read(proposal))
        require(all(t['category'] in ('definition', 'artifact-instance') for t in p['targets']), 'unsupported-local-effect', exit_code=3)
        approval = self.store.authorize(p, self.home / 'operator/owner.pem')
        self.guard('authorize')
        write_package(output, {'approval.json': common.encoded(approval)})
        return {'proposal_digest': approval['proposal_digest'], 'scope_ref': approval['scope_ref'],
                'posture': 'signed-exact-local-effects', 'repository_admission_effect': 'none', 'authority_effect': 'none'}

    def apply(self, proposal, approval):
        self.data('apply')
        result = self.store.apply(decode(read(proposal)), decode(read(approval)))
        return {'transaction_digest': result['transaction_digest'], 'idempotent': result['idempotent'],
                'posture': 'local-native-commit', 'repository_admission_effect': 'none', 'authority_effect': 'none'}

    def reconstruct(self, work_ref, output):
        d = self.data('reconstruct')
        work = resolve(d['projection']['subjects'], work_ref)
        require(work['version_ref'] == work_ref and work['kind'] == 'work' and work['effective_state'] == 'local-admitted-current',
                'exact-committed-work-required', exit_code=3)
        require(work['record']['scope_ref'] == self.grant['scope_ref'] and
                work['record']['payload']['project_ref'] == self.grant['project_ref'], 'work-project-mismatch', exit_code=3)
        outputs = work['record']['payload']['output_refs'];require(len(outputs) == 1, 'single-retained-source-required', exit_code=4)
        source = resolve(d['projection']['subjects'], outputs[0])
        require(source['version_ref'] == outputs[0] and source['kind'] == 'source' and source['effective_state'] == 'local-admitted-current' and
                source['record']['scope_ref'] == self.grant['scope_ref'], 'exact-committed-source-required', exit_code=3)
        payload = source['record']['payload']
        match = re.fullmatch(r'define-lab-retained:([a-z][a-z0-9-]{0,63}):([a-f0-9]{64})', payload['locator'])
        require(match is not None and match[1] == self.grant['store_id'] and payload['content_digest'] == 'sha256:' + match[2],
                'retained-source-binding-mismatch', exit_code=3)
        root = match[2]
        receipt_raw = read(self.home / 'receipts' / (root + '.json'), private=True)
        receipt = verified(decode(receipt_raw), self.public)
        require(payload['provenance_refs'] == ['define-retention-receipt:sha256:' + sha(receipt_raw)] and
                receipt['root_sha256'] == root and receipt['scope_ref'] == self.grant['scope_ref'], 'retention-receipt-mismatch', exit_code=3)
        members = package_members(self.home / 'objects' / root)
        require(sha(members['manifest.json']) == root, 'retained-root-mismatch', exit_code=3)
        restored = invoke('reconstruct', package_members=encoded_members(members))
        require(self.data('reconstruct')['head'] == d['head'], 'changed-head-during-reconstruction', exit_code=3)
        write_package(output, byte_members(restored['package_members']))
        return {'work_ref': work_ref, 'root_sha256': root, 'member_count': len(members),
                'posture': 'exact-frozen-reconstruction-from-committed-local-work',
                'session_memory_restored': False, 'current_semantic_use_authorized': False, 'authority_effect': 'none'}
