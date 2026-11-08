"""Actual rule-control candidate checks over synthetic native transport only."""
import copy
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import retained as R
import rule_control as C
import test_control_probe as CP

class RuleControl(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='cal-rule-control-component-');self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.root.chmod(0o700)
  self.source='a'*64;self.profile='b'*64;self.cut={'synthetic-component':True};self.request={'operation':'failure.assess','expected_source_cut':self.cut}
  self.compact=lambda v:json.dumps(v,sort_keys=True,separators=(',',':')).encode();self.request_sha=R.sha(self.compact(self.request))
  error=json.loads((CP.ROOT/'docs/proposals/0007-lab-integrated-schema-package/examples/error-result.json').read_bytes());error['code']='closure-missing'
  self.reply={'operation':'failure.assess','kind':'error','request_binding':{'sha256':self.request_sha},'contract_profile_binding':{'sha256':self.profile},'message':error}
  self.report={'schema_version':'lab-failure-assessment-rule-checks/v1-candidate','result':'not-evaluable','confirmed_cause_inferred':False,'recovery_or_control_effectiveness_inferred':False}
  mode=json.loads((C.ROOT/'authority/artifact-types/failure-mode/v1/fixtures/valid/record.json').read_bytes());self.mode={'scope_ref':'project:synthetic','identity_ref':mode['node_id'],'version_ref':mode['node_id']+'@1','carrier_ref':'cal.artifact-type.failure-mode/v1','byte_sha256':R.sha(self.compact(mode))};self.records={self.mode['version_ref']:(self.mode,self.compact(mode))}
  self.body=json.loads((C.ROOT/'authority/artifact-types/failure-control-binding/v1/fixtures/valid/record.json').read_bytes());self.body.update(node_id='failure-control-binding:synthetic',scope_ref=self.mode['scope_ref'],lifecycle_state='candidate',authority_effect='none')
  self.body['payload'].update(failure_mode_ref=self.mode['version_ref'],control_subject_ref=C.CONTROL_ID,primary_control_role='detect',installation_posture='candidate-local-runtime-observation',effectiveness_evidence_refs=[])
  self.archive=self.root/'archive';self.archive.mkdir(mode=0o700);(self.archive/'vault').mkdir(mode=0o700);(self.archive/'vault/objects').mkdir(mode=0o700)
  self.result={};self.seal()
  schemas=CP.Schemas();schemas.guard=lambda:None
  protocol=SimpleNamespace(Schemas=lambda pin:schemas,compact=self.compact)
  selected=SimpleNamespace(root=lambda:C.ROOT,guard=lambda:None,binding=lambda key:{'sha256':self.source if key=='api.source' else self.profile},current=lambda:SimpleNamespace(package={'entrypoint':{'api_directory':'synthetic-api'}}))
  self.patches=[patch.dict(sys.modules,{'cal_installed_runtime_selection_v1':selected}),patch.object(C.importlib,'import_module',return_value=protocol)]
  for p in self.patches:p.start();self.addCleanup(p.stop)
 def put(self,path,body):
  raw=self.compact(body);path.write_bytes(raw);path.chmod(0o600);return {'ref':str(path),'sha256':R.sha(raw)}
 def seal(self):
  rb=self.put(self.root/'reply.json',self.reply);pb=self.put(self.root/'report.json',self.report)
  self.body['payload']['execution_evidence_refs']=[rb['ref'],pb['ref']];cb=self.put(self.root/'candidate.json',self.body)
  header={'scope_ref':self.body['scope_ref'],'identity_ref':self.body['node_id'],'version_ref':self.body['node_id']+'@candidate.1','carrier_ref':'cal.artifact-type.failure-control-binding/v1','byte_sha256':cb['sha256']}
  report=self.compact(self.report);member='vault/objects/'+R.sha(report)+'.json';p=self.archive/member
  for old in (self.archive/'vault/objects').iterdir():old.unlink()
  p.write_bytes(report);p.chmod(0o600)
  obs={'schema_version':'lab-retained-actual-caller-vault/v1','Reader_credentials_retained':False,'current_permission_or_Session_reconstructed':False,'authority_effect':'none',
   'observation':{'operation':'failure.assess','mode':'controlled-unknown-rule','known_domain_refusal_is_recorded_metadata_effect':True,'actual_reply':self.reply,'api_source_sha256':self.source,'api_profile_sha256':self.profile,'original_request':self.request},
   'files':[{'path':member,'sha256':R.sha(report),'size_bytes':len(report)}]}
  ob=self.put(self.archive/'OBSERVATION.json',obs)
  self.result.update(schema_version='lab-actual-failure-rule-control-observation/v1',result='PASS-actual-known-rule-refusal-and-candidate-detect-binding',actual_native_common_dispatcher=True,metadata_effect_recorded=True,
   actual_rule_result='not-evaluable',known_result_retry_read_only=True,control_effectiveness_established=False,canonical_admissions=0,authority_effect='none',semantic_control_identity=C.CONTROL_ID,
   actual_rule_source_binding={'ref':C.RULE_REF,'sha256':C.RULE_SHA},api_source_sha256=self.source,api_profile_sha256=self.profile,actual_reply_binding=rb,actual_rule_report_binding=pb,candidate_original_binding=cb,
   retained_originals={'path':str(self.archive),'observation_sha256':ob['sha256']},original_request_sha256=self.request_sha,source_cut=self.cut,original_failure_mode=self.mode,candidate_output=header)
  self.result_binding=self.put(self.root/'RESULT.json',self.result)
 def produce(self,operation='failure.assess',originals=None):return C.produce(records=self.records,observations=[{'actual_reply':{'operation':operation,'kind':'result'},'outputs':list(self.records.values())if originals is None else originals,'original_source_cut':self.cut,'observation_binding':{'ref':'synthetic:successful-failure-producer'}}],controls={'result_binding':self.result_binding})
 def test_complete_exact_observation_preserves_candidate_bytes_and_ceiling(self):
  out=self.produce();self.assertEqual(out['records'][0][1],R.read(Path(self.result['candidate_original_binding']['ref'])));self.assertFalse(out['receipt']['control_effectiveness_established'])
 def test_domain_invalid_reply_cannot_be_accepted_by_outer_envelope(self):
  self.reply['message']['undeclared']=True;self.seal()
  with self.assertRaisesRegex(ValueError,'error-domain'):self.produce()
 def test_mode_or_source_correspondence_refuses(self):
  self.records.clear()
  with self.assertRaisesRegex(ValueError,'failure Mode'):self.produce()
 def test_other_operation_or_different_original_cannot_supply_assessed_mode(self):
  with self.assertRaisesRegex(ValueError,'Mode producer/source'):self.produce(operation='change.prepare')
  h,raw=self.records[self.mode['version_ref']]
  with self.assertRaisesRegex(ValueError,'Mode producer/source'):self.produce(originals=[(h,raw+b' ')])
 def test_inferred_effectiveness_or_actual_control_relabel_refuses(self):
  self.body['payload']['effectiveness_evidence_refs']=['invented:effectiveness'];self.seal()
  with self.assertRaisesRegex(ValueError,'semantics'):self.produce()
 def test_inference_in_rule_report_or_extra_archive_member_refuses(self):
  self.report['confirmed_cause_inferred']=True;self.seal()
  with self.assertRaisesRegex(ValueError,'inference ceiling'):self.produce()
  self.report['confirmed_cause_inferred']=False;self.seal();p=self.archive/'extra.json';p.write_bytes(b'{}');p.chmod(0o600)
  with self.assertRaisesRegex(ValueError,'complete actual'):self.produce()

if __name__=='__main__':unittest.main()
