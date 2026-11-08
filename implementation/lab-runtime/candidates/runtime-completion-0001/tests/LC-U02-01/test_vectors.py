"""Independent Python oracle for the actual Rust wire codec; fixture keys only."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import unittest

sys.dont_write_bytecode = True
R = Path('/home/vlad_/projects/CyberAlchemy-lab')
S = R / 'implementation/lab-runtime/candidates/runtime-completion-0001'
E = R / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U02-01'
OLD = E.parent / 'LC-U01-02'
PREFIX = OLD / 'python-bytecode-cache-disabled-0002'
DEP = R / 'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/deps'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def stable(path, digest, maximum=128 * 1024 * 1024):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_size > maximum:
            raise ValueError('selected input type/size')
        raw = bytearray()
        while len(raw) <= maximum:
            part = os.read(fd, min(1048576, maximum + 1 - len(raw)))
            if not part:
                break
            raw.extend(part)
        after = os.fstat(fd)
        if (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns) != (
                after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise ValueError('selected input changed')
        if len(raw) > maximum or sha(raw) != digest:
            raise ValueError('selected input digest')
        return bytes(raw)
    finally:
        os.close(fd)


stable(PREFIX, 'a5712f1655f68e6f8fe7cacbfb454dc0be0cd1ad8f22f1788fbad7b8adafae29', 58)
if not sys.flags.no_site or not sys.dont_write_bytecode or os.environ.get('PYTHONPYCACHEPREFIX') != str(PREFIX):
    raise ValueError('guarded Python required')
# The accepted predecessor independently selected these import bytes. No new
# package installation, ambient sys.path, or self-issued module enrollment.
selected = json.loads(stable(OLD / 'coordinator-dispatch-0002.json',
    '478e5ab1966aabe8c758121d51543b8366d8eb38558da54b9c3405fda2346864'))
IMPORTS = []
for b in selected['source_bindings']:
    if b['root_id'] == 'repository':
        p = R / b['relative_path']
        if p.is_relative_to(DEP) or p.is_relative_to(S / 'contracts'):
            stable(p, b['sha256'])
            IMPORTS.append((p, b['sha256']))
if not IMPORTS:
    raise ValueError('empty selected import closure')
sys.path[:0] = [str(S / 'contracts'), str(DEP)]
from lab_contracts.codec import canonical, parse, signing_bytes
from lab_contracts.validation import validate
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

KEY = Ed25519PrivateKey.from_private_bytes(bytes([7]) * 32)
BINARY = None
BINARY_SHA = None


def binding(raw, path='selected.json'):
    return {'kind': 'evidence', 'root_id': 'owned-root', 'relative_path': path,
            'sha256': sha(raw), 'size_bytes': len(raw)}


def content(raw):
    return {'schema_version': 'lab-completion-content-digest/v1', 'sha256': sha(raw), 'size_bytes': len(raw)}


def sign(payload):
    unsigned = {'issuer_ref': 'fixture-issuer', 'payload': payload}
    return dict(unsigned, signature=KEY.sign(canonical(unsigned)).hex())


def auth_core(request):
    # Closed, explicit list agrees with the selected normative core, without
    # stripping arbitrary fields from a caller-controlled object.
    names = ('request_id', 'operation_id', 'sequence', 'activation_binding', 'store_id',
             'instance_id', 'slot_epoch', 'principal_ref', 'verb', 'intent_binding', 'payload')
    return dict(schema_version='lab-completion-message-authorization-core/v1',
                request_schema_version=request['schema_version'], **{k: request[k] for k in names})


def fixture(data=b'abc'):
    scope = dict(principal_ref='fixture-principal', scope_ref='fixture-scope', operation='produce',
        store_id='fixture-store', instance_id='fixture-instance', activation_binding=binding(b'activation'),
        slot_epoch=1, intent_binding=binding(b'intent', 'intent.json'))
    limits = dict(max_total_bytes=65536, max_actions=64, max_frame_bytes=65536, max_chunk_bytes=32768)
    slots = [dict(root_id='owned-root', member='payload.bin', preimage_binding=None, max_bytes=65536)]
    basis = sign(dict(schema_version='lab-completion-effect-authority-basis/v1', basis_id='basis',
                     scope=scope, limits=limits, output_slots=slots, not_before=1, expires_at=100))
    core = dict(schema_version='lab-completion-operation-request-core/v1', operation_id='operation-1',
        idempotency_key='idempotency-1', original_request_binding=binding(b'request', 'request.json'),
        semantic_target_binding=binding(b'target', 'target.json'), source_cut_binding=binding(b'cut', 'cut.json'),
        effect_selection_binding=binding(b'effect', 'effect.json'), authority_basis_binding=content(canonical(basis)),
        scope=scope, limits=limits, output_slots=slots, operation_expires_at=90)
    request = dict(schema_version='lab-completion-broker-request/v1', request_id='request-1',
        operation_id='operation-1', sequence=0, activation_binding=scope['activation_binding'],
        store_id=scope['store_id'], instance_id=scope['instance_id'], slot_epoch=1,
        principal_ref=scope['principal_ref'], verb='write_member', intent_binding=scope['intent_binding'],
        authorization_binding=content(b''), payload=dict(root_id='owned-root', member='payload.bin',
            preimage_binding=None, full_sha256=sha(data), full_length=len(data), offset=0, length=len(data),
            chunk_sha256=sha(data), bytes_base64=base64.b64encode(data).decode()))
    grant = dict(kind='member', root_id='owned-root', stage_binding=binding(b'stage', 'stage.json'),
        member='payload.bin', preimage_binding=None, full_sha256=sha(data), full_length=len(data),
        chunk_size=max(1, len(data)), sequence_start=0,
        chunks=[dict(sequence=0, offset=0, length=len(data), core_sha256=sha(signing_bytes(auth_core(request))))])
    permit = sign(dict(schema_version='lab-completion-broker-permit/v1', permit_id='permit',
        operation_fingerprint=sha(signing_bytes(core)), basis_binding=core['authority_basis_binding'],
        scope=scope, limits=limits, allowed_verb='write_member', allowed_phase='staging',
        not_before=1, expires_at=80, grant=grant))
    request['authorization_binding'] = content(canonical(permit))
    frame = dict(schema_version='lab-completion-broker-frame/v1', request=request, permit=permit)
    return frame, basis, core


def run_vectors(raws, frame=False):
    stable(BINARY, BINARY_SHA)
    child = subprocess.run([str(BINARY)] + (['--frame'] if frame else []),
        input=b'\n'.join(raws) + b'\n', stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=15, env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'}, check=True)
    if len(child.stdout) > 4 * 1024 * 1024 or child.stderr:
        raise ValueError('vector output bound')
    stable(BINARY, BINARY_SHA)
    return [json.loads(row) for row in child.stdout.splitlines()]


class WireVectors(unittest.TestCase):
    def test_full_closed_request_response_and_ed25519_bytes(self):
        for data in (b'', b'abc', bytes(range(256)) * 128):
            frame, basis, core = fixture(data)
            raw = canonical(frame)
            self.assertLessEqual(len(raw), 65536)
            rows = run_vectors([raw], frame=True)
            self.assertEqual(len(rows), 1)
            row = rows[0]
            self.assertTrue(row['ok'])
            self.assertEqual(row['frame_sha256'], sha(raw))
            self.assertEqual(bytes.fromhex(row['authorization_core_hex']), canonical(auth_core(frame['request'])))
            result = binding(b'fixture-result', 'result.json')
            receipt = sign(dict(schema_version='lab-completion-broker-response/v1', request_digest=sha(raw),
                operation_id='operation-1', sequence=0, durable_phase='staging', status='PASS', error=None,
                result_binding=result))
            self.assertEqual(bytes.fromhex(row['receipt_hex']), canonical(receipt))
            KEY.public_key().verify(bytes.fromhex(receipt['signature']), canonical({k: receipt[k] for k in ('issuer_ref', 'payload')}))
            for b in (core['source_cut_binding'], frame['request']['activation_binding'], result):
                validate('ByteBinding', b)

    def test_full_domain_records_and_adapter_formats(self):
        frame, basis, core = fixture()
        scope = core['scope']
        disclosure = dict(schema_version='lab-completion-broker-disclosure-permit/v1', authorization_id='fresh',
            operation_id='operation-1', operation_fingerprint=sha(signing_bytes(core)), scope=scope,
            allowed_verb='inspect', message_core_sha256=sha(b'exact-message'), subject_binding=binding(b'receipt'),
            not_before=110, expires_at=150, max_output_bytes=4096)
        recovery = dict(disclosure, schema_version='lab-completion-recovery-authorization/v1', allowed_verb='close_family',
            observed_phase='terminal', action='close_family', preimages=[binding(b'receipt')], next_sequence=1,
            next_offset=3, cumulative_bytes=3, cumulative_actions=1, original_deadline=90)
        del recovery['max_output_bytes']
        challenge = dict(schema_version='lab-context-host-challenge/v1-candidate', host_instance_ref='fixture-host',
            connection_ref='fixture-connection', nonce='01' * 32, policy_sha256='02' * 32,
            expires_at='2026-10-18T12:00:00Z', authority_effect='none')
        pub = KEY.public_key().public_bytes_raw()
        owner = dict(schema_version='lab-completion-issuer-enrollment/v1', issuer_ref='fixture-issuer',
            adapter='owner-hex-v1', purpose='broker-intent', algorithm='ed25519', public_key=pub.hex(), trust_domain='fixture')
        custody = dict(owner, adapter='custody-challenge-base64-v1', purpose='transport-authentication',
                       public_key=base64.b64encode(pub).decode())
        values = [basis['payload'], core, frame['permit']['payload'], auth_core(frame['request']),
                  disclosure, recovery, challenge, owner, custody, content(b'inline')]
        rows = run_vectors([canonical(v) for v in values])
        self.assertEqual(len(rows), len(values))
        for v, row in zip(values, rows):
            self.assertTrue(row['ok'])
            self.assertEqual(bytes.fromhex(row['hex']), signing_bytes(v))
            self.assertEqual(bytes.fromhex(row['envelope_hex']), canonical(sign(v)))
        self.assertNotEqual(KEY.sign(canonical(challenge)), KEY.sign(canonical({'issuer_ref': 'fixture-issuer', 'payload': challenge})))

    def test_closed_frame_and_locator_substitution_refuse(self):
        frame, _, _ = fixture()
        variants = []
        for edit in ('extra', 'two-field', 'content-as-source', 'traversal', 'permit-change', 'unknown-version'):
            v = json.loads(canonical(frame))
            if edit == 'extra': v['request']['command'] = 'arbitrary-code'
            elif edit == 'two-field': v['request']['activation_binding'] = {'sha256': sha(b'activation'), 'size_bytes': 10}
            elif edit == 'content-as-source': v['request']['activation_binding'] = content(b'activation')
            elif edit == 'traversal': v['request']['payload']['member'] = '../foreign'
            elif edit == 'permit-change': v['permit']['payload']['permit_id'] = 'changed'
            else: v['request']['schema_version'] = 'unknown/v2'
            variants.append(canonical(v))
        self.assertTrue(all(not row['ok'] for row in run_vectors(variants, frame=True)))

    def test_duplicate_numeric_unicode_and_noncanonical_wire_refuse(self):
        bad = [b'{"schema_version":"v1","x":1,"x":2}', b'{"schema_version":"v1","x":-0}',
            b'{"schema_version":"v1","x":1.0}', b'{"schema_version":"v1","x":9223372036854775808}',
            b'{"schema_version":"v1","x":"\\ud800"}', b'{"schema_version":"v1","x":NaN}']
        self.assertTrue(all(not row['ok'] for row in run_vectors(bad)))
        frame, _, _ = fixture()
        self.assertFalse(run_vectors([json.dumps(frame).encode()], frame=True)[0]['ok'])
        good = [{'schema_version': 'vector/v1', 'é': '😀é\b\f\n\r\t\x00\x1f/\\"',
                 'i': [-9223372036854775808, 9223372036854775807]}]
        row = run_vectors([canonical(good[0])])[0]
        self.assertEqual(bytes.fromhex(row['hex']), canonical(good[0]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--binary-sha', required=True)
    args = parser.parse_args()
    BINARY, BINARY_SHA = args.binary, args.binary_sha
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(WireVectors))
    for path, digest in IMPORTS:
        stable(path, digest)
    print(json.dumps({'schema_version': 'lab-case-command-result/v1', 'result': 'PASS' if result.wasSuccessful() else 'FAIL',
        'checks': result.testsRun, 'effect_state': 'owned-inert', 'cleanup': 'clean'}))
    raise SystemExit(0 if result.wasSuccessful() else 1)
