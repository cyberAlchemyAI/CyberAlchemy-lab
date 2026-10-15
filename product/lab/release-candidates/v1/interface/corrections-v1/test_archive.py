"""Cold original-byte archives reject substituted pins, closure and signatures."""
import unittest
from episode import *


class ArchiveGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pins=EnginePins(**parse((HERE/'pins.json').read_bytes()))
        cls.archive_value=parse((EXAMPLES/'0004/branch.snapshot').read_bytes())
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='cal-R03-archive-guards-');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.value=copy.deepcopy(self.archive_value)
    def attempt(self,*,expected_sha=None,pins=None):
        path=self.root/'archive.json';path.write_bytes(encoded(self.value))
        return restore(path,expected_sha or sha(path.read_bytes()),self.root/'restored',pins or self.pins)
    def reject(self,**kwargs):
        with self.assertRaises(Exception):self.attempt(**kwargs)
    def alter_document(self,name,change):
        entry=self.value['files'][name];value=parse(base64.b64decode(entry['base64_original_bytes']));change(value)
        raw=encoded(value);entry.update(sha256=sha(raw),base64_original_bytes=base64.b64encode(raw).decode())
    def test_independent_archive_pin_required(self):self.reject(expected_sha='0'*64)
    def test_independent_executable_pin_required(self):
        wrong=EnginePins('0'*64,self.pins.engine_id,self.pins.mapping_sha256,self.pins.profile_sha256,self.pins.correction_profile_sha256)
        self.reject(pins=wrong)
    def test_changed_original_bytes_without_hash_update_rejected(self):
        self.value['files']['HEAD.json']['base64_original_bytes']=base64.b64encode(b'{}\n').decode();self.reject()
    def test_missing_committed_transaction_rejected(self):self.value['files'].pop('transactions/0000000002.json');self.reject()
    def test_unknown_future_transaction_rejected(self):
        self.value['files']['transactions/0000000003.json']=copy.deepcopy(self.value['files']['transactions/0000000002.json']);self.reject()
    def test_private_key_entry_rejected(self):self.value['files']['owner.pem']={'sha256':sha(b'fake'),'base64_original_bytes':base64.b64encode(b'fake').decode()};self.reject()
    def test_traversal_entry_rejected(self):self.value['files']['../escape.json']=self.value['files'].pop('HEAD.json');self.reject()
    def test_changed_configuration_pin_rejected(self):
        self.alter_document('config.json',lambda d:d['authorized_domain_scope_refs'].append('scope:other'));self.reject()
    def test_changed_baseline_pin_rejected(self):self.value['baseline_snapshot_digest']='0'*64;self.reject()
    def test_changed_head_pin_rejected(self):self.value['expected_head']='0'*64;self.reject()
    def test_changed_transaction_approval_rejected(self):
        self.alter_document('transactions/0000000002.json',lambda d:d['approval'].update(signature='0'*128));self.reject()
    def test_changed_signed_record_rejected(self):
        self.alter_document('transactions/0000000002.json',lambda d:d['proposal']['targets'][0]['record'].update(name='forged'));self.reject()


if __name__=='__main__':unittest.main()
