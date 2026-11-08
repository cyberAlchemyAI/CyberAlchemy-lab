import pathlib,types,hashlib,subprocess,json,unittest
from unittest.mock import patch
C=pathlib.Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/context-public-policy-namespace-probe-0002')
b=(C/'observer.py').read_bytes();assert hashlib.sha256(b).hexdigest()=='cca805d3617311c1a6529db5500f2c7547ecaa6d2b713ce32ee1e711b355c3fc'
O=types.ModuleType('exact_observer');O.__file__=str(C/'observer.py');exec(compile(b,O.__file__,'exec'),O.__dict__)
class Cases(unittest.TestCase):
 def test_no_reread_and_child_digest_refusal(self):
  with patch.object(pathlib.Path,'read_bytes',side_effect=AssertionError('PATH_RELOAD')): argv=O.checked_child_argv('--preflight')
  self.assertEqual(argv[:4],['/usr/bin/python3.14','-I','-B','-c'])
  argv[-1]=argv[-1].replace(O.RELEASE_SHA,'0'*64)
  p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=10)
  self.assertNotEqual(p.returncode,0); self.assertEqual(p.stdout,b'');self.assertIn(b'RELEASE_BUFFER_DRIFT',p.stderr)
 def test_parent_drift_refuses(self):
  with patch.object(O,'raw',O.raw+b'\n'),self.assertRaisesRegex(O.Refused,'CHECKED_CHILD_PROGRAM'):O.checked_child_argv('--preflight')
 def test_missing_release_path_still_preflights(self):
  missing=C/'independent-missing-release.py';self.assertFalse(missing.exists())
  with patch.object(O,'RELEASE',missing): argv=O.checked_child_argv('--preflight')
  p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20)
  self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(p.stderr,b'');self.assertTrue(json.loads(p.stdout)['host']['name_absent'])
 def test_selected_runtime_dependency(self):
  p=subprocess.run([O.PYTHON,'-I','-B','-c','import jsonschema; print(jsonschema.__file__)'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=10)
  self.assertEqual(p.returncode,0);self.assertEqual(p.stderr,b'');self.assertEqual(p.stdout.strip(),b'/usr/lib/python3/dist-packages/jsonschema/__init__.py')
 def test_disabled_and_absent(self):
  self.assertFalse(O.EFFECT_ENABLED);self.assertFalse(O.R.EFFECT_ENABLED)
  self.assertFalse(O.OBSERVATION.exists());self.assertFalse(O.R.ATTEMPT.exists())
unittest.main(verbosity=2)
