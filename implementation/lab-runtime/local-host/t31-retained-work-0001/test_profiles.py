"""Retained Work identity/meaning and actual original-stage capture boundaries."""
import copy
import json
from pathlib import Path
import sys
import unittest
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001/deps'),str(HERE)]
import profiles as P
import bundle as B
import coordination as C
class Profiles(unittest.TestCase):
    def test_both_real_original_design_methods_and_all_six_typed_output_sets(self):
        total=0
        for kind in P.SPECS:
            profile=P.load(kind);routes,raws,receipt=B.construct(profile)
            self.assertEqual(len(routes),3);self.assertEqual(receipt['original_work'],profile['original_run']['work']);self.assertFalse(receipt['retained_implementation_or_experiment_rerun'])
            design=receipt['origins']['transition:'+kind+':designed']['receipt'];self.assertTrue(design['actual_original_method_invoked'])
            self.assertEqual(design['actual_original_stage_event']['from'],'prepared');self.assertEqual(design['actual_original_stage_event']['to'],'designed')
            if kind=='engineering':
                body=json.loads(raws[routes['transition:engineering:designed'][0]['version_ref']]);basis=copy.deepcopy(design);basis.pop('output')
                self.assertEqual(body['payload']['output_digest'],'sha256:'+P.sha(P.enc(basis)))
            total+=sum(len(headers) for headers in routes.values())
        self.assertEqual(total,9)
    def test_old_Work_cannot_be_retargeted_to_API30_or_old_cut_rewritten(self):
        profile=P.load('engineering');profile['original_work']['identity_ref']='work:API30'
        with self.assertRaisesRegex(ValueError,'profile changed'):P.guard(profile)
        profile=P.load('research');profile['original_producer_source_cut']['commit_sequence']+=1
        with self.assertRaisesRegex(ValueError,'profile changed'):P.guard(profile)
    def test_captured_raw_replacement_refused_even_without_header_change(self):
        profile=P.load('engineering');ref=profile['manifest']['work_ref'];profile['raws'][ref]+=b' '
        with self.assertRaisesRegex(ValueError,'original record bytes'):P.guard(profile)
        profile=P.load('research');profile['original_run_raw']+=b' '
        with self.assertRaisesRegex(ValueError,'captured original producer'):P.guard(profile)
    def test_private_coordination_preserves_old_goal_Work_and_both_source_cuts(self):
        p=P.load('engineering');project={'scope_ref':p['scope_ref'],'identity_ref':p['scope_ref'],'version_ref':p['scope_ref']+'@fixture.1','carrier_ref':'cal.artifact-type.project-identity/v1','byte_sha256':'1'*64}
        current=copy.deepcopy(p['original_producer_source_cut']);current['store_ref']='current-coordinating-fixture-store'
        capsule,raws=C.construct(p,run_ref='workflow-run:bounded-unit',principal='principal:fixture-reader',source_cut=current,project=project)
        self.assertEqual(capsule['original_work'],p['original_work']);self.assertNotEqual(capsule['original_producer_source_cut'],capsule['current_coordinating_source_cut'])
        self.assertTrue(capsule['original_Work_bytes_and_meaning_unchanged']);self.assertFalse(capsule['original_Work_promoted_to_Source_current']);self.assertEqual(len(raws),5)
        project['identity_ref']='project:foreign'
        with self.assertRaisesRegex(ValueError,'current Project'):C.construct(p,run_ref='workflow-run:bounded-unit',principal='principal:fixture-reader',source_cut=current,project=project)
if __name__=='__main__':unittest.main()
