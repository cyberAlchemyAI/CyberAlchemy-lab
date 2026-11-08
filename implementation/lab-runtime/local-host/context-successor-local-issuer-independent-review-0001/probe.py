import pathlib,hashlib,json,sys,unittest,datetime,os
C=pathlib.Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/context-successor-local-issuer-adapter-0001')
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert h(C/'freeze.json')=='2e49bc067be9340fda9324011b073b579a6a444293a86bc4af6b61c4e8b03a9c'
f=json.loads((C/'freeze.json').read_bytes())
for n,d in f['members'].items():assert h(C/n)==d
sys.path.insert(0,str(C));sys.path.append('/usr/lib/python3/dist-packages')
def audit(event,args):
 if event=='open' and isinstance(args[0],str) and args[0].endswith('branch.snapshot'):raise RuntimeError('PRIVATE_BODY_BLOCKED')
 if event.startswith(('subprocess.','socket.')) or event in ('os.system','os.fork','os.exec'):raise RuntimeError('EFFECT_BLOCKED')
sys.addaudithook(audit)
import adapter as A,test_adapter as T
class Counterexamples(unittest.TestCase):
 def test_failed_authority_marker_can_retry(self):
  m=A.FixtureOneShotModel(A.select(T.NOW));m.claim()
  with self.assertRaises(A.Refused):m.marker(False)
  m.marker(True);m.begin_signed();self.assertEqual(m.state,'SIGNED_OPEN_PENDING')
 def test_failed_signed_close_can_reopen(self):
  s=A.select(T.NOW);m=A.FixtureOneShotModel(s);m.claim();m.marker(True);m.begin_signed()
  facts=T.signed_facts(s);facts['close_ok']=False
  with self.assertRaises(A.Refused):m.observe_signed_fixture(**facts)
  m.marker(True);m.begin_signed();m.observe_signed_fixture(**T.signed_facts(s))
  self.assertEqual(m.state,'SIGNED_CLOSED_FIXTURE_ONLY')
 def test_failed_stage_marker_can_retry(self):
  s=A.select(T.NOW);m=A.FixtureOneShotModel(s);m.claim();m.marker(True);m.begin_signed();m.observe_signed_fixture(**T.signed_facts(s));m.stage_claim()
  with self.assertRaises(A.Refused):m.stage_marker(False)
  m.stage_marker(True);m.issuer_ready(rows=1570,current=True,issuer_local=True,scope_rechecked=True)
  self.assertEqual(m.state,'AUTH_WRITE_ELIGIBLE_MODEL_ONLY')
 def test_no_attestation_transition_before_prewrite(self):
  s=A.select(T.NOW);m=A.FixtureOneShotModel(s);m.claim();m.marker(True);m.begin_signed();m.observe_signed_fixture(**T.signed_facts(s));m.stage_claim();m.stage_marker(True)
  m.issuer_ready(rows=1570,current=True,issuer_local=True,scope_rechecked=True)
  self.assertEqual(m.state,'AUTH_WRITE_ELIGIBLE_MODEL_ONLY')
suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(T),unittest.defaultTestLoader.loadTestsFromTestCase(Counterexamples)])
r=unittest.TextTestRunner(verbosity=2).run(suite)
current=A.select();print(json.dumps({'tests':r.testsRun,'counterexamples':4,'current_selection_status':current['status'],'period_end':current['source_period_end'],'actual_signed_scope':current['scope_actual'],'effect':'UNRUN'}))
for n,d in f['members'].items():assert h(C/n)==d
sys.exit(not r.wasSuccessful())
