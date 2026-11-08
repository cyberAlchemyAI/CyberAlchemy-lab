"""Actual schemas/signed fixture originals; synthetic Session/API transport only."""
import copy
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import learning_records as P

class Learning(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='cal-learning-records-component-');self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.root.chmod(0o700)
  self.api={'path':'synthetic-api/source-manifest.json','sha256':'a'*64};self.profile={'path':'synthetic-api/profile.json','sha256':'b'*64}
  dataset=json.loads((P.ROOT/'implementation/lab-runtime/local-host/t03-long-local-fixture-0001/instances/legacy-local-de585bd7df9a130d/portable-dataset.json').read_bytes());self.bindings=dataset['bindings'];self.family=self.bindings['family.source']
  index=json.loads((P.ROOT/self.bindings['family.record_index']['path']).read_bytes());row=next(r for r in index if r['kind']=='operational-lesson');self.lesson_raw=(P.ROOT/row['original_binding']['path']).read_bytes();lesson=json.loads(self.lesson_raw);self.scope=lesson['scope_ref'];self.cut={'synthetic-only':True}
  self.lesson_h={'scope_ref':self.scope,'identity_ref':lesson['node_id'],'version_ref':row['version_ref'],'carrier_ref':row['carrier_ref'],'byte_sha256':P.R.sha(self.lesson_raw)}
  self.first=self.terminal('first');self.later=self.terminal('later')
  self.first.update(result='PASS-local-current-one-Lesson-selection-and-close',selection_registry_erased=True,explicitly_closed=True,memory_erased=True,closed_refused=True)
  self.report={'schema_version':'lab-T03-live-Lesson-inspection-output/v1-candidate','source_cut':self.cut,'fixture_only':True,'authority_effect':'none','lesson':self.lesson_h,'project_ref':self.scope,'observed_discrepancies':[],'producer_binding':{'path':'synthetic:inspection-method','sha256':'p'*64},'selection_sha256':'s'*64}
  self.counter={'schema_version':'lab-T03-inspection-counterevidence/v1-candidate','source_cut':self.cut,'result':'observed-selection-does-not-establish-state-correctness','authority_effect':'none'}
  app=json.loads((P.ROOT/'authority/artifact-types/lesson-application/v1/fixtures/valid/record.json').read_bytes());app.update(node_id='lesson-application:synthetic',scope_ref=self.scope);app['payload'].update(session_ref='session:synthetic:later',lesson_revision_ref=self.lesson_h['version_ref']);self.app=app
  assessment=json.loads((P.ROOT/'authority/artifact-types/lesson-outcome-assessment/v1/fixtures/valid/record.json').read_bytes());assessment.update(node_id='lesson-outcome-assessment:synthetic',scope_ref=self.scope,owner_ref='principal:T03-independent-assessor');assessment['payload'].update(lesson_application_ref=app['node_id']+'@candidate.1',disposition='recorded-outcome-only',causal_claim_ceiling='Exact recorded application outcome only; no general or causal effectiveness inferred.');self.assessment=assessment
  self.events=[{'phase':phase,'state':'passed','at_utc':'2026-10-26T00:0'+str(i+1)+':00+00:00'}for i,phase in enumerate(['lesson-influenced-inspection','parent.close-before-assessment','lesson.assess'])]
  self.seal()
  portable=SimpleNamespace(binding=lambda key:copy.deepcopy(self.bindings[key]));protocol=SimpleNamespace(source=SimpleNamespace(original=lambda b:(P.ROOT/b['path']).read_bytes()))
  actual=SimpleNamespace(root=lambda:P.ROOT,guard=lambda:None,binding=lambda key:copy.deepcopy(self.api if key=='api.source'else self.profile if key=='api.profile'else self.family),current=lambda:SimpleNamespace(package={'entrypoint':{'api_directory':'synthetic-api'}}))
  patches=[patch.dict(sys.modules,{'cal_installed_runtime_selection_v1':actual}),patch.object(P.importlib,'import_module',side_effect=lambda name:portable if name.endswith('.runtime_selection')else protocol)]
  for p in patches:p.start();self.addCleanup(p.stop)
 def put(self,name,raw):
  raw=raw if type(raw)is bytes else P.enc(raw);path=self.root/name;path.write_bytes(raw);path.chmod(0o600);return {'ref':str(path),'sha256':P.R.sha(raw)}
 def terminal(self,label):
  sid='session:synthetic:'+label;body=json.loads((P.ROOT/'authority/artifact-types/agent-session/v1/fixtures/valid/record.json').read_bytes());body.update(node_id=sid,scope_ref=self.scope);body['payload']['session_memory'].update(working_record_refs=[],unresolved_questions=[],expires_with_session=True)
  value={'session_ref':sid,'formal_session_body':body,'source_cut':self.cut,'api_source_binding':self.api,'family_source_binding':self.family,'short_memory_exported':False,'authority_effect':'none'}
  b=self.put(label+'-formal.json',value)
  return {'api_source_binding':self.api,'profile_binding':self.profile,'family_source_binding':self.family,'source_cut':self.cut,'session_ref_sha256':P.R.sha(sid.encode()),'lesson_version_ref_sha256':P.R.sha(self.lesson_h['version_ref'].encode()),'formal_session_binding':{'path':b['ref'],'sha256':b['sha256']},'fixture_only':True,'authority_effect':'none'}
 def seal(self):
  self.files={'lesson':self.put('lesson.json',self.lesson_raw),'report':self.put('report.json',self.report),'counterevidence':self.put('counter.json',self.counter),'application':self.put('app.json',self.app),'assessment':self.put('assessment.json',self.assessment),'events':self.put('events.jsonl',b'\n'.join(P.enc(e)for e in self.events)+b'\n')}
  self.observations=[];self.records={};replies={}
  for operation,body,kind,key in [('lesson.apply',self.app,'lesson-application','application'),('lesson.assess',self.assessment,'lesson-outcome-assessment','assessment')]:
   raw=P.enc(body);h={'scope_ref':self.scope,'identity_ref':body['node_id'],'version_ref':body['node_id']+'@candidate.1','carrier_ref':'cal.artifact-type.'+kind+'/v1','byte_sha256':P.R.sha(raw)};self.records[h['version_ref']]=(h,raw);message={'targets':[{'artifact':h}]};replies[key]=P.R.sha(P.enc(message));self.observations.append({'actual_reply':{'operation':operation,'kind':'result','message':message},'original_source_cut':self.cut,'outputs':[(h,raw)],'observation_binding':{'ref':'synthetic:'+operation}})
  fb=self.put('FIRST.json',self.first);self.later.update(result='PASS-local-current-Lesson-later-application-independent-assessment',first_session_receipt={'path':fb['ref'],'sha256':fb['sha256']},actual_later_work={'parent_session_closed':True,'independent_assessment_after_parent_close':True,'fixture_only':True,'authority_effect':'none','actual_owner_outcome':None,'inspection_output_sha256':self.files['report']['sha256'],'counterevidence_sha256':self.files['counterevidence']['sha256'],'assessment_candidate_sha256':self.files['assessment']['sha256'],'actual_discrepancy_count':len(self.report['observed_discrepancies']),'application_reply_sha256':replies['application'],'assessment_reply_sha256':replies['assessment']});lb=self.put('LATER.json',self.later);self.controls={'first_binding':fb,'later_binding':lb,'files':self.files}
 def produce(self):return P.produce(records=self.records,observations=self.observations,controls=self.controls)
 def test_exact_formal_identity_and_source_authored_lesson_are_preserved(self):
  out=self.produce();self.assertEqual(len(out['records']),4);self.assertEqual(out['receipt']['actual_later_session_ref'],'session:synthetic:later');self.assertFalse(out['receipt']['new_human_reviewed_Lesson_created']);self.assertEqual(out['records'][-1][1],self.lesson_raw)
 def test_hash_cannot_substitute_for_actual_session_identity(self):
  path=Path(self.later['formal_session_binding']['path']);value=json.loads(path.read_bytes());value['session_ref']=self.later['session_ref_sha256'];b=self.put(path.name,value);self.later['formal_session_binding']={'path':b['ref'],'sha256':b['sha256']};self.seal()
  with self.assertRaisesRegex(ValueError,'formal Session identity'):self.produce()
 def test_working_memory_cannot_enter_formal_receipt(self):
  path=Path(self.later['formal_session_binding']['path']);value=json.loads(path.read_bytes());value['formal_session_body']['payload']['session_memory']['working_record_refs']=['private-note'];b=self.put(path.name,value);self.later['formal_session_binding']={'path':b['ref'],'sha256':b['sha256']};self.seal()
  with self.assertRaisesRegex(ValueError,'refs-only memory'):self.produce()
 def test_assessment_before_actual_close_or_wrong_session_refuses(self):
  self.events[2]['at_utc']='2026-10-26T00:00:00+00:00';self.seal()
  with self.assertRaisesRegex(ValueError,'event order'):self.produce()
  self.events[2]['at_utc']='2026-10-26T00:03:00+00:00';self.app['payload']['session_ref']='session:foreign';self.seal()
  with self.assertRaisesRegex(ValueError,'semantic chain'):self.produce()
 def test_changed_original_lesson_or_missing_actual_api_output_refuses(self):
  self.observations.pop()
  with self.assertRaisesRegex(ValueError,'actual learning API producer'):self.produce()

if __name__=='__main__':unittest.main()
