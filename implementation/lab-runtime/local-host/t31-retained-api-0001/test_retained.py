"""Terminal/custody failure tests with wholly synthetic operation observations."""
import base64
import copy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
import retained as R
class Retained(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='cal-retained-producer-test-');self.addCleanup(self.temp.cleanup)
  self.root=Path(self.temp.name);self.root.chmod(0o700);self.archive=self.root/'archive';self.archive.mkdir(mode=0o700)
  (self.archive/'vault').mkdir(mode=0o700);(self.archive/'vault/objects').mkdir(mode=0o700)
  self.body=b'{ "kind":"synthetic-component-only", "authority_effect":"none" }\n';digest=R.sha(self.body)
  self.object=self.archive/'vault/objects'/(digest+'.json');self.object.write_bytes(self.body);self.object.chmod(0o600)
  self.source='a'*64;self.profile='b'*64;self.operation='failure.assess';self.terminal=self.root/'terminal.json'
  self.request={'operation':self.operation,'expected_source_cut':{'store_ref':'synthetic-component'}};raw=json.dumps(self.request).encode()
  header={'scope_ref':'scope:synthetic','identity_ref':'synthetic:component','version_ref':'synthetic:component@1','carrier_ref':'cal.artifact-type.synthetic/v1','byte_sha256':digest}
  self.reply={'operation':self.operation,'kind':'result','request_binding':{'sha256':R.sha(raw)},'contract_profile_binding':{'ref':'synthetic-profile','sha256':self.profile},'message':{'targets':[{'artifact':header,'operation':'admit','content':{'content_ref':'synthetic:content','byte_sha256':digest,'size_bytes':len(self.body),'media_type':'application/json'}}]}}
  self.workspace=self.archive/'vault/workspace.json';self.workspace.write_text(json.dumps({'materials':[{'ref':'synthetic:content','path':'objects/'+self.object.name,'sha256':digest}]}));self.workspace.chmod(0o600)
  self.case={'operation':self.operation,'result':'PASS','expected_kind':'result','request_sha256':R.sha(raw),'original_request_base64':base64.b64encode(raw).decode(),'actual_reply':self.reply}
  self.observation={'schema_version':'lab-retained-actual-caller-vault/v1','Reader_credentials_retained':False,'current_permission_or_Session_reconstructed':False,
   'requires_unit_terminal_PASS':True,'authority_effect':'none','observation':{'source_sha256':self.source,'profile_sha256':self.profile,'unit':'fixture:failure.assess','case':self.case,'original_request':self.request},
   'files':[{'path':'vault/objects/'+self.object.name,'sha256':digest,'size_bytes':len(self.body)},{'path':'vault/workspace.json','sha256':R.sha(self.workspace.read_bytes()),'size_bytes':self.workspace.stat().st_size}]}
  self.status='PASS';self.seal()
 def seal(self):
  raw=json.dumps(self.observation).encode();p=self.archive/'OBSERVATION.json';p.write_bytes(raw);p.chmod(0o600);self.pin=R.sha(raw)
  case=copy.deepcopy(self.case);case['retained_originals']={'path':str(self.archive),'observation_sha256':self.pin}
  terminal={'result':self.status,'source_sha256':self.source,'profile_sha256':self.profile,'unit':'fixture:failure.assess','cases':[case]}
  raw=json.dumps(terminal).encode();self.terminal.write_bytes(raw);self.terminal.chmod(0o600);self.tpin=R.sha(raw)
 def consume(self):return R.consume(archive=self.archive,observation_sha256=self.pin,terminal_result=self.terminal,terminal_sha256=self.tpin,source_sha256=self.source,profile_sha256=self.profile,operation=self.operation)
 def test_actual_original_byte_preservation_and_explicit_historical_ceiling(self):
  got=self.consume();self.assertEqual(got['outputs'][0][1],self.body);self.assertFalse(got['retained_originals_are_Source_current']);self.assertFalse(got['old_permission_or_Session_reconstructed'])
 def test_review_package_uses_its_two_actual_generated_carriers(self):
  self.operation='proposal.review';self.request['operation']=self.operation;raw=json.dumps(self.request).encode()
  header=self.reply['message']['targets'][0]['artifact'];other=copy.deepcopy(header);other['identity_ref']='synthetic:checkpoint';other['version_ref']='synthetic:checkpoint@1'
  self.reply.update(operation=self.operation,request_binding={'sha256':R.sha(raw)},message={'decision_bundle':header,'checkpoint':other})
  self.case.update(operation=self.operation,request_sha256=R.sha(raw),original_request_base64=base64.b64encode(raw).decode())
  self.seal();got=self.consume();self.assertEqual(len(got['outputs']),2)
 def projection(self):
  self.operation='ontology.project';self.request['operation']=self.operation;raw=json.dumps(self.request).encode()
  header=self.reply['message']['targets'][0]['artifact'];header=copy.deepcopy(header);header['carrier_ref']='cal.artifact-type.ontology-view/v1'
  receipt={'schema_version':'lab-ontology-projection-receipt/v1-candidate','posture':'applied','lab_source_cut':self.request['expected_source_cut'],
           'authority_effect':'none','recovery_required':False,'ontology_view':header}
  self.reply.update(operation=self.operation,request_binding={'sha256':R.sha(raw)},message=receipt)
  self.case.update(operation=self.operation,request_sha256=R.sha(raw),original_request_base64=base64.b64encode(raw).decode())
  original=json.dumps(receipt,indent=3).encode()+b'\n';path=self.archive/'vault/objects'/(R.sha(original)+'.json');path.write_bytes(original);path.chmod(0o600)
  self.observation['files'].append({'path':'vault/objects/'+path.name,'sha256':R.sha(original),'size_bytes':len(original)});self.seal();return path,original
 def test_projection_receipt_and_returned_view_are_preserved_without_inferred_headers(self):
  path,raw=self.projection();got=self.consume();self.assertEqual(got['projection_producer']['receipt_original'],raw)
  self.assertEqual(len(got['outputs']),1);self.assertEqual(got['outputs'][0][0]['carrier_ref'],'cal.artifact-type.ontology-view/v1')
  self.assertFalse(got['projection_producer']['typed_generation_headers_inferred'])
 def test_projection_refuses_missing_original_receipt_or_wrong_cut(self):
  path,raw=self.projection();path.unlink();self.observation['files']=self.observation['files'][:-1];self.seal()
  with self.assertRaisesRegex(ValueError,'projection result original'):self.consume()
  self.reply['message']['lab_source_cut']={'foreign':True};self.seal()
  with self.assertRaisesRegex(ValueError,'bounded representation'):self.consume()
 def test_prospective_candidate_preserves_actual_input_original_without_object_copy(self):
  (self.archive/'vault/inputs').mkdir(mode=0o700);target=self.archive/'vault/inputs/candidate.json';self.object.rename(target)
  workspace={'materials':[{'ref':'synthetic:content','path':'inputs/candidate.json','sha256':R.sha(self.body)}]};self.workspace.write_text(json.dumps(workspace))
  self.observation['files'][0]['path']='vault/inputs/candidate.json';self.observation['files'][1].update(sha256=R.sha(self.workspace.read_bytes()),size_bytes=self.workspace.stat().st_size);self.seal()
  self.assertEqual(self.consume()['outputs'][0][1],self.body)
  self.reply['message']['targets'][0]['content']['content_ref']='invented:content';self.seal()
  with self.assertRaisesRegex(ValueError,'selected original material'):self.consume()
 def test_api_created_candidate_object_exact_workspace_address(self):
  digest=R.sha(self.body);workspace_ref='synthetic-workspace'
  self.workspace.write_text(json.dumps({'workspace_ref':workspace_ref,'materials':[]}))
  self.reply['message']['targets'][0]['content']['content_ref']='workspace-object:'+workspace_ref+':'+digest
  self.observation['files'][1].update(sha256=R.sha(self.workspace.read_bytes()),size_bytes=self.workspace.stat().st_size);self.seal()
  self.assertEqual(self.consume()['outputs'][0][1],self.body)
  self.reply['message']['targets'][0]['content']['content_ref']='workspace-object:foreign:'+digest;self.seal()
  with self.assertRaisesRegex(ValueError,'namespace differs'):self.consume()
  self.reply['message']['targets'][0]['content']['content_ref']='workspace-object:'+workspace_ref+':'+digest
  self.reply['message']['targets'][0]['content']['size_bytes']+=1;self.seal()
  with self.assertRaisesRegex(ValueError,'address or bytes differ'):self.consume()
 def test_api_created_object_and_selected_material_alias_must_match(self):
  digest=R.sha(self.body);workspace_ref='synthetic-workspace'
  ref='workspace-object:'+workspace_ref+':'+digest
  (self.archive/'vault/inputs').mkdir(mode=0o700);alias=self.archive/'vault/inputs/alias.json';alias.write_bytes(self.body);alias.chmod(0o600)
  self.workspace.write_text(json.dumps({'workspace_ref':workspace_ref,
      'materials':[{'ref':ref,'path':'inputs/alias.json','sha256':digest}]}))
  self.reply['message']['targets'][0]['content']['content_ref']=ref
  self.observation['files'][1].update(sha256=R.sha(self.workspace.read_bytes()),size_bytes=self.workspace.stat().st_size)
  self.observation['files'].append({'path':'vault/inputs/alias.json','sha256':digest,'size_bytes':len(self.body)})
  self.seal();self.assertEqual(self.consume()['outputs'][0][1],self.body)
  self.workspace.write_text(json.dumps({'workspace_ref':workspace_ref,
      'materials':[{'ref':ref,'path':'inputs/alias.json','sha256':'0'*64}]}))
  self.observation['files'][1].update(sha256=R.sha(self.workspace.read_bytes()),size_bytes=self.workspace.stat().st_size);self.seal()
  with self.assertRaisesRegex(ValueError,'alias digest differs'):self.consume()
  self.workspace.write_text(json.dumps({'workspace_ref':workspace_ref,
      'materials':[{'ref':ref,'path':'inputs/alias.json','sha256':digest}]}))
  self.observation['files'][1].update(sha256=R.sha(self.workspace.read_bytes()),size_bytes=self.workspace.stat().st_size)
  alias.write_bytes(b'{}');self.observation['files'][-1].update(sha256=R.sha(b'{}'),size_bytes=2);self.seal()
  with self.assertRaisesRegex(ValueError,'material alias differs'):self.consume()
 def test_changed_original_refused(self):
  self.object.write_bytes(self.body+b' ')
  with self.assertRaisesRegex(ValueError,'member differs'):self.consume()
 def test_failed_or_wrong_terminal_case_cannot_authorize_evidence(self):
  self.status='FAIL';self.seal()
  with self.assertRaisesRegex(ValueError,'passing exact'):self.consume()
 def test_substituted_request_reply_binding_refused_even_with_resealed_observation(self):
  self.reply['request_binding']['sha256']='0'*64;self.seal()
  with self.assertRaisesRegex(ValueError,'request/reply'):self.consume()
 def test_extra_or_linked_archive_member_refused(self):
  extra=self.archive/'unexpected';extra.write_bytes(b'owned test');extra.chmod(0o600)
  with self.assertRaisesRegex(ValueError,'closure differs'):self.consume()
  extra.unlink();body=self.root/'actual-body';body.write_bytes(self.body);body.chmod(0o600);self.object.unlink();self.object.symlink_to(body)
  with self.assertRaises((OSError,ValueError)):self.consume()
 def test_credential_content_cannot_enter_producer_evidence(self):
  raw=b'-----BEGIN PRIVATE KEY-----';self.object.write_bytes(raw);self.observation['files'][0].update(sha256=R.sha(raw),size_bytes=len(raw));self.seal()
  with self.assertRaisesRegex(ValueError,'credential'):self.consume()
if __name__=='__main__':unittest.main()
