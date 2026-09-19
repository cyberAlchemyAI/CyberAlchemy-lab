import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from check import assess
from support import ROOT, LAB, PACKAGE, load, dump, binding
class Receipt(unittest.TestCase):
    def setUp(self): self.record=load(PACKAGE/'fixtures/valid/receipt-record.json')
    def reject(self,message):
        with self.assertRaisesRegex(ValueError,message): assess(self.record)
    def test_replay(self):
        result=assess(self.record); self.assertTrue(result['replay_matches']); self.assertTrue(result['local_replay_performed'])
        for key in ['historical_actor_authenticated','external_effect_proven','action_authorized']: self.assertFalse(result[key])
    def test_code_drift(self):
        self.record['implementation']['sha256']='0'*64; self.reject('Bound bytes changed')
    def test_input_drift(self):
        self.record['input']['sha256']='0'*64; self.reject('Bound bytes changed')
    def test_output_drift(self):
        self.record['stdout']['sha256']='0'*64; self.reject('Bound bytes changed')
    def test_snapshot_drift(self):
        self.record['execution_snapshot']['sha256']='0'*64; self.reject('Bound bytes changed')
    def test_result_disagrees(self):
        self.record['reported_result']='invalid-input'; self.reject('Result and exit code disagree')
    def test_false_exit(self):
        self.record.update(exit_code=2,reported_result='invalid-input'); self.reject('Replay exit code mismatch')
    def test_runtime(self):
        self.record['python_version']='other'; self.reject('Python runtime differs')
    def test_wrong_implementation(self):
        self.record['implementation']=self.record['input']; self.reject('Unsupported implementation')
    def test_wrong_input(self):
        self.record['input']=self.record['stdout']; self.reject('Unsupported replay input')
    def test_forged_stdout(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            path=Path(d)/'stdout.json'; dump(path,{'forged':True}); self.record['stdout']=binding(path); self.reject('Replay stdout mismatch')
    def test_forged_stderr(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            path=Path(d)/'stderr.txt'; path.write_text('unexpected'); self.record['stderr']=binding(path); self.reject('Replay stderr mismatch')
    def test_stream_alias(self):
        self.record['stderr']=self.record['stdout']; self.reject('must be distinct')
    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'receipt.json'
            for expected in [0,2]:
                if expected==2: self.record['python_version']='other'
                dump(path,self.record); result=subprocess.run([sys.executable,str(ROOT/'check.py'),str(path)],capture_output=True,text=True)
                self.assertEqual(result.returncode,expected,result.stdout+result.stderr); json.loads(result.stdout)
if __name__=='__main__': unittest.main()
