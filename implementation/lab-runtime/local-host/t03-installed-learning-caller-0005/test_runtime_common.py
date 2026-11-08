"""Caller component checks; not native runtime or API qualification."""
import copy,importlib.util,json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_caller_common_test',HERE/'runtime_common.py');C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
class Tests(unittest.TestCase):
 def runtime(self,root,callback):
  r=object.__new__(C.Runtime);r.evidence=root/'evidence';r.evidence.mkdir(mode=0o700);r.surfaces={};r.pairs=[];r.sequence=0
  compact=lambda value:json.dumps(value,sort_keys=True,separators=(',',':')).encode()
  r.P=SimpleNamespace(compact=compact);r.F=SimpleNamespace(call=lambda context,op,arg,**kw:{'operation':op,**kw});r.schemas=SimpleNamespace(valid=lambda key,value:True,protocol_valid=lambda uri,value:True,profile_binding={'ref':'profile:test','sha256':'f'*64},operations={'lesson.apply':{'request_schema':{'resource_uri':'request:test'},'result_schema':{'resource_uri':'result:test'},'error_schema':{'resource_uri':'error:test'}}})
  workspace=root/'workspace';(workspace/'journal').mkdir(parents=True);(workspace/'objects').mkdir()
  host=SimpleNamespace(channel=SimpleNamespace(context={'context_ref':'context:current'}),vault=SimpleNamespace(root=workspace,control_binding={'ref':'workspace:test','sha256':'a'*64}),schemas=r.schemas)
  class Surface:
   def __init__(self,base):self.base=base;self.schemas=base.schemas
   def call(self,raw):
    reply=callback(host,json.loads(raw));return {**reply,'request_binding':{'ref':'call:test','sha256':C.sha(raw)},'contract_profile_binding':r.schemas.profile_binding}
  r.I=SimpleNamespace(IntegrationService=Surface)
  request={'operation':'lesson.apply','call_id':'call:positive','caller_context_ref':'context:current','deadline':'2026-10-24T12:00:00+00:00','message':{'actor':{'principal_ref':'principal:real'}}}
  r.helpers=SimpleNamespace(call=lambda *args,**kwargs:copy.deepcopy(request));r.M={}
  return r,host,request
 def test_actual_pending_files_survive_inspection(self):
  with tempfile.TemporaryDirectory() as d:
   r,host,_=self.runtime(Path(d),lambda *_:{'kind':'result','message':{'posture':'indeterminate'}})
   pending=host.vault.root/'journal/claim.json';pending.write_bytes(b'original actual pending claim')
   body=host.vault.root/'objects/body.json';body.write_bytes(b'original body')
   result=r.inspect_operation(host,'lesson.apply','exact:key','failed-application')
   self.assertEqual(result['message']['posture'],'indeterminate');self.assertEqual(pending.read_bytes(),b'original actual pending claim');self.assertEqual(body.read_bytes(),b'original body')
   receipt=json.loads((r.evidence/'failed-application-retained-journal.json').read_bytes());self.assertEqual(receipt['idempotency_key'],'exact:key');self.assertTrue(receipt['workspace_retained'])
 def test_refused_inspection_still_retains_original_journal(self):
  with tempfile.TemporaryDirectory() as d:
   def refuse(*_):raise ValueError('actual policy expired')
   r,host,_=self.runtime(Path(d),refuse);pending=host.vault.root/'journal/claim.json';pending.write_bytes(b'pending')
   result=r.inspect_operation(host,'lesson.apply','exact:key','failed-application')
   self.assertEqual(result['kind'],'inspection-refused');self.assertEqual(pending.read_bytes(),b'pending');self.assertTrue((r.evidence/'failed-application-inspect-failure.json').is_file())
 def test_causal_negative_preserves_actual_deadline_context_and_actor(self):
  with tempfile.TemporaryDirectory() as d:
   calls=[]
   def observe(host,request):
    calls.append(copy.deepcopy(request))
    return {'kind':'error','message':{'code':'unauthorized'}} if len(calls)==1 else {'kind':'result','message':{'okay':True}}
   r,host,original=self.runtime(Path(d),observe)
   self.assertEqual(r.call(host,'lesson.apply',original['message'],'key'),{'okay':True})
   self.assertEqual(calls[0]['deadline'],calls[1]['deadline']);self.assertEqual(calls[0]['caller_context_ref'],calls[1]['caller_context_ref']);self.assertEqual(calls[1],original)
   changed=copy.deepcopy(calls[0]);changed['call_id']=original['call_id'];changed['message']['actor']['principal_ref']=original['message']['actor']['principal_ref'];self.assertEqual(changed,original)
 def test_negative_side_effect_stops_before_positive(self):
  with tempfile.TemporaryDirectory() as d:
   calls=[]
   def violate(host,request):calls.append(request);(host.vault.root/'journal/leak.json').write_bytes(b'bad');return {'kind':'error','message':{'code':'unauthorized'}}
   r,host,original=self.runtime(Path(d),violate)
   with self.assertRaisesRegex(ValueError,'negative changed owned Vault'):r.call(host,'lesson.apply',original['message'],'key')
   self.assertEqual(len(calls),1)
 def test_object_staging_without_claim_is_a_negative_side_effect(self):
  with tempfile.TemporaryDirectory() as d:
   def violate(host,request):(host.vault.root/'objects/unclaimed.json').write_bytes(b'unclaimed staging');return {'kind':'error','message':{'code':'unauthorized'}}
   r,host,original=self.runtime(Path(d),violate)
   with self.assertRaisesRegex(ValueError,'negative changed owned Vault'):r.call(host,'lesson.apply',original['message'],'key')
   self.assertEqual(list((host.vault.root/'journal').iterdir()),[])
if __name__=='__main__':unittest.main()
