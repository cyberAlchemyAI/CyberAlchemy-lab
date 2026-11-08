"""Exercise the real pure accounting functions without constructing a host fixture."""
import ast,copy,os,signal,subprocess,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent

def function(file,name):
 tree=ast.parse((HERE/file).read_bytes());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);scope={"os":os,"signal":signal,"subprocess":subprocess};exec(compile(ast.Module(body=[node],type_ignores=[]),str(HERE/file),'exec'),scope);return scope[name]
class Accounting(unittest.TestCase):
 def setUp(self):
  self.pass_bucket=function('regression.py','bucket_pass');self.terminalize=function('regression_worker.py','terminalize');self.ids=['fixture.py:Tests.test_one','fixture.py:Tests.test_two'];self.rows=[{'id':i,'executed':True,'result':'PASS'} for i in self.ids];self.result={'result':'PASS','tests_run':2,'exact_case_set':True,'all_methods_executed':True,'entry_guard_passed':True,'exit_guard_passed':True,'fixture_errors':[],'execution_error':None,'cases':self.rows}
 def test_complete_bucket_and_exact_unexecuted_accounting(self):
  self.assertTrue(self.pass_bucket(self.result,self.ids,0,False));rows,exact,executed=self.terminalize(self.ids,self.rows[:1],[],1,'interrupted','actual UTC');self.assertTrue(exact);self.assertFalse(executed);self.assertFalse(rows[1]['executed']);self.assertEqual(rows[1]['result'],'WORKER-INTERRUPTED')
 def test_teardown_error_and_exit_failure_cannot_be_erased_by_method_passes(self):
  for changes in ({'fixture_errors':[{'fixture':'tearDownClass','result':'ERROR'}]},{'exit_guard_passed':False},{'execution_error':'actual exit refusal'},{'result':'FAIL'},{'tests_run':1},{'all_methods_executed':False},{'exact_case_set':False}):
   with self.subTest(changes=changes):self.assertFalse(self.pass_bucket({**self.result,**changes},self.ids,0,False))
 def test_nonzero_exit_or_timeout_after_pass_receipt_refuses(self):
  self.assertFalse(self.pass_bucket(self.result,self.ids,1,False));self.assertFalse(self.pass_bucket(self.result,self.ids,0,True))
 def test_changed_or_duplicate_case_set_refuses(self):
  for cases in (self.rows[:1],[self.rows[0],self.rows[0]],[{**self.rows[0],'executed':False},self.rows[1]]):self.assertFalse(self.pass_bucket({**self.result,'cases':cases},self.ids,0,False))
 def test_worker_without_bootstrap_refuses_before_test_or_output_creation(self):
  child=subprocess.run([sys.executable,'-B',str(HERE/'regression_worker.py'),'--bucket','invented','--runner-sha256','0'*64,'--run-id','should-not-run'],capture_output=True,check=False);self.assertNotEqual(child.returncode,0);self.assertIn(b'requires the selected native bootstrap',child.stderr)
class ProcessGroup(unittest.TestCase):
 def test_timeout_stops_own_grandchild_and_preserves_unrelated_process(self):
  run=function('regression.py','run_owned_worker')
  unrelated=subprocess.Popen([sys.executable,'-B','-c','import time;time.sleep(60)'])
  try:
   with tempfile.TemporaryFile() as output:
    script="import subprocess,sys,time;child=subprocess.Popen([sys.executable,'-B','-c','import time;time.sleep(60)']);print(child.pid,flush=True);time.sleep(60)"
    code,expired=run([sys.executable,'-B','-c',script],output=output,cwd=HERE,environment={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},timeout=.4)
    self.assertTrue(expired);self.assertNotEqual(code,0);output.seek(0);pid=int(output.read());status=Path('/proc')/str(pid)/'stat'
    if status.exists():self.assertEqual(status.read_text().split()[2],'Z')
    self.assertIsNone(unrelated.poll())
  finally:unrelated.terminate();unrelated.wait()
if __name__=='__main__':unittest.main()

