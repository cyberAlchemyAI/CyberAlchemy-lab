"""Real native-origin bytes/Ed25519 checks; no API authentication is inferred."""
import ast
import base64
import copy
from datetime import datetime,timedelta,timezone
import json
from pathlib import Path
import sys
import unittest
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001/deps'),str(HERE)]
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
import inputs as I
def component_module(path,bindings):
    # Only the top-level relative import binding is replaced by this component
    # harness; every real signature/schema/helper method runs unchanged.
    tree=ast.parse(path.read_bytes());tree.body=[n for n in tree.body if not (isinstance(n,ast.ImportFrom) and n.level)]
    scope={'__file__':str(path),'__name__':'_retained_origin_component',**bindings};exec(compile(tree,str(path),'exec'),scope);return scope
Rdict=component_module(ROOT/'product/lab/release-candidates/v1/interface/api-integration-v75-current-fixtures-0001/fixture_resolution_source.py',{'ROOT':ROOT})
from types import SimpleNamespace
R=SimpleNamespace(**Rdict)
source=SimpleNamespace(require=I.need,sha=I.sha)
F=component_module(HERE/'postimages-0001/fixture_resolution_handler.py',{'R':R,'ROOT':ROOT,'source':source,'compact':I.enc,'binding':lambda ref,raw:{'ref':ref,'sha256':I.sha(raw)}})

class Origin(unittest.TestCase):
    def setUp(self):
        rows=I.load(Path.home()/'.local/share/cyberalchemy-lab/t22-retained-native-origin71-0001');self.rows=rows
        self.now=datetime.now(timezone.utc);self.key=Ed25519PrivateKey.generate();self.public=self.key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw).hex()
        self.sub=json.loads(rows['native-submission.json']);self.obs=json.loads(rows['native-call-observation.json']);self.request=json.loads(rows['native-request.json'])
        self.cap=self.build(self.now);self.outer=copy.deepcopy(self.sub['source_cut']);self.outer['store_ref']='synthetic-current-coordinating-store';self.outer['commit_sha256']='a'*64
        self.obj=object.__new__(F['FixtureResolution']);self.obj.retained=I.wrapper(self.cap,rows,self.outer);self.obj.capsule=self.cap;self.obj.raw=R.canon(self.obj.retained)
    def build(self,time):
        return R.build(submission=self.sub,observation=self.obs,candidate_raw=self.rows['native-candidate.json'],request=self.request,
          now=time,period_end=(self.now+timedelta(hours=3)).isoformat(),signing_key=self.key,fixture_principal_ref='principal:component-fixture-only')
    def verify(self):self.obj.verify_origin(self.public,self.outer,self.now)
    def repin_wrapper(self):self.obj.raw=R.canon(self.obj.retained)
    def test_real_native_origin_and_fresh_different_coordinating_cut_remain_separate(self):
        self.verify();self.assertEqual(self.obj.retained_original('work'),self.rows['original-work.json'])
        self.assertEqual(self.obj.retained_original('challenge-contract'),self.rows['original-contract.json'])
        self.assertEqual(self.obj.capsule['original_request'],self.request);self.assertNotEqual(self.outer,self.cap['envelope']['payload']['source_cut'])
    def test_original_strict_same_cut_branch_is_not_broadened(self):
        self.obj.retained=None;self.obj.capsule=self.cap
        with self.assertRaises(ValueError):self.verify()
        self.obj.verify_origin(self.public,self.sub['source_cut'],self.now)
    def test_valid_signature_cannot_select_wrong_current_coordinating_cut(self):
        self.obj.retained['coordinating_source_cut']=copy.deepcopy(self.sub['source_cut']);self.repin_wrapper()
        with self.assertRaisesRegex(ValueError,'coordinating cut'):self.verify()
    def test_mutated_captured_wrapper_refused(self):
        self.obj.retained['original_source_posture']='admitted-current'
        with self.assertRaisesRegex(ValueError,'routing changed'):self.verify()
    def test_tampered_original_work_or_contract_refused(self):
        for kind in ('work','challenge-contract'):
            old=self.obj.retained['original_source_records'][kind]
            raw=base64.b64decode(old)+b' ';self.obj.retained['original_source_records'][kind]=base64.b64encode(raw).decode();self.repin_wrapper()
            with self.assertRaisesRegex(ValueError,'header/body differs'):self.verify()
            self.obj.retained['original_source_records'][kind]=old;self.repin_wrapper()
    def test_wrong_signer_and_tampered_actual_native_request_refused(self):
        with self.assertRaisesRegex(ValueError,'signer differs'):self.obj.verify_origin('00'*32,self.outer,self.now)
        self.cap['original_request']['subject']['identity_ref']='work:another';self.repin_wrapper()
        with self.assertRaisesRegex(ValueError,'native request bytes changed'):self.verify()
    def test_expired_signed_capsule_is_not_permission(self):
        self.obj.capsule=self.build(self.now-timedelta(hours=2));self.obj.retained['original_signed_source']=self.obj.capsule;self.repin_wrapper()
        with self.assertRaisesRegex(ValueError,'expired or future'):self.verify()
    def test_even_real_fixture_signer_cannot_declare_acceptance(self):
        p=self.cap['envelope']['payload'];p['selected_fixture_outcome']='accept'
        self.cap['envelope']['signature']=base64.b64encode(self.key.sign(R.canon(p))).decode();self.repin_wrapper()
        with self.assertRaisesRegex(ValueError,'scope/lineage/outcome'):self.verify()
    def test_extra_historical_record_cannot_enter_closed_origin_set(self):
        self.obj.retained['original_source_records']['another']=base64.b64encode(b'{}').decode();self.repin_wrapper()
        with self.assertRaisesRegex(ValueError,'closed retained original'):self.verify()

if __name__=='__main__':unittest.main()
