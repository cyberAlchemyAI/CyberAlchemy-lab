"""Pure fixtures test mechanics only; no native or scored calls."""
import json, runpy, tempfile, unittest
from pathlib import Path

M=runpy.run_path(str(Path(__file__).with_name('coverage_runtime.py')))
Runtime=M['Runtime']; save=M['save']; sha=M['sha']; plan=M['plan']
CASE={'case_id':'COV','phase':'coverage','valued_outcome':'fixed goal','hard_constraints':[{'id':'C1','text':'fixed'}],'observations':[{'id':'O1','text':'fixed'}],'resources':[{'id':'R1','text':'present','available':True}],'parent_operations':[{'id':'P1','text':'first'},{'id':'P2','text':'second'}],'available_observables':[{'id':'M1','text':'ledger'}],'unknowns':[{'id':'U1','text':'unknown'}],'ordinary_archive':[]}
class Fake(Runtime):
    def case(self):return CASE
    def methods(self):return {'R07':{'instructions':'exact R07','supplement_branch':'summary'},'R09':{'instructions':'other-recipe-secret','supplement_branch':'summary'}}
    def body(self,jid):
        if jid.endswith('stage2'):return {'summary':[{'id':'s1','text':'retained','source_refs':['C1']}],'residue':[{'id':'r1','text':'excluded-secret','source_refs':['O1']}]}
        return {'guard':'guard-secret'}
class Tests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.r=Fake(self.root)
    def tearDown(self):self.tmp.cleanup()
    def test_exclusive_save_keeps_first_bytes(self):
        p=self.root/'once.json';save(p,{'first':True});original=p.read_bytes()
        with self.assertRaises(FileExistsError):save(p,{'first':False})
        self.assertEqual(p.read_bytes(),original)
    def test_builder_gets_only_own_selected_summary(self):
        p=self.r.payload(self.r.job('COV-R07-builder'));s=json.dumps(p)
        self.assertIn('retained',s)
        for excluded in ['excluded-secret','guard-secret','other-recipe-secret','own_proposal']:self.assertNotIn(excluded,s)
    def test_different_stage_preserves_proposal_access(self):
        p=self.r.payload(self.r.job('COV-R07-stage2'));self.assertIn('guard',p);self.assertIn('own_proposal',p)
    def test_invalid_guard_gates_both_proposals(self):
        self.r.state=lambda jid:({'disposition':'finished','terminal':True,'valid':False} if jid=='COV-guard' else {'disposition':'pending','terminal':False,'valid':False})
        self.assertEqual(set(self.r.ready()['gateable']),{'COV-R07-stage1','COV-R09-stage1'})
        self.assertNotIn('COV-review1',self.r.ready()['gateable'])
    def test_reviews_ready_after_all_terminal_even_gates(self):
        self.r.state=lambda jid:({'disposition':'pending','terminal':False,'valid':False} if 'review' in jid else {'disposition':'gated','terminal':True,'valid':False})
        self.assertEqual(set(self.r.ready()['ready']),{'COV-review1','COV-review2'})
    def test_freeze_rejects_changed_source(self):
        p=self.root/'input.txt';p.write_text('first');save(self.root/'preparation/FREEZE.v1.json',{'sources':{str(p):sha(p)}})
        self.assertTrue(self.r.integrity());p.write_text('changed')
        with self.assertRaisesRegex(RuntimeError,'source drift'):self.r.integrity()
    def test_malformed_raw_remains_visible(self):
        p=self.root/'raw/COV-R07-stage1.json';p.parent.mkdir();p.write_text('{broken')
        self.assertEqual(self.r.raw_packet('COV-R07-stage1'),{'malformed_raw_text':'{broken'})
    def test_incomplete_review_not_accepted(self):
        v={'job_id':'COV-review1','case_id':'COV','recipe_reviews':[]}
        with self.assertRaisesRegex(RuntimeError,'complete review rows'):self.r.validate(self.r.job('COV-review1'),v)
    def test_plan_has_nine_real_role_slots_and_two_full_reviews(self):
        self.assertEqual(len(plan()),9)
        for j in plan():
            if j['role']=='fidelity_review':self.assertEqual(len(j['dependencies']),7)
if __name__=='__main__':unittest.main()
