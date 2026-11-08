"""End-to-end read-only CLI and exact scope/preservation controls."""
import contextlib
import copy
import io
import json
import pathlib
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
HERE=pathlib.Path(__file__).resolve().parents[1];ROOT=HERE.parents[3]
sys.path[:0]=[str(HERE),str(HERE/'tests')]
import cli
import reports
import resolver as r
import test_E03 as fixtures

BASE=reports.BASE
SNAP=BASE+'/current-snapshot.json'
DELIVERY=BASE+'/definitions/cal.definition.semantic-primitive/delivery-manifest.json'

def invoke(root,*args,fmt='json'):
    stream=io.StringIO()
    with contextlib.redirect_stdout(stream):
        status=cli.main(['--repo',str(root),'--format',fmt,*args])
    return status,json.loads(stream.getvalue()) if fmt=='json' else stream.getvalue()

class CLIControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot_ref=reports.reference(ROOT,SNAP);cls.delivery_ref=reports.reference(ROOT,DELIVERY)
        cls.report_args=['report','--snapshot',SNAP,'--snapshot-sha',cls.snapshot_ref['sha256'],'--delivery',DELIVERY,'--delivery-sha',cls.delivery_ref['sha256']]
        cls.manifest=reports.load(ROOT,cls.delivery_ref)
        cls.source_snapshot=reports.load(ROOT,cls.snapshot_ref)
    def preserved(self):
        for ref in self.manifest['files']:
            self.assertEqual(ref,reports.reference(ROOT,ref['path']))
        self.assertEqual(201,r.verify(self.source_snapshot,ROOT)['files'])
    def test_report_exact_full_denominator_separates_projection_and_pending_fidelity(self):
        self.preserved();status,out=invoke(ROOT,*self.report_args)
        self.assertEqual(0,status);self.assertEqual(183,out['current_definitions']);self.assertEqual(189,out['admitted_source_versions'])
        self.assertEqual(8,out['per_definition_partial_drafts']);self.assertEqual(175,len(out['whole_definition_missing_drafts']))
        self.assertEqual(183,len(out['whole_definition_rows']));self.assertEqual(7,out['projection']['identity_count'])
        self.assertEqual(176,len(out['projection']['missing_projection_identities']));self.assertEqual(15,len(out['identities_with_either_partial_draft_or_projection']))
        self.assertEqual(0,out['projection']['whole_definition_credit']);self.assertFalse(out['union_is_whole_translation_coverage'])
        self.assertEqual(0,out['owner_accepted_whole_translations']);self.assertEqual(0,out['whole_definition_proofs']);self.assertFalse(out['semantic_ready'])
        self.assertEqual(139,out['foundation_counts']['deferred_clauses']);self.assertEqual(97,out['foundation_counts']['unresolved_populations']);self.assertEqual([],out['selected_premises'])
        self.assertTrue(all(x['owner_fidelity']=='pending' and x['semantic_ready'] is False for x in out['whole_definition_rows']))
        self.assertEqual([{'case':'counterfactual','native_status':'bounded-no-witness','obligation_id':'relation:TRACE-Position:left-difference','status':'reported-finite-scope-failure-unverified-exhaustion'}],out['recorded_failures_or_unresolved_queries'])
        self.preserved()
    def test_human_report_keeps_every_identity_and_claim_ceiling(self):
        status,text=invoke(ROOT,*self.report_args,fmt='human');self.assertEqual(0,status)
        self.assertIn('Semantic readiness: false',text);self.assertIn('whole-definition credit: 0',text)
        for source in self.source_snapshot['current_entries']:self.assertIn(source['definition_id']+' | ',text)
        self.assertIn('No fresh solver/model run',text)
    def test_capture_is_current_and_performs_no_publication(self):
        with patch.object(r,'publish',side_effect=AssertionError('CLI must not publish')):
            status,out=invoke(ROOT,'capture')
        self.assertEqual(0,status);self.assertFalse(out['semantic_ready']);self.assertTrue(r.same_json(self.source_snapshot,out['snapshot']));self.preserved()
    def test_check_typed_candidate_does_not_promote_full_translation(self):
        p=BASE+'/definitions/cal.definition.semantic-primitive/t.json';ref=reports.reference(ROOT,p)
        status,out=invoke(ROOT,'check','--input',p,'--input-sha',ref['sha256'],'--kind','interpretation','--snapshot',SNAP,'--snapshot-sha',self.snapshot_ref['sha256'])
        self.assertEqual(0,status);self.assertEqual('typed-candidate-interpretation',out['status']);self.assertEqual('verified-live',out['source_currentness'])
        self.assertFalse(out['semantic_ready']);self.assertFalse(out['mechanized_proof']);self.assertEqual('pending',out['source_fidelity'])
    def test_stale_missing_path_traversal_and_symlink_inputs_fail_closed(self):
        for path,sha in [(SNAP,'0'*64),('missing.json','0'*64),('../outside.json','0'*64)]:
            with self.subTest(path=path):
                status,out=invoke(ROOT,'check','--input',path,'--input-sha',sha,'--kind','source')
                self.assertEqual(2,status);self.assertEqual('candidate-command-unresolved',out['status']);self.assertFalse(out['semantic_ready'])
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp);(root/'linked.json').symlink_to(ROOT/SNAP)
            status,out=invoke(root,'check','--input','linked.json','--input-sha',self.snapshot_ref['sha256'],'--kind','source')
            self.assertEqual(2,status);self.assertFalse(out['semantic_ready'])
    def copied_root(self,tmp):
        root=pathlib.Path(tmp)
        for ref in [*self.manifest['files'],self.delivery_ref,*[{'path':x['path']} for x in self.source_snapshot['captured_files']]]:
            target=root/ref['path']
            if target.exists():continue
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/ref['path'],target)
        return root
    def reseal(self,root,path,value):
        (root/path).write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
        manifest=json.loads((root/DELIVERY).read_bytes())
        for ref in manifest['files']:
            if ref['path']==path:ref.update(reports.reference(root,path))
        (root/DELIVERY).write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
        return reports.reference(root,DELIVERY)
    def test_changed_source_candidate_or_dropped_manifest_entry_cannot_pass_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=self.copied_root(tmp)
            p=BASE+'/definitions/cal.definition.axiom/t.json';saved=(root/p).read_bytes();(root/p).write_bytes(saved+b' ')
            with self.assertRaises(reports.ReportFault):reports.coverage(root,self.snapshot_ref,self.delivery_ref)
            (root/p).write_bytes(saved)
            manifest=json.loads((root/DELIVERY).read_bytes());manifest['files']=[x for x in manifest['files'] if x['path']!=p]
            (root/DELIVERY).write_text(json.dumps(manifest)+'\n');ref=reports.reference(root,DELIVERY)
            with self.assertRaises(reports.ReportFault):reports.coverage(root,self.snapshot_ref,ref)
        self.preserved()
    def test_rehashed_forged_foundation_readiness_and_failure_omission_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=self.copied_root(tmp);p=BASE+'/definitions/cal.definition.semantic-primitive/foundation-draft-review.json'
            original=json.loads((root/p).read_bytes());forged=copy.deepcopy(original);forged['semantic_ready']=True
            ref=self.reseal(root,p,forged)
            with self.assertRaises(reports.ReportFault) as caught:reports.coverage(root,self.snapshot_ref,ref)
            self.assertEqual('unsupported-foundation-acceptance',caught.exception.code)
            self.reseal(root,p,original)
            p=BASE+'/units/I03/worked-summary.json';forged=json.loads((root/p).read_bytes());forged['cases']['counterfactual']['failed_or_unresolved_queries']=[]
            ref=self.reseal(root,p,forged)
            with self.assertRaises(reports.ReportFault) as caught:reports.coverage(root,self.snapshot_ref,ref)
            self.assertEqual('projection-failure-ledger-substitution',caught.exception.code)
        self.preserved()
    def test_verify_executes_actual_selected_independent_bundle_checker(self):
        fixture,bundle,required,put,selection=fixtures.setup_selection()
        try:
            fixtures.add_witness(bundle,put,selection,fixture.root)
            published=fixtures.v.b.publish(fixture.root,bundle,required,BASE+'/fixture-publication')
            self.assertEqual('published-candidate',published['status']);ref=put('selected/cli-selection.json',selection)
            status,out=invoke(fixture.root,'verify','--bundle',published['bundle_ref'],'--selection',ref['path'],'--selection-sha',ref['sha256'])
            self.assertEqual(0,status,out);self.assertEqual('verified-candidate-accounting',out['status'])
            self.assertFalse(out['semantic_ready']);self.assertFalse(out['mechanized_proof']);self.assertGreaterEqual(len(out['checked_logical']),1)
        finally:fixture.doCleanups()
    def test_diff_generates_actual_revision_requirements_with_pending_gates(self):
        p=BASE+'/units/I02/unchanged-selection.json';ref=reports.reference(ROOT,p)
        status,out=invoke(ROOT,'diff','--selection',p,'--selection-sha',ref['sha256'])
        self.assertEqual(0,status,out);self.assertEqual('candidate-revision-generated',out['status']);self.assertFalse(out['semantic_ready'])
        self.assertFalse(out['result']['evidence_verified']);self.assertEqual('pending',out['result']['source_fidelity']);self.preserved()

if __name__=='__main__':unittest.main()
