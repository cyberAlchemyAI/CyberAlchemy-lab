"""Causal preallocation checks against the actual selected commit method.

Pure harness: no source, native, grant, Session or journal qualification.
"""
import ast,copy,hashlib,json,sys,threading,types,unittest
from dataclasses import fields,dataclass
from datetime import datetime,timedelta,timezone
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v66-t16-durable-open-0001'
def compact(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def require(v,msg):
 if not v:raise ValueError(msg)
def digest(v):return hashlib.sha256(v).hexdigest()
class CommitChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  tree=ast.parse((API/'current_legacy_context_sessions.py').read_text());owner=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ContextSessions');method=copy.deepcopy(next(n for n in owner.body if isinstance(n,ast.FunctionDef) and n.name=='open'))
  seal=copy.deepcopy(next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_open_plan_digest'));module=ast.Module(body=[seal,method],type_ignores=[]);ast.fix_missing_locations(module)
  cls.namespace={'_plan_fields':fields,'_PlanDatetime':datetime,'EL':types.SimpleNamespace(SourceRecord=type('Record',(),{}),SignedRevisionWitness=type('Witness',(),{})),'__package__':'_t16_commit_checks','source':types.SimpleNamespace(require=require,sha=digest),'compact':compact,'now':lambda:datetime.now(timezone.utc),'instant':datetime.fromisoformat,'copy':copy,'threading':threading,'D':types.SimpleNamespace(FACT_SCOPE=types.SimpleNamespace(require_outside_scope=lambda:None))}
  exec(compile(module,str(API/'current_legacy_context_sessions.py'),'exec'),cls.namespace)
  cls.commit=staticmethod(cls.namespace['open'])
 def setUp(self):
  self.allocated=0;self.persisted=0;self.fresh=True;self.policy_fresh=True
  expires=(datetime.now(timezone.utc)+timedelta(seconds=30)).isoformat()
  self.message={'request_ref':'test:message','context_delivery_binding':{'ref':'test:delivery','sha256':'d'*64},'assignment':{'version_ref':'test:assignment'}};self.raw=compact(self.message);self.request={'ref':'test:request','sha256':digest(self.raw)};self.cut={'sequence':1}
  self.proof={'expires_at':expires};self.plan={'plan':{'expires_at':expires},'proof':copy.deepcopy(self.proof),'policy_sha256':'a'*64,'message_sha256':digest(self.raw),'request':self.request.copy(),'raw_sha256':digest(self.raw),'source_cut':self.cut.copy(),'family':{'test:path':'b'*64},'sid':'test:session','aid':'test:agent','started':datetime.now(timezone.utc).isoformat(),'agent':{},'session':{},'classification':{},'connections':[],'result':{'result':'active'}}
  self.owner=types.SimpleNamespace(closed=False,live={},timers={},mutex=threading.RLock(),source=types.SimpleNamespace(source_cut=self.cut.copy()),channel=types.SimpleNamespace(termination_guard=self.policy_guard,expected_sha='a'*64,policy={'principal_ref':'test:principal'},context={'principal_ref':'test:principal'}),delivery=lambda wanted:copy.deepcopy(self.proof),reserve_runtime_identities=lambda *args:None,persist=self.persist)
  self.owner._prepared_opens={(self.request['ref'],self.request['sha256']):(self.plan,self.namespace['_open_plan_digest'](self.plan))}
  self.owner.bridge=None;self.owner.expire=lambda sid:None
  outer=self
  class Resource:
   def __init__(self,*args):outer.allocated+=1;self.expires=datetime.fromisoformat(expires)
   def guard(self):pass
   def dispose(self):pass
  self.namespace['LiveReader']=Resource
  mod=types.ModuleType('_t16_commit_checks.session_source_freshness');mod.fresh_selected_source=self.fresh_guard
  self.modules=patch.dict(sys.modules,{'_t16_commit_checks':types.ModuleType('_t16_commit_checks'),'_t16_commit_checks.session_source_freshness':mod});self.modules.start();self.addCleanup(self.modules.stop)
 def policy_guard(self):require(self.policy_fresh,'private permission changed or revoked')
 def fresh_guard(self,*args):require(self.fresh,'selected physical source changed');return self.plan['family']
 def persist(self,*args):self.persisted+=1
 def invoke(self):return self.commit(self.owner,self.message,self.request,self.cut,self.raw,self.plan)
 def refused(self):
  with self.assertRaises(ValueError):self.invoke()
  self.assertEqual((self.allocated,self.persisted),(0,0))
 def test_unchanged_prepared_plan_reaches_allocation_once(self):
  result,_=self.invoke();self.assertEqual(result,{'result':'active'});self.assertEqual((self.allocated,self.persisted),(1,1));self.owner.timers['test:session'].cancel()
 def test_other_prepared_request_survives_first_commit(self):
  other=copy.deepcopy(self.plan);other['request']['ref']='other:request';key=(other['request']['ref'],other['request']['sha256']);self.owner._prepared_opens[key]=(other,self.namespace['_open_plan_digest'](other))
  self.invoke();self.owner.timers['test:session'].cancel();self.assertIn(key,self.owner._prepared_opens)
 def test_changed_prepared_bytes_refuse(self):self.plan['result']['result']='forged';self.refused()
 def test_changed_message_refuses(self):self.message['request_ref']='other';self.refused()
 def test_changed_cut_refuses(self):self.cut['sequence']=2;self.refused()
 def test_changed_private_policy_sha_refuses(self):self.owner.channel.expected_sha='c'*64;self.refused()
 def test_revoked_private_permission_refuses(self):self.policy_fresh=False;self.refused()
 def test_changed_physical_source_refuses(self):self.fresh=False;self.refused()
 def test_changed_delivery_refuses(self):self.proof['expires_at']=(datetime.now(timezone.utc)+timedelta(seconds=40)).isoformat();self.refused()
 def test_expired_session_refuses(self):
  self.plan['plan']['expires_at']=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat();self.owner._prepared_opens[(self.request['ref'],self.request['sha256'])]=(self.plan,self.namespace['_open_plan_digest'](self.plan));self.refused()
 def test_unminted_plan_refuses(self):self.owner._prepared_opens.clear();self.refused()
if __name__=='__main__':unittest.main(verbosity=2)
