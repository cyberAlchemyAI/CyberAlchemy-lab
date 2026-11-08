"""Private data transport is closed, exact and independent of old native roots."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import inputs as I
class Inputs(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='cal-origin-data-test-');self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.bundle=self.root/'bundle.json'
        I.package(Path.home()/'.local/share/cyberalchemy-lab/t22-retained-native-origin71-0001',self.bundle)
    def test_exact_bundle_provisions_without_old_signer_or_runtime_and_retry_is_readonly(self):
        destination=self.root/'private'/'qualification'/'t22-origin71';r=I.provision(self.bundle,destination)
        self.assertEqual(r['result'],'provisioned-exact-fixture-origin');self.assertTrue(r['no_old_signer_or_runtime_required'])
        rows=I.load(destination);self.assertEqual({n:I.sha(raw) for n,raw in rows.items()},I.PINS)
        before={p.name:p.read_bytes() for p in destination.iterdir()};self.assertEqual(I.provision(self.bundle,destination)['result'],'already-provisioned-exact-fixture-origin')
        self.assertEqual(before,{p.name:p.read_bytes() for p in destination.iterdir()})
    def test_changed_payload_refused_before_destination_creation(self):
        body=json.loads(self.bundle.read_bytes());body['originals_base64']['native-candidate.json']='e30='
        self.bundle.write_bytes(I.enc(body))
        with self.assertRaisesRegex(ValueError,'payload changed'):I.provision(self.bundle,self.root/'bad')
        self.assertFalse((self.root/'bad').exists())
    def test_extra_member_cannot_transport_a_signer_or_unknown_file(self):
        body=json.loads(self.bundle.read_bytes());body['originals_base64']['reader.pem']='private'
        self.bundle.write_bytes(I.enc(body))
        with self.assertRaisesRegex(ValueError,'closed classified'):I.provision(self.bundle,self.root/'bad')
    def test_public_mode_or_symlink_bundle_refused(self):
        self.bundle.chmod(0o644)
        with self.assertRaisesRegex(ValueError,'private bounded'):I.provision(self.bundle,self.root/'bad')
        self.bundle.chmod(0o600);link=self.root/'linked';link.symlink_to(self.bundle)
        with self.assertRaisesRegex(ValueError,'linked origin'):I.provision(link,self.root/'bad')
    def test_changed_installed_original_never_becomes_idempotent_success(self):
        destination=self.root/'private';I.provision(self.bundle,destination)
        changed=destination/'native-request.json';changed.write_bytes(changed.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'original bytes changed'):I.provision(self.bundle,destination)
    def test_only_exact_audited_public_seed_may_be_readable(self):
        seed=self.root/'public-seed.json'
        I.package(Path.home()/'.local/share/cyberalchemy-lab/t22-retained-native-origin71-0001',seed,public_seed=True)
        self.assertEqual(I.sha(seed.read_bytes()),I.PUBLIC_SEED_SHA);seed.chmod(0o644)
        destination=self.root/'private-seeded';I.provision(seed,destination)
        self.assertEqual(destination.stat().st_mode&0o777,0o700)
        self.assertTrue(all(p.stat().st_mode&0o777==0o600 for p in destination.iterdir()))
        seed.write_bytes(seed.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'exact audited public seed'):I.provision(seed,self.root/'refused')
if __name__=='__main__':unittest.main()
