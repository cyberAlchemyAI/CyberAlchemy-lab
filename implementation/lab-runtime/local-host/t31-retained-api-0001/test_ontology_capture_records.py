"""Actual schemas/receipt joins using explicitly synthetic capture transport."""
import copy
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import ontology_capture_records as P
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'implementation/lab-runtime/local-host/t31-current-ontology-capture-0001'));import capture_current as C

class CaptureRecords(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='cal-capture-records-component-');self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.root.chmod(0o700)
  self.source='a'*64;self.profile='b'*64;self.scope='ontology-store:synthetic';self.project='project:synthetic';self.cut={'synthetic-source-only':True}
  self.actor={'principal_ref':'principal:synthetic-private','agent_instance_ref':None,'assignment_ref':None,'session_ref':None,'role_assignment_refs':[]}
  self.work={'scope_ref':self.project,'identity_ref':'work:synthetic','version_ref':'work:synthetic@1','carrier_ref':'cal.artifact-type.work/v1','byte_sha256':'w'*64}
  self.head={'generation':'generation-synthetic','store_ref':self.scope};self.hraw=C.enc(self.head);self.native=b'{"synthetic-native-only":true}'
  self.mraw=C.enc({'native_read_sha256':P.R.sha(self.native)});self.mapping=C.enc({'source_cut':self.cut})
  self.view={'scope_ref':self.scope,'identity_ref':'ontology-view:actual-api-synthetic','version_ref':'ontology-view:actual-api-synthetic@1','carrier_ref':'cal.artifact-type.ontology-view/v1','byte_sha256':'v'*64}
  self.records={self.view['version_ref']:(self.view,b'synthetic retained-view transport')}
  self.observed={'actual_reply':{'operation':'ontology.project','kind':'result'},'projection_producer':{'receipt':{'ontology_view':self.view}},'original_source_cut':self.cut,
   'observation_binding':{'ref':'synthetic:projection-observation','sha256':'o'*64},'files':{'vault/ontology/HEAD.json':self.hraw,'vault/ontology/generation-synthetic/manifest.json':self.mraw}}
  selected=SimpleNamespace(root=lambda:ROOT,guard=lambda:None,binding=lambda key:{'sha256':self.source if key=='api.source'else self.profile})
  p=patch.dict(sys.modules,{'cal_installed_runtime_selection_v1':selected});p.start();self.addCleanup(p.stop)
  self.bindings=[];self.results=[];self.prior_scope=None
  self.capture('mapped');self.capture('candidate-validated')
 def capture(self,phase):
  folder=self.root/phase;folder.mkdir(mode=0o700);version='native-capture-'+phase+'.1';before={'ref':'synthetic:run-'+phase,'sha256':P.R.sha(phase.encode())};headers=[];rows=[]
  for kind,count,v in [('ontology-node',18,'v2'),('ontology-edge',12,'v1'),('ontology-cut',1,'v1'),('ontology-view',1,'v1')]:
   for n in range(count):
    body=json.loads((ROOT/'authority/artifact-types'/kind/v/'fixtures/valid/record.json').read_bytes());identity=kind+':synthetic:'+str(n);body.update(node_id=identity,scope_ref=self.scope,owner_ref=self.actor['principal_ref']);raw=C.enc(body)
    h={'scope_ref':self.scope,'identity_ref':identity,'version_ref':identity+'@'+version,'carrier_ref':'cal.artifact-type.'+kind+'/'+v,'byte_sha256':P.R.sha(raw)}
    rows.append({'artifact':h,'original_binding':C.write(folder/(P.R.sha(raw)+'.json'),raw)});headers.append(h)
  replay={'schema_version':'lab-original-ontology-cold-correspondence/v1-candidate','cold_replayed':True,'head_binding':{'ref':'synthetic:head','sha256':P.R.sha(self.hraw)},'manifest_binding':{'ref':'synthetic:manifest','sha256':P.R.sha(self.mraw)},'native_read_binding':{'ref':'synthetic:native','sha256':P.R.sha(self.native)}}
  replayraw=C.enc(replay);receipt={'schema_version':'lab-original-ontology-typed-capture/v1-candidate','run_binding':before,'work_ref':self.work['version_ref'],'source_cut':self.cut,'work_satisfaction_asserted':False,'authority_effect':'none','artifacts':headers,'record_version_contract':version,
   'original_head_binding':replay['head_binding'],'original_manifest_binding':replay['manifest_binding'],'original_cold_replay_binding':{'ref':'synthetic:cold','sha256':P.R.sha(replayraw)}}
  receipt_raw=C.enc(receipt);receiptbinding=C.write(folder/'capture-receipt.json',receipt_raw);returned={'ref':'synthetic:original-returned-binding','sha256':P.R.sha(receipt_raw)}
  transition='transition:ontology-migration:'+phase;stage=headers[:30]if phase=='mapped'else headers[30:]
  sb,index=C.scope_observation(evidence=folder,capture={'transition_ref':transition,'receipt_binding':receiptbinding,'returned_receipt_binding':returned,'receipt_original':receipt_raw},outputs=stage,run_binding=before,work=self.work,actor=self.actor,run_ref='workflow-run:synthetic',cut=self.cut,config_sha='c'*64,producer={'path':str(ROOT/P.VARIANT),'sha256':P.VARIANT_SHA},source_binding={'ref':'synthetic:source','sha256':'s'*64},prior=self.prior_scope)
  self.prior_scope=P.SC.capture(sb)
  cold={name:C.write(folder/('cold-'+name+'.json'),raw)for name,raw in {'head':self.hraw,'manifest':self.mraw,'native_read':self.native,'cold_replay':replayraw,'mapping_policy':b'{}','mapping':self.mapping}.items()}
  result={'schema_version':'lab-actual-native-ontology-capture-observation/v1','result':'PASS-actual-native-capture-and-scope-observation','actual_capture_producer_binding':{'path':str(ROOT/P.VARIANT),'sha256':P.VARIANT_SHA},'scope_observation_is_wrapper':True,'public_workflow_transition_dispatched':False,'SourceAdmission_requirement_satisfied':False,'api_source_sha256':self.source,'api_profile_sha256':self.profile,'source_cut':self.cut,'authority_effect':'none','transition_ref':transition,'work':self.work,'actor':self.actor,'run_ref':'workflow-run:synthetic','run_binding':before,'journal_config_sha256':'c'*64,'actual_capture_receipt_binding':receiptbinding,'actual_returned_capture_receipt_binding':returned,'additional_cold_originals':cold,'additional_actual_cold_replay':True,'original_capture_cold_receipt_reconstructed':False,'scope_index_binding':sb,'original_records':rows,'selected_stage_outputs':stage}
  self.results.append(result);self.bindings.append(C.write(folder/'RESULT.json',result))
 def produce(self,bindings=None,assessment=False):return P.produce(records=self.records,observations=[self.observed],controls={'capture_bindings':bindings or self.bindings,'produce_assessment':assessment})
 def test_complete_actual_shape_preserves64_originals_and_bounded_project_assessment(self):
  out=self.produce(assessment=True);self.assertEqual(len(out['records']),65);body=json.loads(out['records'][-1][1]);self.assertEqual(body['scope_ref'],self.project);self.assertEqual(body['payload']['subject_ref'],self.work['version_ref']);self.assertIn('gap:original-Work-completion-not-assessed',body['payload']['gap_refs']);self.assertFalse(out['receipt']['Work_completion_established'])
 def test_changed_original_typed_body_or_result_binding_refuses(self):
  binding=self.results[0]['original_records'][0]['original_binding'];path=Path(binding['ref']);path.write_bytes(path.read_bytes()+b' ')
  with self.assertRaisesRegex(ValueError,'original differs'):self.produce()
 def test_capture_producer_or_work_receipt_cannot_be_rebound(self):
  result=copy.deepcopy(self.results[0]);result['actual_capture_producer_binding']['path']='/tmp/foreign-producer.py';binding=C.write(self.root/'bad-result.json',result)
  with self.assertRaisesRegex(ValueError,'selection/outcome'):self.produce([binding])
 def test_additional_cold_originals_are_required_and_not_reconstructed(self):
  result=copy.deepcopy(self.results[0]);result['original_capture_cold_receipt_reconstructed']=True;binding=C.write(self.root/'bad-cold-result.json',result)
  with self.assertRaisesRegex(ValueError,'cold replay original'):self.produce([binding])
 def test_assessment_requires_both_original_capture_stages_in_order(self):
  with self.assertRaisesRegex(ValueError,'both actual capture stages'):self.produce(self.bindings[:1],assessment=True)
  with self.assertRaisesRegex(ValueError,'in order'):self.produce(list(reversed(self.bindings)),assessment=True)

if __name__=='__main__':unittest.main()
