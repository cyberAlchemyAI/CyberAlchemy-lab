"""Failed native process outputs survive before any success validation."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_cal_constructor_observer_test',HERE/'construction_runner.py');R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)
class Observation(unittest.TestCase):
 def test_actual_failure_retains_output_without_pass_outcome(self):
  with tempfile.TemporaryDirectory(prefix='cal-native-observation-') as tmp:
   root=Path(tmp)/'runtime/repository';root.mkdir(parents=True,mode=0o700);private=root.parent/'.cal-runtime';private.mkdir(mode=0o700)
   raw=R.C.encoded({'members':[]});(root/'.cal-package-manifest.json').write_bytes(raw);receipt=R.C.encoded({'phase':'construct-context'});R.C.atomic_control(private/'installation.json',receipt)
   with self.assertRaisesRegex(ValueError,'outputs retained'):R.observe(root,R.C.sha(raw),R.C.sha(receipt),b'actual child stdout\n',b'actual causal stderr\n',1)
   attempts=list((private/'construction-attempts').iterdir());self.assertEqual(len(attempts),1);attempt=attempts[0]
   self.assertEqual((attempt/'stdout.log').read_bytes(),b'actual child stdout\n');self.assertEqual((attempt/'stderr.log').read_bytes(),b'actual causal stderr\n');v=json.loads((attempt/'observation.json').read_bytes());self.assertEqual(v['returncode'],1);self.assertEqual(v['result'],'PROCESS-EXITED');self.assertFalse((private/'construction-outcome.json').exists())
if __name__=='__main__':unittest.main()
