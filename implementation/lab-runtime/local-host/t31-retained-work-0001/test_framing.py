"""Real original input resolution plus private candidate declaration; no API auth."""
import copy
from pathlib import Path
import sys
import unittest
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001/deps'),str(HERE)]
import profiles as P
import coordination as C
import framing as F

class Framing(unittest.TestCase):
    def setUp(self):
        self.profile=P.load('engineering');scope=self.profile['scope_ref']
        project={'scope_ref':scope,'identity_ref':scope,'version_ref':scope+'@fixture.1','carrier_ref':'cal.artifact-type.project-identity/v1','byte_sha256':'1'*64}
        self.cap,self.raws=C.construct(self.profile,run_ref='workflow-run:framing-component',principal='principal:fixture-only',source_cut=self.profile['original_producer_source_cut'],project=project)
    def test_original_constructor_prepares_and_two_exact_output_carriers_validate(self):
        transitions,raws,receipt=F.construct(self.profile,self.cap,self.raws)
        self.assertTrue(receipt['actual_original_resolver_prepared']);self.assertEqual(len(transitions),2);self.assertEqual(len(raws),2)
        work=self.profile['original_work'];self.assertEqual(raws[work['version_ref']],self.profile['raws'][work['version_ref']])
        self.assertIsNone(receipt['human_Intent_resolution_or_actual_owner_outcome']);self.assertFalse(receipt['original_Work_promoted_to_Source_current'])
    def test_unrelated_resolution_rejected(self):
        self.cap['records']['intent-resolution']['payload']['selected_subject_refs']=[]
        with self.assertRaisesRegex(ValueError,'captured framing original'):F.construct(self.profile,self.cap,self.raws)
    def test_original_Work_retarget_refused(self):
        self.profile['original_work']['identity_ref']='work:another'
        with self.assertRaisesRegex(ValueError,'profile changed'):F.construct(self.profile,self.cap,self.raws)
    def test_changed_original_resolution_bytes_refused(self):
        h=self.cap['artifacts']['intent-resolution'];self.raws[h['version_ref']]+=b' '
        with self.assertRaises(Exception):F.construct(self.profile,self.cap,self.raws)

if __name__=='__main__':unittest.main()
