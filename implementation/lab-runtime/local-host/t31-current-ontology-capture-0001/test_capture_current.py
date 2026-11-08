"""Scope wrapper causal tests with explicitly synthetic capture receipts only."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
import capture_current as C
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'implementation/lab-runtime/local-host/t31-retained-api-0001'));import scope_profile as SP

class CaptureScope(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='cal-actual-capture-wrapper-component-');self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.root.chmod(0o700)
  self.actor={'principal_ref':'principal:synthetic-private','agent_instance_ref':None,'assignment_ref':None,'session_ref':None,'role_assignment_refs':[]};self.run='workflow-run:synthetic'
  self.work={'scope_ref':'project:synthetic','identity_ref':'work:synthetic','version_ref':'work:synthetic@1','carrier_ref':'cal.artifact-type.work/v1','byte_sha256':'w'*64};self.cut={'synthetic-only':True};self.before={'ref':'synthetic:run-before','sha256':'r'*64}
  self.producer={'path':str(ROOT/C.VARIANT),'sha256':C.VARIANT_SHA};self.source={'ref':'synthetic:signed-source','sha256':'s'*64}
  self.headers=[]
  for carrier,count in [('ontology-node/v2',18),('ontology-edge/v1',12),('ontology-cut/v1',1),('ontology-view/v1',1)]:
   for n in range(count):
    identity=carrier.split('/')[0]+':synthetic:'+str(n);self.headers.append({'scope_ref':'ontology-store:synthetic','identity_ref':identity,'version_ref':identity+'@synthetic.1','carrier_ref':'cal.artifact-type.'+carrier,'byte_sha256':C.sha(identity.encode())})
 def capture(self,transition=None,before=None):
  transition=transition or 'transition:ontology-migration:mapped';before=before or self.before
  raw=C.enc({'schema_version':'lab-original-ontology-typed-capture/v1-candidate','run_binding':before,'work_ref':self.work['version_ref'],'source_cut':self.cut,
             'artifacts':self.headers,'work_satisfaction_asserted':False,'authority_effect':'none','test_ceiling':'Synthetic receipt; no actual native call occurred.'})
  return {'transition_ref':transition,'receipt_binding':{'ref':'synthetic:retained-receipt','sha256':C.sha(raw)},'returned_receipt_binding':{'ref':'synthetic:actual-returned-logical-binding','sha256':C.sha(raw)},'receipt_original':raw}
 def observe(self,name='first',capture=None,outputs=None,before=None,prior=None):
  root=self.root/name;root.mkdir(mode=0o700)
  return C.scope_observation(evidence=root,capture=capture or self.capture(),outputs=outputs or self.headers[:30],run_binding=before or self.before,work=self.work,
   actor=self.actor,run_ref=self.run,cut=self.cut,config_sha='c'*64,producer=self.producer,source_binding=self.source,prior=prior)
 def test_complete_wrapper_preserves_actual_receipt_and_explicit_observer_boundary(self):
  before=copy.deepcopy(self.actor);binding,index=self.observe();self.assertEqual(len(index['entries']),30);self.assertEqual(self.actor,before)
  raw,index,files=SP.capture(binding);receipt=json.loads(next(body for name,body in files.items()if 'capture-observation'in name))
  self.assertFalse(receipt['capture_returned_scope_proof']);self.assertTrue(receipt['scope_observer_created_wrapper_only'])
  self.assertEqual(receipt['actual_returned_capture_receipt_binding'],self.capture()['returned_receipt_binding'])
 def test_wrong_route_or_work_receipt_binding_refuses(self):
  cap=self.capture();cap['transition_ref']='transition:review-admission:applied'
  with self.assertRaisesRegex(ValueError,'route'):self.observe(capture=cap)
  cap=self.capture();raw=json.loads(cap['receipt_original']);raw['work_ref']='work:foreign@1';cap['receipt_original']=C.enc(raw);cap['receipt_binding']['sha256']=cap['returned_receipt_binding']['sha256']=C.sha(cap['receipt_original'])
  with self.assertRaisesRegex(ValueError,'receipt/Run/Work'):self.observe('second',capture=cap)
 def test_unreturned_header_or_missing_required_output_refuses(self):
  headers=copy.deepcopy(self.headers[:30]);headers[0]['byte_sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'absent'):self.observe(outputs=headers)
  with self.assertRaisesRegex(ValueError,'categories'):self.observe('second',outputs=self.headers[:29])
 def test_second_actual_run_preimage_extends_prior_original_scope_entries(self):
  binding,index=self.observe();prior=SP.capture(binding);before={'ref':'synthetic:run-after-first','sha256':'n'*64};cap=self.capture('transition:ontology-migration:candidate-validated',before)
  new,index=self.observe('second',capture=cap,outputs=self.headers[30:],before=before,prior=prior)
  self.assertEqual(index['entries'][:30],prior[1]['entries']);self.assertEqual(len(index['entries']),32)
  raw,current,files=SP.capture(new)
  for name,body in prior[2].items():self.assertEqual(files[name],body)

if __name__=='__main__':unittest.main()
