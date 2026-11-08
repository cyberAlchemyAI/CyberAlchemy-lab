"""Real native helpers in isolated local scopes; no canonical admission."""
import copy
from datetime import datetime, timedelta, timezone
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE))
from define_lab.bootstrap import integrity
integrity()
from define_lab.host import Host, setup, sign, package_members
from define_lab.example import author
from define_core.exact import Refusal, decode, encode, read, sha
from lab_runtime.common import RuntimeFault


class Connector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='define-lab-qualification-')
        cls.root = Path(cls.tmp.name)
        cls.home = cls.root / 'operator'
        setup(cls.home, 'principal:connector-test', store_id='connector-test')
        cls.host = Host(cls.home)
        cls.input = cls.root / 'input';author(cls.host, cls.input)
        cls.package = cls.root / 'package';cls.host.prepare(cls.input, cls.package, permit_retention=True)

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def test_01_exact_native_roundtrip_and_fresh_process(self):
        review = self.root / 'review'
        result = self.host.review(self.package, review, 'user-journey-test')
        self.assertEqual(result['target_count'], 3)
        self.assertTrue(result['approval_required'])
        self.assertIsNone(result['actual_owner_outcome'])
        proposal = review / 'proposal.json'
        self.assertEqual(self.host.store.replay()['head']['sequence'], 0)
        approved = self.root / 'approval';self.host.authorize(proposal, approved)
        first = self.host.apply(proposal, approved / 'approval.json')
        self.assertFalse(first['idempotent'])
        again = self.host.apply(proposal, approved / 'approval.json')
        self.assertTrue(again['idempotent'])
        self.assertEqual(first['transaction_digest'], again['transaction_digest'])
        restored = self.root / 'restored'
        proc = subprocess.run([sys.executable, '-I', '-B', str(PACKAGE / 'define.py'), 'reconstruct',
                               '--home', str(self.home), '--work', result['work_ref'], '--output', str(restored)],
                              capture_output=True, timeout=90)
        self.assertEqual(proc.returncode, 0, proc.stdout.decode())
        self.assertEqual(package_members(self.package), package_members(restored))
        self.assertFalse(decode(proc.stdout)['result']['session_memory_restored'])
        context, selected = self.host.context(['cal.definition.user-journey'])
        self.assertEqual(selected[0]['effective_state'], 'local-admitted-current')
        self.assertEqual(context['project_ref'], self.host.grant['project_ref'])

    def test_02_stale_context_cannot_prepare(self):
        with self.assertRaisesRegex(Refusal, 'stale-context-head'):
            self.host.prepare(self.input, self.root / 'stale-package')
        self.assertFalse((self.root / 'stale-package').exists())

    def test_context_signature_expiry_and_cross_host_refuse(self):
        context, _ = self.host.context()
        changed = copy.deepcopy(context);changed['project_ref'] = 'project:other'
        with self.assertRaisesRegex(Refusal, 'signature-invalid'):self.host.check_context(encode(changed))
        core = {k: v for k, v in context.items() if k != 'signature'}
        core['expires_at'] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        with self.assertRaisesRegex(Refusal, 'context-expired'):self.host.check_context(encode(sign(core, self.host.key())))
        other = self.root / 'other-operator';setup(other, 'principal:other', store_id='other-test')
        with self.assertRaisesRegex(Refusal, 'signature-invalid'):Host(other).check_context(encode(context))

    def test_existing_destinations_and_revocation_refuse(self):
        context, _ = self.host.context()
        from define_core.exact import write_package
        with self.assertRaises(Refusal):write_package(self.input, {'changed.json': b'{}\n'})
        revoked = self.home / 'REVOKED';revoked.write_text('qualification revocation\n')
        try:
            with self.assertRaisesRegex(Refusal, 'operator-revoked'):Host(self.home)
        finally:revoked.unlink()

    def test_altered_grant_and_receipt_refuse(self):
        path = self.home / 'operator.json';original = read(path, private=True)
        changed = decode(original);changed['operations'].append('ungranted-effect')
        path.write_bytes(encode(changed))
        try:
            with self.assertRaisesRegex(Refusal, 'signature-invalid'):Host(self.home)
        finally:path.write_bytes(original)
        root = sha(package_members(self.package)['manifest.json'])
        receipt = self.home / 'receipts' / (root + '.json');original = read(receipt, private=True)
        changed = decode(original);changed['root_sha256'] = 'f' * 64;receipt.write_bytes(encode(changed))
        try:
            with self.assertRaises(Refusal):self.host.reconstruct('work:define-lab:user-journey-test@candidate.1', self.root / 'bad-receipt')
        finally:receipt.write_bytes(original)

    def test_retention_requires_explicit_rights_and_context_binds_source_bytes(self):
        from define_core.exact import binding
        source = self.root / 'retention-input';author(self.host, source)
        destination = self.root / 'unpermitted-package'
        self.host.prepare(source, destination)
        with self.assertRaisesRegex(Refusal, 'retention-not-permitted'):self.host.retain(destination)
        body_path = source / 'product-definition.json';body_path.write_bytes(read(body_path) + b' ')
        request_path = source / 'request.json';request = decode(read(request_path))
        request['source_bindings'][0] = binding(read(body_path), 'product-definition.json')
        request_path.write_bytes(encode(request))
        with self.assertRaisesRegex(Refusal, 'context-definition-source-mismatch'):
            self.host.prepare(source, self.root / 'mixed-source-package', permit_retention=True)

    def test_operator_expiry_and_explicit_renewal(self):
        home = self.root / 'renewable-operator';setup(home, 'principal:renewal-test', store_id='renewal-test')
        host = Host(home);grant = copy.deepcopy(host.grant)
        grant['expires_at'] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        (home / 'operator.json').write_bytes(encode(sign(grant, host.key())))
        with self.assertRaisesRegex(Refusal, 'operator-expired'):Host(home)
        expired = Host(home, allow_expired=True)
        with self.assertRaisesRegex(Refusal, 'operator-expired'):expired.status()
        self.assertEqual(expired.renew(1)['native_store'], 'initialized')


if __name__ == '__main__':unittest.main()
