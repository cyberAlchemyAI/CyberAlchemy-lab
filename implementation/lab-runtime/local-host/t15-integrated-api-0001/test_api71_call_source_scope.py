"""Pure causal checks of actual Reader call-scope code; no live qualification."""
import ast,copy,threading,types,unittest
from contextlib import contextmanager
from datetime import datetime,timedelta,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v71-t15-integrated-closure-0001'
def require(value,message):
 if not value:raise ValueError(message)
class SourceCallScope(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  tree=ast.parse((API/'auth.py').read_text());original=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ReaderChannel');methods=[copy.deepcopy(n) for n in original.body if isinstance(n,ast.FunctionDef) and n.name in ('verified_source_call','guard','termination_guard')]
  model=ast.ClassDef(name='ReaderChannel',bases=[],keywords=[],body=methods,decorator_list=[],type_params=[]);unit=ast.Module(body=[model],type_ignores=[]);ast.fix_missing_locations(unit)
  cls.ns={'source':types.SimpleNamespace(require=require),'copy':copy,'contextmanager':contextmanager,'instant':datetime.fromisoformat,'now':lambda:datetime.now(timezone.utc)};exec(compile(unit,str(API/'auth.py'),'exec'),cls.ns);cls.Reader=cls.ns['ReaderChannel']
 def setUp(self):
  self.ns['now']=lambda:datetime.now(timezone.utc)
  self.reader=self.Reader();self.reader._source_call_local=threading.local();self.reader.expected_sha='a'*64;self.reader.connection='connection:fixture';self.reader.context={'context_ref':'opaque:actual-authentication','expires_at':(datetime.now(timezone.utc)+timedelta(seconds=60)).isoformat()};self.reader.bound_termination_call=False
  self.full=0;self.live=0;self.permission=True;self.physical=True
  def policy(check_source=True):
   if check_source:self.full+=1;require(self.physical,'full original source changed')
   require(self.permission,'actual private permission revoked')
  self.reader.policy_guard=policy
  def fresh():
   self.live+=1;require(self.physical,'fresh physical source changed');return self.reader.termination_guard()
  self.bridge=types.SimpleNamespace(channel=self.reader,live_guard=fresh)
 def test_one_full_proof_but_every_boundary_rechecks_permission(self):
  with self.reader.verified_source_call(self.bridge) as allowed:
   self.assertTrue(allowed)
   for _ in range(4):self.reader.guard()
  self.assertEqual(self.full,1);self.assertEqual(self.live,5);self.assertIsNone(getattr(self.reader._source_call_local,'value',None))
 def test_next_call_requires_full_proof_again(self):
  with self.reader.verified_source_call(self.bridge):self.reader.guard()
  self.reader.guard();self.assertEqual(self.full,2)
 def test_changed_physical_source_refuses_within_call(self):
  with self.reader.verified_source_call(self.bridge):
   self.physical=False
   with self.assertRaises(ValueError):self.reader.guard()
 def test_revocation_is_not_cached(self):
  with self.reader.verified_source_call(self.bridge):
   self.permission=False
   with self.assertRaises(ValueError):self.reader.guard()
 def test_actual_clock_is_not_cached(self):
  with self.reader.verified_source_call(self.bridge):
   self.ns['now']=lambda:datetime.now(timezone.utc)+timedelta(seconds=120)
   with self.assertRaises(ValueError):self.reader.guard()
 def test_opaque_context_substitution_refuses(self):
  with self.reader.verified_source_call(self.bridge):
   self.reader.context['context_ref']='forged:wire-claim'
   with self.assertRaises(ValueError):self.reader.guard()
 def test_changed_policy_sha_refuses(self):
  with self.reader.verified_source_call(self.bridge):
   self.reader.expected_sha='b'*64
   with self.assertRaises(ValueError):self.reader.guard()
 def test_scope_cleanup_on_exception(self):
  with self.assertRaises(RuntimeError):
   with self.reader.verified_source_call(self.bridge):raise RuntimeError('fixture')
  self.assertIsNone(getattr(self.reader._source_call_local,'value',None))
 def test_scope_does_not_cross_threads(self):
  with self.reader.verified_source_call(self.bridge):
   seen=[]
   def child():seen.append(self.reader.guard())
   thread=threading.Thread(target=child);thread.start();thread.join()
   self.assertEqual(len(seen),1);self.assertEqual(self.full,2)
 def test_scope_cannot_nest(self):
  with self.reader.verified_source_call(self.bridge):
   with self.assertRaises(ValueError):
    with self.reader.verified_source_call(self.bridge):pass
 def test_invalid_entry_yields_no_scope(self):
  self.permission=False
  with self.reader.verified_source_call(self.bridge) as allowed:self.assertFalse(allowed)
  self.assertIsNone(getattr(self.reader._source_call_local,'value',None))
 def test_another_channel_cannot_supply_scope(self):
  self.bridge.channel=object()
  with self.assertRaises(ValueError):
   with self.reader.verified_source_call(self.bridge):pass
if __name__=='__main__':unittest.main(verbosity=2)
