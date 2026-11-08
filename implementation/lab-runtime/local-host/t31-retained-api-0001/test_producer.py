"""Causal producer-selection tests using explicitly synthetic API transport."""
import copy
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import test_retained as TR
from producer import ArchiveProof
import producer as P
import retained as R

class Producer(unittest.TestCase):
 def setUp(self):
  self.fixture=TR.Retained();self.fixture.setUp();self.addCleanup(self.fixture.temp.cleanup)
  f=self.fixture
  self.selection={'archive':str(f.archive),'observation_sha256':f.pin,'terminal_result':str(f.terminal),'terminal_sha256':f.tpin,
   'source_sha256':f.source,'profile_sha256':f.profile,'operation':f.operation}
  self.ref=f.reply['message']['targets'][0]['artifact']['version_ref']
  self.transitions={'transition:synthetic:observed':[self.ref]}
 def proof(self):return ArchiveProof([self.selection],transitions=self.transitions)
 def test_exact_returned_original_and_receipt_custody(self):
  proof=self.proof();profile=proof.profile()
  self.assertEqual(profile['records'][self.ref][1],self.fixture.body)
  self.assertFalse(profile['originals_are_Source_current']);self.assertTrue(proof.guard())
 def test_output_cannot_be_added_without_actual_returned_original(self):
  self.transitions['transition:synthetic:observed']=['invented:output@1']
  with self.assertRaisesRegex(ValueError,'actual returned'):self.proof()
 def test_retained_terminal_failure_or_change_invalidates_existing_proof(self):
  proof=self.proof();self.fixture.status='FAIL';self.fixture.seal()
  with self.assertRaisesRegex(ValueError,'terminal'):proof.guard()
 def test_private_selection_or_body_rebinding_refuses(self):
  proof=self.proof();proof.transitions['transition:synthetic:observed']=[]
  with self.assertRaisesRegex(ValueError,'controls changed'):proof.guard()
  proof=self.proof();self.fixture.object.write_bytes(self.fixture.body+b' ')
  with self.assertRaisesRegex(ValueError,'member differs'):proof.guard()
 def test_profile_mutation_does_not_change_private_producer_selection(self):
  proof=self.proof();profile=proof.profile();profile['records'].clear();profile['outputs'].clear()
  self.assertTrue(proof.guard());self.assertIn(self.ref,proof.profile()['records'])
 def test_direct_intent_bundle_requires_native_lineage_and_identical_source_originals(self):
  raw=b'{}';header={'scope_ref':'scope:fixture','identity_ref':'intent:fixture',
    'version_ref':'intent:fixture@1','carrier_ref':'cal.artifact-type.intent/v1',
    'byte_sha256':R.sha(raw)}
  source={'path':'api/source-manifest.json','sha256':'a'*64}
  profile={'path':'api/contract-profile.json','sha256':'b'*64}
  cut={'store_ref':'fixture-source'}
  kinds=('intent','work','goal','coordination')
  intent={'records':{header['version_ref']:(header,raw)},
    'transitions':{'transition:intent-framing:resolved':[header]},
    'manifest_binding':{'ref':'/private/MANIFEST.json','sha256':'c'*64},
    'receipt_raw':b'{}','source_binding':source,'profile_binding':profile,
    'source_cut':cut,'principal_ref':'principal:fixture','run_ref':'workflow-run:fixture',
    'source_inputs':{kind:(header,raw) for kind in kinds}}
  native={'source_binding':source,'profile_binding':profile,'source_cut':cut,
    'identity':{'principal_ref':'principal:fixture','run_ref':'workflow-run:fixture'},
    'coordination_inputs':{kind:(header,raw) for kind in kinds}}
  native['coordination_inputs']['coordination-context']=(header,raw)
  selection={'kind':'intent-framing','manifest_path':'/private/MANIFEST.json','manifest_sha256':'c'*64}
  emission={'terminal_result':'/private/first/FIRST-SESSION.json'}
  intent_path=P.ROOT/'implementation/lab-runtime/local-host/t31-native-intent-framing-0001/intent_bundle.py'
  native_path=P.ROOT/'implementation/lab-runtime/local-host/t31-remaining-eighteen-0001/native_emission_bundle.py'
  names={'_cal_t31_original_bundle_'+R.sha(intent_path.read_bytes()):SimpleNamespace(__file__=str(intent_path),consume=lambda _:intent),
         '_cal_t31_native_emission_bundle_'+R.sha(native_path.read_bytes()):SimpleNamespace(__file__=str(native_path),consume=lambda _:native)}
  transitions={'transition:intent-framing:resolved':[header['version_ref']]}
  with patch.dict(sys.modules,names):
   with self.assertRaisesRegex(ValueError,'requires exact native'):
    ArchiveProof([],transitions=transitions,original_bundles=[selection])
   native['identity']['principal_ref']='principal:foreign'
   with self.assertRaisesRegex(ValueError,'lineage differ'):
    ArchiveProof([],transitions=transitions,original_bundles=[selection],native_emissions=[emission])
   native['identity']['principal_ref']='principal:fixture'
   native['coordination_inputs']['work']=(header,b'foreign')
   with self.assertRaisesRegex(ValueError,'Source original differs'):
    ArchiveProof([],transitions=transitions,original_bundles=[selection],native_emissions=[emission])
 def test_product_source_cut_survives_guard_recapture(self):
  with tempfile.TemporaryDirectory() as temporary:
   root=Path(temporary)
   relative=Path('implementation/lab-runtime/local-host/t31-remaining-eighteen-0001/product_fixture_production.py')
   path=root/relative;path.parent.mkdir(parents=True)
   body=b'{"kind":"fixture"}';digest=R.sha(body)
   path.write_text('''def produce(*, records, observations, controls):
    artifact = {'scope_ref': 'scope:fixture', 'identity_ref': 'product:fixture',
                'version_ref': 'product:fixture@1',
                'carrier_ref': 'cal.artifact-type.work-outcome-assessment/v1',
                'byte_sha256': '%s'}
    return {'records': [(artifact, b'{"kind":"fixture"}')],
            'receipt': {'schema_version': 'lab-local-product-fixture-production/v1',
                        'source_cut': controls['source_cut']},
            'consumed_input_refs': [next(iter(records))],
            'consumed_observation_refs': [observations[0]['observation_binding']['ref']]}
''' % digest)
   cut={'store_ref':'current-fixture'}
   typed=[{'module_binding':{'path':relative.as_posix(),'sha256':R.sha(path.read_bytes())},
           'entrypoint':'produce','controls':{'source_cut':cut}}]
   with patch.object(P,'ROOT',root):
    proof=ArchiveProof([self.selection],transitions={'transition:product-adoption-release:pilot-assessed':['product:fixture@1']},typed_productions=typed)
    self.assertEqual(proof.product_source_cut,cut)
    self.assertTrue(proof.guard())

if __name__=='__main__':unittest.main()
