"""Actual isolated-store context, references and short-memory lifecycle checks."""
import base64,copy,json
from pathlib import Path
import shutil,sys
from tempfile import TemporaryDirectory
import unittest
PACKAGE=Path(__file__).resolve().parents[1];ROOT=PACKAGE.parents[3];sys.path.insert(0,str(PACKAGE));sys.path.insert(0,str(PACKAGE/'tests'))
import test_replay
from test_replay import Store,keygen,example,LEGACY
from lab_runtime.common import RuntimeFault,byte_digest,digest,encoded,load,sealed
from lab_runtime.profiles import select
from lab_runtime.replay import ReplayPins
from lab_runtime.session import Session,reference
from lab_runtime.sources import capture
from lab_runtime.store import VerifiedLegacyReadStore

class Clock:
 def __init__(self):self.value=1000.0
 def __call__(self):return self.value

class SessionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.observed_packs=[]
  cls.temp=TemporaryDirectory(prefix='lab-context-source-fixture-');cls.root=Path(cls.temp.name);cls.repository=cls.root/'repository';cls.repository.mkdir()
  row=next(x for x in load(PACKAGE/'profiles/selections.json')['selections'] if x['name']=='d75');cls.row=row
  cls.snapshot=capture(select(ROOT,**{k:v for k,v in row.items() if k not in ['name','source_materials','source_bytes']}))
  files={p:base64.b64decode(v) for p,v in cls.snapshot['byte_contents'].items()}
  files.update({cls.snapshot['controls'][name]['path']:base64.b64decode(v) for name,v in cls.snapshot['control_bytes'].items()})
  files.update({p:base64.b64decode(v) for p,v in cls.snapshot['executable_byte_contents'].items()})
  for names in cls.snapshot['epoch_inventory'].values():
   for path in names:files[path]=(ROOT/path).read_bytes()
  for name,raw in files.items():
   p=cls.repository/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
  cls.private=cls.root/'test-only.pem';public=cls.root/'test-only.pub';keygen(cls.private,public)
  cls.fixture=cls.root/'store';Store(cls.fixture,cls.repository).initialize(load(LEGACY/'profile.json'),'context-fixture','role:test-only-candidate-operator',public.read_text().strip())
  m=PACKAGE/'design/legacy-runtime-bindings.json';cls.pins=ReplayPins('v2',m.relative_to(ROOT).as_posix(),byte_digest(m.read_bytes()),byte_digest((cls.fixture/'config.json').read_bytes()),load(cls.fixture/'baseline.json')['snapshot_digest'])
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def setUp(self):
  self.temp=TemporaryDirectory(prefix='lab-context-case-');self.root=Path(self.temp.name);self.path=self.root/'store';shutil.copytree(self.fixture,self.path);self.clock=Clock();self.sessions=[]
  self.adapter=VerifiedLegacyReadStore(self.path,self.repository,ROOT,self.pins)
 def tearDown(self):
  for session in self.sessions:session.close()
  self.temp.cleanup()
 def session(self,**kwargs):
  args={'expected_profile_sha256':self.row['profile_sha256'],'expected_snapshot_digest':self.snapshot['snapshot_digest'],'subject_ref':'product:cyberalchemy-lab','clock':self.clock,'wall_clock':lambda:1791424453.0}
  args.update(kwargs);session=Session(self.adapter,self.snapshot,**args);self.sessions.append(session);return session
 def test_bounded_views_and_independent_histories(self):
  s=self.session(max_nodes=10,max_edges=15,depth=1);p=s.context();self.observed_packs.append(copy.deepcopy(p));self.assertLessEqual(len(p['ontology_view']['graph']['nodes']),10);self.assertLessEqual(len(p['ontology_view']['graph']['connections']),15)
  self.assertIsNone(p['ontology_view']['canonical_ontology_cut_ref']);self.assertIsNone(p['ontology_view']['ontology_semantic_cursor']);self.assertIsNone(p['ontology_view']['ontology_governance_cursor']);self.assertEqual(len(p['project_history_bindings']),2)
  self.assertTrue(any(x['reference']=='ontology-native-cut' for x in p['reference_diagnostics']));self.assertEqual(p['action_permission'],'none')
 def test_governed_references_resolve_and_unknowns_reported(self):
  p=self.session(references={'assignment_ref':'runtime-context-request:fake','implementation_ref':'implementation:lab-operational-runtime/v1'}).context()
  self.assertTrue(any(r['reference']=='runtime-context-request:fake' and not r['governed_claim'] for r in p['reference_diagnostics']))
  data=self.adapter.replay(require_current=True)
  for r in p['context_view']['selected_governed_references']:self.assertIn(r['version_ref'],data['projection']['subjects'])
 def test_related_implementation_is_not_generator_alias(self):
  p=self.session(references={'implementation_ref':'implementation:cyberalchemy-lab:operational-runtime:v1@decision-0075'}).context()
  self.assertTrue(any(r.get('role')=='implementation_ref' for r in p['context_view']['selected_governed_references']));self.assertIsNone(p['generator_provenance']['governed_implementation_revision']);self.assertEqual(p['generator_provenance']['executable_manifest_binding'],self.snapshot['controls']['executable_manifest'])
 def test_literal_assignment_never_grants_permission(self):
  p=self.session(references={'assignment_ref':'role:assigned-worker'}).context();self.assertEqual(p['action_permission'],'none');self.assertTrue(any(r['reference']=='role:assigned-worker' for r in p['reference_diagnostics']))
 def test_closed_and_new_session_have_no_prior_memory(self):
  s=self.session();s.note('one session private scratch note');p=s.context();self.assertNotIn('private scratch note',json.dumps(p));s.close();self.assertEqual(s._memory,[]);self.assertIsNone(s._pack)
  with self.assertRaisesRegex(RuntimeFault,'closed'):s.context()
  other=self.session();self.assertEqual(other._memory,[]);self.assertNotEqual(s.instance_id,other.instance_id)
 def test_ttl_failure_erases_memory(self):
  s=self.session(ttl=1);s.note('expires');self.clock.value+=2
  with self.assertRaisesRegex(RuntimeFault,'expired'):s.context()
  self.assertEqual(s._memory,[]);self.assertIsNone(s._pack);self.assertTrue(s.closed)
 def test_source_change_erases_memory(self):
  s=self.session();s.note('must disappear');name=next(iter(self.snapshot['materials']));file=self.repository/name;raw=file.read_bytes()
  try:
   file.write_bytes(raw+b'\n')
   with self.assertRaisesRegex(RuntimeFault,'source changed'):s.context()
   self.assertEqual(s._memory,[]);self.assertTrue(s.closed)
  finally:file.write_bytes(raw)
 def test_actual_signed_head_change_invalidates_and_erases(self):
  s=self.session();s.note('old head');store=Store(self.path,self.repository);proposal=example(store,'changed-head');store.apply(proposal,store.authorize(proposal,self.private))
  with self.assertRaisesRegex(RuntimeFault,'head/configuration/state changed'):s.context()
  self.assertEqual(s._memory,[]);self.assertTrue(s.closed)
 def test_invalid_configuration_erases(self):
  s=self.session();s.note('private');path=self.path/'config.json';obj=load(path);obj['owner_ref']='role:forged';path.write_bytes(encoded(sealed({k:v for k,v in obj.items() if k!='digest'})))
  with self.assertRaises(RuntimeFault):s.context()
  self.assertTrue(s.closed);self.assertEqual(s._memory,[])
 def test_snapshot_self_reseal_cannot_supply_context(self):
  snapshot=copy.deepcopy(self.snapshot);snapshot['subjects'][next(iter(snapshot['subjects']))]['effective_state']='forged';snapshot['snapshot_digest']=digest({k:v for k,v in snapshot.items() if k!='snapshot_digest'})
  with self.assertRaisesRegex(RuntimeFault,'independent context source snapshot pin'):Session(self.adapter,snapshot,expected_profile_sha256=self.row['profile_sha256'],expected_snapshot_digest=self.snapshot['snapshot_digest'],subject_ref='product:cyberalchemy-lab')
 def test_context_return_is_detached(self):
  s=self.session();p=s.context();p['action_permission']='forged';self.assertEqual(s.context()['action_permission'],'none')
 def test_limits_and_unknown_root_reject(self):
  with self.assertRaises(RuntimeFault):self.session(max_nodes=101)
  with self.assertRaisesRegex(RuntimeFault,'root unresolved'):self.session(subject_ref='missing:subject')
 def test_session_has_no_effect_or_persistence_methods(self):
  s=self.session()
  for name in ['apply','authorize','dispatch','persist','install']:self.assertFalse(hasattr(s,name))

if __name__=='__main__':unittest.main()
